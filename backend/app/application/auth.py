import hashlib
import json
import math
import secrets
import uuid
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import jwt
from sqlalchemy import delete, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.domain.cartao import competencia_da_fatura, dividir_parcelas, somar_meses
from app.domain.financeiro import aporte_necessario
from app.domain.financial_stress import StressScenario, simulate_stress
from app.domain.financing import simulate_financing
from app.domain.identity import User, normalize_email
from app.infrastructure.account_deletion import DeletionJournal, erase_user
from app.infrastructure.email_delivery import EmailConfirmationDelivery, EmailDeliveryError
from app.infrastructure.models import (
    AccountRecord,
    AdvancedMetricsPreferenceRecord,
    AuditLogRecord,
    BonusRecord,
    BudgetGoalRecord,
    CategoryRecord,
    ConfirmedFinancingRecord,
    CreditCardRecord,
    DefaultCategoryVisibilityRecord,
    EmailConfirmationTokenRecord,
    ExpenseRecord,
    HealthScoreRecord,
    HealthScoreRuleRecord,
    InvestmentAllocationTargetRecord,
    InvestmentAssetClassRecord,
    LoginAttemptRecord,
    MarketIndicatorRecord,
    NamedAssetGoalRecord,
    NetWorthItemRecord,
    NetWorthSnapshotRecord,
    NotificationDeliveryRecord,
    NotificationPreferenceRecord,
    NotificationRecord,
    OfficialDocumentRecord,
    OneTimeIncomeRecord,
    PasswordResetTokenRecord,
    PublicCompanyRecord,
    PushDeviceRecord,
    RecurringIncomeRecord,
    RefreshRecord,
    SessionRecord,
    SimulationRecord,
    TreasuryBondRateRecord,
    UsageEventRecord,
    UserPreferencesRecord,
    UserRecord,
    WatchlistRecord,
)
from app.infrastructure.security import Security, token_digest


class AuthError(Exception):
    def __init__(
        self,
        code: str,
        status: int = 401,
        retry_after: int | None = None,
        manual_entry_permitted: bool = False,
    ):
        self.code = code
        self.status = status
        self.retry_after = retry_after
        self.manual_entry_permitted = manual_entry_permitted


class SessionNotFoundError(AuthError):
    """Foreign and nonexistent session IDs intentionally share one public error."""

    def __init__(self):
        super().__init__("session_not_found", 404)


DEFAULT_CATEGORIES = (
    {"key": "moradia", "name": "Moradia", "color": "#5B8FF9"},
    {"key": "custos-basicos", "name": "Custos básicos", "color": "#61DDAA"},
    {"key": "alimentacao", "name": "Alimentação", "color": "#F6BD16"},
    {"key": "locomocao", "name": "Locomoção", "color": "#7262FD"},
    {"key": "saude", "name": "Saúde", "color": "#78D3F8"},
    {"key": "educacao", "name": "Educação", "color": "#9661BC"},
    {"key": "lazer", "name": "Lazer", "color": "#F6903D"},
    {"key": "investimentos", "name": "Investimentos", "color": "#008685"},
    {"key": "doacoes", "name": "Doações", "color": "#F08BB4"},
)
DEFAULT_CATEGORY_KEYS = {category["key"] for category in DEFAULT_CATEGORIES}
NOTIFICATION_KINDS = (
    "invoice_due",
    "budget_goal_exceeded",
    "watchlist_document",
    "recurring_expense_due",
    "achievement_unlocked",
    "monthly_summary",
)
NOTIFICATION_CONTENT = {
    "invoice_due": (
        "Fatura próxima do vencimento",
        "Revise sua fatura antes da data de vencimento.",
    ),
    "budget_goal_exceeded": ("Meta ultrapassada", "Uma meta de orçamento foi ultrapassada."),
    "watchlist_document": (
        "Novo documento na watchlist",
        "Há um novo documento para uma empresa acompanhada.",
    ),
    "recurring_expense_due": (
        "Despesa recorrente próxima do vencimento",
        "Uma despesa recorrente está próxima da data de vencimento.",
    ),
    "achievement_unlocked": (
        "Nova conquista desbloqueada",
        "Parabéns! Você desbloqueou uma conquista. Veja seu progresso na tela de conquistas.",
    ),
    "monthly_summary": (
        "Resumo mensal disponível",
        "O resumo financeiro do mês anterior foi gerado.",
    ),
}
QUIZ_QUESTIONS = (
    {
        "id": "knowledge",
        "prompt": "Como você avalia seu conhecimento sobre investimentos?",
        "options": [
            "Ainda estou começando",
            "Conheço os conceitos básicos",
            "Tenho experiência prática",
        ],
    },
    {
        "id": "loss",
        "prompt": "Como reagiria a uma queda temporária de 15%?",
        "options": [
            "Resgataria para evitar novas perdas",
            "Esperaria antes de decidir",
            "Manteria o plano de longo prazo",
        ],
    },
    {
        "id": "horizon",
        "prompt": "Qual é o horizonte principal para investir?",
        "options": ["Até 1 ano", "De 1 a 5 anos", "Mais de 5 anos"],
    },
    {
        "id": "liquidity",
        "prompt": "Quanto desse valor pode ficar investido sem uso imediato?",
        "options": ["Quase nada", "Uma parte", "A maior parte"],
    },
    {
        "id": "volatility",
        "prompt": "Qual oscilação no valor investido você aceita?",
        "options": ["Baixa", "Moderada", "Maior, buscando retorno potencial"],
    },
)
PROFILE_GUIDANCE = {
    "conservador": (
        "Priorize liquidez, previsibilidade e entendimento dos riscos antes de assumir oscilações."
    ),
    "moderado": (
        "Busque equilíbrio entre estabilidade e crescimento, diversificando com atenção ao prazo."
    ),
    "arrojado": "Oscilações podem ser maiores; diversificação e prazo longo continuam essenciais.",
}


class AuthService:
    def __init__(
        self,
        db: Session,
        settings: Settings,
        security: Security,
        clock: Callable[[], datetime] | None = None,
        email_delivery: EmailConfirmationDelivery | None = None,
        channel_delivery: dict[str, object] | None = None,
    ):
        self.db, self.settings, self.security = db, settings, security
        self.email_delivery = email_delivery
        # SPEC-061: adaptadores por canal externo ({"email": ..., "push": ...}).
        self.channel_delivery = channel_delivery or {}
        self.clock = clock or (lambda: datetime.now(UTC))

    def public_user(self, record: UserRecord) -> User:
        return User(
            record.id,
            self.security.decrypt(record.name_encrypted),
            self.security.decrypt(record.email_encrypted),
            record.role,
            record.email_verified_at is not None,
            record.investor_profile,
        )

    def is_initial_admin(self, user: UserRecord) -> bool:
        configured = self.settings.initial_admin_email
        if configured is None or user.email_verified_at is None:
            return False
        return (
            normalize_email(configured) == self.security.decrypt(user.email_encrypted)
            and self.db.scalar(select(UserRecord.id).where(UserRecord.role == "administrador"))
            is None
        )

    def require_admin(self, user: User) -> None:
        if user.role != "administrador":
            raise AuthError("admin_access_denied", 403)

    def list_admin_users(
        self,
        query: str | None,
        status: str | None,
        profile: str | None,
        page: int,
        page_size: int,
        actor_id: uuid.UUID,
    ) -> dict[str, object]:
        # Names and e-mails are encrypted at rest, therefore filter after decryption.
        # This admin-only capability deliberately returns no financial relation or payload.
        if profile not in {None, "unassigned"} or status not in {None, "active"}:
            matching: list[dict[str, object]] = []
        else:
            needle = query.strip().casefold() if query else ""
            matching = []
            records = self.db.scalars(select(UserRecord).order_by(UserRecord.created_at.desc()))
            for record in records:
                name = self.security.decrypt(record.name_encrypted)
                email = self.security.decrypt(record.email_encrypted)
                if needle and needle not in name.casefold() and needle not in email.casefold():
                    continue
                matching.append(
                    {
                        "id": record.id,
                        "name": name,
                        "email": email,
                        "created_at": record.created_at,
                        "investor_profile": record.investor_profile,
                        "status": record.account_status,
                    }
                )
        total = len(matching)
        start = (page - 1) * page_size
        self.db.add(
            AuditLogRecord(user_id=actor_id, action="admin_users_listed", occurred_at=self.clock())
        )
        self.db.commit()
        return {
            "items": matching[start : start + page_size],
            "page": page,
            "page_size": page_size,
            "total": total,
        }

    @staticmethod
    def preference_values(record: UserPreferencesRecord | None) -> dict[str, bool | str]:
        if record is None:
            return {
                "language": "pt",
                "theme": "light",
                "in_app_notifications": True,
                "email_notifications": False,
                "push_notifications": False,
            }
        return {
            "language": record.language,
            "theme": record.theme,
            "in_app_notifications": record.in_app_notifications,
            "email_notifications": record.email_notifications,
            "push_notifications": record.push_notifications,
        }

    def profile(self, user_id: uuid.UUID) -> tuple[User, str | None, dict[str, bool | str]]:
        user = self.db.get(UserRecord, user_id)
        if user is None:
            raise AuthError("invalid_session")
        pending = (
            self.security.decrypt(user.pending_email_encrypted)
            if user.pending_email_encrypted is not None
            else None
        )
        return (
            self.public_user(user),
            pending,
            self.preference_values(self.db.get(UserPreferencesRecord, user_id)),
        )

    @staticmethod
    def classify_quiz(answers: list[int]) -> tuple[str, int]:
        score = sum(answers)
        if score <= 3:
            return "conservador", score
        if score <= 6:
            return "moderado", score
        return "arrojado", score

    def investor_profile(self, user_id: uuid.UUID) -> dict[str, str | None]:
        user = self.db.get(UserRecord, user_id)
        if user is None:
            raise AuthError("invalid_session")
        profile = user.investor_profile
        return {"profile": profile, "guidance": PROFILE_GUIDANCE.get(profile)}

    def complete_quiz(self, user_id: uuid.UUID, answers: list[int]) -> dict[str, str | int]:
        user = self.db.scalar(select(UserRecord).where(UserRecord.id == user_id).with_for_update())
        if user is None:
            raise AuthError("invalid_session")
        profile, score = self.classify_quiz(answers)
        user.investor_profile = profile
        self.db.commit()
        return {"profile": profile, "guidance": PROFILE_GUIDANCE[profile], "score": score}

    def delete_account(self, user_id: uuid.UUID, password: str) -> None:
        user = self.db.scalar(select(UserRecord).where(UserRecord.id == user_id).with_for_update())
        if user is None or not self.security.verify(user.password_hash, password):
            raise AuthError("invalid_current_password")
        # Durable intent precedes erasure. Failure is not acknowledged as success;
        # a persisted intent can be safely replayed after a database outage/restore.
        journal = DeletionJournal(
            self.settings.deletion_journal_path, self.settings.data_key.get_secret_value()
        )
        journal.record(user_id)
        email = self.security.decrypt(user.email_encrypted)
        self.db.execute(
            delete(LoginAttemptRecord).where(
                LoginAttemptRecord.email_key == self.security.lookup(f"login-attempt:{email}")
            )
        )
        self.db.add(
            AuditLogRecord(user_id=user_id, action="account_deleted", occurred_at=self.clock())
        )
        erase_user(self.db, user_id)
        self.db.commit()

    def record_usage_event(self, user_id: uuid.UUID, module: str, action: str) -> None:
        """Persist only the whitelisted, payload-free use data."""
        self.db.add(
            UsageEventRecord(
                user_id=user_id, module=module, action=action, occurred_at=self.clock()
            )
        )
        self.db.commit()

    def record_audit(self, user_id: uuid.UUID, action: str) -> None:
        self.db.add(AuditLogRecord(user_id=user_id, action=action, occurred_at=self.clock()))
        self.db.commit()

    def register(self, name: str, email: str, password: str) -> User:
        email = normalize_email(email)
        lookup = self.security.lookup(email)
        if self.db.scalar(
            select(UserRecord.id).where(
                or_(UserRecord.email_lookup == lookup, UserRecord.pending_email_lookup == lookup)
            )
        ):
            raise AuthError("email_exists", 409)
        record = UserRecord(
            name_encrypted=self.security.encrypt(name.strip()),
            email_encrypted=self.security.encrypt(email),
            email_lookup=lookup,
            password_hash=self.security.hasher.hash(password),
            role="usuario",
        )
        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AuthError("email_exists", 409) from exc
        return self.public_user(record)

    def request_email_confirmation(self, user_id: uuid.UUID) -> None:
        """Deliver and persist a new one-time confirmation token for its owner."""
        now = self.clock()
        user = self.db.scalar(select(UserRecord).where(UserRecord.id == user_id).with_for_update())
        if user is None:
            raise AuthError("invalid_session")
        if user.email_verified_at is not None:
            self.db.rollback()
            raise AuthError("email_already_verified", 409)
        last_issued = self.db.scalar(
            select(EmailConfirmationTokenRecord.issued_at)
            .where(
                EmailConfirmationTokenRecord.user_id == user.id,
                EmailConfirmationTokenRecord.purpose == "email_confirmation",
            )
            .order_by(EmailConfirmationTokenRecord.issued_at.desc())
            .limit(1)
        )
        if last_issued is not None and now < last_issued + timedelta(seconds=60):
            retry = max(1, math.ceil((last_issued + timedelta(seconds=60) - now).total_seconds()))
            self.db.rollback()
            raise AuthError("confirmation_resend_limited", 429, retry)
        raw_token = secrets.token_urlsafe(48)
        try:
            if self.email_delivery is None:
                raise EmailDeliveryError("confirmation delivery is not configured")
            self.email_delivery.deliver_confirmation(
                recipient=self.security.decrypt(user.email_encrypted), token=raw_token
            )
        except EmailDeliveryError as exc:
            self.db.rollback()
            raise AuthError("email_delivery_unavailable", 503) from exc
        self.db.execute(
            update(EmailConfirmationTokenRecord)
            .where(
                EmailConfirmationTokenRecord.user_id == user.id,
                EmailConfirmationTokenRecord.purpose == "email_confirmation",
                EmailConfirmationTokenRecord.used_at.is_(None),
                EmailConfirmationTokenRecord.invalidated_at.is_(None),
            )
            .values(invalidated_at=now)
        )
        self.db.add(
            EmailConfirmationTokenRecord(
                digest=token_digest(raw_token),
                user_id=user.id,
                purpose="email_confirmation",
                issued_at=now,
                expires_at=now + timedelta(hours=24),
            )
        )
        self.db.commit()

    def confirm_email(self, raw_token: str) -> bool:
        now = self.clock()
        token = self.db.scalar(
            select(EmailConfirmationTokenRecord)
            .where(EmailConfirmationTokenRecord.digest == token_digest(raw_token))
            .with_for_update()
        )
        if (
            token is None
            or token.purpose not in {"email_confirmation", "email_change"}
            or token.used_at is not None
            or token.invalidated_at is not None
            or token.expires_at <= now
        ):
            self.db.rollback()
            raise AuthError("invalid_confirmation_token", 400)
        user = self.db.scalar(
            select(UserRecord).where(UserRecord.id == token.user_id).with_for_update()
        )
        if user is None:
            self.db.rollback()
            raise AuthError("invalid_confirmation_token", 400)
        if token.purpose == "email_change":
            if user.pending_email_encrypted is None or user.pending_email_lookup is None:
                self.db.rollback()
                raise AuthError("invalid_confirmation_token", 400)
            user.email_encrypted = user.pending_email_encrypted
            user.email_lookup = user.pending_email_lookup
            user.pending_email_encrypted = None
            user.pending_email_lookup = None
        token.used_at = now
        user.email_verified_at = now
        if self.is_initial_admin(user):
            user.role = "administrador"
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AuthError("email_exists", 409) from exc
        return True

    def update_profile(
        self,
        user_id: uuid.UUID,
        name: str | None,
        email: str | None,
        current_password: str | None,
    ) -> tuple[User, str | None, dict[str, bool | str]]:
        user = self.db.scalar(select(UserRecord).where(UserRecord.id == user_id).with_for_update())
        if user is None:
            raise AuthError("invalid_session")
        if name is not None:
            user.name_encrypted = self.security.encrypt(name)
        if email is not None:
            normalized = normalize_email(email)
            lookup = self.security.lookup(normalized)
            if lookup == user.email_lookup:
                self.db.rollback()
                raise AuthError("email_unchanged", 409)
            if current_password is None or not self.security.verify(
                user.password_hash, current_password
            ):
                self.db.rollback()
                raise AuthError("invalid_current_password")
            existing = self.db.scalar(
                select(UserRecord.id).where(
                    UserRecord.id != user.id,
                    or_(
                        UserRecord.email_lookup == lookup, UserRecord.pending_email_lookup == lookup
                    ),
                )
            )
            if existing is not None:
                self.db.rollback()
                raise AuthError("email_exists", 409)
            raw_token = secrets.token_urlsafe(48)
            try:
                if self.email_delivery is None:
                    raise EmailDeliveryError("confirmation delivery is not configured")
                self.email_delivery.deliver_confirmation(recipient=normalized, token=raw_token)
            except EmailDeliveryError as exc:
                self.db.rollback()
                raise AuthError("email_delivery_unavailable", 503) from exc
            now = self.clock()
            self.db.execute(
                update(EmailConfirmationTokenRecord)
                .where(
                    EmailConfirmationTokenRecord.user_id == user.id,
                    EmailConfirmationTokenRecord.purpose == "email_change",
                    EmailConfirmationTokenRecord.used_at.is_(None),
                    EmailConfirmationTokenRecord.invalidated_at.is_(None),
                )
                .values(invalidated_at=now)
            )
            user.pending_email_encrypted = self.security.encrypt(normalized)
            user.pending_email_lookup = lookup
            self.db.add(
                EmailConfirmationTokenRecord(
                    digest=token_digest(raw_token),
                    user_id=user.id,
                    purpose="email_change",
                    issued_at=now,
                    expires_at=now + timedelta(hours=24),
                )
            )
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AuthError("email_exists", 409) from exc
        return self.profile(user_id)

    def update_preferences(
        self, user_id: uuid.UUID, values: dict[str, bool | str]
    ) -> dict[str, bool | str]:
        preferences = self.db.get(UserPreferencesRecord, user_id)
        if preferences is None:
            preferences = UserPreferencesRecord(user_id=user_id, **values)
            self.db.add(preferences)
        else:
            for key, value in values.items():
                setattr(preferences, key, value)
        self.db.commit()
        return self.preference_values(preferences)

    @staticmethod
    def notification_output(record: NotificationRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "kind": record.kind,
            "title": record.title,
            "message": record.message,
            "created_at": record.created_at,
            "read_at": record.read_at,
        }

    def notification_preferences(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        configured = {
            record.kind: record.enabled
            for record in self.db.scalars(
                select(NotificationPreferenceRecord).where(
                    NotificationPreferenceRecord.user_id == user_id
                )
            )
        }
        return [
            {"kind": kind, "enabled": configured.get(kind, True)} for kind in NOTIFICATION_KINDS
        ]

    def update_notification_preference(
        self, user_id: uuid.UUID, kind: str, enabled: bool
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        if kind not in NOTIFICATION_KINDS:
            raise AuthError("notification_kind_not_found", 404)
        preference = self.db.get(NotificationPreferenceRecord, (user_id, kind))
        if preference is None:
            preference = NotificationPreferenceRecord(user_id=user_id, kind=kind, enabled=enabled)
            self.db.add(preference)
        else:
            preference.enabled = enabled
        self.db.commit()
        return {"kind": preference.kind, "enabled": preference.enabled}

    def watchlist_output(self, record: WatchlistRecord) -> dict[str, object]:
        company = self.db.get(PublicCompanyRecord, record.company_id)
        return {
            "company": {
                "id": company.id,
                "ticker": company.ticker,
                "cnpj": company.cnpj,
                "legal_name": company.legal_name,
                "sector": company.sector,
            },
            "created_at": record.created_at,
        }

    def add_watchlist(
        self, user_id: uuid.UUID, company_id: uuid.UUID
    ) -> tuple[bool, dict[str, object]]:
        self.require_category_owner(user_id)
        company = self.db.get(PublicCompanyRecord, company_id)
        if company is None:
            raise AuthError("company_not_found", 404)
        existing = self.db.get(WatchlistRecord, (user_id, company_id))
        if existing is not None:
            return False, self.watchlist_output(existing)
        total = len(
            list(self.db.scalars(select(WatchlistRecord).where(WatchlistRecord.user_id == user_id)))
        )
        if total >= 50:
            raise AuthError("watchlist_limit_reached", 422)
        record = WatchlistRecord(user_id=user_id, company_id=company_id, created_at=self.clock())
        self.db.add(record)
        self.db.commit()
        return True, self.watchlist_output(record)

    def list_watchlist(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        return [
            self.watchlist_output(record)
            for record in self.db.scalars(
                select(WatchlistRecord)
                .where(WatchlistRecord.user_id == user_id)
                .order_by(WatchlistRecord.created_at.desc())
            )
        ]

    def remove_watchlist(self, user_id: uuid.UUID, company_id: uuid.UUID) -> None:
        record = self.db.get(WatchlistRecord, (user_id, company_id))
        if record is None:
            raise AuthError("watchlist_not_found", 404)
        self.db.delete(record)
        self.db.commit()

    def notify_watchlist_document(self, document_id: uuid.UUID) -> int:
        document = self.db.get(OfficialDocumentRecord, document_id)
        if document is None:
            raise AuthError("official_document_not_found", 404)
        if document.status != "active":
            return 0
        owners = self.db.scalars(
            select(WatchlistRecord.user_id).where(WatchlistRecord.company_id == document.company_id)
        )
        count = 0
        for user_id in owners:
            created, _ = self.create_notification(
                user_id, "watchlist_document", f"document:{document.id}"
            )
            count += int(created)
        return count

    def create_notification(
        self, user_id: uuid.UUID, kind: str, source_key: str
    ) -> tuple[bool, dict[str, object] | None]:
        self.require_category_owner(user_id)
        if kind not in NOTIFICATION_CONTENT:
            raise AuthError("notification_kind_not_found", 404)
        preferences = self.db.get(UserPreferencesRecord, user_id)
        per_kind = self.db.get(NotificationPreferenceRecord, (user_id, kind))
        if (preferences is not None and not preferences.in_app_notifications) or (
            per_kind is not None and not per_kind.enabled
        ):
            return False, None
        existing = self.db.scalar(
            select(NotificationRecord).where(
                NotificationRecord.user_id == user_id,
                NotificationRecord.kind == kind,
                NotificationRecord.source_key == source_key,
            )
        )
        if existing is not None:
            return False, self.notification_output(existing)
        title, message = NOTIFICATION_CONTENT[kind]
        record = NotificationRecord(
            user_id=user_id,
            kind=kind,
            source_key=source_key,
            title=title,
            message=message,
            created_at=self.clock(),
        )
        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(NotificationRecord).where(
                    NotificationRecord.user_id == user_id,
                    NotificationRecord.kind == kind,
                    NotificationRecord.source_key == source_key,
                )
            )
            return False, self.notification_output(existing) if existing is not None else None
        self.dispatch_external(user_id, record.title, record.message, record.id, kind)
        return True, self.notification_output(record)

    def dispatch_external(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_id: uuid.UUID | None,
        source: str,
        channels: tuple[str, ...] = ("email", "push"),
        attachment: tuple[str, bytes] | None = None,
    ) -> dict[str, str]:
        """SPEC-061: entrega em canais opcionais habilitados; o in-app continua sendo a base.

        Falhas são registradas com resultado mínimo (sem conteúdo nem destino) e nunca
        desfazem a notificação in-app nem registram sucesso indevido.
        """
        from app.infrastructure.channel_delivery import ChannelDeliveryError, ChannelUnavailable

        preferences = self.db.get(UserPreferencesRecord, user_id)
        enabled = {
            "email": preferences is not None and preferences.email_notifications,
            "push": preferences is not None and preferences.push_notifications,
        }
        results: dict[str, str] = {}
        for channel in channels:
            if not enabled[channel]:
                continue
            if channel == "email":
                user = self.db.get(UserRecord, user_id)
                destinations = [self.security.decrypt(user.email_encrypted)] if user else []
            else:
                destinations = [
                    self.security.decrypt(device.token_encrypted)
                    for device in self.db.scalars(
                        select(PushDeviceRecord).where(PushDeviceRecord.user_id == user_id)
                    )
                ]
            adapter = self.channel_delivery.get(channel)
            status = "no_destination" if not destinations else "sent"
            for destination in destinations:
                try:
                    if adapter is None:
                        raise ChannelUnavailable(channel)
                    adapter.send(
                        channel=channel,
                        destination=destination,
                        title=title,
                        message=message,
                        attachment=attachment,
                    )
                except ChannelUnavailable:
                    status = "provider_unavailable"
                except (ChannelDeliveryError, OSError):
                    status = "failed"
            self.db.add(
                NotificationDeliveryRecord(
                    user_id=user_id,
                    notification_id=notification_id,
                    source=source,
                    channel=channel,
                    status=status,
                    attempted_at=self.clock(),
                )
            )
            results[channel] = status
        if results:
            self.db.commit()
        return results

    def list_notifications(
        self, user_id: uuid.UUID, unread_only: bool = False
    ) -> list[dict[str, object]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        statement = select(NotificationRecord).where(NotificationRecord.user_id == user_id)
        if unread_only:
            statement = statement.where(NotificationRecord.read_at.is_(None))
        records = self.db.scalars(
            statement.order_by(
                NotificationRecord.created_at.desc(), NotificationRecord.id.desc()
            ).limit(100)
        )
        return [self.notification_output(record) for record in records]

    def mark_notification_read(
        self, user_id: uuid.UUID, notification_id: uuid.UUID
    ) -> dict[str, object]:
        record = self.db.scalar(
            select(NotificationRecord).where(
                NotificationRecord.id == notification_id, NotificationRecord.user_id == user_id
            )
        )
        if record is None:
            raise AuthError("notification_not_found", 404)
        if record.read_at is None:
            record.read_at = self.clock()
            self.db.commit()
        return self.notification_output(record)

    def advanced_metrics_preference(self, user_id: uuid.UUID) -> dict[str, bool]:
        user = self.db.get(UserRecord, user_id)
        if user is None:
            raise AuthError("invalid_session")
        preference = self.db.get(AdvancedMetricsPreferenceRecord, user_id)
        enabled = user.investor_profile == "arrojado" or (
            preference is not None and preference.enabled
        )
        return {
            "enabled": enabled,
            "available_by_default": user.investor_profile == "arrojado",
        }

    def set_advanced_metrics_preference(self, user_id: uuid.UUID, enabled: bool) -> dict[str, bool]:
        self.require_category_owner(user_id)
        preference = self.db.get(AdvancedMetricsPreferenceRecord, user_id)
        if preference is None:
            preference = AdvancedMetricsPreferenceRecord(user_id=user_id, enabled=enabled)
            self.db.add(preference)
        else:
            preference.enabled = enabled
        self.db.commit()
        return self.advanced_metrics_preference(user_id)

    def category_lookup(self, user_id: uuid.UUID, name: str) -> str:
        return self.security.lookup(f"category:{user_id}:{name.strip().casefold()}")

    def require_category_owner(self, user_id: uuid.UUID) -> UserRecord:
        user = self.db.get(UserRecord, user_id)
        if user is None:
            raise AuthError("invalid_session")
        if user.email_verified_at is None:
            raise AuthError("email_not_verified", 403)
        return user

    def list_categories(self, user_id: uuid.UUID) -> list[dict[str, bool | str]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        visibility = {
            record.category_key: record.active
            for record in self.db.scalars(
                select(DefaultCategoryVisibilityRecord).where(
                    DefaultCategoryVisibilityRecord.user_id == user_id
                )
            )
        }
        defaults = [
            {
                "key": f"standard:{category['key']}",
                "name": category["name"],
                "color": category["color"],
                "kind": "standard",
                "active": visibility.get(category["key"], True),
            }
            for category in DEFAULT_CATEGORIES
        ]
        personal = [
            {
                "key": f"personal:{record.id}",
                "name": self.security.decrypt(record.name_encrypted),
                "color": record.color.upper(),
                "kind": "personal",
                "active": record.active,
            }
            for record in self.db.scalars(
                select(CategoryRecord)
                .where(CategoryRecord.user_id == user_id)
                .order_by(CategoryRecord.name_lookup)
            )
        ]
        return defaults + personal

    def create_category(self, user_id: uuid.UUID, name: str, color: str) -> dict[str, bool | str]:
        self.require_category_owner(user_id)
        name = name.strip()
        if name.casefold() in {category["name"].casefold() for category in DEFAULT_CATEGORIES}:
            raise AuthError("category_exists", 409)
        record = CategoryRecord(
            user_id=user_id,
            name_encrypted=self.security.encrypt(name),
            name_lookup=self.category_lookup(user_id, name),
            color=color.upper(),
        )
        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AuthError("category_exists", 409) from exc
        return {
            "key": f"personal:{record.id}",
            "name": name,
            "color": record.color,
            "kind": "personal",
            "active": record.active,
        }

    def set_default_category_visibility(
        self, user_id: uuid.UUID, category_key: str, active: bool
    ) -> dict[str, bool | str]:
        self.require_category_owner(user_id)
        if category_key not in DEFAULT_CATEGORY_KEYS:
            raise AuthError("category_not_found", 404)
        record = self.db.scalar(
            select(DefaultCategoryVisibilityRecord)
            .where(
                DefaultCategoryVisibilityRecord.user_id == user_id,
                DefaultCategoryVisibilityRecord.category_key == category_key,
            )
            .with_for_update()
        )
        if record is None:
            record = DefaultCategoryVisibilityRecord(
                user_id=user_id, category_key=category_key, active=active
            )
            self.db.add(record)
        else:
            record.active = active
        self.db.commit()
        category = next(item for item in DEFAULT_CATEGORIES if item["key"] == category_key)
        return {
            "key": f"standard:{category_key}",
            "name": category["name"],
            "color": category["color"],
            "kind": "standard",
            "active": active,
        }

    def account_output(self, record: AccountRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "name": self.security.decrypt(record.name_encrypted),
            "account_type": record.account_type,
            "initial_balance": record.initial_balance,
        }

    def card_output(self, record: CreditCardRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "name": self.security.decrypt(record.name_encrypted),
            "credit_limit": record.credit_limit,
            "closing_day": record.closing_day,
            "due_day": record.due_day,
            "alert_threshold": record.alert_threshold,
        }

    def list_financial_sources(self, user_id: uuid.UUID) -> dict[str, list[dict[str, object]]]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        return {
            "accounts": [
                self.account_output(record)
                for record in self.db.scalars(
                    select(AccountRecord)
                    .where(AccountRecord.user_id == user_id)
                    .order_by(AccountRecord.id)
                )
            ],
            "credit_cards": [
                self.card_output(record)
                for record in self.db.scalars(
                    select(CreditCardRecord)
                    .where(CreditCardRecord.user_id == user_id)
                    .order_by(CreditCardRecord.id)
                )
            ],
        }

    def create_account(
        self, user_id: uuid.UUID, name: str, account_type: str, initial_balance: Decimal
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        record = AccountRecord(
            user_id=user_id,
            name_encrypted=self.security.encrypt(name),
            account_type=account_type,
            initial_balance=initial_balance,
        )
        self.db.add(record)
        self.db.commit()
        return self.account_output(record)

    def create_credit_card(
        self,
        user_id: uuid.UUID,
        name: str,
        credit_limit: Decimal,
        closing_day: int,
        due_day: int,
        alert_threshold: Decimal = Decimal("80"),
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        record = CreditCardRecord(
            user_id=user_id,
            name_encrypted=self.security.encrypt(name),
            credit_limit=credit_limit,
            closing_day=closing_day,
            due_day=due_day,
            alert_threshold=alert_threshold,
        )
        self.db.add(record)
        self.db.commit()
        return self.card_output(record)

    def update_card_alert_threshold(
        self, user_id: uuid.UUID, card_id: uuid.UUID, alert_threshold: Decimal
    ) -> dict[str, object]:
        """OPEN-12: percentual de alerta de proximidade do limite, por cartão (70% a 100%)."""
        self.require_category_owner(user_id)
        card = self.db.scalar(
            select(CreditCardRecord).where(
                CreditCardRecord.id == card_id, CreditCardRecord.user_id == user_id
            )
        )
        if card is None:
            raise AuthError("credit_card_not_found", 404)
        card.alert_threshold = alert_threshold
        self.db.commit()
        return self.card_output(card)

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
        starts_on: date,
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
            starts_on=starts_on,
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(RecurringIncomeRecord).where(
                    RecurringIncomeRecord.user_id == user_id,
                    RecurringIncomeRecord.idempotency_key == idempotency_key,
                )
            )
            if existing is None:
                raise
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
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(OneTimeIncomeRecord).where(
                    OneTimeIncomeRecord.user_id == user_id,
                    OneTimeIncomeRecord.idempotency_key == idempotency_key,
                )
            )
            if existing is None:
                raise
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
        starts_on: date,
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
            starts_on=starts_on,
            reference_month=reference_month,
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(BonusRecord).where(
                    BonusRecord.user_id == user_id, BonusRecord.idempotency_key == idempotency_key
                )
            )
            if existing is None:
                raise
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

    def balance_summary(self, user_id: uuid.UUID, competence: date) -> dict[str, Decimal | str]:
        summary = self.income_summary(user_id, competence)
        month_start = competence.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        expenses = sum(
            (
                record.amount
                for record in self.db.scalars(
                    select(ExpenseRecord).where(ExpenseRecord.user_id == user_id)
                )
                if (record.recurring and record.occurred_on < next_month)
                or (
                    not record.recurring
                    and record.occurred_on >= month_start
                    and record.occurred_on < next_month
                )
            ),
            Decimal("0"),
        )
        return {
            **summary,
            "expenses": expenses,
            "balance_variation": summary["total"] - expenses,
        }

    @staticmethod
    def _month_starts(start: date, end: date):
        cursor = start.replace(day=1)
        while cursor <= end:
            yield cursor
            cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)

    def statement_entries(
        self, user_id: uuid.UUID, start: date, end: date
    ) -> list[dict[str, object]]:
        """A derived export view; it never becomes an authoritative balance."""
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        entries: list[dict[str, object]] = []
        for record in self.db.scalars(
            select(ExpenseRecord).where(ExpenseRecord.user_id == user_id)
        ):
            dates = [record.occurred_on]
            if record.recurring:
                dates = [
                    month.replace(day=min(record.occurred_on.day, 28))
                    for month in self._month_starts(max(start, record.occurred_on), end)
                ]
            for occurred_on in dates:
                if start <= occurred_on <= end:
                    entries.append(
                        {
                            "date": occurred_on,
                            "type": "despesa",
                            "description": self.security.decrypt(record.description_encrypted),
                            "category": record.category_key,
                            "amount": -record.amount,
                        }
                    )
        for record in self.db.scalars(
            select(OneTimeIncomeRecord).where(
                OneTimeIncomeRecord.user_id == user_id,
                OneTimeIncomeRecord.occurred_on >= start,
                OneTimeIncomeRecord.occurred_on <= end,
            )
        ):
            entries.append(
                {
                    "date": record.occurred_on,
                    "type": "receita",
                    "description": self.security.decrypt(record.description_encrypted),
                    "category": "receita",
                    "amount": record.amount,
                }
            )
        for record in self.db.scalars(
            select(RecurringIncomeRecord).where(RecurringIncomeRecord.user_id == user_id)
        ):
            for month in self._month_starts(max(start, record.starts_on), end):
                occurred_on = month.replace(day=min(record.starts_on.day, 28))
                entries.append(
                    {
                        "date": occurred_on,
                        "type": "receita",
                        "description": self.security.decrypt(record.description_encrypted),
                        "category": "receita recorrente",
                        "amount": record.amount,
                    }
                )
        for record in self.db.scalars(select(BonusRecord).where(BonusRecord.user_id == user_id)):
            for month in self._month_starts(max(start, record.starts_on), end):
                if record.periodicity == "monthly" or record.reference_month == month.month:
                    occurred_on = month.replace(day=min(record.starts_on.day, 28))
                    entries.append(
                        {
                            "date": occurred_on,
                            "type": "receita",
                            "description": self.security.decrypt(record.description_encrypted),
                            "category": "bônus",
                            "amount": record.amount,
                        }
                    )
        return sorted(entries, key=lambda item: (item["date"], item["type"], item["description"]))

    @staticmethod
    def month_bounds(competence: date) -> tuple[date, date]:
        start = competence.replace(day=1)
        return start, (start.replace(day=28) + timedelta(days=4)).replace(day=1)

    def expenses_for_month(
        self, user_id: uuid.UUID, competence: date, category_key: str | None = None
    ) -> Decimal:
        start, end = self.month_bounds(competence)
        return sum(
            (
                record.amount
                for record in self.db.scalars(
                    select(ExpenseRecord).where(ExpenseRecord.user_id == user_id)
                )
                if (category_key is None or record.category_key == category_key)
                and (
                    (record.recurring and record.occurred_on < end)
                    or (not record.recurring and start <= record.occurred_on < end)
                )
            ),
            Decimal("0"),
        )

    def indicator(self, code: str) -> dict[str, object]:
        record = self.db.get(MarketIndicatorRecord, code)
        if record is None:
            raise AuthError("indicator_unavailable", 503)
        stale = self.clock() - record.checked_at > timedelta(hours=23)
        return {
            "code": record.code,
            "value": record.value,
            "unit": record.unit,
            "reference_date": record.reference_date,
            "checked_at": record.checked_at,
            "source": record.source,
            "stale": stale,
        }

    def treasury_rates(self) -> list[dict[str, object]]:
        """SPEC-007-R04: taxas do Tesouro Direto do cache local; nunca chama a fonte."""
        records = self.db.scalars(
            select(TreasuryBondRateRecord).order_by(
                TreasuryBondRateRecord.bond_type, TreasuryBondRateRecord.maturity
            )
        )
        now = self.clock()
        return [
            {
                "bond_type": record.bond_type,
                "maturity": record.maturity,
                "buy_rate": record.buy_rate,
                "reference_date": record.reference_date,
                "checked_at": record.checked_at,
                "source": record.source,
                "stale": now - record.checked_at > timedelta(hours=24),
            }
            for record in records
        ]

    def save_simulation(
        self, user_id: uuid.UUID, kind: str, label: str, payload: dict[str, object], final: Decimal
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        record = SimulationRecord(
            user_id=user_id,
            kind=kind,
            label_encrypted=self.security.encrypt(label),
            payload=payload,
            final_amount=final,
        )
        self.db.add(record)
        self.db.commit()
        return self.simulation_output(record)

    def simulation_output(self, record: SimulationRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "kind": record.kind,
            "label": self.security.decrypt(record.label_encrypted),
            "payload": record.payload,
            "final_amount": record.final_amount,
            "created_at": record.created_at,
            "risk_metrics": record.payload.get("risk_metrics"),
            "foreign_currency": record.payload.get("foreign_currency"),
        }

    def list_simulations(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        return [
            self.simulation_output(record)
            for record in self.db.scalars(
                select(SimulationRecord)
                .where(SimulationRecord.user_id == user_id)
                .order_by(SimulationRecord.created_at.desc(), SimulationRecord.id)
            )
        ]

    def compare_simulations(self, user_id: uuid.UUID, ids: list[uuid.UUID]) -> dict[str, object]:
        records = list(
            self.db.scalars(
                select(SimulationRecord).where(
                    SimulationRecord.user_id == user_id, SimulationRecord.id.in_(ids)
                )
            )
        )
        by_id = {record.id: record for record in records}
        if len(by_id) != len(set(ids)):
            raise AuthError("simulation_not_found", 404)
        ordered = [by_id[item] for item in ids]
        baseline = ordered[0].final_amount
        best = max(ordered, key=lambda record: record.final_amount)  # empate: o primeiro
        return {
            "simulations": [self.simulation_output(record) for record in ordered],
            "difference_from_first": [record.final_amount - baseline for record in ordered],
            # SPEC-010-R04/R05: diferença percentual e cenário de maior resultado final.
            "difference_percent_from_first": [
                ((record.final_amount - baseline) / baseline * Decimal("100")).quantize(
                    Decimal("0.01")
                )
                if baseline
                else None
                for record in ordered
            ],
            "best_simulation_id": best.id,
        }

    def card_invoice(
        self, user_id: uuid.UUID, card_id: uuid.UUID, competence: date
    ) -> dict[str, object]:
        card = self.db.scalar(
            select(CreditCardRecord).where(
                CreditCardRecord.id == card_id, CreditCardRecord.user_id == user_id
            )
        )
        if card is None:
            raise AuthError("credit_card_not_found", 404)
        # OPEN-12: a compra entra na fatura pelo dia de fechamento, não pelo mês civil.
        invoice_month = competence.replace(day=1)
        total = Decimal("0")
        future = Decimal("0")
        for record in self.db.scalars(
            select(ExpenseRecord).where(
                ExpenseRecord.user_id == user_id, ExpenseRecord.credit_card_id == card_id
            )
        ):
            cycle = competencia_da_fatura(record.occurred_on, card.closing_day)
            if record.recurring:
                total += record.amount if cycle <= invoice_month else Decimal("0")
            elif cycle == invoice_month:
                total += record.amount
            elif cycle > invoice_month and record.installment_group is not None:
                future += record.amount
        # Limite disponível = limite − fatura aberta − parcelas futuras; faturas anteriores
        # são tratadas como pagas (pagamento de fatura segue fora da OPEN-12).
        committed = total + future
        return {
            "card_id": card.id,
            "competence": invoice_month.strftime("%Y-%m"),
            "invoice_total": total,
            "credit_limit": card.credit_limit,
            "available_limit": max(Decimal("0"), card.credit_limit - committed),
            "future_installments": future,
            "near_limit": committed * Decimal("100") >= card.credit_limit * card.alert_threshold,
            "alert_threshold": card.alert_threshold,
            "closing_day": card.closing_day,
            "due_day": card.due_day,
        }

    def net_worth_item_output(self, record: NetWorthItemRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "kind": record.kind,
            "name": self.security.decrypt(record.name_encrypted),
            "value": record.value,
            "annual_rate": record.annual_rate,
            "origin": "manual",
        }

    def _account_current_balance(self, record: AccountRecord, as_of: date) -> Decimal:
        # Recurring records contribute once for each started calendar month through the as-of month.
        recurring = sum(
            row.amount
            * ((as_of.year - row.starts_on.year) * 12 + as_of.month - row.starts_on.month + 1)
            for row in self.db.scalars(
                select(RecurringIncomeRecord).where(RecurringIncomeRecord.account_id == record.id)
            )
            if row.starts_on <= as_of
        )
        one_time = sum(
            (
                row.amount
                for row in self.db.scalars(
                    select(OneTimeIncomeRecord).where(OneTimeIncomeRecord.account_id == record.id)
                )
                if row.occurred_on <= as_of
            ),
            Decimal("0"),
        )
        expenses = sum(
            (
                row.amount
                for row in self.db.scalars(
                    select(ExpenseRecord).where(ExpenseRecord.account_id == record.id)
                )
                if row.occurred_on <= as_of
            ),
            Decimal("0"),
        )
        return record.initial_balance + recurring + one_time - expenses

    def net_worth(self, user_id: uuid.UUID, as_of: date | None = None) -> dict[str, object]:
        if self.db.get(UserRecord, user_id) is None:
            raise AuthError("invalid_session")
        reference = as_of or self.clock().date()
        assets: list[dict[str, object]] = []
        liabilities: list[dict[str, object]] = []
        for account in self.db.scalars(
            select(AccountRecord).where(AccountRecord.user_id == user_id)
        ):
            assets.append(
                {
                    "id": account.id,
                    "kind": "asset",
                    "name": self.security.decrypt(account.name_encrypted),
                    "value": self._account_current_balance(account, reference),
                    "annual_rate": None,
                    "origin": "account",
                }
            )
        for card in self.db.scalars(
            select(CreditCardRecord).where(CreditCardRecord.user_id == user_id)
        ):
            # OPEN-12: passivo é a fatura aberta no ciclo que contém a data de referência.
            invoice = self.card_invoice(
                user_id, card.id, competencia_da_fatura(reference, card.closing_day)
            )
            if invoice["invoice_total"] > 0:
                liabilities.append(
                    {
                        "id": card.id,
                        "kind": "liability",
                        "name": self.security.decrypt(card.name_encrypted),
                        "value": invoice["invoice_total"],
                        "annual_rate": None,
                        "origin": "credit_card_invoice",
                    }
                )
        for item in self.db.scalars(
            select(NetWorthItemRecord).where(NetWorthItemRecord.user_id == user_id)
        ):
            (assets if item.kind == "asset" else liabilities).append(
                self.net_worth_item_output(item)
            )
        for financing in self.db.scalars(
            select(ConfirmedFinancingRecord).where(ConfirmedFinancingRecord.user_id == user_id)
        ):
            liabilities.append(
                {
                    "id": financing.id,
                    "kind": "liability",
                    "name": self.security.decrypt(financing.name_encrypted),
                    "value": financing.principal,
                    "annual_rate": financing.annual_rate,
                    "origin": "financing",
                }
            )
        total_assets = sum((item["value"] for item in assets), Decimal("0"))
        total_liabilities = sum((item["value"] for item in liabilities), Decimal("0"))
        return {
            "as_of": reference,
            "assets": assets,
            "liabilities": liabilities,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": total_assets - total_liabilities,
        }

    INVESTMENT_CLASSES = ("fixed_income", "stocks", "fiis", "savings", "other")

    def investment_allocation(self, user_id: uuid.UUID) -> dict[str, object]:
        """Real invested balances only; never classify an unknown item by guesswork."""
        self.require_category_owner(user_id)
        worth = self.net_worth(user_id)
        classes = {name: Decimal("0") for name in self.INVESTMENT_CLASSES}
        assignments = {
            item.asset_id: item.asset_class
            for item in self.db.scalars(
                select(InvestmentAssetClassRecord).where(
                    InvestmentAssetClassRecord.user_id == user_id
                )
            )
        }
        account_types = {
            account.id: account.account_type
            for account in self.db.scalars(
                select(AccountRecord).where(AccountRecord.user_id == user_id)
            )
        }
        unclassified = []
        classified = []
        for asset in worth["assets"]:
            asset_class = None
            if asset["origin"] == "manual":
                asset_class = assignments.get(asset["id"])
                if asset_class is None:
                    unclassified.append(asset)
            elif asset["origin"] == "account":
                kind = account_types.get(asset["id"])
                if kind == "savings":
                    asset_class = "savings"
                elif kind == "investment":
                    asset_class = "other"
            if asset["origin"] == "manual" and asset_class is not None:
                classified.append(
                    {
                        "id": asset["id"],
                        "name": asset["name"],
                        "value": asset["value"],
                        "asset_class": asset_class,
                    }
                )
            if asset_class is not None and asset["value"] > 0:
                classes[asset_class] += asset["value"]
        total = sum(classes.values(), Decimal("0"))
        targets = {
            row.asset_class: row.target_percent
            for row in self.db.scalars(
                select(InvestmentAllocationTargetRecord).where(
                    InvestmentAllocationTargetRecord.user_id == user_id
                )
            )
        }
        has_targets = len(targets) == len(self.INVESTMENT_CLASSES)
        rows = []
        for name in self.INVESTMENT_CLASSES:
            actual = (
                (classes[name] * Decimal("100") / total).quantize(Decimal("0.01"))
                if total > 0
                else None
            )
            goal = targets.get(name) if has_targets else None
            rows.append(
                {
                    "asset_class": name,
                    "amount": classes[name],
                    "actual_percent": actual,
                    "target_percent": goal,
                    "deviation_points": (
                        actual - goal if actual is not None and goal is not None else None
                    ),
                }
            )
        return {
            "total_invested": total,
            "classes": rows,
            "unclassified": unclassified,
            "classified": classified,
            "has_targets": has_targets,
        }

    def classify_investment_asset(
        self, user_id: uuid.UUID, asset_id: uuid.UUID, asset_class: str
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        item = self.db.scalar(
            select(NetWorthItemRecord).where(
                NetWorthItemRecord.user_id == user_id,
                NetWorthItemRecord.id == asset_id,
                NetWorthItemRecord.kind == "asset",
            )
        )
        if item is None:
            raise AuthError("investment_asset_not_found", 404)
        assignment = self.db.scalar(
            select(InvestmentAssetClassRecord).where(
                InvestmentAssetClassRecord.user_id == user_id,
                InvestmentAssetClassRecord.asset_id == asset_id,
            )
        )
        if assignment is None:
            assignment = InvestmentAssetClassRecord(
                user_id=user_id, asset_id=asset_id, asset_class=asset_class
            )
            self.db.add(assignment)
        else:
            assignment.asset_class = asset_class
        self.db.commit()
        return self.investment_allocation(user_id)

    def unclassify_investment_asset(
        self, user_id: uuid.UUID, asset_id: uuid.UUID
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        self.db.execute(
            delete(InvestmentAssetClassRecord).where(
                InvestmentAssetClassRecord.user_id == user_id,
                InvestmentAssetClassRecord.asset_id == asset_id,
            )
        )
        self.db.commit()
        return self.investment_allocation(user_id)

    def set_investment_targets(
        self, user_id: uuid.UUID, targets: dict[str, Decimal]
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        self.db.execute(
            delete(InvestmentAllocationTargetRecord).where(
                InvestmentAllocationTargetRecord.user_id == user_id
            )
        )
        self.db.add_all(
            InvestmentAllocationTargetRecord(
                user_id=user_id, asset_class=name, target_percent=targets[name]
            )
            for name in self.INVESTMENT_CLASSES
        )
        self.db.commit()
        return self.investment_allocation(user_id)

    def compare_financial_stress(
        self,
        user_id: uuid.UUID,
        minimum_reserve_months: int,
        first: StressScenario,
        second: StressScenario,
    ) -> dict[str, object]:
        """Read only current position and the three last completed monthly budgets."""
        self.require_category_owner(user_id)
        current = self.clock().astimezone(ZoneInfo("America/Sao_Paulo")).date()
        reference = current.replace(day=1) - timedelta(days=1)
        worth = self.net_worth(user_id, current)
        liquid_accounts = {
            row.id
            for row in self.db.scalars(
                select(AccountRecord).where(
                    AccountRecord.user_id == user_id,
                    AccountRecord.account_type.in_(("checking", "savings", "cash")),
                )
            )
        }
        reserve = max(
            Decimal("0"),
            sum(
                (
                    item["value"]
                    for item in worth["assets"]
                    if item["origin"] == "account" and item["id"] in liquid_accounts
                ),
                Decimal("0"),
            ),
        )
        expenses = Decimal("0")
        incomes = Decimal("0")
        for _ in range(3):
            budget = self.balance_summary(user_id, reference)
            expenses += budget["expenses"]
            incomes += budget["total"]
            reference = reference.replace(day=1) - timedelta(days=1)
        average_expenses = expenses / Decimal("3")
        average_income = incomes / Decimal("3")
        if average_expenses <= 0:
            raise AuthError("stress_expense_history_required", 422)
        try:
            first_result = simulate_stress(
                reserve, average_income, average_expenses, first, minimum_reserve_months
            )
            second_result = simulate_stress(
                reserve, average_income, average_expenses, second, minimum_reserve_months
            )
        except ValueError as exc:
            raise AuthError(str(exc), 422) from exc
        return {
            "reserve": reserve,
            "real_net_worth": worth["net_worth"],
            "average_monthly_income": average_income.quantize(Decimal("0.01")),
            "average_monthly_expenses": average_expenses.quantize(Decimal("0.01")),
            "window_months": 3,
            "minimum_reserve_months": minimum_reserve_months,
            "rule_version": "stress-v1",
            "first": first_result,
            "second": second_result,
        }

    def net_worth_heatmap(self, user_id: uuid.UUID) -> dict[str, object]:
        """Only real owned positions enter the heatmap; zero positions remain identifiable."""
        self.require_category_owner(user_id)
        position = self.net_worth(user_id)
        items = [*position["assets"], *position["liabilities"]]
        return {
            "as_of": position["as_of"],
            "items": items,
            "total_absolute": sum((abs(item["value"]) for item in items), Decimal("0")),
        }

    def net_worth_history(
        self, user_id: uuid.UUID, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        self.require_category_owner(user_id)
        if start is not None and end is not None and start > end:
            raise AuthError("invalid_history_interval", 422)
        statement = select(NetWorthSnapshotRecord).where(NetWorthSnapshotRecord.user_id == user_id)
        if start is not None:
            statement = statement.where(
                NetWorthSnapshotRecord.competence >= date(start.year, start.month, 1)
            )
        if end is not None:
            statement = statement.where(
                NetWorthSnapshotRecord.competence <= date(end.year, end.month, 1)
            )
        records = self.db.scalars(statement.order_by(NetWorthSnapshotRecord.competence)).all()
        return [
            {
                "competence": row.competence,
                "total_assets": row.total_assets,
                "total_liabilities": row.total_liabilities,
                "net_worth": row.net_worth,
                "captured_at": row.captured_at,
            }
            for row in records
        ]

    def capture_net_worth_snapshot(self, user_id: uuid.UUID) -> dict[str, object]:
        """Capture once per local calendar month; never invent or overwrite past positions."""
        self.require_category_owner(user_id)
        today = self.clock().astimezone(ZoneInfo("America/Sao_Paulo")).date()
        competence = date(today.year, today.month, 1)
        existing = self.db.scalar(
            select(NetWorthSnapshotRecord).where(
                NetWorthSnapshotRecord.user_id == user_id,
                NetWorthSnapshotRecord.competence == competence,
            )
        )
        if existing is None:
            totals = self.net_worth(user_id, today)
            candidate = NetWorthSnapshotRecord(
                user_id=user_id,
                competence=competence,
                total_assets=totals["total_assets"],
                total_liabilities=totals["total_liabilities"],
                net_worth=totals["net_worth"],
                captured_at=self.clock(),
            )
            # Nested transaction avoids invalidating the request on concurrent captures.
            try:
                with self.db.begin_nested():
                    self.db.add(candidate)
                    self.db.flush()
                existing = candidate
                self.db.commit()
                self.db.refresh(existing)
            except IntegrityError:
                self.db.rollback()
                existing = self.db.scalar(
                    select(NetWorthSnapshotRecord).where(
                        NetWorthSnapshotRecord.user_id == user_id,
                        NetWorthSnapshotRecord.competence == competence,
                    )
                )
                if existing is None:
                    raise
        return {
            "competence": existing.competence,
            "total_assets": existing.total_assets,
            "total_liabilities": existing.total_liabilities,
            "net_worth": existing.net_worth,
            "captured_at": existing.captured_at,
        }

    def _named_goal_output(self, goal: NamedAssetGoalRecord) -> dict[str, object]:
        asset = self.db.scalar(
            select(NetWorthItemRecord).where(
                NetWorthItemRecord.id == goal.asset_id,
                NetWorthItemRecord.user_id == goal.user_id,
                NetWorthItemRecord.kind == "asset",
            )
        )
        if asset is None:
            raise AuthError("named_goal_asset_not_found", 404)
        today = self.clock().astimezone(ZoneInfo("America/Sao_Paulo")).date()
        months = max(
            0,
            (goal.deadline.year - today.year) * 12
            + goal.deadline.month
            - today.month
            + (goal.deadline.day > today.day),
        )
        progress = asset.value * Decimal("100") / goal.target_amount
        remaining = max(Decimal("0"), goal.target_amount - asset.value)
        if remaining == 0:
            monthly = Decimal("0.00")
            status = "on_track"
        elif months == 0:
            monthly = None
            status = "overdue"
        else:
            monthly = aporte_necessario(
                alvo=goal.target_amount,
                inicial=asset.value,
                taxa_percentual=goal.annual_rate,
                prazo_meses=months,
            ).quantize(Decimal("0.01"))
            status = "needs_contribution"
        return {
            "id": goal.id,
            "name": self.security.decrypt(goal.name_encrypted),
            "category": goal.category,
            "asset_id": goal.asset_id,
            "asset_name": self.security.decrypt(asset.name_encrypted),
            "target_amount": goal.target_amount,
            "deadline": goal.deadline,
            "annual_rate": goal.annual_rate,
            "current_value": asset.value,
            "progress_percent": progress.quantize(Decimal("0.01")),
            "remaining_amount": remaining,
            "months_remaining": months,
            "monthly_contribution_needed": monthly,
            "projection_status": status,
        }

    def list_named_asset_goals(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        self.require_category_owner(user_id)
        goals = self.db.scalars(
            select(NamedAssetGoalRecord)
            .where(NamedAssetGoalRecord.user_id == user_id)
            .order_by(NamedAssetGoalRecord.created_at, NamedAssetGoalRecord.id)
        ).all()
        return [self._named_goal_output(goal) for goal in goals]

    def create_named_asset_goal(
        self, user_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        asset = self.db.scalar(
            select(NetWorthItemRecord).where(
                NetWorthItemRecord.id == values["asset_id"],
                NetWorthItemRecord.user_id == user_id,
                NetWorthItemRecord.kind == "asset",
            )
        )
        if asset is None:
            raise AuthError("named_goal_asset_not_found", 404)
        today = self.clock().astimezone(ZoneInfo("America/Sao_Paulo")).date()
        if values["deadline"] <= today:
            raise AuthError("named_goal_deadline_must_be_future", 422)
        goal = NamedAssetGoalRecord(
            user_id=user_id,
            asset_id=asset.id,
            name_encrypted=self.security.encrypt(str(values["name"])),
            category=values["category"],
            target_amount=values["target_amount"],
            deadline=values["deadline"],
            annual_rate=values["annual_rate"],
        )
        self.db.add(goal)
        self.db.commit()
        return self._named_goal_output(goal)

    def delete_named_asset_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        self.require_category_owner(user_id)
        goal = self.db.scalar(
            select(NamedAssetGoalRecord).where(
                NamedAssetGoalRecord.id == goal_id, NamedAssetGoalRecord.user_id == user_id
            )
        )
        if goal is None:
            raise AuthError("named_goal_not_found", 404)
        self.db.delete(goal)
        self.db.commit()

    def confirmed_financing_output(self, record: ConfirmedFinancingRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "name": self.security.decrypt(record.name_encrypted),
            "principal": record.principal,
            "asset_value": record.asset_value,
            "down_payment": record.down_payment,
            "installments": record.installments,
            "annual_rate": record.annual_rate,
            "installment_amount": record.installment_amount,
            "first_payment_on": record.first_payment_on,
            "expense_id": record.expense_id,
            "confirmed_at": record.confirmed_at,
            "origin": "financing",
            "current_balance_policy": "initial_until_reconciled",
        }

    def list_confirmed_financings(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        self.require_category_owner(user_id)
        records = self.db.scalars(
            select(ConfirmedFinancingRecord)
            .where(ConfirmedFinancingRecord.user_id == user_id)
            .order_by(ConfirmedFinancingRecord.confirmed_at, ConfirmedFinancingRecord.id)
        ).all()
        return [self.confirmed_financing_output(record) for record in records]

    def confirm_real_financing(
        self, user_id: uuid.UUID, data: dict[str, object], idempotency_key: str
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        # A repeated request returns the same real financing or conflicts;
        # it never creates a second liability or an extra expense.
        encoded = json.dumps(
            {key: str(value) for key, value in sorted(data.items())},
            sort_keys=True,
        ).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        existing = self.db.scalar(
            select(ConfirmedFinancingRecord).where(
                ConfirmedFinancingRecord.user_id == user_id,
                ConfirmedFinancingRecord.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if existing.request_digest != digest:
                raise AuthError("financing_idempotency_conflict", 409)
            return self.confirmed_financing_output(existing)

        plan = simulate_financing(
            data["asset_value"],
            data["down_payment"],
            data["installments"],
            data["annual_rate"],
        )
        if plan.financed_amount <= 0 or plan.installment_amount <= 0:
            raise AuthError("financing_requires_positive_debt", 422)
        expense = None
        if data["create_recurring_expense"]:
            category = str(data["expense_category_key"])
            if not self.valid_expense_category(user_id, category):
                raise AuthError("category_not_found", 404)
            account = self.db.scalar(
                select(AccountRecord).where(
                    AccountRecord.id == data["expense_account_id"],
                    AccountRecord.user_id == user_id,
                )
            )
            if account is None:
                raise AuthError("account_not_found", 404)
            expense = ExpenseRecord(
                user_id=user_id,
                account_id=account.id,
                credit_card_id=None,
                category_key=category,
                description_encrypted=self.security.encrypt(
                    "Parcela do financiamento: " + str(data["name"])
                ),
                amount=plan.installment_amount,
                occurred_on=data["first_payment_on"],
                recurring=True,
                idempotency_key="financing:" + idempotency_key,
            )
            self.db.add(expense)
            self.db.flush()

        record = ConfirmedFinancingRecord(
            user_id=user_id,
            name_encrypted=self.security.encrypt(str(data["name"])),
            principal=plan.financed_amount,
            asset_value=plan.asset_value,
            down_payment=plan.down_payment,
            installments=plan.installments,
            annual_rate=plan.annual_rate,
            installment_amount=plan.installment_amount,
            expense_id=expense.id if expense is not None else None,
            first_payment_on=data["first_payment_on"],
            idempotency_key=idempotency_key,
            request_digest=digest,
        )
        self.db.add(record)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(ConfirmedFinancingRecord).where(
                    ConfirmedFinancingRecord.user_id == user_id,
                    ConfirmedFinancingRecord.idempotency_key == idempotency_key,
                )
            )
            if existing is None:
                raise
            if existing.request_digest != digest:
                raise AuthError("financing_idempotency_conflict", 409) from None
            return self.confirmed_financing_output(existing)
        self.db.refresh(record)
        return self.confirmed_financing_output(record)

    def create_net_worth_item(
        self, user_id: uuid.UUID, kind: str, name: str, value: Decimal, annual_rate: Decimal | None
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        item = NetWorthItemRecord(
            user_id=user_id,
            kind=kind,
            name_encrypted=self.security.encrypt(name),
            value=value,
            annual_rate=annual_rate,
        )
        self.db.add(item)
        self.db.commit()
        return self.net_worth_item_output(item)

    def update_net_worth_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        item = self.db.scalar(
            select(NetWorthItemRecord).where(
                NetWorthItemRecord.id == item_id, NetWorthItemRecord.user_id == user_id
            )
        )
        if item is None:
            raise AuthError("net_worth_item_not_found", 404)
        if values.get("name") is not None:
            item.name_encrypted = self.security.encrypt(str(values["name"]))
        if values.get("value") is not None:
            item.value = values["value"]
        if "annual_rate" in values:
            item.annual_rate = values["annual_rate"]
        item.updated_at = self.clock()
        self.db.commit()
        return self.net_worth_item_output(item)

    def delete_net_worth_item(self, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
        self.require_category_owner(user_id)
        item = self.db.scalar(
            select(NetWorthItemRecord).where(
                NetWorthItemRecord.id == item_id, NetWorthItemRecord.user_id == user_id
            )
        )
        if item is None:
            raise AuthError("net_worth_item_not_found", 404)
        self.db.delete(item)
        self.db.commit()

    def upsert_budget_goal(
        self, user_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        category_key = values.get("category_key")
        if values["kind"] == "category_expense":
            if category_key is None or not self.valid_expense_category(user_id, str(category_key)):
                raise AuthError("category_not_found", 404)
        elif category_key is not None:
            raise AuthError("category_not_applicable", 400)
        record = self.db.scalar(
            select(BudgetGoalRecord)
            .where(BudgetGoalRecord.user_id == user_id, BudgetGoalRecord.kind == values["kind"])
            .where(BudgetGoalRecord.category_key == category_key)
            .with_for_update()
        )
        if record is None:
            record = BudgetGoalRecord(user_id=user_id, **values)
            self.db.add(record)
        else:
            record.target = values["target"]
            record.alert_threshold = values["alert_threshold"]
        self.db.commit()
        return self.budget_goal_output(record)

    @staticmethod
    def budget_goal_output(record: BudgetGoalRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "kind": record.kind,
            "category_key": record.category_key,
            "target": record.target,
            "alert_threshold": record.alert_threshold,
        }

    def budget_progress(self, user_id: uuid.UUID, competence: date) -> list[dict[str, object]]:
        output = []
        income = self.income_summary(user_id, competence)["total"]
        goals = self.db.scalars(select(BudgetGoalRecord).where(BudgetGoalRecord.user_id == user_id))
        for goal in goals:
            actual = (
                income
                if goal.kind == "income_total"
                else self.expenses_for_month(user_id, competence, goal.category_key)
            )
            percentage = actual / goal.target * Decimal("100")
            level = "on_track"
            if goal.kind == "income_total":
                # SPEC-021-R06: meta de renda é piso; sinaliza quando não foi atingida.
                level = "reached" if percentage >= Decimal("100") else "below_target"
            elif percentage >= Decimal("100"):
                level = "exceeded"
            elif percentage >= goal.alert_threshold:
                level = "alert"
            elif percentage >= Decimal("70"):
                level = "attention"
            output.append(
                {
                    **self.budget_goal_output(goal),
                    "actual": actual,
                    "percentage": percentage,
                    "status": level,
                }
            )
        return output

    @staticmethod
    def _score_band(score: Decimal) -> str:
        if score < 40:
            return "critical"
        if score < 60:
            return "attention"
        if score < 80:
            return "healthy"
        return "excellent"

    def health_score(self, user_id: uuid.UUID, competence: date | None = None) -> dict[str, object]:
        self.require_category_owner(user_id)
        month = (competence or self.clock().date()).replace(day=1)
        income = self.income_summary(user_id, month)["total"]
        if income <= 0:
            raise AuthError("health_score_income_unavailable", 422)
        rule = self.db.get(HealthScoreRuleRecord, "default")
        if rule is None:
            raise AuthError("health_score_rule_unavailable", 503)
        expenses = self.expenses_for_month(user_id, month, None)
        spending_ratio = expenses / income
        spending = max(
            Decimal("0"),
            min(
                Decimal("100"),
                (Decimal("1") - max(Decimal("0"), spending_ratio - Decimal("0.5")) * 2) * 100,
            ),
        )
        liquid = sum(
            (
                self._account_current_balance(account, month)
                for account in self.db.scalars(
                    select(AccountRecord).where(
                        AccountRecord.user_id == user_id,
                        AccountRecord.account_type.in_(("checking", "savings", "cash")),
                    )
                )
            ),
            Decimal("0"),
        )
        reserve = (
            Decimal("100")
            if expenses == 0
            else max(Decimal("0"), min(Decimal("100"), liquid / expenses / 6 * 100))
        )
        debt = sum(
            (
                self.card_invoice(user_id, card.id, month)["invoice_total"]
                for card in self.db.scalars(
                    select(CreditCardRecord).where(CreditCardRecord.user_id == user_id)
                )
            ),
            Decimal("0"),
        )
        debt_ratio = debt / income
        debt_factor = max(
            Decimal("0"),
            min(
                Decimal("100"),
                (Decimal("1") - max(Decimal("0"), debt_ratio - Decimal("0.2")) / Decimal("0.3"))
                * 100,
            ),
        )
        goals = self.budget_progress(user_id, month)
        goal_factor = (
            Decimal("100")
            if not goals
            else sum(
                (
                    min(Decimal("100"), row["percentage"])
                    if row["kind"] == "income_total"
                    else max(Decimal("0"), Decimal("200") - row["percentage"])
                    for row in goals
                ),
                Decimal("0"),
            )
            / len(goals)
        )
        factors = [
            ("spending", spending, "Reduza gastos para manter mais da renda disponível."),
            ("reserve", reserve, "Amplie sua reserva líquida para cobrir despesas essenciais."),
            ("debt", debt_factor, "Reduza o comprometimento da renda com faturas e dívidas."),
            ("goals", goal_factor, "Aproxime os gastos e a renda das metas definidas."),
        ]
        weights = (rule.spending_weight, rule.reserve_weight, rule.debt_weight, rule.goals_weight)
        score = sum(
            (factor[1] * weight for factor, weight in zip(factors, weights, strict=True)),
            Decimal("0"),
        ) / Decimal("100")
        score = score.quantize(Decimal("0.01"))
        record = self.db.scalar(
            select(HealthScoreRecord)
            .where(HealthScoreRecord.user_id == user_id, HealthScoreRecord.competence == month)
            .with_for_update()
        )
        serialized = {name: str(value) for name, value, _ in factors}
        if record is None:
            record = HealthScoreRecord(
                user_id=user_id,
                competence=month,
                score=score,
                classification=self._score_band(score),
                factors=serialized,
                rule_version=rule.version,
            )
            self.db.add(record)
        else:
            record.score, record.classification, record.factors, record.rule_version = (
                score,
                self._score_band(score),
                serialized,
                rule.version,
            )
        self.db.commit()
        history = self.db.scalars(
            select(HealthScoreRecord)
            .where(HealthScoreRecord.user_id == user_id)
            .order_by(HealthScoreRecord.competence)
        )
        weakest = sorted(factors, key=lambda item: item[1])[:2]
        return {
            "competence": month,
            "score": score,
            "classification": self._score_band(score),
            "factors": [
                {"key": name, "score": value, "suggestion": suggestion}
                for name, value, suggestion in weakest
            ],
            "history": [{"competence": row.competence, "score": row.score} for row in history],
            "rule_version": rule.version,
            "educational": True,
        }

    def spending_by_category(
        self, user_id: uuid.UUID, start: date, end: date
    ) -> list[dict[str, object]]:
        """SPEC-022-R03/R05: total por categoria no intervalo; categorias sem gasto não aparecem."""
        if start > end:
            raise AuthError("invalid_period", 400)
        self.require_category_owner(user_id)
        totals: dict[str, Decimal] = {}
        current = start.replace(day=1)
        while current <= end.replace(day=1):
            month_start, month_end = self.month_bounds(current)
            for record in self.db.scalars(
                select(ExpenseRecord).where(ExpenseRecord.user_id == user_id)
            ):
                if (record.recurring and record.occurred_on < month_end) or (
                    not record.recurring and month_start <= record.occurred_on < month_end
                ):
                    totals[record.category_key] = (
                        totals.get(record.category_key, Decimal("0")) + record.amount
                    )
            current = month_end
        grand = sum(totals.values(), Decimal("0"))
        return [
            {
                "category_key": key,
                "total": value,
                "percentage": (value / grand * Decimal("100")).quantize(Decimal("0.01")),
            }
            for key, value in sorted(totals.items(), key=lambda item: (-item[1], item[0]))
            if value > 0
        ]

    def dashboard(self, user_id: uuid.UUID, start: date, end: date) -> list[dict[str, object]]:
        if start > end:
            raise AuthError("invalid_period", 400)
        result = []
        current = start.replace(day=1)
        last = end.replace(day=1)
        while current <= last:
            summary = self.balance_summary(user_id, current)
            result.append(summary)
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        return result

    def expense_output(self, record: ExpenseRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "description": self.security.decrypt(record.description_encrypted),
            "amount": record.amount,
            "category_key": record.category_key,
            "occurred_on": record.occurred_on,
            "recurring": record.recurring,
            "account_id": record.account_id,
            "credit_card_id": record.credit_card_id,
            "installment_group": record.installment_group,
            "installment_number": record.installment_number,
            "installment_count": record.installment_count,
        }

    def valid_expense_category(self, user_id: uuid.UUID, key: str) -> bool:
        if key.startswith("standard:"):
            category = key.removeprefix("standard:")
            return category in DEFAULT_CATEGORY_KEYS
        if not key.startswith("personal:"):
            return False
        try:
            category_id = uuid.UUID(key.removeprefix("personal:"))
        except ValueError:
            return False
        return (
            self.db.scalar(
                select(CategoryRecord.id).where(
                    CategoryRecord.id == category_id,
                    CategoryRecord.user_id == user_id,
                    CategoryRecord.active.is_(True),
                )
            )
            is not None
        )

    def create_expense(
        self, user_id: uuid.UUID, data: dict[str, object], idempotency_key: str
    ) -> dict[str, object]:
        self.require_category_owner(user_id)
        existing = self.db.scalar(
            select(ExpenseRecord).where(
                ExpenseRecord.user_id == user_id, ExpenseRecord.idempotency_key == idempotency_key
            )
        )
        if existing is not None:
            return self.expense_output(existing)
        account_id, card_id, category_key = (
            data["account_id"],
            data["credit_card_id"],
            data["category_key"],
        )
        if not self.valid_expense_category(user_id, str(category_key)):
            raise AuthError("category_not_found", 404)
        if account_id is not None:
            account = self.db.get(AccountRecord, account_id)
            if account is None or account.user_id != user_id:
                raise AuthError("account_not_found", 404)
        if card_id is not None:
            card = self.db.get(CreditCardRecord, card_id)
            if card is None or card.user_id != user_id:
                raise AuthError("credit_card_not_found", 404)
        count = int(data.get("installments") or 1)
        if count > 1 and (card_id is None or data["recurring"]):
            raise AuthError("installments_require_card", 422)
        amounts = (
            dividir_parcelas(Decimal(data["amount"]), count) if count > 1 else [data["amount"]]
        )
        group = uuid.uuid4() if count > 1 else None
        # A chave do cliente fica na 1ª parcela; as demais derivam dela (reenvio não duplica).
        derived = hashlib.sha256(idempotency_key.encode()).hexdigest()[:64]
        records = [
            ExpenseRecord(
                user_id=user_id,
                account_id=account_id,
                credit_card_id=card_id,
                category_key=str(category_key),
                description_encrypted=self.security.encrypt(str(data["description"])),
                amount=amount,
                occurred_on=somar_meses(data["occurred_on"], index),
                recurring=bool(data["recurring"]),
                idempotency_key=idempotency_key if index == 0 else f"{derived}#{index + 1}",
                installment_group=group,
                installment_number=index + 1 if group else None,
                installment_count=count if group else None,
            )
            for index, amount in enumerate(amounts)
        ]
        self.db.add_all(records)
        self.db.commit()
        return self.expense_output(records[0])

    def list_expenses(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        return [
            self.expense_output(r)
            for r in self.db.scalars(
                select(ExpenseRecord)
                .where(ExpenseRecord.user_id == user_id)
                .order_by(ExpenseRecord.occurred_on, ExpenseRecord.id)
            )
        ]

    def update_expense(
        self, user_id: uuid.UUID, expense_id: uuid.UUID, values: dict[str, object]
    ) -> dict[str, object]:
        record = self.db.scalar(
            select(ExpenseRecord)
            .where(ExpenseRecord.id == expense_id, ExpenseRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("expense_not_found", 404)
        if values.get("category_key") is not None and not self.valid_expense_category(
            user_id, str(values["category_key"])
        ):
            raise AuthError("category_not_found", 404)
        if values.get("description") is not None:
            record.description_encrypted = self.security.encrypt(str(values["description"]))
        for key in ("amount", "category_key", "occurred_on", "recurring"):
            if values.get(key) is not None:
                setattr(record, key, values[key])
        self.db.commit()
        return self.expense_output(record)

    def delete_expense(self, user_id: uuid.UUID, expense_id: uuid.UUID) -> None:
        record = self.db.scalar(
            select(ExpenseRecord)
            .where(ExpenseRecord.id == expense_id, ExpenseRecord.user_id == user_id)
            .with_for_update()
        )
        if record is None:
            raise AuthError("expense_not_found", 404)
        linked = self.db.scalar(
            select(ConfirmedFinancingRecord.id).where(
                ConfirmedFinancingRecord.user_id == user_id,
                ConfirmedFinancingRecord.expense_id == expense_id,
            )
        )
        if linked is not None:
            raise AuthError("financing_expense_linked", 409)
        self.db.delete(record)
        self.db.commit()

    def request_password_recovery(self, email: str) -> None:
        """Request a reset without revealing whether the address belongs to an account."""
        now = self.clock()
        normalized = normalize_email(email)
        user = self.db.scalar(
            select(UserRecord)
            .where(UserRecord.email_lookup == self.security.lookup(normalized))
            .with_for_update()
        )
        if user is None:
            self.db.rollback()
            return
        last_issued = self.db.scalar(
            select(PasswordResetTokenRecord.issued_at)
            .where(PasswordResetTokenRecord.user_id == user.id)
            .order_by(PasswordResetTokenRecord.issued_at.desc())
            .limit(1)
        )
        if last_issued is not None and now < last_issued + timedelta(seconds=60):
            self.db.rollback()
            return
        raw_token = secrets.token_urlsafe(48)
        try:
            if self.email_delivery is None:
                raise EmailDeliveryError("password reset delivery is not configured")
            self.email_delivery.deliver_password_reset(recipient=normalized, token=raw_token)
        except (AttributeError, EmailDeliveryError):
            # It has the same response for unknown addresses and delivery failures.
            self.db.rollback()
            return
        self.db.execute(
            update(PasswordResetTokenRecord)
            .where(
                PasswordResetTokenRecord.user_id == user.id,
                PasswordResetTokenRecord.used_at.is_(None),
                PasswordResetTokenRecord.invalidated_at.is_(None),
            )
            .values(invalidated_at=now)
        )
        self.db.add(
            PasswordResetTokenRecord(
                digest=token_digest(raw_token),
                user_id=user.id,
                issued_at=now,
                expires_at=now + timedelta(minutes=30),
            )
        )
        self.db.commit()

    def reset_password(self, raw_token: str, new_password: str) -> None:
        now = self.clock()
        token = self.db.scalar(
            select(PasswordResetTokenRecord)
            .where(PasswordResetTokenRecord.digest == token_digest(raw_token))
            .with_for_update()
        )
        if (
            token is None
            or token.used_at is not None
            or token.invalidated_at is not None
            or token.expires_at <= now
        ):
            self.db.rollback()
            raise AuthError("invalid_password_reset_token", 400)
        user = self.db.scalar(
            select(UserRecord).where(UserRecord.id == token.user_id).with_for_update()
        )
        if user is None:
            self.db.rollback()
            raise AuthError("invalid_password_reset_token", 400)
        user.password_hash = self.security.hasher.hash(new_password)
        token.used_at = now
        self.db.execute(
            update(SessionRecord)
            .where(SessionRecord.user_id == user.id, SessionRecord.revoked.is_(False))
            .values(revoked=True)
        )
        self.db.add(
            AuditLogRecord(user_id=user.id, action="password_changed", occurred_at=self.clock())
        )
        self.db.commit()

    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> None:
        user = self.db.scalar(select(UserRecord).where(UserRecord.id == user_id).with_for_update())
        if user is None or not self.security.verify(
            user.password_hash if user else self.security.dummy_hash, current_password
        ):
            self.db.rollback()
            raise AuthError("invalid_current_password")
        user.password_hash = self.security.hasher.hash(new_password)
        self.db.execute(
            update(SessionRecord)
            .where(SessionRecord.user_id == user.id, SessionRecord.revoked.is_(False))
            .values(revoked=True)
        )
        self.db.add(
            AuditLogRecord(user_id=user.id, action="password_changed", occurred_at=self.clock())
        )
        self.db.commit()

    def login(self, email: str, password: str) -> tuple[str, str]:
        now = self.clock()
        normalized = normalize_email(email)
        key = self.security.lookup(f"login-attempt:{normalized}")
        # Bounded retention for abandoned failures; preserves any active lock.
        self.db.execute(
            delete(LoginAttemptRecord).where(
                LoginAttemptRecord.touched_at < now - timedelta(days=1),
                (LoginAttemptRecord.blocked_until.is_(None))
                | (LoginAttemptRecord.blocked_until <= now),
            )
        )
        self.db.execute(
            insert(LoginAttemptRecord)
            .values(email_key=key, failures=0, touched_at=now)
            .on_conflict_do_nothing(index_elements=[LoginAttemptRecord.email_key])
        )
        # Lock before verifying so concurrent failures and successes are serialized
        # across workers and IPs, including the first attempt at a new address.
        attempt = self.db.scalar(
            select(LoginAttemptRecord).where(LoginAttemptRecord.email_key == key).with_for_update()
        )
        user = self.db.scalar(
            select(UserRecord).where(UserRecord.email_lookup == self.security.lookup(normalized))
        )
        valid = self.security.verify(
            user.password_hash if user else self.security.dummy_hash, password
        )
        now = self.clock()
        # Hash work is still done for locked and nonexistent addresses.
        if attempt.blocked_until is not None:
            if now < attempt.blocked_until:
                retry = max(1, math.ceil((attempt.blocked_until - now).total_seconds()))
                self.db.commit()  # Release the row lock without extending the deadline.
                raise AuthError("login_temporarily_unavailable", 429, retry)
            attempt.failures = 0
            attempt.blocked_until = None
        attempt.touched_at = now
        if not valid or user is None:
            attempt.failures += 1
            if attempt.failures >= 5:
                attempt.blocked_until = now + timedelta(minutes=15)
                self.db.commit()
                raise AuthError("login_temporarily_unavailable", 429, 900)
            self.db.commit()  # Failed credentials must not roll back their counter.
            raise AuthError("invalid_credentials")
        attempt.failures = 0
        attempt.blocked_until = None
        if self.security.hasher.check_needs_rehash(user.password_hash):
            user.password_hash = self.security.hasher.hash(password)
        self.db.execute(delete(SessionRecord).where(SessionRecord.expires_at < now))
        session = SessionRecord(
            user_id=user.id,
            created_at=now,
            expires_at=now + timedelta(seconds=self.settings.refresh_seconds),
        )
        self.db.add(session)
        self.db.flush()
        result = self.issue(session)
        self.db.commit()
        return result

    def issue(self, session: SessionRecord) -> tuple[str, str]:
        now = self.clock()
        access = jwt.encode(
            {
                "sub": str(session.user_id),
                "sid": str(session.id),
                "jti": str(uuid.uuid4()),
                "iat": now,
                "exp": now + timedelta(seconds=self.settings.access_seconds),
                "iss": "finnova",
                "aud": "finnova-clients",
                "type": "access",
            },
            self.settings.jwt_secret.get_secret_value(),
            algorithm="HS256",
        )
        refresh = secrets.token_urlsafe(48)
        self.db.add(RefreshRecord(digest=token_digest(refresh), session_id=session.id))
        return access, refresh

    def authenticate(self, access: str) -> tuple[User, SessionRecord]:
        try:
            claims = jwt.decode(
                access,
                self.settings.jwt_secret.get_secret_value(),
                algorithms=["HS256"],
                audience="finnova-clients",
                issuer="finnova",
                options={"require": ["sub", "sid", "jti", "iat", "exp", "type"]},
            )
            if claims["type"] != "access":
                raise ValueError("Invalid token type")
            session = self.db.get(SessionRecord, uuid.UUID(claims["sid"]))
            if (
                session is None
                or session.revoked
                or session.expires_at <= self.clock()
                or str(session.user_id) != claims["sub"]
            ):
                raise ValueError("Invalid session")
            user = self.db.get(UserRecord, session.user_id)
            if user is None:
                raise ValueError("Missing user")
            journal = DeletionJournal(
                self.settings.deletion_journal_path, self.settings.data_key.get_secret_value()
            )
            if journal.contains(user.id):
                raise ValueError("Deleted account")
        except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError, KeyError) as exc:
            raise AuthError("invalid_session") from exc
        return self.public_user(user), session

    def refresh(self, raw_token: str) -> tuple[str, str]:
        token = self.db.get(RefreshRecord, token_digest(raw_token))
        if token is None:
            raise AuthError("invalid_session")
        # Serializes refresh/logout for a family, including simultaneous replay.
        session = self.db.scalar(
            select(SessionRecord).where(SessionRecord.id == token.session_id).with_for_update()
        )
        self.db.refresh(token)
        if session is None or session.revoked or session.expires_at <= self.clock():
            raise AuthError("invalid_session")
        if token.used:
            session.revoked = True
            self.db.commit()
            raise AuthError("invalid_session")
        token.used = True
        result = self.issue(session)
        self.db.commit()
        return result

    def logout(self, access: str | None, refresh: str | None) -> None:
        session_id = None
        if refresh:
            token = self.db.get(RefreshRecord, token_digest(refresh))
            if token:
                session_id = token.session_id
        if access:
            try:
                _, session = self.authenticate(access)
            except AuthError:
                if not session_id:
                    raise
            else:
                if session_id and session_id != session.id:
                    raise AuthError("invalid_session")
                session_id = session.id
        if session_id:
            session = self.db.scalar(
                select(SessionRecord).where(SessionRecord.id == session_id).with_for_update()
            )
            if session:
                session.revoked = True
                self.db.commit()

    def list_sessions(self, user_id: uuid.UUID) -> list[SessionRecord]:
        """Return active sessions of the authenticated owner, never refresh records."""
        now = self.clock()
        return list(
            self.db.scalars(
                select(SessionRecord)
                .where(
                    SessionRecord.user_id == user_id,
                    SessionRecord.revoked.is_(False),
                    SessionRecord.expires_at > now,
                )
                .order_by(SessionRecord.created_at.desc())
            )
        )

    def revoke_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> bool:
        """Revoke one owned session. Repeating the request is intentionally harmless."""
        session = self.db.scalar(
            select(SessionRecord)
            .where(SessionRecord.id == session_id, SessionRecord.user_id == user_id)
            .with_for_update()
        )
        if session is None:
            self.db.rollback()
            raise SessionNotFoundError()
        if not session.revoked:
            session.revoked = True
            self.db.commit()
        else:
            self.db.rollback()
        return True

    def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        """Revoke every active session of the owner, including the requesting session."""
        result = self.db.execute(
            update(SessionRecord)
            .where(SessionRecord.user_id == user_id, SessionRecord.revoked.is_(False))
            .values(revoked=True)
        )
        self.db.add(
            AuditLogRecord(user_id=user_id, action="sessions_revoked", occurred_at=self.clock())
        )
        self.db.commit()
        return int(result.rowcount or 0)
