"""Operações de renda recorrente, renda pontual e bônus (SPEC-056, SPEC-057, SPEC-058).

Extraídas de AuthService (dívida técnica DT-03, Mover Função) sem mudança de comportamento.
Dependem de atributos e métodos de AuthService (db, security, clock, require_category_owner,
local_today, month_bounds, _commit_or_existing), que as herda.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.application.errors import AuthError
from app.infrastructure.models import (
    AccountRecord,
    BonusRecord,
    OneTimeIncomeRecord,
    RecurringIncomeRecord,
    UserRecord,
)


class OperacoesRenda:
    def recurring_income_output(self, record: RecurringIncomeRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "description": self.security.decrypt(record.description_encrypted),
            "amount": record.amount,
            "account_id": record.account_id,
            "starts_on": record.starts_on,
        }

    def list_recurring_incomes(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        return [
            self.recurring_income_output(record)
            for record in self.db.scalars(
                select(RecurringIncomeRecord)
                .where(RecurringIncomeRecord.user_id == user_id)
                .order_by(RecurringIncomeRecord.starts_on, RecurringIncomeRecord.id)
            )
        ]

    def create_recurring_income(
        self,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        account_id: uuid.UUID | None,
        starts_on: date | None,
        idempotency_key: str,
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        existing = self.db.scalar(
            select(RecurringIncomeRecord)
            .where(
                RecurringIncomeRecord.user_id == user_id,
                RecurringIncomeRecord.idempotency_key == idempotency_key,
            )
            .with_for_update()
        )
        if existing is not None:
            self.db.rollback()
            return self.recurring_income_output(existing)
        if account_id is not None and self.db.get(AccountRecord, account_id) is None:
            self.db.rollback()
            raise AuthError("account_not_found", 404)
        if account_id is not None and self.db.get(AccountRecord, account_id).user_id != user_id:
            self.db.rollback()
            raise AuthError("account_not_found", 404)
        record = RecurringIncomeRecord(
            user_id=user_id,
            account_id=account_id,
            description_encrypted=self.security.encrypt(description),
            amount=amount,
            starts_on=starts_on or self.local_today(),
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        existing = self._commit_or_existing(
            RecurringIncomeRecord, user_id=user_id, idempotency_key=idempotency_key
        )
        if existing is not None:
            return self.recurring_income_output(existing)
        return self.recurring_income_output(record)

    def update_recurring_income(
        self, user_id: uuid.UUID, income_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        record = self.db.scalar(
            select(RecurringIncomeRecord)
            .where(RecurringIncomeRecord.id == income_id, RecurringIncomeRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("recurring_income_not_found", 404)
        if values.get("description") is not None:
            record.description_encrypted = self.security.encrypt(str(values["description"]))
        for key in ("amount", "starts_on"):
            if values.get(key) is not None:
                setattr(record, key, values[key])
        self.db.commit()
        return self.recurring_income_output(record)

    def delete_recurring_income(self, user_id: uuid.UUID, income_id: uuid.UUID) -> None:
        record = self.db.scalar(
            select(RecurringIncomeRecord)
            .where(RecurringIncomeRecord.id == income_id, RecurringIncomeRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("recurring_income_not_found", 404)
        self.db.delete(record)
        self.db.commit()

    def one_time_income_output(self, record: OneTimeIncomeRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "description": self.security.decrypt(record.description_encrypted),
            "amount": record.amount,
            "account_id": record.account_id,
            "occurred_on": record.occurred_on,
        }

    def list_one_time_incomes(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        return [
            self.one_time_income_output(record)
            for record in self.db.scalars(
                select(OneTimeIncomeRecord)
                .where(OneTimeIncomeRecord.user_id == user_id)
                .order_by(OneTimeIncomeRecord.occurred_on, OneTimeIncomeRecord.id)
            )
        ]

    def create_one_time_income(
        self,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        account_id: uuid.UUID | None,
        occurred_on: date,
        idempotency_key: str,
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        existing = self.db.scalar(
            select(OneTimeIncomeRecord)
            .where(
                OneTimeIncomeRecord.user_id == user_id,
                OneTimeIncomeRecord.idempotency_key == idempotency_key,
            )
            .with_for_update()
        )
        if existing is not None:
            self.db.rollback()
            return self.one_time_income_output(existing)
        if account_id is not None:
            account = self.db.get(AccountRecord, account_id)
            if account is None or account.user_id != user_id:
                self.db.rollback()
                raise AuthError("account_not_found", 404)
        record = OneTimeIncomeRecord(
            user_id=user_id,
            account_id=account_id,
            description_encrypted=self.security.encrypt(description),
            amount=amount,
            occurred_on=occurred_on,
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        existing = self._commit_or_existing(
            OneTimeIncomeRecord, user_id=user_id, idempotency_key=idempotency_key
        )
        if existing is not None:
            return self.one_time_income_output(existing)
        return self.one_time_income_output(record)

    def update_one_time_income(
        self, user_id: uuid.UUID, income_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        record = self.db.scalar(
            select(OneTimeIncomeRecord)
            .where(OneTimeIncomeRecord.id == income_id, OneTimeIncomeRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("one_time_income_not_found", 404)
        if values.get("description") is not None:
            record.description_encrypted = self.security.encrypt(str(values["description"]))
        for key in ("amount", "occurred_on"):
            if values.get(key) is not None:
                setattr(record, key, values[key])
        self.db.commit()
        return self.one_time_income_output(record)

    def delete_one_time_income(self, user_id: uuid.UUID, income_id: uuid.UUID) -> None:
        record = self.db.scalar(
            select(OneTimeIncomeRecord)
            .where(OneTimeIncomeRecord.id == income_id, OneTimeIncomeRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("one_time_income_not_found", 404)
        self.db.delete(record)
        self.db.commit()

    def bonus_output(self, record: BonusRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "description": self.security.decrypt(record.description_encrypted),
            "amount": record.amount,
            "periodicity": record.periodicity,
            "starts_on": record.starts_on,
            "reference_month": record.reference_month,
        }

    def list_bonuses(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        return [
            self.bonus_output(record)
            for record in self.db.scalars(
                select(BonusRecord)
                .where(BonusRecord.user_id == user_id)
                .order_by(BonusRecord.starts_on, BonusRecord.id)
            )
        ]

    def create_bonus(
        self,
        user_id: uuid.UUID,
        description: str,
        amount: Decimal,
        periodicity: str,
        starts_on: date | None,
        reference_month: int | None,
        idempotency_key: str,
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        existing = self.db.scalar(
            select(BonusRecord)
            .where(BonusRecord.user_id == user_id, BonusRecord.idempotency_key == idempotency_key)
            .with_for_update()
        )
        if existing is not None:
            self.db.rollback()
            return self.bonus_output(existing)
        record = BonusRecord(
            user_id=user_id,
            description_encrypted=self.security.encrypt(description),
            amount=amount,
            periodicity=periodicity,
            starts_on=starts_on or self.local_today(),
            reference_month=reference_month,
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        existing = self._commit_or_existing(
            BonusRecord, user_id=user_id, idempotency_key=idempotency_key
        )
        if existing is not None:
            return self.bonus_output(existing)
        return self.bonus_output(record)

    def update_bonus(
        self, user_id: uuid.UUID, bonus_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        record = self.db.scalar(
            select(BonusRecord)
            .where(BonusRecord.id == bonus_id, BonusRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("bonus_not_found", 404)
        periodicity = values.get("periodicity") or record.periodicity
        reference_month = values.get("reference_month")
        if reference_month is None:
            reference_month = record.reference_month
        if periodicity == "annual" and reference_month is None:
            raise AuthError("reference_month_required", 400)
        if periodicity == "monthly":
            reference_month = None
        if values.get("description") is not None:
            record.description_encrypted = self.security.encrypt(str(values["description"]))
        for key in ("amount", "starts_on"):
            if values.get(key) is not None:
                setattr(record, key, values[key])
        record.periodicity, record.reference_month = str(periodicity), reference_month
        self.db.commit()
        return self.bonus_output(record)

    def delete_bonus(self, user_id: uuid.UUID, bonus_id: uuid.UUID) -> None:
        record = self.db.scalar(
            select(BonusRecord)
            .where(BonusRecord.id == bonus_id, BonusRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("bonus_not_found", 404)
        self.db.delete(record)
        self.db.commit()

    def income_summary(self, user_id: uuid.UUID, competence: date) -> dict[str, Decimal | str]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        month_start = competence.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        monthly_recurring = sum(
            (
                record.amount
                for record in self.db.scalars(
                    select(RecurringIncomeRecord).where(
                        RecurringIncomeRecord.user_id == user_id,
                        RecurringIncomeRecord.starts_on < next_month,
                    )
                )
            ),
            Decimal("0"),
        )
        one_time = sum(
            (
                record.amount
                for record in self.db.scalars(
                    select(OneTimeIncomeRecord).where(
                        OneTimeIncomeRecord.user_id == user_id,
                        OneTimeIncomeRecord.occurred_on >= month_start,
                        OneTimeIncomeRecord.occurred_on < next_month,
                    )
                )
            ),
            Decimal("0"),
        )
        bonus = sum(
            (
                record.amount
                for record in self.db.scalars(
                    select(BonusRecord).where(BonusRecord.user_id == user_id)
                )
                if (record.periodicity == "monthly" and record.starts_on <= month_start)
                or (
                    record.periodicity == "annual"
                    and record.starts_on.year == month_start.year
                    and record.reference_month == month_start.month
                )
            ),
            Decimal("0"),
        )
        return {
            "competence": month_start.strftime("%Y-%m"),
            "recurring_income": monthly_recurring,
            "one_time_income": one_time,
            "bonus": bonus,
            "total": monthly_recurring + one_time + bonus,
        }
