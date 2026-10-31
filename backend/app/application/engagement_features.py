"""SPEC-050 (score por grupo), SPEC-051 (conquistas) e SPEC-052 (tour de primeiro acesso)."""

import uuid
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from statistics import median
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.application.auth import AuthError, AuthService
from app.infrastructure.models import (
    AchievementRecord,
    BonusRecord,
    ExpenseRecord,
    HealthScoreRecord,
    OnboardingTourRecord,
    OneTimeIncomeRecord,
    PrivacySettingsRecord,
    RecurringIncomeRecord,
    SimulationRecord,
    UserRecord,
)

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
MIN_GROUP_SIZE = 30
TWO = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return value.quantize(TWO, ROUND_HALF_EVEN)


def _shift(month: date, delta: int) -> date:
    index = month.year * 12 + month.month - 1 + delta
    return date(index // 12, index % 12 + 1, 1)


class EngagementFeaturesService:
    def __init__(self, db, auth: AuthService):
        self.db, self.auth = db, auth

    def _month_now(self) -> date:
        return self.auth.clock().astimezone(SAO_PAULO).date().replace(day=1)

    # ------------------------------------------------------------------ SPEC-050
    def privacy(self, user_id: uuid.UUID) -> dict[str, bool]:
        record = self.db.get(PrivacySettingsRecord, user_id)
        return {
            "score_benchmark_enabled": True if record is None else record.score_benchmark_enabled
        }

    def set_privacy(self, user_id: uuid.UUID, enabled: bool) -> dict[str, bool]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        record = self.db.get(PrivacySettingsRecord, user_id)
        if record is None:
            record = PrivacySettingsRecord(user_id=user_id)
            self.db.add(record)
        record.score_benchmark_enabled, record.updated_at = enabled, self.auth.clock()
        self.db.commit()
        return self.privacy(user_id)

    def _savings_rate(self, user_id: uuid.UUID, competence: date) -> Decimal | None:
        summary = self.auth.balance_summary(user_id, competence)
        income = Decimal(summary["total"])
        if income <= 0:
            return None
        return (income - Decimal(summary["expenses"])) / income * Decimal("100")

    def benchmark(self, user_id: uuid.UUID, competence: date | None) -> dict[str, object]:
        owner = self.auth.require_category_owner(user_id)
        result: dict[str, object] = {
            "enabled": self.privacy(user_id)["score_benchmark_enabled"],
            "available": False,
            "reason": None,
            "profile": owner.investor_profile,
            "competence": None,
            "minimum_group_size": MIN_GROUP_SIZE,
            "my_score": None,
            "group_average_score": None,
            "group_median_score": None,
            "my_savings_rate": None,
            "group_average_savings_rate": None,
            "group_median_savings_rate": None,
        }
        if not result["enabled"]:
            return {**result, "reason": "opted_out"}
        if owner.investor_profile is None:
            return {**result, "reason": "no_profile"}
        query = select(HealthScoreRecord).where(HealthScoreRecord.user_id == user_id)
        if competence is not None:
            query = query.where(HealthScoreRecord.competence == competence.replace(day=1))
        mine = self.db.scalar(query.order_by(HealthScoreRecord.competence.desc()).limit(1))
        if mine is None:
            return {**result, "reason": "no_score"}
        # Grupo: mesmo perfil, mesma competência e sem opt-out (quem desativa também sai do grupo).
        opted_out = select(PrivacySettingsRecord.user_id).where(
            PrivacySettingsRecord.score_benchmark_enabled.is_(False)
        )
        peers = self.db.execute(
            select(HealthScoreRecord.user_id, HealthScoreRecord.score)
            .join(UserRecord, UserRecord.id == HealthScoreRecord.user_id)
            .where(
                UserRecord.investor_profile == owner.investor_profile,
                HealthScoreRecord.competence == mine.competence,
                HealthScoreRecord.user_id.not_in(opted_out),
            )
        ).all()
        base = {
            **result,
            "competence": mine.competence.strftime("%Y-%m"),
            "my_score": mine.score,
            "my_savings_rate": (
                None if (rate := self._savings_rate(user_id, mine.competence)) is None else _q(rate)
            ),
        }
        # INV-001: abaixo do mínimo nada é exibido (nem o tamanho do grupo).
        if len(peers) < MIN_GROUP_SIZE:
            return {**base, "reason": "insufficient_group"}
        scores = [Decimal(score) for _, score in peers]
        rates = [
            rate
            for peer_id, _ in peers
            if (rate := self._savings_rate(peer_id, mine.competence)) is not None
        ]
        savings_ok = len(rates) >= MIN_GROUP_SIZE
        return {
            **base,
            "available": True,
            "group_average_score": _q(sum(scores) / len(scores)),
            "group_median_score": _q(Decimal(median(scores))),
            "group_average_savings_rate": _q(sum(rates) / len(rates)) if savings_ok else None,
            "group_median_savings_rate": _q(Decimal(median(rates))) if savings_ok else None,
        }

    # ------------------------------------------------------------------ SPEC-051
    CATALOG = (
        (
            "named_goal_reached",
            "Meta conquistada",
            "Atingir o valor-alvo de uma meta nomeada (RF-40).",
        ),
        (
            "budget_month_on_track",
            "Mês no orçamento",
            "Fechar o mês anterior dentro de todas as metas de gasto (RF-14/RF-15).",
        ),
        (
            "three_months_on_budget",
            "3 meses no orçamento",
            "Ficar 3 meses seguidos dentro das metas de gasto.",
        ),
    )

    def _month_on_budget(self, user_id: uuid.UUID, month: date) -> bool:
        goals = [
            row
            for row in self.auth.budget_progress(user_id, month)
            if row["kind"] != "income_total"
        ]
        return bool(goals) and all(Decimal(row["percentage"]) <= 100 for row in goals)

    def achievements(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        self.auth.require_category_owner(user_id)
        goals = self.auth.list_named_asset_goals(user_id)
        named = max((Decimal(goal["progress_percent"]) for goal in goals), default=Decimal("0"))
        previous = _shift(self._month_now(), -1)
        streak = 0
        for offset in range(3):
            if not self._month_on_budget(user_id, _shift(previous, -offset)):
                break
            streak += 1
        progress = {
            "named_goal_reached": min(Decimal("100"), named),
            "budget_month_on_track": Decimal("100") if streak >= 1 else Decimal("0"),
            "three_months_on_budget": _q(Decimal(streak) * 100 / 3),
        }
        unlocked = {
            record.code: record
            for record in self.db.scalars(
                select(AchievementRecord).where(AchievementRecord.user_id == user_id)
            )
        }
        for code, value in progress.items():
            if value >= 100 and code not in unlocked:
                record = AchievementRecord(
                    user_id=user_id, code=code, unlocked_at=self.auth.clock()
                )
                self.db.add(record)
                try:
                    self.db.commit()
                except IntegrityError:  # concessão concorrente: mantém a primeira
                    self.db.rollback()
                    continue
                unlocked[code] = record
                # R05: notificação in-app respeitando preferências (SPEC-039). Apenas cosmético.
                self.auth.create_notification(user_id, "achievement_unlocked", code)
        return [
            {
                "code": code,
                "title": title,
                "description": description,
                "unlocked": code in unlocked,
                "unlocked_at": unlocked[code].unlocked_at if code in unlocked else None,
                "progress_percent": Decimal("100") if code in unlocked else progress[code],
            }
            for code, title, description in self.CATALOG
        ]

    # ------------------------------------------------------------------ SPEC-052
    def _has(self, model, user_id: uuid.UUID) -> bool:
        return bool(
            self.db.scalar(select(func.count()).select_from(model).where(model.user_id == user_id))
        )

    def tour(self, user_id: uuid.UUID) -> dict[str, object]:
        user = self.db.get(UserRecord, user_id)
        if user is None:
            raise AuthError("invalid_session")
        record = self.db.get(OnboardingTourRecord, user_id)
        status = "not_started" if record is None else record.status
        # Perfil não respondido não recebe classificação inventada: usa o roteiro didático.
        variant = "concise" if user.investor_profile in ("moderado", "arrojado") else "didactic"
        has_income = any(
            self._has(model, user_id)
            for model in (RecurringIncomeRecord, OneTimeIncomeRecord, BonusRecord)
        )
        steps = [
            ("first_income", "transactions", has_income),
            ("first_expense", "transactions", self._has(ExpenseRecord, user_id)),
            ("investor_quiz", "account", user.investor_profile is not None),
            ("simulator", "investments", self._has(SimulationRecord, user_id)),
        ]
        return {
            "status": status,
            "show": status in ("not_started", "in_progress"),
            "step": 0 if record is None else record.step,
            "variant": variant,
            "profile": user.investor_profile,
            "steps": [{"key": key, "tab": tab, "done": done} for key, tab, done in steps],
        }

    def update_tour(self, user_id: uuid.UUID, action: str, step: int | None) -> dict[str, object]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        record = self.db.get(OnboardingTourRecord, user_id)
        if record is None:
            record = OnboardingTourRecord(user_id=user_id, status="not_started", step=0)
            self.db.add(record)
        transitions = {
            "start": ("in_progress", 0),
            "advance": ("in_progress", step if step is not None else record.step + 1),
            "complete": ("completed", record.step),
            "skip": ("skipped", record.step),
            "reopen": ("in_progress", 0),
        }
        record.status, record.step = transitions[action]
        record.step = max(0, min(3, record.step))
        record.updated_at = self.auth.clock()
        self.db.commit()
        return self.tour(user_id)
