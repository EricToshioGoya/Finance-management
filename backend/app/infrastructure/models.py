import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ExternalApiKeyRecord(Base):
    """Separate, hashed, owner-revocable credentials for read-only third-party API."""

    __tablename__ = "external_api_keys"
    __table_args__ = (CheckConstraint("request_count >= 0", name="nonnegative_external_api_count"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_digest: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    scopes: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    window_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class WebhookSubscriptionRecord(Base):
    __tablename__ = "webhook_subscriptions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    secret_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WebhookAttemptRecord(Base):
    __tablename__ = "webhook_attempts"
    __table_args__ = (
        CheckConstraint("outcome IN ('succeeded', 'failed')", name="valid_webhook_attempt_outcome"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    payload_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    outcome: Mapped[str] = mapped_column(String(12), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer)
    failure_code: Mapped[str | None] = mapped_column(String(40))
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retry_of_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("webhook_attempts.id", ondelete="SET NULL")
    )


class UserRecord(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('usuario', 'administrador')", name="valid_user_role"),
        CheckConstraint("account_status = 'active'", name="valid_user_account_status"),
        CheckConstraint(
            "investor_profile IN ('conservador', 'moderado', 'arrojado') "
            "OR investor_profile IS NULL",
            name="valid_investor_profile",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    email_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    email_lookup: Mapped[str] = mapped_column(String(64), unique=True)
    pending_email_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    pending_email_lookup: Mapped[str | None] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="usuario")
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    account_status: Mapped[str] = mapped_column(
        String(20), default="active", server_default="active", nullable=False
    )
    investor_profile: Mapped[str | None] = mapped_column(String(20))


class PublicCompanyRecord(Base):
    """CVM catalogue metadata; this table deliberately has no user ownership or PDF content."""

    __tablename__ = "public_companies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, index=True)
    legal_name: Mapped[str] = mapped_column(String(180), index=True)
    sector: Mapped[str] = mapped_column(String(100))


class OfficialDocumentRecord(Base):
    """Index-only CVM document record. No binary document column is permitted here."""

    __tablename__ = "official_documents"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('DFP', 'ITR', 'FRE', 'IPE')", name="valid_document_type"
        ),
        CheckConstraint(
            "status IN ('active', 'restated', 'replaced')", name="valid_official_document_status"
        ),
        CheckConstraint(
            "link_status IN ('unchecked', 'available', 'broken')", name="valid_official_link_status"
        ),
        # OPEN-27: DFP/ITR por referência + versão; IPE por protocolo de entrega + versão.
        Index(
            "uq_official_document_identity",
            "company_id",
            "document_type",
            "cvm_reference_date",
            "cvm_version",
            unique=True,
            postgresql_where=text("document_type <> 'IPE'"),
        ),
        Index(
            "uq_official_ipe_identity",
            "company_id",
            "cvm_protocol",
            "cvm_version",
            unique=True,
            postgresql_where=text("document_type = 'IPE'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public_companies.id", ondelete="CASCADE"), index=True
    )
    document_type: Mapped[str] = mapped_column(String(8))
    subject: Mapped[str] = mapped_column(String(180))
    reference_period: Mapped[str] = mapped_column(String(80))
    delivered_at: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(12))
    official_url: Mapped[str] = mapped_column(String(1000))
    link_status: Mapped[str] = mapped_column(String(12), default="unchecked")
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # OPEN-27: identidade CNPJ (via empresa) + tipo + data de referência + versão.
    cvm_reference_date: Mapped[date | None] = mapped_column(Date)
    cvm_version: Mapped[int | None] = mapped_column(Integer)
    cvm_protocol: Mapped[str | None] = mapped_column(String(40))


class FinancialIndicatorRecord(Base):
    """Structured public CVM values; deliberately distinct from market indicators and PDFs."""

    __tablename__ = "financial_indicators"
    __table_args__ = (
        CheckConstraint(
            "metric IN ('net_revenue', 'net_income', 'equity')", name="valid_financial_metric"
        ),
        CheckConstraint(
            "period_kind IN ('annual', 'quarterly')", name="valid_financial_period_kind"
        ),
        CheckConstraint("unit = 'BRL_THOUSANDS'", name="valid_financial_indicator_unit"),
        CheckConstraint(
            "status IN ('active', 'restated')", name="valid_financial_indicator_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public_companies.id", ondelete="CASCADE"), index=True
    )
    metric: Mapped[str] = mapped_column(String(30), index=True)
    period_kind: Mapped[str] = mapped_column(String(12))
    reference_period: Mapped[str] = mapped_column(String(80))
    reference_date: Mapped[date] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    unit: Mapped[str] = mapped_column(String(20))
    source_name: Mapped[str] = mapped_column(String(180))
    source_url: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(12))
    published_at: Mapped[date] = mapped_column(Date)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CvmCachePurgeRunRecord(Base):
    """Aggregated public-cache maintenance evidence; no user or document payload is logged."""

    __tablename__ = "cvm_cache_purge_runs"
    __table_args__ = (CheckConstraint("status = 'completed'", name="valid_cvm_purge_status"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    documents_expunged: Mapped[int] = mapped_column(Integer, nullable=False)
    indicators_expunged: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(12), nullable=False)


class MarketQuoteRecord(Base):
    """Versioned local market reference; it is never represented as a live B3 feed."""

    __tablename__ = "market_quotes"
    __table_args__ = (
        CheckConstraint("asset_kind IN ('stock', 'fii')", name="valid_market_asset_kind"),
        CheckConstraint(
            "availability IN ('available', 'unavailable')", name="valid_market_availability"
        ),
    )

    ticker: Mapped[str] = mapped_column(String(12), primary_key=True)
    asset_kind: Mapped[str] = mapped_column(String(12), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    previous_close: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    referenced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    availability: Mapped[str] = mapped_column(String(12), nullable=False, default="available")
    source_name: Mapped[str] = mapped_column(String(180), nullable=False)


class MarketQuoteHistoryRecord(Base):
    """Closing-price history for educational return calculations, never a forecast."""

    __tablename__ = "market_quote_history"
    __table_args__ = (UniqueConstraint("ticker", "quoted_on", name="uq_market_quote_history_day"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(
        ForeignKey("market_quotes.ticker", ondelete="CASCADE"), index=True
    )
    quoted_on: Mapped[date] = mapped_column(Date, nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)


class NetWorthItemRecord(Base):
    """User-owned manual real asset or liability; projections never enter this table."""

    __tablename__ = "net_worth_items"
    __table_args__ = (
        CheckConstraint("kind IN ('asset', 'liability')", name="valid_net_worth_item_kind"),
        CheckConstraint("value > 0", name="positive_net_worth_item_value"),
        CheckConstraint(
            "annual_rate IS NULL OR annual_rate >= 0", name="nonnegative_net_worth_item_rate"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(12), nullable=False)
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    annual_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ConfirmedFinancingRecord(Base):
    """Real debt, separate from editable manual liabilities and hypothetical runs."""

    __tablename__ = "confirmed_financings"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_financing_user_request"),
        CheckConstraint("principal > 0", name="positive_confirmed_financing_principal"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    principal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    asset_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    down_payment: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    installments: Mapped[int] = mapped_column(Integer, nullable=False)
    annual_rate: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    installment_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    first_payment_on: Mapped[date | None] = mapped_column(Date)
    expense_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("expenses.id", ondelete="RESTRICT")
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class NamedAssetGoalRecord(Base):
    """A goal references one real manual asset, never creates a new balance."""

    __tablename__ = "named_asset_goals"
    __table_args__ = (
        CheckConstraint("target_amount > 0", name="positive_named_asset_goal"),
        CheckConstraint("annual_rate >= 0", name="nonnegative_named_goal_rate"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("net_worth_items.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    annual_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class InvestmentAssetClassRecord(Base):
    """Explicit owner classification of a real manual asset."""

    __tablename__ = "investment_asset_classes"
    __table_args__ = (
        UniqueConstraint("user_id", "asset_id", name="uq_investment_asset_class_owner"),
        CheckConstraint(
            "asset_class IN ('fixed_income', 'stocks', 'fiis', 'savings', 'other')",
            name="valid_investment_asset_class",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("net_worth_items.id", ondelete="CASCADE"), nullable=False
    )
    asset_class: Mapped[str] = mapped_column(String(20), nullable=False)


class InvestmentAllocationTargetRecord(Base):
    """Owner-set allocation target per fixed investment class."""

    __tablename__ = "investment_allocation_targets"
    __table_args__ = (
        UniqueConstraint("user_id", "asset_class", name="uq_allocation_target_owner_class"),
        CheckConstraint(
            "asset_class IN ('fixed_income', 'stocks', 'fiis', 'savings', 'other')",
            name="valid_allocation_target_class",
        ),
        CheckConstraint("target_percent >= 0 AND target_percent <= 100", name="target_pct_range"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_class: Mapped[str] = mapped_column(String(20), nullable=False)
    target_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)


class NetWorthSnapshotRecord(Base):
    """Immutable monthly position of real assets and liabilities."""

    __tablename__ = "net_worth_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "competence", name="uq_net_worth_snapshot_month"),
        CheckConstraint("total_liabilities >= 0", name="nonnegative_snapshot_liabilities"),
        CheckConstraint(
            "net_worth = total_assets - total_liabilities",
            name="consistent_snapshot_net_worth",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    competence: Mapped[date] = mapped_column(Date, nullable=False)
    total_assets: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    total_liabilities: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    net_worth: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class HealthScoreRuleRecord(Base):
    """Persisted default formula, editable as data rather than deployed source code."""

    __tablename__ = "health_score_rules"

    key: Mapped[str] = mapped_column(String(20), primary_key=True)
    spending_weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    reserve_weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    debt_weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    goals_weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    version: Mapped[str] = mapped_column(String(30), nullable=False)


class HealthScoreRecord(Base):
    __tablename__ = "health_scores"
    __table_args__ = (UniqueConstraint("user_id", "competence", name="uq_health_score_month"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    competence: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    rule_version: Mapped[str] = mapped_column(String(30), nullable=False)


class UsageEventRecord(Base):
    """Minimal product-use event; it deliberately has no payload column."""

    __tablename__ = "usage_events"
    __table_args__ = (
        CheckConstraint(
            "module IN ('dashboard', 'simulator', 'financial', 'profile')",
            name="valid_usage_event_module",
        ),
        CheckConstraint("action IN ('opened', 'viewed')", name="valid_usage_event_action"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    module: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(20))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AuditLogRecord(Base):
    """Append-only operational audit metadata, without request or financial payloads."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "action IN ('password_changed', 'sessions_revoked', 'account_deleted', "
            "'admin_users_listed')",
            name="valid_audit_action",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(40))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SessionRecord(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(default=False)


class RefreshRecord(Base):
    __tablename__ = "refresh_tokens"

    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_sessions.id", ondelete="CASCADE"), index=True
    )
    used: Mapped[bool] = mapped_column(default=False)


class RateBucket(Base):
    __tablename__ = "auth_rate_buckets"

    client_endpoint: Mapped[str] = mapped_column(String(64), primary_key=True)
    window: Mapped[int] = mapped_column(Integer, primary_key=True)
    count: Mapped[int] = mapped_column(Integer)


class LoginAttemptRecord(Base):
    __tablename__ = "auth_login_attempts"
    __table_args__ = (CheckConstraint("failures >= 0 AND failures <= 5", name="valid_failures"),)

    # Same normalized address policy as users, with a separate HMAC purpose.
    # No FK: nonexistent addresses must have exactly the same lock behavior.
    email_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    touched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class EmailConfirmationTokenRecord(Base):
    __tablename__ = "email_confirmation_tokens"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('email_confirmation', 'email_change')",
            name="valid_email_confirmation_purpose",
        ),
    )

    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    purpose: Mapped[str] = mapped_column(String(40), default="email_confirmation")
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PasswordResetTokenRecord(Base):
    __tablename__ = "password_reset_tokens"

    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserPreferencesRecord(Base):
    __tablename__ = "user_preferences"
    __table_args__ = (
        CheckConstraint("language IN ('pt', 'en')", name="valid_preference_language"),
        CheckConstraint("theme IN ('light', 'dark')", name="valid_preference_theme"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    language: Mapped[str] = mapped_column(String(2), default="pt")
    theme: Mapped[str] = mapped_column(String(10), default="light")
    in_app_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=False)


class AdvancedMetricsPreferenceRecord(Base):
    """An explicit opt-in for non-arrojado investor profiles."""

    __tablename__ = "advanced_metrics_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class WatchlistRecord(Base):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_watchlist_owner_company"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("public_companies.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NotificationPreferenceRecord(Base):
    """Per-kind in-app opt-out. Delivery channels stay outside this local capability."""

    __tablename__ = "notification_preferences"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('invoice_due', 'budget_goal_exceeded', 'watchlist_document', "
            "'recurring_expense_due', 'achievement_unlocked', 'monthly_summary')",
            name="valid_notification_preference_kind",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    kind: Mapped[str] = mapped_column(String(40), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NotificationRecord(Base):
    """Owner-only in-app notification; never a financial transaction or a delivery log."""

    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('invoice_due', 'budget_goal_exceeded', 'watchlist_document', "
            "'recurring_expense_due', 'achievement_unlocked', 'monthly_summary')",
            name="valid_notification_kind",
        ),
        UniqueConstraint("user_id", "kind", "source_key", name="uq_notification_event"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    source_key: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(String(280), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CategoryRecord(Base):
    __tablename__ = "categories"
    __table_args__ = (CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="valid_category_color"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    name_lookup: Mapped[str] = mapped_column(String(64))
    color: Mapped[str] = mapped_column(String(7))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class DefaultCategoryVisibilityRecord(Base):
    __tablename__ = "default_category_visibility"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    category_key: Mapped[str] = mapped_column(String(40), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class AccountRecord(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint(
            "account_type IN ('checking', 'savings', 'cash', 'investment')",
            name="valid_account_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    account_type: Mapped[str] = mapped_column(String(20))


class CreditCardRecord(Base):
    __tablename__ = "credit_cards"
    __table_args__ = (
        CheckConstraint("credit_limit > 0", name="positive_credit_limit"),
        CheckConstraint("closing_day BETWEEN 1 AND 31", name="valid_closing_day"),
        CheckConstraint("due_day BETWEEN 1 AND 31", name="valid_due_day"),
        CheckConstraint("alert_threshold BETWEEN 70 AND 100", name="valid_card_alert_threshold"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    closing_day: Mapped[int] = mapped_column(Integer)
    due_day: Mapped[int] = mapped_column(Integer)
    # OPEN-12: percentual do limite que dispara o alerta de proximidade (SPEC-020-R05).
    alert_threshold: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("80"), server_default="80"
    )


class RecurringIncomeRecord(Base):
    __tablename__ = "recurring_incomes"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_recurring_income"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL")
    )
    description_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128))


class OneTimeIncomeRecord(Base):
    __tablename__ = "one_time_incomes"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_one_time_income"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL")
    )
    description_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    occurred_on: Mapped[date] = mapped_column(Date, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128))


class BonusRecord(Base):
    __tablename__ = "bonuses"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="nonnegative_bonus"),
        CheckConstraint("periodicity IN ('monthly', 'annual')", name="valid_bonus_periodicity"),
        CheckConstraint(
            "(periodicity = 'monthly' AND reference_month IS NULL) OR "
            "(periodicity = 'annual' AND reference_month BETWEEN 1 AND 12)",
            name="valid_bonus_reference_month",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    description_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    periodicity: Mapped[str] = mapped_column(String(10))
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    reference_month: Mapped[int | None] = mapped_column(Integer)
    idempotency_key: Mapped[str] = mapped_column(String(128))


class ExpenseRecord(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_expense"),
        CheckConstraint(
            "(account_id IS NOT NULL) <> (credit_card_id IS NOT NULL)", name="one_expense_source"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT")
    )
    credit_card_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("credit_cards.id", ondelete="RESTRICT")
    )
    category_key: Mapped[str] = mapped_column(String(80))
    description_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    occurred_on: Mapped[date] = mapped_column(Date)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    # OPEN-12: parcelas de uma mesma compra no cartão compartilham o grupo.
    installment_group: Mapped[uuid.UUID | None] = mapped_column(index=True)
    installment_number: Mapped[int | None] = mapped_column(Integer)
    installment_count: Mapped[int | None] = mapped_column(Integer)


class ExchangeRateRecord(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        CheckConstraint("currency IN ('USD', 'EUR')", name="valid_exchange_currency"),
        CheckConstraint("rate_to_brl > 0", name="positive_exchange_rate"),
        CheckConstraint(
            "availability IN ('available', 'unavailable')", name="valid_exchange_availability"
        ),
    )

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    rate_to_brl: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    reference_date: Mapped[date] = mapped_column(Date)
    referenced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_name: Mapped[str] = mapped_column(String(120))
    availability: Mapped[str] = mapped_column(String(20), default="available")


class MarketIndicatorRecord(Base):
    __tablename__ = "market_indicators"
    __table_args__ = (
        CheckConstraint("code IN ('selic', 'cdi', 'ipca')", name="valid_indicator_code"),
    )

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    unit: Mapped[str] = mapped_column(String(20), default="percentual_anual")
    reference_date: Mapped[date] = mapped_column(Date)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(120), default="BCB_SGS")


class TreasuryBondRateRecord(Base):
    """Taxa de compra do Tesouro Direto na data-base mais recente (SPEC-007-R04, ADR-009)."""

    __tablename__ = "treasury_bond_rates"
    __table_args__ = (CheckConstraint("buy_rate > 0", name="positive_treasury_rate"),)

    bond_type: Mapped[str] = mapped_column(String(80), primary_key=True)
    maturity: Mapped[date] = mapped_column(Date, primary_key=True)
    buy_rate: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    reference_date: Mapped[date] = mapped_column(Date)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(120), default="Tesouro Transparente")


class SimulationRecord(Base):
    __tablename__ = "simulations"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('fixed_income', 'variable_income', 'foreign_currency')",
            name="valid_simulation_kind",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(20))
    label_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    payload: Mapped[dict] = mapped_column(JSON)
    final_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BudgetGoalRecord(Base):
    __tablename__ = "budget_goals"
    __table_args__ = (
        CheckConstraint("target > 0", name="positive_budget_goal"),
        CheckConstraint(
            "kind IN ('expense_total', 'income_total', 'category_expense')",
            name="valid_budget_goal_kind",
        ),
        CheckConstraint(
            "(kind = 'category_expense' AND category_key IS NOT NULL) OR "
            "(kind <> 'category_expense' AND category_key IS NULL)",
            name="valid_budget_goal_category",
        ),
        CheckConstraint(
            "alert_threshold >= 70 AND alert_threshold <= 100", name="valid_budget_alert_threshold"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(20))
    category_key: Mapped[str | None] = mapped_column(String(80))
    target: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    alert_threshold: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("90"))


class SharedLinkRecord(Base):
    """SPEC-044: convite e vínculo entre dois titulares (conta compartilhada)."""

    __tablename__ = "shared_links"
    __table_args__ = (
        CheckConstraint("inviter_id <> invitee_id", name="distinct_shared_members"),
        CheckConstraint(
            "status IN ('pending', 'active', 'declined', 'cancelled', 'expired', 'ended')",
            name="valid_shared_link_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    inviter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    invitee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(12))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SharedExpenseRecord(Base):
    """SPEC-045: despesa do pagador marcada como compartilhada dentro de um vínculo."""

    __tablename__ = "shared_expenses"
    __table_args__ = (
        CheckConstraint(
            "payer_percent > 0 AND payer_percent < 100", name="valid_shared_payer_percent"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    link_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("shared_links.id", ondelete="CASCADE"), index=True
    )
    expense_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE"), unique=True
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    payer_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SettlementRecord(Base):
    """SPEC-045: acerto de contas registrado entre os membros (sem transferência bancária)."""

    __tablename__ = "shared_settlements"
    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_settlement"),
        UniqueConstraint(
            "link_id", "payer_id", "idempotency_key", name="uq_settlement_idempotency"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    link_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("shared_links.id", ondelete="CASCADE"), index=True
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TaxEstimateRecord(Base):
    """SPEC-048: estimativa educativa de IR registrada pelo titular (alimenta a SPEC-049)."""

    __tablename__ = "tax_estimates"
    __table_args__ = (
        CheckConstraint(
            "regime IN ('fixed_income', 'stock', 'fii', 'day_trade')", name="valid_tax_regime"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    regime: Mapped[str] = mapped_column(String(12))
    competence: Mapped[date] = mapped_column(Date)
    sales: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    result: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    tax: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    exempt: Mapped[bool] = mapped_column(Boolean)
    darf_due_on: Mapped[date | None] = mapped_column(Date)
    rule_version: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PrivacySettingsRecord(Base):
    """SPEC-050: opção de privacidade da comparação anônima do score."""

    __tablename__ = "privacy_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    score_benchmark_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AchievementRecord(Base):
    """SPEC-051: conquista cosmética concedida uma única vez por titular."""

    __tablename__ = "achievements"
    __table_args__ = (UniqueConstraint("user_id", "code", name="uq_achievement_user_code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(40))
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OnboardingTourRecord(Base):
    """SPEC-052: estado do tour de primeiro acesso por titular."""

    __tablename__ = "onboarding_tours"
    __table_args__ = (
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'skipped')",
            name="valid_tour_status",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String(12))
    step: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PushDeviceRecord(Base):
    """SPEC-061: destino push do titular (token do dispositivo, cifrado em repouso)."""

    __tablename__ = "push_devices"
    __table_args__ = (UniqueConstraint("user_id", "token_lookup", name="uq_push_device_token"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_encrypted: Mapped[bytes] = mapped_column(LargeBinary)
    token_lookup: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NotificationDeliveryRecord(Base):
    """SPEC-061: resultado mínimo de cada tentativa externa (sem conteúdo nem destino)."""

    __tablename__ = "notification_deliveries"
    __table_args__ = (
        CheckConstraint("channel IN ('email', 'push')", name="valid_delivery_channel"),
        CheckConstraint(
            "status IN ('sent', 'failed', 'provider_unavailable', 'no_destination')",
            name="valid_delivery_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    notification_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE")
    )
    source: Mapped[str] = mapped_column(String(40))
    channel: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(24))
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReportSettingsRecord(Base):
    """SPEC-040: opt-in do resumo mensal automático."""

    __tablename__ = "report_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    monthly_summary_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MonthlySummaryRecord(Base):
    """SPEC-040: um resumo por titular e competência (idempotência do envio)."""

    __tablename__ = "monthly_summaries"
    __table_args__ = (
        UniqueConstraint("user_id", "competence", name="uq_monthly_summary"),
        CheckConstraint(
            "status IN ('sent', 'failed', 'provider_unavailable', 'no_destination')",
            name="valid_monthly_summary_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    competence: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(24))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
