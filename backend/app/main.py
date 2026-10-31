# ruff: noqa
import asyncio
import sqlite3
import time
import uuid
from collections import defaultdict
from collections.abc import Generator
from contextlib import asynccontextmanager
from csv import writer
from datetime import UTC, date, datetime, timedelta
from datetime import time as clock_time
from decimal import Decimal
from io import StringIO
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, Depends, FastAPI, Header, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.application.auth import PROFILE_GUIDANCE, QUIZ_QUESTIONS, AuthError, AuthService
from app.application.companies import CompanyService
from app.application.cvm_cache import CvmCacheService
from app.application.exchange_rates import ExchangeRateService
from app.application.external_api import ExternalApiService
from app.application.engagement import EngagementService
from app.application.profile_distribution import ProfileDistributionService
from app.application.sharing import SharingService
from app.application.planning_tax import PlanningTaxService
from app.application.engagement_features import EngagementFeaturesService
from app.application.monthly_summary import MonthlySummaryService
from app.application.webhooks import HttpWebhookDelivery, WebhookService
from app.application.market_quotes import MarketQuoteService
from app.config import Settings, get_settings
from app.domain.education import get_article, search_articles
from app.domain.financeiro import (
    aliquota_ir_renda_fixa,
    aporte_necessario,
    projetar,
    resultado_liquido,
)
from app.domain.financing import simulate_financing
from app.domain.financing_comparison import compare_financing_and_investing
from app.domain.foreign_currency import calcular_projecao_moeda_estrangeira
from app.domain.juros_compostos import ErroCalculo, MotorJurosCompostos, arredondar_moeda
from app.infrastructure.account_deletion import DeletionJournal
from app.infrastructure.email_delivery import (
    EmailConfirmationDelivery,
    UnconfiguredEmailConfirmationDelivery,
    WebhookEmailConfirmationDelivery,
)
from app.infrastructure.models import (
    NotificationDeliveryRecord,
    PushDeviceRecord,
    RateBucket,
)
from app.infrastructure.pdf import pdf_document
from app.infrastructure.channel_delivery import HttpsChannelDelivery, UnconfiguredChannelDelivery
from app.infrastructure.security import Security
from app.presentation.schemas import (
    AccountCreateInput,
    AccountDeletionInput,
    AccountOutput,
    AdminUsersPageOutput,
    AdvancedMetricsPreferenceInput,
    AdvancedMetricsPreferenceOutput,
    BalanceSummaryOutput,
    BonusCreateInput,
    BonusOutput,
    BonusUpdateInput,
    BudgetGoalInput,
    BudgetProgressOutput,
    CalculatorInput,
    CalculatorOutput,
    CardInvoiceOutput,
    CategoryCreateInput,
    CategoryOutput,
    CategoryVisibilityInput,
    ConfirmationInput,
    ConfirmationOutput,
    ConfirmedFinancingOutput,
    ConfirmFinancingInput,
    CreditCardCreateInput,
    CreditCardOutput,
    DashboardMonthOutput,
    EducationalArticleOutput,
    ErrorOutput,
    ExpenseCreateInput,
    ExpenseOutput,
    ExpenseUpdateInput,
    ExternalApiGrantCreated,
    ExternalApiGrantInput,
    ExternalApiGrantOutput,
    ExternalBalanceOutput,
    ExternalNetWorthOutput,
    EngagementOutput,
    ProfileDistributionOutput,
    AnnualSummaryOutput,
    CategorySpendingOutput,
    DeliveryOutput,
    MonthlySummaryOutput,
    PushDeviceInput,
    ReportSettingsInput,
    ReportSettingsOutput,
    AchievementOutput,
    PrivacySettingsInput,
    PrivacySettingsOutput,
    ScoreBenchmarkOutput,
    TourActionInput,
    TourOutput,
    PensionInput,
    PensionOutput,
    RetirementInput,
    RetirementOutput,
    TaxEstimateInput,
    TaxEstimateOutput,
    SettlementInput,
    ShareExpenseInput,
    SharedBalanceOutput,
    ShareSplitInput,
    SharingInviteInput,
    SharingInviteOutput,
    SharingOverviewOutput,
    FinancialIndicatorOutput,
    FinancialSourcesOutput,
    FinancingComparisonInput,
    FinancingComparisonOutput,
    FinancingInput,
    FinancingOutput,
    ForeignCurrencySimulationInput,
    ForeignCurrencySimulationOutput,
    HealthScoreOutput,
    IncomeSummaryOutput,
    IndicatorOutput,
    InvestmentAllocationOutput,
    InvestmentClassInput,
    InvestmentTargetInput,
    InvestorProfileOutput,
    LoginInput,
    MarketQuoteOutput,
    NamedAssetGoalInput,
    NamedAssetGoalOutput,
    NetWorthHeatmapOutput,
    NetWorthItemInput,
    NetWorthItemOutput,
    NetWorthItemUpdateInput,
    NetWorthOutput,
    NetWorthSnapshotOutput,
    NotificationEventInput,
    NotificationEventOutput,
    NotificationOutput,
    NotificationPreferenceInput,
    NotificationPreferenceOutput,
    OfficialDocumentOutput,
    OneTimeIncomeCreateInput,
    OneTimeIncomeOutput,
    OneTimeIncomeUpdateInput,
    PasswordChangeInput,
    PasswordRecoveryRequestInput,
    PasswordResetInput,
    PreferencesInput,
    PreferencesOutput,
    ProfileOutput,
    ProfileUpdateInput,
    PublicCompanyOutput,
    PublicUser,
    QuizAnswersInput,
    QuizQuestionOutput,
    QuizResultOutput,
    RecurringIncomeCreateInput,
    RecurringIncomeOutput,
    RecurringIncomeUpdateInput,
    RegisterInput,
    RevokeAllSessionsOutput,
    RiskMetricsOutput,
    SessionView,
    SimulationComparisonInput,
    SimulationComparisonOutput,
    SimulationCreateInput,
    SimulationOutput,
    StressCompareInput,
    StressCompareOutput,
    TargetContributionInput,
    TargetContributionOutput,
    TaxProjectionInput,
    TaxProjectionOutput,
    TokenOutput,
    UsageEventInput,
    WebhookAttemptOutput,
    WebhookSubscriptionCreated,
    WebhookSubscriptionInput,
    WebhookSubscriptionOutput,
    VariableIncomeSimulationInput,
    WatchlistMutationOutput,
    WatchlistOutput,
)

COOKIE = "__Secure-finnova_refresh"
COOKIE_PATH = "/api/v1/auth"
SENSITIVE = {
    f"{COOKIE_PATH}/{name}"
    for name in ("register", "login", "refresh", "logout", "email-confirmation")
} | {f"{COOKIE_PATH}/email-confirmation/confirm"}
SENSITIVE |= {
    f"{COOKIE_PATH}/password-recovery",
    f"{COOKIE_PATH}/password-recovery/confirm",
    f"{COOKIE_PATH}/password",
    f"{COOKIE_PATH}/account",
}
SESSION_PREFIX = f"{COOKIE_PATH}/sessions"
PROFILE_PREFIX = f"{COOKIE_PATH}/profile"
CATEGORY_PREFIX = f"{COOKIE_PATH}/categories"
FINANCIAL_PREFIX = f"{COOKIE_PATH}/financial"
COMPANY_PREFIX = "/api/v1/companies"
MARKET_PREFIX = "/api/v1/market"
ADMIN_PREFIX = "/api/v1/admin"
NOTIFICATION_PREFIX = "/api/v1/notifications"
bearer = HTTPBearer(auto_error=False)


def create_app(
    settings: Settings | None = None, email_delivery: EmailConfirmationDelivery | None = None
) -> FastAPI:
    settings = settings or get_settings()
    engine = create_engine(settings.database_url.get_secret_value(), pool_pre_ping=True)
    sessions = sessionmaker(engine, expire_on_commit=False)
    security = Security(settings.data_key.get_secret_value())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Fail closed: no request is served if replay of deletion intents fails.
        with sessions() as db:
            DeletionJournal(
                settings.deletion_journal_path, settings.data_key.get_secret_value()
            ).apply(db)
        task = asyncio.create_task(run_daily_cvm_cache_purge(app))
        summary_task = asyncio.create_task(run_daily_monthly_summary(app))
        try:
            yield
        finally:
            for running in (task, summary_task):
                running.cancel()
                try:
                    await running
                except asyncio.CancelledError:
                    pass

    app = FastAPI(
        lifespan=lifespan,
        title="FinNova",
        version="0.1.0",
        docs_url=None,
        openapi_url="/api/v1/openapi.json",
        redoc_url=None,
        responses={
            status: {"model": ErrorOutput} for status in (400, 401, 403, 404, 409, 422, 429, 503)
        },
    )
    if email_delivery is None:
        email_delivery = (
            WebhookEmailConfirmationDelivery(
                settings.email_webhook_url.get_secret_value(), settings.public_origin
            )
            if settings.email_webhook_url is not None
            else UnconfiguredEmailConfirmationDelivery()
        )
    app.state.engine, app.state.sessions, app.state.security = engine, sessions, security
    app.state.email_delivery = email_delivery
    app.state.webhook_delivery = HttpWebhookDelivery()
    # SPEC-061: canais externos opcionais; sem despachante configurado, nada é enviado.
    app.state.channel_delivery = {
        "email": HttpsChannelDelivery(settings.email_webhook_url.get_secret_value())
        if settings.email_webhook_url is not None
        else UnconfiguredChannelDelivery(),
        "push": HttpsChannelDelivery(settings.push_webhook_url.get_secret_value())
        if settings.push_webhook_url is not None
        else UnconfiguredChannelDelivery(),
    }
    app.state.clock = lambda: datetime.now(UTC)

    async def run_daily_cvm_cache_purge(application: FastAPI) -> None:
        sao_paulo = ZoneInfo("America/Sao_Paulo")
        while True:
            now = application.state.clock().astimezone(sao_paulo)
            scheduled = datetime.combine(now.date(), clock_time(hour=3), tzinfo=sao_paulo)
            if now >= scheduled:
                scheduled += timedelta(days=1)
            await asyncio.sleep((scheduled - now).total_seconds())
            try:
                with sessions() as db:
                    CvmCacheService(db, clock=application.state.clock).purge_expired()
            except (OSError, SQLAlchemyError):
                # No completed run is persisted on a failed transaction; retry at the next schedule.
                continue

    async def run_daily_monthly_summary(application: FastAPI) -> None:
        """SPEC-040: às 06h de São Paulo gera o resumo do mês anterior (idempotente)."""
        sao_paulo = ZoneInfo("America/Sao_Paulo")
        while True:
            now = application.state.clock().astimezone(sao_paulo)
            scheduled = datetime.combine(now.date(), clock_time(hour=6), tzinfo=sao_paulo)
            if now >= scheduled:
                scheduled += timedelta(days=1)
            await asyncio.sleep((scheduled - now).total_seconds())
            try:
                with sessions() as db:
                    auth = AuthService(
                        db,
                        settings,
                        security,
                        clock=application.state.clock,
                        channel_delivery=application.state.channel_delivery,
                    )
                    MonthlySummaryService(db, auth).run()
            except (OSError, SQLAlchemyError):
                continue

    def persist_usage_event(user_id: uuid.UUID, module: str, action: str) -> None:
        """A telemetry failure is isolated from the already accepted user flow."""
        try:
            with sessions() as db:
                AuthService(db, settings, security, clock=app.state.clock).record_usage_event(
                    user_id, module, action
                )
        except (OSError, SQLAlchemyError):
            # Retry/alerting requires future queue policy; never claim the action succeeded twice.
            return

    def service() -> Generator[AuthService, None, None]:
        with sessions() as db:
            yield AuthService(
                db,
                settings,
                security,
                clock=app.state.clock,
                email_delivery=app.state.email_delivery,
                channel_delivery=app.state.channel_delivery,
            )

    def company_service() -> Generator[CompanyService, None, None]:
        with sessions() as db:
            yield CompanyService(db, clock=app.state.clock)

    def exchange_rate_service() -> Generator[ExchangeRateService, None, None]:
        with sessions() as db:
            yield ExchangeRateService(db, app.state.clock)

    def market_quote_service() -> Generator[MarketQuoteService, None, None]:
        with sessions() as db:
            yield MarketQuoteService(db, clock=app.state.clock)

    Service = Annotated[AuthService, Depends(service)]
    CompanyServiceDependency = Annotated[CompanyService, Depends(company_service)]
    ExchangeRateServiceDependency = Annotated[ExchangeRateService, Depends(exchange_rate_service)]
    MarketQuoteServiceDependency = Annotated[MarketQuoteService, Depends(market_quote_service)]
    Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]

    @app.exception_handler(AuthError)
    async def auth_error(request: Request, error: AuthError):
        headers = {"WWW-Authenticate": "Bearer"} if error.status == 401 else {}
        if error.retry_after is not None:
            headers["Retry-After"] = str(error.retry_after)
        headers["Cache-Control"] = "no-store"
        payload: dict[str, object] = {"detail": error.code}
        if error.manual_entry_permitted:
            payload["manual_entry_permitted"] = True
        return JSONResponse(payload, status_code=error.status, headers=headers)

    @app.exception_handler(ErroCalculo)
    async def calculation_error(request: Request, error: ErroCalculo):
        return JSONResponse(
            {"detail": error.codigo}, status_code=422, headers={"Cache-Control": "no-store"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        # FastAPI's default errors include the raw input: never echo credentials.
        return JSONResponse({"detail": "invalid_input"}, status_code=422)

    @app.exception_handler(SQLAlchemyError)
    @app.exception_handler(OSError)
    @app.exception_handler(sqlite3.Error)
    async def database_error(request: Request, error: SQLAlchemyError):
        return JSONResponse({"detail": "service_unavailable"}, status_code=503)

    @app.middleware("http")
    async def protections(request: Request, call_next):
        if request.url.scheme != "https":
            return JSONResponse({"detail": "https_required"}, status_code=400)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin and origin != settings.public_origin:
                return JSONResponse({"detail": "invalid_origin"}, status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "invalid_origin"}, status_code=403)
        sensitive_path = (
            request.url.path in SENSITIVE
            or request.url.path.startswith(SESSION_PREFIX)
            or request.url.path.startswith(PROFILE_PREFIX)
            or request.url.path.startswith(CATEGORY_PREFIX)
            or request.url.path.startswith(FINANCIAL_PREFIX)
            or request.url.path.startswith(COMPANY_PREFIX)
            or request.url.path.startswith(NOTIFICATION_PREFIX)
        )
        if sensitive_path and request.method in {"POST", "PATCH", "DELETE"}:
            window = int(time.time()) // 60
            client = request.client.host if request.client else "unknown"
            endpoint = request.url.path
            if request.url.path.startswith(SESSION_PREFIX):
                endpoint = SESSION_PREFIX
            if request.url.path.startswith(PROFILE_PREFIX):
                endpoint = PROFILE_PREFIX
            if request.url.path.startswith(CATEGORY_PREFIX):
                endpoint = CATEGORY_PREFIX
            if request.url.path.startswith(FINANCIAL_PREFIX):
                endpoint = FINANCIAL_PREFIX
            if request.url.path.startswith(COMPANY_PREFIX):
                endpoint = COMPANY_PREFIX
            if request.url.path.startswith(NOTIFICATION_PREFIX):
                endpoint = NOTIFICATION_PREFIX
            key = security.lookup(f"rate:{client}:{endpoint}")
            try:
                with sessions() as db:
                    statement = insert(RateBucket).values(
                        client_endpoint=key, window=window, count=1
                    )
                    count = db.scalar(
                        statement.on_conflict_do_update(
                            index_elements=[RateBucket.client_endpoint, RateBucket.window],
                            set_={"count": RateBucket.count + 1},
                        ).returning(RateBucket.count)
                    )
                    db.execute(delete(RateBucket).where(RateBucket.window < window - 1))
                    db.commit()
                if count > settings.rate_limit:
                    return JSONResponse(
                        {"detail": "rate_limited"},
                        status_code=429,
                        headers={"Retry-After": str(60 - int(time.time()) % 60)},
                    )
            except SQLAlchemyError:
                return JSONResponse({"detail": "service_unavailable"}, status_code=503)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        return response

    def token_response(response: Response, tokens: tuple[str, str]) -> TokenOutput:
        access, refresh = tokens
        response.set_cookie(
            COOKIE,
            refresh,
            max_age=settings.refresh_seconds,
            secure=True,
            httponly=True,
            samesite="strict",
            path=COOKIE_PATH,
        )
        return TokenOutput(access_token=access, expires_in=settings.access_seconds)

    @app.get(f"{COOKIE_PATH}/account/deletion-preview", tags=["profile"])
    def deletion_preview(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return {
            "deleted": [
                "perfil e credenciais",
                "sessões e tokens",
                "contas e cartões",
                "receitas e despesas",
                "categorias, metas e simulações",
            ],
            "timing": "Exclusão imediata da base ativa após senha e confirmação por texto.",
            "legal_retention": (
                "Nenhuma retenção legal identificável configurada neste projeto acadêmico."
            ),
            "backups": "Exclusões são reaplicadas antes de liberar a aplicação após restauração.",
            "technical_retention": (
                "Registro técnico restrito, sem nome, e-mail ou UUID direto, "
                "impede reintrodução por backup."
            ),
        }

    @app.delete(f"{COOKIE_PATH}/account", status_code=204, tags=["profile"])
    def delete_account(
        data: AccountDeletionInput, response: Response, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_account(user.id, data.current_password.get_secret_value())
        response.delete_cookie(
            COOKIE, path=COOKIE_PATH, secure=True, httponly=True, samesite="strict"
        )

    @app.post(f"{COOKIE_PATH}/usage-events", status_code=202, tags=["telemetry"])
    def collect_usage_event(
        data: UsageEventInput,
        background_tasks: BackgroundTasks,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        background_tasks.add_task(persist_usage_event, user.id, data.module, data.action)

    @app.get(f"{ADMIN_PREFIX}/users", response_model=AdminUsersPageOutput, tags=["admin"])
    def list_admin_users(
        auth: Service,
        credentials: Credentials,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        query: str | None = Query(default=None, max_length=100),
        status: str | None = Query(default=None, max_length=20),
        profile: str | None = Query(default=None, max_length=40),
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_admin(user)
        return auth.list_admin_users(query, status, profile, page, page_size, user.id)

    @app.get(
        f"{COOKIE_PATH}/webhooks", response_model=list[WebhookSubscriptionOutput], tags=["webhooks"]
    )
    def list_webhooks(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return WebhookService(
            auth.db, security, auth, app.state.webhook_delivery
        ).list_subscriptions(user.id)

    @app.post(
        f"{COOKIE_PATH}/webhooks",
        response_model=WebhookSubscriptionCreated,
        status_code=201,
        tags=["webhooks"],
    )
    def create_webhook(data: WebhookSubscriptionInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return WebhookService(
            auth.db, security, auth, app.state.webhook_delivery
        ).create_subscription(user.id, data.url)

    @app.delete(f"{COOKIE_PATH}/webhooks/{{subscription_id}}", status_code=204, tags=["webhooks"])
    def disable_webhook(subscription_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        WebhookService(auth.db, security, auth, app.state.webhook_delivery).disable_subscription(
            user.id, subscription_id
        )

    @app.get(
        f"{COOKIE_PATH}/webhooks/{{subscription_id}}/attempts",
        response_model=list[WebhookAttemptOutput],
        tags=["webhooks"],
    )
    def list_webhook_attempts(subscription_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return WebhookService(auth.db, security, auth, app.state.webhook_delivery).list_attempts(
            user.id, subscription_id
        )

    @app.post(
        f"{COOKIE_PATH}/webhooks/{{subscription_id}}/attempts/{{attempt_id}}/retry",
        response_model=WebhookAttemptOutput,
        tags=["webhooks"],
    )
    def retry_webhook_attempt(
        subscription_id: uuid.UUID, attempt_id: uuid.UUID, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return WebhookService(auth.db, security, auth, app.state.webhook_delivery).retry_attempt(
            user.id, subscription_id, attempt_id
        )

    @app.get(f"{ADMIN_PREFIX}/engagement", response_model=EngagementOutput, tags=["admin"])
    def engagement_report(
        auth: Service,
        credentials: Credentials,
        start: date | None = None,
        end: date | None = None,
        inactive_days: int = Query(default=30, ge=1, le=365),
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return EngagementService(auth.db, auth).report(user, start, end, inactive_days)

    @app.get(
        f"{ADMIN_PREFIX}/investor-profiles",
        response_model=ProfileDistributionOutput,
        tags=["admin"],
    )
    def investor_profile_distribution(
        auth: Service,
        credentials: Credentials,
        start: date | None = None,
        end: date | None = None,
    ):
        """SPEC-062: distribuição agregada por resultado do quiz, filtrável por cadastro."""
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return ProfileDistributionService(auth.db, auth).distribution(user, start, end)

    # ---------- SPEC-044/045: vínculo entre usuários e despesas compartilhadas ----------
    SHARING_PREFIX = f"{COOKIE_PATH}/sharing"

    def sharing_user(auth: AuthService, credentials) -> uuid.UUID:
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return user.id

    def split_percent(data: ShareSplitInput) -> Decimal:
        try:
            return data.resolved_payer_percent()
        except ValueError as exc:
            raise AuthError("split_must_total_100", 422) from exc

    @app.get(SHARING_PREFIX, response_model=SharingOverviewOutput, tags=["sharing"])
    def sharing_overview(auth: Service, credentials: Credentials):
        return SharingService(auth.db, auth).overview(sharing_user(auth, credentials))

    @app.post(
        f"{SHARING_PREFIX}/invitations",
        response_model=SharingInviteOutput,
        status_code=202,
        tags=["sharing"],
    )
    def sharing_invite(data: SharingInviteInput, auth: Service, credentials: Credentials):
        return SharingService(auth.db, auth).invite(sharing_user(auth, credentials), data.email)

    @app.post(
        f"{SHARING_PREFIX}/invitations/{{link_id}}/accept",
        response_model=SharingOverviewOutput,
        tags=["sharing"],
    )
    def sharing_accept(link_id: uuid.UUID, auth: Service, credentials: Credentials):
        return SharingService(auth.db, auth).accept(sharing_user(auth, credentials), link_id)

    @app.post(
        f"{SHARING_PREFIX}/invitations/{{link_id}}/decline", status_code=204, tags=["sharing"]
    )
    def sharing_decline(link_id: uuid.UUID, auth: Service, credentials: Credentials):
        SharingService(auth.db, auth).decline(sharing_user(auth, credentials), link_id)
        return Response(status_code=204)

    @app.post(f"{SHARING_PREFIX}/invitations/{{link_id}}/cancel", status_code=204, tags=["sharing"])
    def sharing_cancel(link_id: uuid.UUID, auth: Service, credentials: Credentials):
        SharingService(auth.db, auth).cancel(sharing_user(auth, credentials), link_id)
        return Response(status_code=204)

    @app.post(f"{SHARING_PREFIX}/links/{{link_id}}/end", status_code=204, tags=["sharing"])
    def sharing_end(link_id: uuid.UUID, auth: Service, credentials: Credentials):
        SharingService(auth.db, auth).end(sharing_user(auth, credentials), link_id)
        return Response(status_code=204)

    @app.get(f"{SHARING_PREFIX}/balance", response_model=SharedBalanceOutput, tags=["sharing"])
    def sharing_balance(auth: Service, credentials: Credentials, link_id: uuid.UUID | None = None):
        return SharingService(auth.db, auth).balance(sharing_user(auth, credentials), link_id)

    @app.post(
        f"{SHARING_PREFIX}/expenses",
        response_model=SharedBalanceOutput,
        status_code=201,
        tags=["sharing"],
    )
    def sharing_share_expense(data: ShareExpenseInput, auth: Service, credentials: Credentials):
        return SharingService(auth.db, auth).share_expense(
            sharing_user(auth, credentials), data.expense_id, split_percent(data)
        )

    @app.patch(
        f"{SHARING_PREFIX}/expenses/{{share_id}}",
        response_model=SharedBalanceOutput,
        tags=["sharing"],
    )
    def sharing_update_expense(
        share_id: uuid.UUID, data: ShareSplitInput, auth: Service, credentials: Credentials
    ):
        return SharingService(auth.db, auth).update_share(
            sharing_user(auth, credentials), share_id, split_percent(data)
        )

    @app.delete(f"{SHARING_PREFIX}/expenses/{{share_id}}", status_code=204, tags=["sharing"])
    def sharing_unshare(share_id: uuid.UUID, auth: Service, credentials: Credentials):
        SharingService(auth.db, auth).unshare(sharing_user(auth, credentials), share_id)
        return Response(status_code=204)

    @app.post(
        f"{SHARING_PREFIX}/settlements",
        response_model=SharedBalanceOutput,
        status_code=201,
        tags=["sharing"],
    )
    def sharing_settle(
        data: SettlementInput, request: Request, auth: Service, credentials: Credentials
    ):
        return SharingService(auth.db, auth).settle(
            sharing_user(auth, credentials), data.amount, idempotency_key(request), data.link_id
        )

    @app.get("/api/v1/health", tags=["system"])
    def health():
        with engine.connect() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok"}

    @app.get("/api/v1/docs", include_in_schema=False, response_class=HTMLResponse)
    def docs():
        return (
            '<!doctype html><html lang="en"><head><title>FinNova API</title>'
            '<link rel="stylesheet" href="/swagger-ui.css"></head><body>'
            '<div id="swagger-ui"></div><script src="/swagger-ui-bundle.js"></script>'
            '<script src="/swagger-init.js"></script></body></html>'
        )

    @app.post(f"{COOKIE_PATH}/register", response_model=PublicUser, status_code=201, tags=["auth"])
    def register(data: RegisterInput, auth: Service):
        return auth.register(data.name, str(data.email), data.password.get_secret_value())

    @app.post(f"{COOKIE_PATH}/login", response_model=TokenOutput, tags=["auth"])
    def login(data: LoginInput, response: Response, auth: Service):
        return token_response(
            response, auth.login(str(data.email), data.password.get_secret_value())
        )

    @app.post(f"{COOKIE_PATH}/refresh", response_model=TokenOutput, tags=["auth"])
    def refresh(request: Request, response: Response, auth: Service):
        raw = request.cookies.get(COOKIE)
        if not raw:
            raise AuthError("invalid_session")
        return token_response(response, auth.refresh(raw))

    @app.post(f"{COOKIE_PATH}/email-confirmation", status_code=204, tags=["auth"])
    def request_email_confirmation(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        _, session = auth.authenticate(credentials.credentials)
        auth.request_email_confirmation(session.user_id)

    @app.post(
        f"{COOKIE_PATH}/email-confirmation/confirm",
        response_model=ConfirmationOutput,
        tags=["auth"],
    )
    def confirm_email_confirmation(data: ConfirmationInput, auth: Service):
        return ConfirmationOutput(email_verified=auth.confirm_email(data.token.get_secret_value()))

    @app.post(f"{COOKIE_PATH}/password-recovery", status_code=204, tags=["auth"])
    def request_password_recovery(data: PasswordRecoveryRequestInput, auth: Service):
        auth.request_password_recovery(str(data.email))

    @app.post(f"{COOKIE_PATH}/password-recovery/confirm", status_code=204, tags=["auth"])
    def reset_password(data: PasswordResetInput, auth: Service):
        auth.reset_password(data.token.get_secret_value(), data.new_password.get_secret_value())

    @app.patch(f"{COOKIE_PATH}/password", status_code=204, tags=["auth"])
    def change_password(
        data: PasswordChangeInput, response: Response, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.change_password(
            user.id, data.current_password.get_secret_value(), data.new_password.get_secret_value()
        )
        response.delete_cookie(
            COOKIE, path=COOKIE_PATH, secure=True, httponly=True, samesite="strict"
        )

    @app.get(f"{COOKIE_PATH}/me", response_model=PublicUser, tags=["auth"])
    def me(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        return auth.authenticate(credentials.credentials)[0]

    def profile_output(auth: AuthService, user_id: uuid.UUID) -> ProfileOutput:
        user, pending_email, preferences = auth.profile(user_id)
        return ProfileOutput(
            user=PublicUser.model_validate(user),
            pending_email=pending_email,
            preferences=PreferencesOutput.model_validate(preferences),
        )

    @app.get(PROFILE_PREFIX, response_model=ProfileOutput, tags=["auth"])
    def profile(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return profile_output(auth, user.id)

    @app.get(
        f"{COOKIE_PATH}/investor-profile/quiz",
        response_model=list[QuizQuestionOutput],
        tags=["auth"],
    )
    def investor_profile_quiz(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return QUIZ_QUESTIONS

    @app.get(f"{COOKIE_PATH}/investor-profile", response_model=InvestorProfileOutput, tags=["auth"])
    def get_investor_profile(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return auth.investor_profile(user.id)

    @app.put(f"{COOKIE_PATH}/investor-profile", response_model=QuizResultOutput, tags=["auth"])
    def complete_investor_profile(data: QuizAnswersInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return auth.complete_quiz(user.id, data.answers)

    @app.get(COMPANY_PREFIX, response_model=list[PublicCompanyOutput], tags=["companies"])
    def search_companies(
        auth: Service,
        companies: CompanyServiceDependency,
        credentials: Credentials,
        query: str | None = Query(default=None, min_length=1, max_length=120),
        limit: int = Query(default=10, ge=1, le=20),
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return companies.search(query, limit)

    @app.get(
        f"{COMPANY_PREFIX}/{{company_id}}", response_model=PublicCompanyOutput, tags=["companies"]
    )
    def get_company(
        company_id: uuid.UUID,
        auth: Service,
        companies: CompanyServiceDependency,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return companies.company(company_id)

    @app.get(
        f"{COMPANY_PREFIX}/{{company_id}}/documents",
        response_model=list[OfficialDocumentOutput],
        tags=["companies"],
    )
    def list_official_documents(
        company_id: uuid.UUID,
        auth: Service,
        companies: CompanyServiceDependency,
        credentials: Credentials,
        document_type: str | None = Query(default=None, pattern="^(DFP|ITR|FRE|IPE)$"),
        starts_on: date | None = None,
        ends_on: date | None = None,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        if starts_on is not None and ends_on is not None and starts_on > ends_on:
            raise AuthError("invalid_document_date_range", 422)
        return companies.documents(company_id, document_type, starts_on, ends_on)

    @app.get(
        f"{COMPANY_PREFIX}/{{company_id}}/financial-indicators",
        response_model=list[FinancialIndicatorOutput],
        tags=["companies"],
    )
    def list_financial_indicators(
        company_id: uuid.UUID,
        auth: Service,
        companies: CompanyServiceDependency,
        credentials: Credentials,
        metric: str | None = Query(default=None, pattern="^(net_revenue|net_income|equity)$"),
        period_kind: str | None = Query(default=None, pattern="^(annual|quarterly)$"),
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return companies.financial_indicators(company_id, metric, period_kind)

    @app.post(
        f"{COMPANY_PREFIX}/documents/{{document_id}}/link-check",
        response_model=OfficialDocumentOutput,
        tags=["companies"],
    )
    def check_official_document_link(
        document_id: uuid.UUID,
        auth: Service,
        companies: CompanyServiceDependency,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return companies.check_link(document_id)

    @app.get(
        f"{MARKET_PREFIX}/quotes/{{ticker}}", response_model=MarketQuoteOutput, tags=["market"]
    )
    def get_market_quote(
        ticker: str,
        auth: Service,
        quotes: MarketQuoteServiceDependency,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return quotes.quote(ticker)

    @app.patch(PROFILE_PREFIX, response_model=ProfileOutput, tags=["auth"])
    def update_profile(data: ProfileUpdateInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        updated = auth.update_profile(
            user.id,
            data.name,
            str(data.email) if data.email is not None else None,
            data.current_password.get_secret_value() if data.current_password is not None else None,
        )
        return ProfileOutput(
            user=PublicUser.model_validate(updated[0]),
            pending_email=updated[1],
            preferences=PreferencesOutput.model_validate(updated[2]),
        )

    @app.get(
        f"{PROFILE_PREFIX}/advanced-metrics",
        response_model=AdvancedMetricsPreferenceOutput,
        tags=["auth"],
    )
    def advanced_metrics_preference(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return AdvancedMetricsPreferenceOutput.model_validate(
            auth.advanced_metrics_preference(user.id)
        )

    @app.put(
        f"{PROFILE_PREFIX}/advanced-metrics",
        response_model=AdvancedMetricsPreferenceOutput,
        tags=["auth"],
    )
    def set_advanced_metrics_preference(
        data: AdvancedMetricsPreferenceInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return AdvancedMetricsPreferenceOutput.model_validate(
            auth.set_advanced_metrics_preference(user.id, data.enabled)
        )

    @app.patch(f"{PROFILE_PREFIX}/preferences", response_model=PreferencesOutput, tags=["auth"])
    def update_preferences(data: PreferencesInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return PreferencesOutput.model_validate(auth.update_preferences(user.id, data.model_dump()))

    @app.get(CATEGORY_PREFIX, response_model=list[CategoryOutput], tags=["categories"])
    def list_categories(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [CategoryOutput.model_validate(item) for item in auth.list_categories(user.id)]

    @app.post(CATEGORY_PREFIX, response_model=CategoryOutput, status_code=201, tags=["categories"])
    def create_category(data: CategoryCreateInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return CategoryOutput.model_validate(auth.create_category(user.id, data.name, data.color))

    @app.patch(
        f"{CATEGORY_PREFIX}/standard/{{category_key}}",
        response_model=CategoryOutput,
        tags=["categories"],
    )
    def update_default_category_visibility(
        category_key: str,
        data: CategoryVisibilityInput,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return CategoryOutput.model_validate(
            auth.set_default_category_visibility(user.id, category_key, data.active)
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/sources",
        response_model=FinancialSourcesOutput,
        tags=["financial"],
    )
    def list_financial_sources(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return FinancialSourcesOutput.model_validate(auth.list_financial_sources(user.id))

    @app.post(
        f"{FINANCIAL_PREFIX}/accounts",
        response_model=AccountOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_account(data: AccountCreateInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return AccountOutput.model_validate(
            auth.create_account(user.id, data.name, data.account_type, data.initial_balance)
        )

    @app.post(
        f"{FINANCIAL_PREFIX}/credit-cards",
        response_model=CreditCardOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_credit_card(data: CreditCardCreateInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return CreditCardOutput.model_validate(
            auth.create_credit_card(
                user.id, data.name, data.credit_limit, data.closing_day, data.due_day
            )
        )

    @app.get(f"{FINANCIAL_PREFIX}/net-worth", response_model=NetWorthOutput, tags=["financial"])
    def get_net_worth(auth: Service, credentials: Credentials, as_of: date | None = None):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NetWorthOutput.model_validate(auth.net_worth(user.id, as_of))

    @app.post(
        f"{FINANCIAL_PREFIX}/stress/compare",
        response_model=StressCompareOutput,
        tags=["financial"],
    )
    def compare_financial_stress(data: StressCompareInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        from app.domain.financial_stress import StressScenario

        return StressCompareOutput.model_validate(
            auth.compare_financial_stress(
                user.id,
                data.minimum_reserve_months,
                StressScenario(**data.first.model_dump()),
                StressScenario(**data.second.model_dump()),
            )
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/investment-allocation",
        response_model=InvestmentAllocationOutput,
        tags=["financial"],
    )
    def get_investment_allocation(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return InvestmentAllocationOutput.model_validate(auth.investment_allocation(user.id))

    @app.put(
        f"{FINANCIAL_PREFIX}/investment-allocation/targets",
        response_model=InvestmentAllocationOutput,
        tags=["financial"],
    )
    def put_investment_targets(
        data: InvestmentTargetInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return InvestmentAllocationOutput.model_validate(
            auth.set_investment_targets(user.id, data.targets)
        )

    @app.put(
        f"{FINANCIAL_PREFIX}/investment-allocation/assets/{{asset_id}}",
        response_model=InvestmentAllocationOutput,
        tags=["financial"],
    )
    def put_investment_asset_class(
        asset_id: uuid.UUID,
        data: InvestmentClassInput,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return InvestmentAllocationOutput.model_validate(
            auth.classify_investment_asset(user.id, asset_id, data.asset_class)
        )

    @app.delete(
        f"{FINANCIAL_PREFIX}/investment-allocation/assets/{{asset_id}}",
        response_model=InvestmentAllocationOutput,
        tags=["financial"],
    )
    def delete_investment_asset_class(asset_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return InvestmentAllocationOutput.model_validate(
            auth.unclassify_investment_asset(user.id, asset_id)
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/net-worth/heatmap",
        response_model=NetWorthHeatmapOutput,
        tags=["financial"],
    )
    def get_net_worth_heatmap(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NetWorthHeatmapOutput.model_validate(auth.net_worth_heatmap(user.id))

    @app.get(
        f"{FINANCIAL_PREFIX}/net-worth/history",
        response_model=list[NetWorthSnapshotOutput],
        tags=["financial"],
    )
    def get_net_worth_history(
        auth: Service, credentials: Credentials, start: date | None = None, end: date | None = None
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        history = auth.net_worth_history(user.id, start, end)
        return [NetWorthSnapshotOutput.model_validate(item) for item in history]

    @app.post(
        f"{FINANCIAL_PREFIX}/net-worth/history/snapshots",
        response_model=NetWorthSnapshotOutput,
        status_code=201,
        tags=["financial"],
    )
    def capture_net_worth_snapshot(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NetWorthSnapshotOutput.model_validate(auth.capture_net_worth_snapshot(user.id))

    @app.get(
        "/api/v1/education/articles",
        response_model=list[EducationalArticleOutput],
        tags=["education"],
    )
    def education_articles(
        auth: Service,
        credentials: Credentials,
        q: str = Query(default="", max_length=100),
        lang: str = Query(default="pt", pattern="^(pt|en)$"),
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            EducationalArticleOutput.model_validate(article)
            for article in search_articles(q, lang, user.investor_profile)
        ]

    @app.get(
        "/api/v1/education/articles/{article_key}",
        response_model=EducationalArticleOutput,
        tags=["education"],
    )
    def education_article(
        article_key: str,
        auth: Service,
        credentials: Credentials,
        lang: str = Query(default="pt", pattern="^(pt|en)$"),
    ):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        article = get_article(article_key, lang)
        if article is None:
            raise AuthError("educational_article_not_found", 404)
        return EducationalArticleOutput.model_validate(article)

    @app.get(
        f"{FINANCIAL_PREFIX}/health-score", response_model=HealthScoreOutput, tags=["financial"]
    )
    def get_health_score(auth: Service, credentials: Credentials, competence: date | None = None):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return HealthScoreOutput.model_validate(auth.health_score(user.id, competence))

    @app.get(
        f"{FINANCIAL_PREFIX}/named-asset-goals",
        response_model=list[NamedAssetGoalOutput],
        tags=["financial"],
    )
    def list_named_asset_goals(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            NamedAssetGoalOutput.model_validate(item)
            for item in auth.list_named_asset_goals(user.id)
        ]

    @app.post(
        f"{FINANCIAL_PREFIX}/named-asset-goals",
        response_model=NamedAssetGoalOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_named_asset_goal(data: NamedAssetGoalInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NamedAssetGoalOutput.model_validate(
            auth.create_named_asset_goal(user.id, data.model_dump())
        )

    @app.delete(
        f"{FINANCIAL_PREFIX}/named-asset-goals/{{goal_id}}",
        status_code=204,
        tags=["financial"],
    )
    def delete_named_asset_goal(goal_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_named_asset_goal(user.id, goal_id)
        return Response(status_code=204)

    @app.post(
        f"{FINANCIAL_PREFIX}/net-worth/items",
        response_model=NetWorthItemOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_net_worth_item(data: NetWorthItemInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NetWorthItemOutput.model_validate(
            auth.create_net_worth_item(user.id, **data.model_dump())
        )

    @app.patch(
        f"{FINANCIAL_PREFIX}/net-worth/items/{{item_id}}",
        response_model=NetWorthItemOutput,
        tags=["financial"],
    )
    def update_net_worth_item(
        item_id: uuid.UUID, data: NetWorthItemUpdateInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NetWorthItemOutput.model_validate(
            auth.update_net_worth_item(user.id, item_id, data.model_dump(exclude_unset=True))
        )

    @app.delete(
        f"{FINANCIAL_PREFIX}/net-worth/items/{{item_id}}", status_code=204, tags=["financial"]
    )
    def delete_net_worth_item(item_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_net_worth_item(user.id, item_id)
        return Response(status_code=204)

    def with_rate_source(data, auth: AuthService):
        """Resolve a origem da taxa: indicador oficial em cache ou valor manual informado."""
        if data.indicator_code is None:
            return data, {"origin": "manual"}
        indicator = auth.indicator(data.indicator_code)  # 503 se ausente: nunca zero (C-08)
        source = {
            "origin": data.indicator_code,
            "value": str(indicator["value"]),
            "reference_date": indicator["reference_date"].isoformat(),
            "stale": indicator["stale"],
            "notice": "Último valor disponível; a fonte oficial não foi atualizada no prazo."
            if indicator["stale"]
            else None,
        }
        return (
            data.model_copy(update={"annual_rate": indicator["value"], "rate_period": "annual"}),
            source,
        )

    def calculator_result(
        data: CalculatorInput,
        investor_profile: str | None = None,
        rate_source: dict[str, object] | None = None,
    ) -> CalculatorOutput:
        result = MotorJurosCompostos.calcular(
            valor_inicial=data.initial_amount,
            aporte_mensal=data.monthly_contribution,
            taxa_percentual=data.annual_rate,
            periodicidade_taxa="mensal" if data.rate_period == "monthly" else "anual",
            prazo=data.term_months,
            unidade_prazo="anos" if data.term_unit == "years" else "meses",
        )
        return CalculatorOutput(
            invested=arredondar_moeda(result.total_investido),
            interest=arredondar_moeda(result.total_juros),
            gross_amount=arredondar_moeda(result.montante),
            monthly_series=[
                {
                    "month": row.mes,
                    "opening_balance": arredondar_moeda(row.saldo_inicial),
                    "contribution": arredondar_moeda(row.aporte),
                    "interest": arredondar_moeda(row.juros),
                    "closing_balance": arredondar_moeda(row.saldo_final),
                }
                for row in result.serie
            ],
            rate_explanation=(
                "A taxa anual é convertida para a taxa mensal equivalente por juros compostos; "
                "os aportes entram ao fim de cada mês."
                if data.rate_period == "annual"
                else "A taxa informada já é mensal e é aplicada diretamente a cada mês; "
                "os aportes entram ao fim de cada mês."
            ),
            investor_guidance=PROFILE_GUIDANCE.get(investor_profile),
            rate_source=rate_source,
        )

    # SPEC-041: only the owner uses the ordinary access session to grant/revoke.
    # Consumers must use a different credential on separate read-only routes.
    @app.get(
        "/api/v1/external/grants",
        response_model=list[ExternalApiGrantOutput],
        tags=["external-integrations"],
    )
    def external_grants(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return ExternalApiService(auth.db, security, auth).list_grants(user.id)

    @app.post(
        "/api/v1/external/grants",
        response_model=ExternalApiGrantCreated,
        status_code=201,
        tags=["external-integrations"],
    )
    def create_external_grant(data: ExternalApiGrantInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return ExternalApiService(auth.db, security, auth).create_grant(
            user.id, data.name, data.scopes
        )

    @app.delete(
        "/api/v1/external/grants/{grant_id}",
        status_code=204,
        tags=["external-integrations"],
    )
    def revoke_external_grant(grant_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        ExternalApiService(auth.db, security, auth).revoke_grant(user.id, grant_id)

    @app.get(
        "/api/v1/external/balance",
        response_model=ExternalBalanceOutput,
        tags=["external-integrations"],
    )
    def external_read_balance(
        competence: str,
        auth: Service,
        api_key: str | None = Header(default=None, alias="X-FinNova-API-Key"),
    ):
        # A user JWT alone never authenticates a third-party consumer.
        owner_id = ExternalApiService(auth.db, security, auth).consume(api_key, "balance:read")
        try:
            selected = date.fromisoformat(f"{competence}-01")
            if selected.strftime("%Y-%m") != competence:
                raise ValueError("Invalid competence")
        except ValueError as exc:
            raise AuthError("invalid_competence", 400) from exc
        summary = auth.balance_summary(owner_id, selected)
        return ExternalBalanceOutput(
            competence=competence,
            income=summary["total"],
            expenses=summary["expenses"],
            balance_variation=summary["balance_variation"],
        )

    @app.get(
        "/api/v1/external/net-worth",
        response_model=ExternalNetWorthOutput,
        tags=["external-integrations"],
    )
    def external_read_net_worth(
        auth: Service,
        api_key: str | None = Header(default=None, alias="X-FinNova-API-Key"),
    ):
        owner_id = ExternalApiService(auth.db, security, auth).consume(api_key, "net_worth:read")
        data = auth.net_worth(owner_id)
        # Explicit allowlist: names, IDs and individual balances are not exported.
        return ExternalNetWorthOutput(
            as_of=data["as_of"],
            total_assets=data["total_assets"],
            total_liabilities=data["total_liabilities"],
            net_worth=data["net_worth"],
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/financing/confirmed",
        response_model=list[ConfirmedFinancingOutput],
        tags=["financial"],
    )
    def list_confirmed_financings(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            ConfirmedFinancingOutput.model_validate(item)
            for item in auth.list_confirmed_financings(user.id)
        ]

    @app.post(
        f"{FINANCIAL_PREFIX}/financing/confirm",
        response_model=ConfirmedFinancingOutput,
        status_code=201,
        tags=["financial"],
    )
    def confirm_real_financing(
        data: ConfirmFinancingInput, request: Request, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return ConfirmedFinancingOutput.model_validate(
            auth.confirm_real_financing(user.id, data.model_dump(), idempotency_key(request))
        )

    @app.post(
        f"{FINANCIAL_PREFIX}/financing/compare",
        response_model=FinancingComparisonOutput,
        tags=["financial"],
    )
    def financing_comparison_route(
        data: FinancingComparisonInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        from dataclasses import asdict

        result = compare_financing_and_investing(**data.model_dump())
        return FinancingComparisonOutput.model_validate(asdict(result))

    @app.post(
        f"{FINANCIAL_PREFIX}/financing/simulate",
        response_model=FinancingOutput,
        tags=["financial"],
    )
    def simulate_financing_route(data: FinancingInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        plan = simulate_financing(
            data.asset_value, data.down_payment, data.installments, data.annual_rate
        )
        from dataclasses import asdict

        return FinancingOutput.model_validate(asdict(plan))

    @app.post(f"{FINANCIAL_PREFIX}/calculator", response_model=CalculatorOutput, tags=["financial"])
    def calculator(data: CalculatorInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        data, source = with_rate_source(data, auth)
        return calculator_result(data, user.investor_profile, source)

    @app.post(
        f"{FINANCIAL_PREFIX}/fixed-income-projections",
        response_model=TaxProjectionOutput,
        tags=["financial"],
    )
    def fixed_income_projection(data: TaxProjectionInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        data, source = with_rate_source(data, auth)
        calculation = calculator_result(data, user.investor_profile, source)
        tax, net = resultado_liquido(
            calculation.gross_amount, calculation.invested, data.months, data.product
        )
        return TaxProjectionOutput(
            **calculation.model_dump(),
            tax_rate=aliquota_ir_renda_fixa(data.months, data.product),
            estimated_tax=arredondar_moeda(tax),
            net_amount=arredondar_moeda(net),
        )

    @app.post(
        f"{FINANCIAL_PREFIX}/simulations/fixed-income",
        response_model=SimulationOutput,
        status_code=201,
        tags=["financial"],
    )
    def save_fixed_income_simulation(
        data: SimulationCreateInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        data, source = with_rate_source(data, auth)
        calculation = calculator_result(data, user.investor_profile, source)
        tax, net = resultado_liquido(
            calculation.gross_amount, calculation.invested, data.months, data.product
        )
        return SimulationOutput.model_validate(
            auth.save_simulation(
                user.id,
                "fixed_income",
                data.label,
                {
                    "product": data.product,
                    "initial_amount": str(data.initial_amount),
                    "monthly_contribution": str(data.monthly_contribution),
                    "annual_rate": str(data.annual_rate),
                    "term_months": data.months,
                    "gross_amount": str(calculation.gross_amount),
                    "estimated_tax": str(tax),
                    "net_amount": str(net),
                    "tax_rate": str(aliquota_ir_renda_fixa(data.months, data.product)),
                    "rate_source": source,
                },
                net,
            )
        )

    @app.get(
        f"{MARKET_PREFIX}/quotes/{{ticker}}/metrics",
        response_model=RiskMetricsOutput,
        tags=["market"],
    )
    def market_risk_metrics(
        ticker: str,
        auth: Service,
        quotes: MarketQuoteServiceDependency,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        if not auth.advanced_metrics_preference(user.id)["enabled"]:
            raise AuthError("advanced_metrics_disabled", 403)
        selic = auth.indicator("selic")
        return RiskMetricsOutput.model_validate(quotes.metrics(ticker, selic["value"]))

    @app.post(
        f"{FINANCIAL_PREFIX}/simulations/foreign-currency",
        response_model=SimulationOutput,
        status_code=201,
        tags=["financial"],
    )
    def save_foreign_currency_simulation(
        data: ForeignCurrencySimulationInput,
        auth: Service,
        exchange_rates: ExchangeRateServiceDependency,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        rate = exchange_rates.rate(data.currency)
        calculation = calcular_projecao_moeda_estrangeira(
            initial_amount=data.initial_amount,
            monthly_contribution=data.monthly_contribution,
            asset_annual_return=data.asset_annual_return,
            expected_exchange_annual_change=data.expected_exchange_annual_change,
            term_months=data.term_months,
            exchange_rate_to_brl=rate["exchange_rate_to_brl"],
        )
        foreign_currency = ForeignCurrencySimulationOutput.model_validate(
            {
                "currency": data.currency,
                "initial_amount": data.initial_amount,
                **rate,
                **calculation,
                "risk_notice": (
                    "A variação cambial é uma fonte de risco e retorno distinta da rentabilidade "
                    "do ativo; esta é uma estimativa educacional, sem garantia."
                ),
            }
        )
        return SimulationOutput.model_validate(
            auth.save_simulation(
                user.id,
                "foreign_currency",
                data.label,
                {
                    "foreign_currency": foreign_currency.model_dump(mode="json"),
                    "disclaimer": (
                        "Simulação educacional: não compra moeda, não movimenta patrimônio "
                        "e não garante retorno."
                    ),
                },
                foreign_currency.final_amount_brl,
            )
        )

    @app.post(
        f"{FINANCIAL_PREFIX}/simulations/variable-income",
        response_model=SimulationOutput,
        status_code=201,
        tags=["financial"],
    )
    def save_variable_income_simulation(
        data: VariableIncomeSimulationInput,
        auth: Service,
        quotes: MarketQuoteServiceDependency,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        result = projetar(
            inicial=data.initial_amount,
            aporte=data.monthly_contribution,
            taxa=data.expected_annual_return,
            prazo=data.term_months,
        )
        quote_snapshot = None
        if data.ticker:
            # SPEC-009-R04: preço atual e histórico pré-preenchidos quando há referência válida.
            try:
                found = quotes.quote(data.ticker)
                quote_snapshot = {
                    "price": str(found["price"]),
                    "referenced_at": found["referenced_at"].isoformat(),
                    "source_name": found["source_name"],
                    "history": [
                        {
                            "quoted_on": row["quoted_on"].isoformat(),
                            "close": str(row["close_price"]),
                        }
                        for row in found["history"]
                    ],
                }
            except AuthError:
                quote_snapshot = None
        risk_metrics = None
        if data.ticker and auth.advanced_metrics_preference(user.id)["enabled"]:
            risk_metrics = RiskMetricsOutput.model_validate(
                quotes.metrics(data.ticker, auth.indicator("selic")["value"])
            ).model_dump(mode="json")
        return SimulationOutput.model_validate(
            auth.save_simulation(
                user.id,
                "variable_income",
                data.label,
                {
                    "initial_amount": str(data.initial_amount),
                    "monthly_contribution": str(data.monthly_contribution),
                    "expected_annual_return": str(data.expected_annual_return),
                    "term_months": data.term_months,
                    "ticker": data.ticker.upper() if data.ticker else None,
                    "risk_metrics": risk_metrics,
                    "quote": quote_snapshot,
                    # SPEC-009-R06: evolução estimada mês a mês (saldo ao fim de cada mês).
                    "monthly_series": [
                        {
                            "month": row.mes,
                            "closing_balance": str(arredondar_moeda(row.saldo_final)),
                        }
                        for row in result.serie
                    ],
                    "disclaimer": (
                        "Projeção educacional com retorno informado manualmente; "
                        "não é cotação nem garantia."
                    ),
                },
                arredondar_moeda(result.montante),
            )
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/simulations", response_model=list[SimulationOutput], tags=["financial"]
    )
    def list_simulations(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [SimulationOutput.model_validate(item) for item in auth.list_simulations(user.id)]

    @app.post(
        f"{FINANCIAL_PREFIX}/simulations/compare",
        response_model=SimulationComparisonOutput,
        tags=["financial"],
    )
    def compare_simulations(
        data: SimulationComparisonInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return SimulationComparisonOutput.model_validate(
            auth.compare_simulations(user.id, data.simulation_ids)
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/indicators/{{code}}",
        response_model=IndicatorOutput,
        tags=["financial"],
    )
    def indicator(code: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        return IndicatorOutput.model_validate(auth.indicator(code))

    @app.post(
        f"{FINANCIAL_PREFIX}/target-contributions",
        response_model=TargetContributionOutput,
        tags=["financial"],
    )
    def target_contribution(data: TargetContributionInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        needed = aporte_necessario(
            alvo=data.target_amount,
            inicial=data.initial_amount,
            taxa_percentual=data.annual_rate,
            prazo_meses=data.term_months,
        )
        feasible = data.available_monthly_amount is None or needed <= data.available_monthly_amount
        return TargetContributionOutput(
            monthly_contribution_needed=arredondar_moeda(needed),
            feasible=feasible,
            warning=None
            if feasible
            else "O aporte necessário supera a disponibilidade mensal informada.",
        )

    @app.get(NOTIFICATION_PREFIX, response_model=list[NotificationOutput], tags=["notifications"])
    def list_notifications(unread_only: bool = False, *, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            NotificationOutput.model_validate(item)
            for item in auth.list_notifications(user.id, unread_only)
        ]

    @app.get(
        f"{NOTIFICATION_PREFIX}/preferences",
        response_model=list[NotificationPreferenceOutput],
        tags=["notifications"],
    )
    def list_notification_preferences(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            NotificationPreferenceOutput.model_validate(item)
            for item in auth.notification_preferences(user.id)
        ]

    @app.put(
        f"{NOTIFICATION_PREFIX}/preferences/{{kind}}",
        response_model=NotificationPreferenceOutput,
        tags=["notifications"],
    )
    def update_notification_preference(
        kind: str, data: NotificationPreferenceInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NotificationPreferenceOutput.model_validate(
            auth.update_notification_preference(user.id, kind, data.enabled)
        )

    @app.post(
        "/api/v1/companies/{company_id}/watchlist",
        response_model=WatchlistMutationOutput,
        tags=["companies"],
    )
    def add_watchlist(company_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        created, item = auth.add_watchlist(user.id, company_id)
        return WatchlistMutationOutput(created=created, item=WatchlistOutput.model_validate(item))

    @app.get(
        "/api/v1/companies/watchlist", response_model=list[WatchlistOutput], tags=["companies"]
    )
    def list_watchlist(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [WatchlistOutput.model_validate(item) for item in auth.list_watchlist(user.id)]

    @app.delete("/api/v1/companies/{company_id}/watchlist", status_code=204, tags=["companies"])
    def remove_watchlist(company_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.remove_watchlist(user.id, company_id)

    @app.post(
        "/api/v1/companies/documents/{document_id}/watchlist-notifications", tags=["companies"]
    )
    def notify_watchlist_document(document_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        auth.authenticate(credentials.credentials)
        return {"created": auth.notify_watchlist_document(document_id)}

    @app.post(
        f"{NOTIFICATION_PREFIX}/events",
        response_model=NotificationEventOutput,
        tags=["notifications"],
    )
    def receive_notification_event(
        data: NotificationEventInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        created, notification = auth.create_notification(user.id, data.kind, data.source_key)
        if created:
            WebhookService(
                auth.db, security, auth, app.state.webhook_delivery
            ).dispatch_notification(user.id, notification)
        return NotificationEventOutput(
            created=created,
            notification=NotificationOutput.model_validate(notification) if notification else None,
        )

    @app.patch(
        f"{NOTIFICATION_PREFIX}/{{notification_id}}/read",
        response_model=NotificationOutput,
        tags=["notifications"],
    )
    def mark_notification_read(notification_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return NotificationOutput.model_validate(
            auth.mark_notification_read(user.id, notification_id)
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/credit-cards/{{card_id}}/invoice",
        response_model=CardInvoiceOutput,
        tags=["financial"],
    )
    def card_invoice(card_id: uuid.UUID, competence: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        try:
            selected = date.fromisoformat(f"{competence}-01")
        except ValueError as exc:
            raise AuthError("invalid_competence", 400) from exc
        user, _ = auth.authenticate(credentials.credentials)
        return CardInvoiceOutput.model_validate(auth.card_invoice(user.id, card_id, selected))

    @app.put(
        f"{FINANCIAL_PREFIX}/budget-goals", response_model=BudgetProgressOutput, tags=["financial"]
    )
    def upsert_budget_goal(data: BudgetGoalInput, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        goal = auth.upsert_budget_goal(user.id, data.model_dump())
        return BudgetProgressOutput.model_validate(
            {**goal, "actual": Decimal("0"), "percentage": Decimal("0"), "status": "on_track"}
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/budget-progress",
        response_model=list[BudgetProgressOutput],
        tags=["financial"],
    )
    def budget_progress(competence: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        try:
            selected = date.fromisoformat(f"{competence}-01")
        except ValueError as exc:
            raise AuthError("invalid_competence", 400) from exc
        user, _ = auth.authenticate(credentials.credentials)
        return [
            BudgetProgressOutput.model_validate(item)
            for item in auth.budget_progress(user.id, selected)
        ]

    @app.get(
        f"{FINANCIAL_PREFIX}/spending-by-category",
        response_model=list[CategorySpendingOutput],
        tags=["financial"],
    )
    def spending_by_category(start: str, end: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        try:
            start_month = date.fromisoformat(f"{start}-01")
            end_month = date.fromisoformat(f"{end}-01")
        except ValueError as exc:
            raise AuthError("invalid_period", 400) from exc
        return auth.spending_by_category(user.id, start_month, end_month)

    @app.get(
        f"{FINANCIAL_PREFIX}/dashboard",
        response_model=list[DashboardMonthOutput],
        tags=["financial"],
    )
    def dashboard(start: str, end: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        try:
            start_month = date.fromisoformat(f"{start}-01")
            end_month = date.fromisoformat(f"{end}-01")
        except ValueError as exc:
            raise AuthError("invalid_period", 400) from exc
        user, _ = auth.authenticate(credentials.credentials)
        return [
            DashboardMonthOutput.model_validate(item)
            for item in auth.dashboard(user.id, start_month, end_month)
        ]

    @app.get(
        f"{FINANCIAL_PREFIX}/recurring-incomes",
        response_model=list[RecurringIncomeOutput],
        tags=["financial"],
    )
    def list_recurring_incomes(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            RecurringIncomeOutput.model_validate(item)
            for item in auth.list_recurring_incomes(user.id)
        ]

    @app.post(
        f"{FINANCIAL_PREFIX}/recurring-incomes",
        response_model=RecurringIncomeOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_recurring_income(
        data: RecurringIncomeCreateInput,
        request: Request,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        idempotency_key = request.headers.get("Idempotency-Key")
        if idempotency_key is None or not 1 <= len(idempotency_key) <= 128:
            raise AuthError("idempotency_key_required", 400)
        user, _ = auth.authenticate(credentials.credentials)
        return RecurringIncomeOutput.model_validate(
            auth.create_recurring_income(
                user.id,
                data.description,
                data.amount,
                data.account_id,
                data.starts_on or date.today(),
                idempotency_key,
            )
        )

    @app.patch(
        f"{FINANCIAL_PREFIX}/recurring-incomes/{{income_id}}",
        response_model=RecurringIncomeOutput,
        tags=["financial"],
    )
    def update_recurring_income(
        income_id: uuid.UUID,
        data: RecurringIncomeUpdateInput,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return RecurringIncomeOutput.model_validate(
            auth.update_recurring_income(user.id, income_id, data.model_dump())
        )

    @app.delete(
        f"{FINANCIAL_PREFIX}/recurring-incomes/{{income_id}}", status_code=204, tags=["financial"]
    )
    def delete_recurring_income(income_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_recurring_income(user.id, income_id)

    def idempotency_key(request: Request) -> str:
        key = request.headers.get("Idempotency-Key")
        if key is None or not 1 <= len(key) <= 128:
            raise AuthError("idempotency_key_required", 400)
        return key

    @app.get(
        f"{FINANCIAL_PREFIX}/one-time-incomes",
        response_model=list[OneTimeIncomeOutput],
        tags=["financial"],
    )
    def list_one_time_incomes(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [
            OneTimeIncomeOutput.model_validate(item) for item in auth.list_one_time_incomes(user.id)
        ]

    @app.post(
        f"{FINANCIAL_PREFIX}/one-time-incomes",
        response_model=OneTimeIncomeOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_one_time_income(
        data: OneTimeIncomeCreateInput,
        request: Request,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return OneTimeIncomeOutput.model_validate(
            auth.create_one_time_income(
                user.id,
                data.description,
                data.amount,
                data.account_id,
                data.occurred_on,
                idempotency_key(request),
            )
        )

    @app.patch(
        f"{FINANCIAL_PREFIX}/one-time-incomes/{{income_id}}",
        response_model=OneTimeIncomeOutput,
        tags=["financial"],
    )
    def update_one_time_income(
        income_id: uuid.UUID,
        data: OneTimeIncomeUpdateInput,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return OneTimeIncomeOutput.model_validate(
            auth.update_one_time_income(user.id, income_id, data.model_dump())
        )

    @app.delete(
        f"{FINANCIAL_PREFIX}/one-time-incomes/{{income_id}}", status_code=204, tags=["financial"]
    )
    def delete_one_time_income(income_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_one_time_income(user.id, income_id)

    @app.get(f"{FINANCIAL_PREFIX}/bonuses", response_model=list[BonusOutput], tags=["financial"])
    def list_bonuses(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [BonusOutput.model_validate(item) for item in auth.list_bonuses(user.id)]

    @app.post(
        f"{FINANCIAL_PREFIX}/bonuses",
        response_model=BonusOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_bonus(
        data: BonusCreateInput,
        request: Request,
        auth: Service,
        credentials: Credentials,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return BonusOutput.model_validate(
            auth.create_bonus(
                user.id,
                data.description,
                data.amount,
                data.periodicity,
                data.starts_on or date.today(),
                data.reference_month,
                idempotency_key(request),
            )
        )

    @app.patch(
        f"{FINANCIAL_PREFIX}/bonuses/{{bonus_id}}", response_model=BonusOutput, tags=["financial"]
    )
    def update_bonus(
        bonus_id: uuid.UUID, data: BonusUpdateInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return BonusOutput.model_validate(auth.update_bonus(user.id, bonus_id, data.model_dump()))

    @app.delete(f"{FINANCIAL_PREFIX}/bonuses/{{bonus_id}}", status_code=204, tags=["financial"])
    def delete_bonus(bonus_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_bonus(user.id, bonus_id)

    @app.get(
        f"{FINANCIAL_PREFIX}/income-summary",
        response_model=IncomeSummaryOutput,
        tags=["financial"],
    )
    def income_summary(competence: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        try:
            selected = date.fromisoformat(f"{competence}-01")
        except ValueError as exc:
            raise AuthError("invalid_competence", 400) from exc
        user, _ = auth.authenticate(credentials.credentials)
        return IncomeSummaryOutput.model_validate(auth.income_summary(user.id, selected))

    @app.get(
        f"{FINANCIAL_PREFIX}/balance-summary",
        response_model=BalanceSummaryOutput,
        tags=["financial"],
    )
    def balance_summary(competence: str, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        try:
            selected = date.fromisoformat(f"{competence}-01")
        except ValueError as exc:
            raise AuthError("invalid_competence", 400) from exc
        user, _ = auth.authenticate(credentials.credentials)
        return BalanceSummaryOutput.model_validate(auth.balance_summary(user.id, selected))

    @app.get(f"{FINANCIAL_PREFIX}/expenses", response_model=list[ExpenseOutput], tags=["financial"])
    def list_expenses(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return [ExpenseOutput.model_validate(item) for item in auth.list_expenses(user.id)]

    def export_period(start: str | None, end: str | None, month: str | None, year: int | None):
        if month is not None:
            try:
                start_date = date.fromisoformat(f"{month}-01")
            except ValueError as exc:
                raise AuthError("invalid_period", 400) from exc
            return start_date, (start_date.replace(day=28) + timedelta(days=4)).replace(
                day=1
            ) - timedelta(days=1)
        if year is not None:
            return date(year, 1, 1), date(year, 12, 31)
        if start is None or end is None:
            raise AuthError("invalid_period", 400)
        try:
            start_date, end_date = date.fromisoformat(start), date.fromisoformat(end)
        except ValueError as exc:
            raise AuthError("invalid_period", 400) from exc
        if start_date > end_date:
            raise AuthError("invalid_period", 400)
        return start_date, end_date

    def csv_cell(value: object) -> str:
        rendered = str(value)
        return "'" + rendered if rendered.lstrip().startswith(("=", "+", "-", "@")) else rendered

    # ---------- SPEC-046 a SPEC-049 ----------
    def owner_id(auth: AuthService, credentials) -> uuid.UUID:
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return user.id

    @app.post(
        f"{FINANCIAL_PREFIX}/retirement-projections",
        response_model=RetirementOutput,
        tags=["planning"],
    )
    def retirement_projection(data: RetirementInput, auth: Service, credentials: Credentials):
        """SPEC-046: patrimônio na idade-alvo e renda mensal estimada (projeção educativa)."""
        return PlanningTaxService(auth.db, auth).retirement(owner_id(auth, credentials), data)

    @app.post(
        f"{FINANCIAL_PREFIX}/pension-comparisons", response_model=PensionOutput, tags=["planning"]
    )
    def pension_comparison(data: PensionInput, auth: Service, credentials: Credentials):
        """SPEC-047: PGBL, VGBL e carteira própria com os mesmos parâmetros."""
        return PlanningTaxService(auth.db, auth).pension(owner_id(auth, credentials), data)

    @app.post(
        f"{FINANCIAL_PREFIX}/tax-estimates",
        response_model=TaxEstimateOutput,
        status_code=201,
        tags=["taxes"],
    )
    def create_tax_estimate(data: TaxEstimateInput, auth: Service, credentials: Credentials):
        """SPEC-048: IR estimado por regime e data-limite do DARF (sem gerar DARF)."""
        return PlanningTaxService(auth.db, auth).create_tax_estimate(
            owner_id(auth, credentials), data
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/tax-estimates",
        response_model=list[TaxEstimateOutput],
        tags=["taxes"],
    )
    def list_tax_estimates(auth: Service, credentials: Credentials):
        return PlanningTaxService(auth.db, auth).list_tax_estimates(owner_id(auth, credentials))

    @app.delete(
        f"{FINANCIAL_PREFIX}/tax-estimates/{{estimate_id}}", status_code=204, tags=["taxes"]
    )
    def delete_tax_estimate(estimate_id: uuid.UUID, auth: Service, credentials: Credentials):
        PlanningTaxService(auth.db, auth).delete_tax_estimate(
            owner_id(auth, credentials), estimate_id
        )
        return Response(status_code=204)

    def annual_summary_data(auth: AuthService, credentials, year: int) -> dict[str, object]:
        if not 2000 <= year <= 2100:
            raise AuthError("invalid_year", 422)
        return PlanningTaxService(auth.db, auth).annual_summary(owner_id(auth, credentials), year)

    @app.get(
        f"{FINANCIAL_PREFIX}/annual-summary", response_model=AnnualSummaryOutput, tags=["taxes"]
    )
    def annual_summary(year: int, auth: Service, credentials: Credentials):
        """SPEC-049: resumo anual auxiliar (não é informe oficial)."""
        return annual_summary_data(auth, credentials, year)

    def annual_lines(data: dict[str, object]) -> list[list[str]]:
        income = data["registered_income"]
        rows = [["seção", "item", "origem", "valor"]]
        rows += [
            ["rendimentos registrados", key, "registrado", str(income[key])]
            for key in ("recurring_income", "one_time_income", "bonus", "total")
        ]
        rows += [
            [
                "IR estimado",
                f"{item['regime']} {item['competence']}",
                "registrado",
                str(item["tax"]),
            ]
            for item in data["tax_estimates"]
        ]
        rows += [
            ["simulações", csv_cell(item["label"]), "simulado", str(item["final_amount"])]
            for item in data["simulations"]
        ]
        return rows

    @app.get(f"{FINANCIAL_PREFIX}/annual-summary/csv", tags=["taxes"])
    def annual_summary_csv(year: int, auth: Service, credentials: Credentials):
        data = annual_summary_data(auth, credentials, year)
        buffer = StringIO()
        output = writer(buffer)
        output.writerow([f"# {data['notice']}"])
        output.writerows(annual_lines(data))
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=resumo-anual-{year}.csv"},
        )

    @app.get(f"{FINANCIAL_PREFIX}/annual-summary/pdf", tags=["taxes"])
    def annual_summary_pdf(year: int, auth: Service, credentials: Credentials):
        data = annual_summary_data(auth, credentials, year)
        lines = [f"FinNova - Resumo anual auxiliar {year}", str(data["notice"]), ""]
        lines += [" | ".join(row) for row in annual_lines(data)[1:]]
        lines += ["", f"IR estimado total: {data['estimated_tax_total']}"]
        return Response(
            content=pdf_document(lines),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resumo-anual-{year}.pdf"},
        )

    # ---------- SPEC-050/051/052 ----------
    @app.get(f"{PROFILE_PREFIX}/privacy", response_model=PrivacySettingsOutput, tags=["profile"])
    def get_privacy(auth: Service, credentials: Credentials):
        return EngagementFeaturesService(auth.db, auth).privacy(owner_id(auth, credentials))

    @app.put(f"{PROFILE_PREFIX}/privacy", response_model=PrivacySettingsOutput, tags=["profile"])
    def put_privacy(data: PrivacySettingsInput, auth: Service, credentials: Credentials):
        """SPEC-050: desativar a comparação não remove o acesso ao score (R05)."""
        return EngagementFeaturesService(auth.db, auth).set_privacy(
            owner_id(auth, credentials), data.score_benchmark_enabled
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/health-score/benchmark",
        response_model=ScoreBenchmarkOutput,
        tags=["financial"],
    )
    def score_benchmark(auth: Service, credentials: Credentials, competence: date | None = None):
        """SPEC-050: média/mediana agregadas do grupo do mesmo perfil (mínimo de 30)."""
        return EngagementFeaturesService(auth.db, auth).benchmark(
            owner_id(auth, credentials), competence
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/achievements",
        response_model=list[AchievementOutput],
        tags=["financial"],
    )
    def achievements(auth: Service, credentials: Credentials):
        """SPEC-051: conquistas cosméticas obtidas e progresso das próximas."""
        return EngagementFeaturesService(auth.db, auth).achievements(owner_id(auth, credentials))

    @app.get(f"{PROFILE_PREFIX}/tour", response_model=TourOutput, tags=["profile"])
    def get_tour(auth: Service, credentials: Credentials):
        """SPEC-052: estado do tour de primeiro acesso e roteiro adaptado ao perfil."""
        return EngagementFeaturesService(auth.db, auth).tour(owner_id(auth, credentials))

    @app.put(f"{PROFILE_PREFIX}/tour", response_model=TourOutput, tags=["profile"])
    def put_tour(data: TourActionInput, auth: Service, credentials: Credentials):
        return EngagementFeaturesService(auth.db, auth).update_tour(
            owner_id(auth, credentials), data.action, data.step
        )

    # ---------- SPEC-061: canais externos opcionais ----------
    @app.post(f"{NOTIFICATION_PREFIX}/push-devices", status_code=201, tags=["notifications"])
    def register_push_device(data: PushDeviceInput, auth: Service, credentials: Credentials):
        user_id = owner_id(auth, credentials)
        auth.require_category_owner(user_id)
        lookup = security.lookup(data.token)
        exists = auth.db.scalar(
            select(PushDeviceRecord.id).where(
                PushDeviceRecord.user_id == user_id, PushDeviceRecord.token_lookup == lookup
            )
        )
        if exists is None:
            auth.db.add(
                PushDeviceRecord(
                    user_id=user_id,
                    token_encrypted=security.encrypt(data.token),
                    token_lookup=lookup,
                    created_at=auth.clock(),
                )
            )
            auth.db.commit()
        return {"registered": True}

    @app.delete(f"{NOTIFICATION_PREFIX}/push-devices", status_code=204, tags=["notifications"])
    def remove_push_devices(auth: Service, credentials: Credentials):
        user_id = owner_id(auth, credentials)
        for device in auth.db.scalars(
            select(PushDeviceRecord).where(PushDeviceRecord.user_id == user_id)
        ):
            auth.db.delete(device)
        auth.db.commit()
        return Response(status_code=204)

    @app.get(
        f"{NOTIFICATION_PREFIX}/deliveries",
        response_model=list[DeliveryOutput],
        tags=["notifications"],
    )
    def list_deliveries(auth: Service, credentials: Credentials):
        """Resultado mínimo das tentativas externas do próprio titular (sem conteúdo)."""
        user_id = owner_id(auth, credentials)
        return list(
            auth.db.scalars(
                select(NotificationDeliveryRecord)
                .where(NotificationDeliveryRecord.user_id == user_id)
                .order_by(NotificationDeliveryRecord.attempted_at.desc())
                .limit(50)
            )
        )

    # ---------- SPEC-040: resumo mensal automático optativo ----------
    @app.get(f"{PROFILE_PREFIX}/reports", response_model=ReportSettingsOutput, tags=["profile"])
    def get_report_settings(auth: Service, credentials: Credentials):
        return MonthlySummaryService(auth.db, auth).settings(owner_id(auth, credentials))

    @app.put(f"{PROFILE_PREFIX}/reports", response_model=ReportSettingsOutput, tags=["profile"])
    def put_report_settings(data: ReportSettingsInput, auth: Service, credentials: Credentials):
        return MonthlySummaryService(auth.db, auth).set_settings(
            owner_id(auth, credentials), data.monthly_summary_enabled
        )

    @app.get(
        f"{FINANCIAL_PREFIX}/monthly-summaries",
        response_model=list[MonthlySummaryOutput],
        tags=["financial"],
    )
    def monthly_summaries(auth: Service, credentials: Credentials):
        return MonthlySummaryService(auth.db, auth).history(owner_id(auth, credentials))

    @app.get(f"{FINANCIAL_PREFIX}/monthly-summaries/{{competence}}/pdf", tags=["financial"])
    def monthly_summary_pdf(competence: str, auth: Service, credentials: Credentials):
        try:
            month = date.fromisoformat(f"{competence}-01")
        except ValueError as exc:
            raise AuthError("invalid_competence", 400) from exc
        content = MonthlySummaryService(auth.db, auth).download(owner_id(auth, credentials), month)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resumo-{competence}.pdf"},
        )

    @app.get(f"{FINANCIAL_PREFIX}/exports/csv", tags=["financial"])
    def export_csv(
        auth: Service,
        credentials: Credentials,
        start: str | None = None,
        end: str | None = None,
        month: str | None = None,
        year: int | None = None,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        start_date, end_date = export_period(start, end, month, year)
        data = StringIO()
        output = writer(data)
        output.writerow(["data", "tipo", "descrição", "categoria", "valor"])
        for item in auth.statement_entries(user.id, start_date, end_date):
            output.writerow(
                [
                    item["date"],
                    item["type"],
                    csv_cell(item["description"]),
                    item["category"],
                    item["amount"],
                ]
            )
        return StreamingResponse(
            iter([data.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=extrato.csv"},
        )

    @app.get(f"{FINANCIAL_PREFIX}/exports/pdf", tags=["financial"])
    def export_pdf(
        auth: Service,
        credentials: Credentials,
        start: str | None = None,
        end: str | None = None,
        month: str | None = None,
        year: int | None = None,
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.require_category_owner(user.id)
        start_date, end_date = export_period(start, end, month, year)
        entries = auth.statement_entries(user.id, start_date, end_date)
        categories: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for item in entries:
            categories[str(item["category"])] += item["amount"]
        total = sum((item["amount"] for item in entries), Decimal("0"))
        lines = [
            "FinNova - Extrato financeiro",
            f"Período: {start_date} a {end_date}",
            f"Saldo do período: R$ {total:.2f}",
            "Resumo por categoria:",
            *[f"{category}: R$ {amount:.2f}" for category, amount in sorted(categories.items())],
            "Detalhamento:",
        ]
        lines.extend(
            (
                f"{item['date']} | {item['type']} | {item['category']} | "
                f"{item['description']} | R$ {item['amount']:.2f}"
            )
            for item in entries
        )
        if not entries:
            lines.append("Sem lançamentos no período.")
        return Response(
            content=pdf_document(lines),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=extrato.pdf"},
        )

    @app.post(
        f"{FINANCIAL_PREFIX}/expenses",
        response_model=ExpenseOutput,
        status_code=201,
        tags=["financial"],
    )
    def create_expense(
        data: ExpenseCreateInput, request: Request, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return ExpenseOutput.model_validate(
            auth.create_expense(user.id, data.model_dump(), idempotency_key(request))
        )

    @app.patch(
        f"{FINANCIAL_PREFIX}/expenses/{{expense_id}}",
        response_model=ExpenseOutput,
        tags=["financial"],
    )
    def update_expense(
        expense_id: uuid.UUID, data: ExpenseUpdateInput, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        return ExpenseOutput.model_validate(
            auth.update_expense(user.id, expense_id, data.model_dump())
        )

    @app.delete(f"{FINANCIAL_PREFIX}/expenses/{{expense_id}}", status_code=204, tags=["financial"])
    def delete_expense(expense_id: uuid.UUID, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        auth.delete_expense(user.id, expense_id)

    @app.get(
        f"{SESSION_PREFIX}",
        response_model=list[SessionView],
        tags=["auth"],
    )
    def list_sessions(auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, current = auth.authenticate(credentials.credentials)
        return [
            SessionView(
                id=session.id,
                started_at=session.created_at,
                expires_at=session.expires_at,
                current=session.id == current.id,
            )
            for session in auth.list_sessions(user.id)
        ]

    @app.post(
        f"{SESSION_PREFIX}/revoke-all",
        response_model=RevokeAllSessionsOutput,
        tags=["auth"],
    )
    def revoke_all_sessions(response: Response, auth: Service, credentials: Credentials):
        if not credentials:
            raise AuthError("invalid_session")
        user, _ = auth.authenticate(credentials.credentials)
        count = auth.revoke_all_sessions(user.id)
        response.delete_cookie(
            COOKIE, path=COOKIE_PATH, secure=True, httponly=True, samesite="strict"
        )
        return RevokeAllSessionsOutput(revoked_sessions=count)

    @app.post(f"{SESSION_PREFIX}/{{session_id}}/revoke", status_code=204, tags=["auth"])
    def revoke_session(
        session_id: str, response: Response, auth: Service, credentials: Credentials
    ):
        if not credentials:
            raise AuthError("invalid_session")
        try:
            target = uuid.UUID(session_id)
        except ValueError as exc:
            raise AuthError("session_not_found", 404) from exc
        user, current = auth.authenticate(credentials.credentials)
        auth.revoke_session(user.id, target)
        if target == current.id:
            response.delete_cookie(
                COOKIE, path=COOKIE_PATH, secure=True, httponly=True, samesite="strict"
            )

    @app.post(f"{COOKIE_PATH}/logout", status_code=204, tags=["auth"])
    def logout(request: Request, response: Response, auth: Service, credentials: Credentials):
        auth.logout(credentials.credentials if credentials else None, request.cookies.get(COOKIE))
        response.delete_cookie(
            COOKIE, path=COOKIE_PATH, secure=True, httponly=True, samesite="strict"
        )

    @app.api_route(
        "/api/{rest:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    def api_not_found(rest: str):
        """Rota de API inexistente responde 404 JSON, mesmo com o cliente web montado em /."""
        raise AuthError("not_found", 404)

    frontend = Path(__file__).resolve().parents[2] / "frontend/dist"
    if frontend.is_dir():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="web")
    return app
