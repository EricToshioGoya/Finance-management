from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


class AccountDeletionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: SecretStr = Field(min_length=1, max_length=128)
    confirmation: str = Field(pattern="^EXCLUIR MINHA CONTA$")


class UsageEventInput(BaseModel):
    """The closed vocabulary prevents this telemetry endpoint becoming a payload sink."""

    model_config = ConfigDict(extra="forbid")
    module: Literal["dashboard", "simulator", "financial", "profile"]
    action: Literal["opened", "viewed"]


class AdminUserOutput(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    created_at: datetime
    investor_profile: Literal["conservador", "moderado", "arrojado"] | None = None
    status: Literal["active"]


class AdminUsersPageOutput(BaseModel):
    items: list[AdminUserOutput]
    page: int
    page_size: int
    total: int


class QuizQuestionOutput(BaseModel):
    id: Literal["knowledge", "loss", "horizon", "liquidity", "volatility"]
    prompt: str
    options: list[str]


class QuizAnswersInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answers: list[int] = Field(min_length=5, max_length=5)

    @field_validator("answers")
    @classmethod
    def answers_are_scores(cls, answers: list[int]) -> list[int]:
        if any(answer not in {0, 1, 2} for answer in answers):
            raise ValueError("Each answer must be 0, 1 or 2")
        return answers


class InvestorProfileOutput(BaseModel):
    profile: Literal["conservador", "moderado", "arrojado"] | None
    guidance: str | None


class QuizResultOutput(InvestorProfileOutput):
    score: int


class PublicCompanyOutput(BaseModel):
    id: UUID
    ticker: str
    cnpj: str
    legal_name: str
    sector: str


class OfficialDocumentOutput(BaseModel):
    id: UUID
    company_id: UUID
    document_type: Literal["DFP", "ITR", "FRE", "IPE"]
    subject: str
    reference_period: str
    delivered_at: date
    status: Literal["active", "restated", "replaced"]
    official_url: str
    link_status: Literal["unchecked", "available", "broken"]
    last_checked_at: datetime | None


class FinancialIndicatorOutput(BaseModel):
    id: UUID
    company_id: UUID
    metric: Literal["net_revenue", "net_income", "equity"]
    period_kind: Literal["annual", "quarterly"]
    reference_period: str
    reference_date: date
    value: Decimal
    unit: Literal["BRL_THOUSANDS"]
    source_name: str
    source_url: str
    status: Literal["active", "restated"]
    published_at: date
    synced_at: datetime
    effective: bool


class MarketPriceHistoryOutput(BaseModel):
    quoted_on: date
    close_price: Decimal


class MarketQuoteOutput(BaseModel):
    ticker: str
    asset_kind: Literal["stock", "fii"]
    price: Decimal
    daily_change_percent: Decimal
    referenced_at: datetime
    fresh_until: datetime
    source_name: str
    catalogue_type: Literal["local_reference"]
    history: list[MarketPriceHistoryOutput]


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=254)
    password: SecretStr

    @field_validator("password")
    @classmethod
    def valid_password(cls, password: SecretStr) -> SecretStr:
        if not 8 <= len(password.get_secret_value()) <= 128:
            raise ValueError("Password must contain 8 to 128 characters")
        return password


class RegisterInput(LoginInput):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def valid_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Name is required")
        return name.strip()


class ConfirmationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: SecretStr = Field(min_length=32, max_length=512)


class ConfirmationOutput(BaseModel):
    email_verified: bool


class PasswordRecoveryRequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=254)


class PasswordResetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: SecretStr = Field(min_length=32, max_length=512)
    new_password: SecretStr

    @field_validator("new_password")
    @classmethod
    def valid_new_password(cls, password: SecretStr) -> SecretStr:
        if not 8 <= len(password.get_secret_value()) <= 128:
            raise ValueError("Password must contain 8 to 128 characters")
        return password


class PasswordChangeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: SecretStr
    new_password: SecretStr

    @field_validator("current_password", "new_password")
    @classmethod
    def valid_password(cls, password: SecretStr) -> SecretStr:
        if not 8 <= len(password.get_secret_value()) <= 128:
            raise ValueError("Password must contain 8 to 128 characters")
        return password


class CategoryCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=60)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def valid_category_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Category name is required")
        return name.strip()


class CategoryVisibilityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active: bool


class CategoryOutput(BaseModel):
    key: str
    name: str
    color: str
    kind: str
    active: bool


class AccountCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=60)
    account_type: str = Field(pattern="^(checking|savings|cash|investment)$")
    initial_balance: Decimal = Field(max_digits=14, decimal_places=2)

    @field_validator("name")
    @classmethod
    def valid_account_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Account name is required")
        return name.strip()


class AccountOutput(BaseModel):
    id: UUID
    name: str
    account_type: str
    initial_balance: Decimal


class CreditCardCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=60)
    credit_limit: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    closing_day: int = Field(ge=1, le=31)
    due_day: int = Field(ge=1, le=31)

    @field_validator("name")
    @classmethod
    def valid_card_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Card name is required")
        return name.strip()


class CreditCardOutput(BaseModel):
    id: UUID
    name: str
    credit_limit: Decimal
    closing_day: int
    due_day: int


class FinancialSourcesOutput(BaseModel):
    accounts: list[AccountOutput]
    credit_cards: list[CreditCardOutput]


class NetWorthItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["asset", "liability"]
    name: str = Field(min_length=1, max_length=100)
    value: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    annual_rate: Decimal | None = Field(default=None, ge=0, le=1000, max_digits=8, decimal_places=4)

    @field_validator("name")
    @classmethod
    def valid_net_worth_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name is required")
        return value.strip()


class NetWorthItemUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    value: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    annual_rate: Decimal | None = Field(default=None, ge=0, le=1000, max_digits=8, decimal_places=4)

    @field_validator("name")
    @classmethod
    def valid_optional_net_worth_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Name is required")
        return value.strip() if value is not None else None


class NetWorthItemOutput(BaseModel):
    id: UUID
    kind: Literal["asset", "liability"]
    name: str
    value: Decimal
    annual_rate: Decimal | None
    origin: Literal["manual", "account", "credit_card_invoice", "financing"]


class NamedAssetGoalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    category: Literal["emergency", "travel", "home", "education", "other"]
    asset_id: UUID
    target_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    deadline: date
    annual_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, decimal_places=6)

    @field_validator("name")
    @classmethod
    def normalize_goal_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Goal name cannot be blank")
        return name.strip()


class NamedAssetGoalOutput(BaseModel):
    id: UUID
    name: str
    category: Literal["emergency", "travel", "home", "education", "other"]
    asset_id: UUID
    asset_name: str
    target_amount: Decimal
    deadline: date
    annual_rate: Decimal
    current_value: Decimal
    progress_percent: Decimal
    remaining_amount: Decimal
    months_remaining: int
    monthly_contribution_needed: Decimal | None
    projection_status: Literal["on_track", "needs_contribution", "overdue"]


class ExternalApiGrantInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=60)
    scopes: list[Literal["balance:read", "net_worth:read"]] = Field(min_length=1, max_length=2)

    @field_validator("name")
    @classmethod
    def validate_grant_label(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Grant label cannot be blank")
        return name.strip()

    @field_validator("scopes")
    @classmethod
    def unique_grant_scopes(cls, scopes: list[str]) -> list[str]:
        if len(scopes) != len(set(scopes)):
            raise ValueError("Duplicate scopes are not permitted")
        return scopes


class ExternalApiGrantOutput(BaseModel):
    id: UUID
    name: str
    scopes: list[str]
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None


class ExternalApiGrantCreated(ExternalApiGrantOutput):
    api_key: str


class ExternalBalanceOutput(BaseModel):
    competence: str
    income: Decimal
    expenses: Decimal
    balance_variation: Decimal


class ExternalNetWorthOutput(BaseModel):
    as_of: date
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal


class NetWorthOutput(BaseModel):
    as_of: date
    assets: list[NetWorthItemOutput]
    liabilities: list[NetWorthItemOutput]
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal


InvestmentClass = Literal["fixed_income", "stocks", "fiis", "savings", "other"]


class InvestmentClassInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_class: InvestmentClass


class InvestmentTargetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    targets: dict[InvestmentClass, Decimal]

    @model_validator(mode="after")
    def validate_allocation(self):
        expected = {"fixed_income", "stocks", "fiis", "savings", "other"}
        if set(self.targets) != expected:
            raise ValueError("All five allocation classes must be supplied")
        if any(
            value < 0 or value > 100 or value.as_tuple().exponent < -2
            for value in self.targets.values()
        ):
            raise ValueError("Targets must be percentages between 0 and 100 with two decimals")
        if sum(self.targets.values(), Decimal("0")) != Decimal("100"):
            raise ValueError("Allocation targets must sum to 100 percent")
        return self


class InvestmentAllocationRowOutput(BaseModel):
    asset_class: InvestmentClass
    amount: Decimal
    actual_percent: Decimal | None
    target_percent: Decimal | None
    deviation_points: Decimal | None


class InvestmentClassifiedAssetOutput(BaseModel):
    id: UUID
    name: str
    value: Decimal
    asset_class: InvestmentClass


class InvestmentAllocationOutput(BaseModel):
    total_invested: Decimal
    classes: list[InvestmentAllocationRowOutput]
    unclassified: list[NetWorthItemOutput]
    classified: list[InvestmentClassifiedAssetOutput]
    has_targets: bool


class ConfirmFinancingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    asset_value: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    down_payment: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    installments: int = Field(ge=1, le=600)
    annual_rate: Decimal = Field(ge=0, le=100, max_digits=9, decimal_places=6)
    confirmation: Literal["CONFIRMAR FINANCIAMENTO REAL"]
    create_recurring_expense: bool = False
    expense_category_key: str | None = Field(default=None, max_length=80)
    expense_account_id: UUID | None = None
    first_payment_on: date | None = None

    @field_validator("name")
    @classmethod
    def validate_financing_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Name cannot be blank")
        return name.strip()

    @model_validator(mode="after")
    def validate_real_financing(self):
        if self.down_payment >= self.asset_value:
            raise ValueError("Financed principal must be positive")
        options = (
            self.expense_category_key,
            self.expense_account_id,
            self.first_payment_on,
        )
        if self.create_recurring_expense and any(option is None for option in options):
            raise ValueError("Expense category, account and due date are required")
        if not self.create_recurring_expense and any(option is not None for option in options):
            raise ValueError("Expense fields require the recurring expense option")
        return self


class ConfirmedFinancingOutput(BaseModel):
    id: UUID
    name: str
    principal: Decimal
    asset_value: Decimal
    down_payment: Decimal
    installments: int
    annual_rate: Decimal
    installment_amount: Decimal
    first_payment_on: date | None
    expense_id: UUID | None
    confirmed_at: datetime
    origin: Literal["financing"] = "financing"
    current_balance_policy: Literal["initial_until_reconciled"] = "initial_until_reconciled"


class FinancingComparisonInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_value: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    down_payment: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    installments: int = Field(ge=1, le=600)
    financing_annual_rate: Decimal = Field(ge=0, le=100, max_digits=9, decimal_places=6)
    investment_annual_rate: Decimal = Field(ge=0, le=100, max_digits=9, decimal_places=6)
    horizon_months: int = Field(ge=1, le=600)

    @model_validator(mode="after")
    def validate_down_payment(self):
        if self.down_payment > self.asset_value:
            raise ValueError("Down payment cannot exceed asset value")
        return self


class FinancingComparisonOutput(BaseModel):
    asset_value: Decimal
    down_payment: Decimal
    financing_months: int
    comparison_horizon_months: int
    financing_annual_rate: Decimal
    investment_annual_rate: Decimal
    monthly_investment: Decimal
    financing_total_paid: Decimal
    financing_total_interest: Decimal
    financing_possession_month: int
    invest_possession_month: int | None
    invested_by_horizon: Decimal
    investment_balance_at_horizon: Decimal
    invest_cost_to_possession: Decimal | None
    invest_balance_at_possession: Decimal | None
    nominal_purchase_price: Decimal
    nominal_cost_difference: Decimal | None
    lower_nominal_cost: Literal["finance_now", "invest_then_buy", "tie", "not_comparable"]
    assumptions: list[str]
    simulated_only: Literal[True] = True


class FinancingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_value: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    down_payment: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    installments: int = Field(ge=1, le=600)
    annual_rate: Decimal = Field(ge=0, le=100, max_digits=9, decimal_places=6)

    @model_validator(mode="after")
    def down_payment_must_fit_asset(self):
        if self.down_payment > self.asset_value:
            raise ValueError("Down payment cannot exceed asset value")
        return self


class FinancingInstallmentOutput(BaseModel):
    number: int
    payment: Decimal
    interest: Decimal
    principal: Decimal
    remaining_balance: Decimal


class FinancingOutput(BaseModel):
    asset_value: Decimal
    down_payment: Decimal
    financed_amount: Decimal
    installments: int
    annual_rate: Decimal
    monthly_rate: Decimal
    installment_amount: Decimal
    total_installments: Decimal
    total_paid: Decimal
    total_interest: Decimal
    schedule: list[FinancingInstallmentOutput]
    amortization_system: Literal["price"] = "price"
    rate_assumption: str = "annual_effective_equivalent_monthly"
    includes_fees: bool = False
    simulated_only: bool = True


class StressScenarioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["income_loss", "income_reduction", "emergency_expense"]
    months: int = Field(ge=1, le=120)
    reduction_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    emergency_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    expense_cut_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    @model_validator(mode="after")
    def validate_shock(self):
        if self.kind != "income_reduction" and self.reduction_percent != 0:
            raise ValueError("Reduction percent applies only to income reduction")
        if self.kind == "income_reduction" and self.reduction_percent <= 0:
            raise ValueError("Positive income reduction required")
        if self.kind != "emergency_expense" and self.emergency_amount != 0:
            raise ValueError("Emergency amount applies only to emergency expense")
        if self.kind == "emergency_expense" and self.emergency_amount <= 0:
            raise ValueError("Positive emergency expense required")
        return self


class StressCompareInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minimum_reserve_months: int = Field(default=3, ge=3, le=6)
    first: StressScenarioInput
    second: StressScenarioInput


class StressResultOutput(BaseModel):
    months_supported: Decimal | None
    remaining_reserve: Decimal
    reserve_months_before_shock: Decimal
    low_reserve: bool
    falls_below_threshold: bool
    horizon_reached: bool


class StressCompareOutput(BaseModel):
    reserve: Decimal
    real_net_worth: Decimal
    average_monthly_income: Decimal
    average_monthly_expenses: Decimal
    window_months: int
    minimum_reserve_months: int
    rule_version: str
    first: StressResultOutput
    second: StressResultOutput


class NetWorthHeatmapOutput(BaseModel):
    as_of: date
    items: list[NetWorthItemOutput]
    total_absolute: Decimal


class NetWorthSnapshotOutput(BaseModel):
    competence: date
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    captured_at: datetime


class HealthScoreFactorOutput(BaseModel):
    key: Literal["spending", "reserve", "debt", "goals"]
    score: Decimal
    suggestion: str


class HealthScoreHistoryOutput(BaseModel):
    competence: date
    score: Decimal


class EducationalArticleOutput(BaseModel):
    key: str
    title: str
    body: str
    language: Literal["pt", "en"]
    fallback: bool
    version: str


class HealthScoreOutput(BaseModel):
    competence: date
    score: Decimal
    classification: Literal["critical", "attention", "healthy", "excellent"]
    factors: list[HealthScoreFactorOutput]
    history: list[HealthScoreHistoryOutput]
    rule_version: str
    educational: bool


class RecurringIncomeCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    account_id: UUID | None = None
    starts_on: date | None = None

    @field_validator("description")
    @classmethod
    def valid_description(cls, description: str) -> str:
        if not description.strip():
            raise ValueError("Income description is required")
        return description.strip()


class RecurringIncomeOutput(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    account_id: UUID | None
    starts_on: date


class RecurringIncomeUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    starts_on: date | None = None

    @field_validator("description")
    @classmethod
    def valid_description(cls, description: str | None) -> str | None:
        if description is not None and description.strip():
            return description.strip()
        return description


class OneTimeIncomeCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    account_id: UUID | None = None
    occurred_on: date

    @field_validator("description")
    @classmethod
    def valid_one_time_description(cls, description: str) -> str:
        if not description.strip():
            raise ValueError("Income description is required")
        return description.strip()


class OneTimeIncomeOutput(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    account_id: UUID | None
    occurred_on: date


class OneTimeIncomeUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    occurred_on: date | None = None

    @field_validator("description")
    @classmethod
    def valid_description(cls, description: str | None) -> str | None:
        if description is not None and description.strip():
            return description.strip()
        return description


class BonusCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    periodicity: str = Field(pattern="^(monthly|annual)$")
    starts_on: date | None = None
    reference_month: int | None = Field(default=None, ge=1, le=12)

    @model_validator(mode="after")
    def annual_requires_reference_month(self):
        if self.periodicity == "annual" and self.reference_month is None:
            raise ValueError("Reference month is required for annual bonus")
        if self.periodicity == "monthly" and self.reference_month is not None:
            raise ValueError("Reference month only applies to annual bonus")
        return self

    @field_validator("description")
    @classmethod
    def valid_bonus_description(cls, description: str) -> str:
        if not description.strip():
            raise ValueError("Bonus description is required")
        return description.strip()


class BonusOutput(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    periodicity: str
    starts_on: date
    reference_month: int | None


class BonusUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    periodicity: str | None = Field(default=None, pattern="^(monthly|annual)$")
    starts_on: date | None = None
    reference_month: int | None = Field(default=None, ge=1, le=12)


class IncomeSummaryOutput(BaseModel):
    competence: str
    recurring_income: Decimal
    one_time_income: Decimal
    bonus: Decimal
    total: Decimal


class ExpenseCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    category_key: str = Field(min_length=1, max_length=80)
    occurred_on: date
    recurring: bool = False
    account_id: UUID | None = None
    credit_card_id: UUID | None = None

    @model_validator(mode="after")
    def exactly_one_source(self):
        if (self.account_id is None) == (self.credit_card_id is None):
            raise ValueError("Exactly one source is required")
        return self


class ExpenseUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    category_key: str | None = Field(default=None, min_length=1, max_length=80)
    occurred_on: date | None = None
    recurring: bool | None = None

    @field_validator("description")
    @classmethod
    def valid_description(cls, description: str | None) -> str | None:
        if description is not None and description.strip():
            return description.strip()
        return description


class ExpenseOutput(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    category_key: str
    occurred_on: date
    recurring: bool
    account_id: UUID | None
    credit_card_id: UUID | None


class BalanceSummaryOutput(IncomeSummaryOutput):
    expenses: Decimal
    balance_variation: Decimal


class CalculatorInput(BaseModel):
    """Shared contract for the calculator and manual simulation scenarios."""

    model_config = ConfigDict(extra="forbid")
    initial_amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    monthly_contribution: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    annual_rate: Decimal = Field(ge=0, max_digits=10, decimal_places=6)
    term_months: int = Field(ge=1, le=720)


class CalculatorOutput(BaseModel):
    invested: Decimal
    interest: Decimal
    gross_amount: Decimal
    monthly_series: list[dict[str, Decimal | int]]
    rate_explanation: str
    investor_guidance: str | None = None


class TaxProjectionInput(CalculatorInput):
    product: str = Field(pattern="^(cdb|tesouro|poupanca)$")


class TaxProjectionOutput(CalculatorOutput):
    tax_rate: Decimal
    estimated_tax: Decimal
    net_amount: Decimal


class TargetContributionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    initial_amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    annual_rate: Decimal = Field(ge=0, max_digits=10, decimal_places=6)
    term_months: int = Field(ge=1, le=720)
    available_monthly_amount: Decimal | None = Field(
        default=None, ge=0, max_digits=14, decimal_places=2
    )


class TargetContributionOutput(BaseModel):
    monthly_contribution_needed: Decimal
    feasible: bool
    warning: str | None = None


class IndicatorOutput(BaseModel):
    code: str
    value: Decimal
    unit: str
    reference_date: date
    checked_at: datetime
    source: str
    stale: bool


class SimulationCreateInput(CalculatorInput):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=100)
    product: str = Field(pattern="^(cdb|tesouro|poupanca)$")

    @field_validator("label")
    @classmethod
    def valid_label(cls, label: str) -> str:
        if not label.strip():
            raise ValueError("Simulation label is required")
        return label.strip()


class ForeignCurrencySimulationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=100)
    currency: Literal["BRL", "USD", "EUR"]
    initial_amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    monthly_contribution: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    asset_annual_return: Decimal = Field(ge=0, max_digits=10, decimal_places=6)
    expected_exchange_annual_change: Decimal = Field(
        ge=Decimal("-99.999999"), max_digits=10, decimal_places=6
    )
    term_months: int = Field(ge=1, le=720)

    @model_validator(mode="after")
    def brl_has_no_exchange_hypothesis(self):
        if self.currency == "BRL" and self.expected_exchange_annual_change != 0:
            raise ValueError("BRL exchange variation must be zero")
        return self


class ForeignCurrencySimulationOutput(BaseModel):
    currency: Literal["BRL", "USD", "EUR"]
    initial_amount: Decimal
    final_amount_original: Decimal
    exchange_rate_to_brl: Decimal
    projected_exchange_rate_to_brl: Decimal
    final_amount_brl: Decimal
    reference_date: date
    referenced_at: datetime
    source: str
    risk_notice: str
    rule_version: str


class VariableIncomeSimulationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=100)
    ticker: str | None = Field(default=None, pattern=r"^[A-Za-z]{4,5}[0-9]{1,2}$")
    initial_amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    monthly_contribution: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    expected_annual_return: Decimal = Field(ge=0, max_digits=10, decimal_places=6)
    term_months: int = Field(ge=1, le=720)

    @field_validator("label")
    @classmethod
    def valid_label(cls, label: str) -> str:
        if not label.strip():
            raise ValueError("Simulation label is required")
        return label.strip()


class RiskMetricsOutput(BaseModel):
    ticker: str
    period_start: date
    period_end: date
    observations: int
    volatility_annualized: Decimal
    sharpe: Decimal | None
    status: Literal["available", "zero_volatility"]
    disclaimer: str
    rule_version: str


class AdvancedMetricsPreferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool


class AdvancedMetricsPreferenceOutput(AdvancedMetricsPreferenceInput):
    available_by_default: bool


class SimulationOutput(BaseModel):
    id: UUID
    kind: str
    label: str
    payload: dict
    final_amount: Decimal
    created_at: datetime
    risk_metrics: RiskMetricsOutput | None = None
    foreign_currency: ForeignCurrencySimulationOutput | None = None


class SimulationComparisonInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    simulation_ids: list[UUID] = Field(min_length=2, max_length=10)


class SimulationComparisonOutput(BaseModel):
    simulations: list[SimulationOutput]
    difference_from_first: list[Decimal]


class CardInvoiceOutput(BaseModel):
    card_id: UUID
    competence: str
    invoice_total: Decimal
    credit_limit: Decimal
    available_limit: Decimal
    near_limit: bool
    due_day: int


class BudgetGoalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str = Field(pattern="^(expense_total|income_total|category_expense)$")
    category_key: str | None = Field(default=None, min_length=1, max_length=80)
    target: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    alert_threshold: Decimal = Field(default=Decimal("90"), ge=70, le=100)

    @model_validator(mode="after")
    def category_rule(self):
        if (self.kind == "category_expense") != (self.category_key is not None):
            raise ValueError("Category is required only for category expense goals")
        return self


class BudgetProgressOutput(BudgetGoalInput):
    id: UUID
    actual: Decimal
    percentage: Decimal
    status: str


class DashboardMonthOutput(BalanceSummaryOutput):
    pass


class PublicUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    role: str
    email_verified: bool
    investor_profile: Literal["conservador", "moderado", "arrojado"] | None = None


class PreferencesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    language: str = Field(pattern="^(pt|en)$")
    theme: str = Field(pattern="^(light|dark)$")
    in_app_notifications: bool
    email_notifications: bool
    push_notifications: bool


class PreferencesOutput(PreferencesInput):
    pass


class WatchlistOutput(BaseModel):
    company: PublicCompanyOutput
    created_at: datetime


class WatchlistMutationOutput(BaseModel):
    created: bool
    item: WatchlistOutput | None = None


NotificationKind = Literal[
    "invoice_due",
    "budget_goal_exceeded",
    "watchlist_document",
    "recurring_expense_due",
    "achievement_unlocked",
    "monthly_summary",
]


class NotificationEventInput(BaseModel):
    """Stable, payload-minimal hand-off from an owned producer to the in-app centre."""

    model_config = ConfigDict(extra="forbid")
    # Conquistas e resumo mensal são gerados só pelo servidor (SPEC-051/040).
    kind: Literal[
        "invoice_due", "budget_goal_exceeded", "watchlist_document", "recurring_expense_due"
    ]
    source_key: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9:_-]+$")


class NotificationPreferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool


class NotificationPreferenceOutput(NotificationPreferenceInput):
    kind: NotificationKind


class NotificationOutput(BaseModel):
    id: UUID
    kind: NotificationKind
    title: str
    message: str
    created_at: datetime
    read_at: datetime | None


class NotificationEventOutput(BaseModel):
    created: bool
    notification: NotificationOutput | None = None


class WebhookSubscriptionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(min_length=12, max_length=2048)


class WebhookSubscriptionOutput(BaseModel):
    id: UUID
    url: str
    enabled: bool
    created_at: datetime
    disabled_at: datetime | None


class WebhookSubscriptionCreated(WebhookSubscriptionOutput):
    signing_secret: str


class WebhookAttemptOutput(BaseModel):
    id: UUID
    subscription_id: UUID
    event_type: Literal["notification.created"]
    outcome: Literal["succeeded", "failed"]
    status_code: int | None
    failure_code: str | None
    attempted_at: datetime
    retry_of_id: UUID | None


class EngagementModuleOutput(BaseModel):
    module: Literal["dashboard", "simulator", "financial", "profile"]
    accesses: int
    unique_users: int


class RecurringModuleOutput(BaseModel):
    module: Literal["dashboard", "simulator", "financial", "profile"]
    recurring_users: int


class EngagementTrendOutput(BaseModel):
    date: date
    accesses: int
    unique_users: int


class ProfileDistributionItemOutput(BaseModel):
    profile: Literal["conservador", "moderado", "arrojado"]
    count: int
    percentage: Decimal


class ProfileDistributionOutput(BaseModel):
    start: date | None
    end: date | None
    total_users: int
    profiled_users: int
    without_profile: int
    items: list[ProfileDistributionItemOutput]
    generated_at: datetime


class EngagementOutput(BaseModel):
    start: date
    end: date
    modules: list[EngagementModuleOutput]
    most_used_module: str | None
    least_used_module: str | None
    dau: int
    wau: int
    mau: int
    average_frequency: float
    inactive_users: int
    inactive_days: int
    recurring_modules: list[RecurringModuleOutput]
    trend: list[EngagementTrendOutput]


class ProfileOutput(BaseModel):
    user: PublicUser
    pending_email: str | None
    preferences: PreferencesOutput


class ProfileUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=254)
    current_password: SecretStr | None = None

    @field_validator("name")
    @classmethod
    def valid_name(cls, name: str | None) -> str | None:
        if name is not None and not name.strip():
            raise ValueError("Name is required")
        return name.strip() if name is not None else None

    @model_validator(mode="after")
    def valid_change(self):
        if self.name is None and self.email is None:
            raise ValueError("A profile field is required")
        if self.email is not None:
            if self.current_password is None:
                raise ValueError("Current password is required")
            size = len(self.current_password.get_secret_value())
            if not 8 <= size <= 128:
                raise ValueError("Password must contain 8 to 128 characters")
        return self


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ErrorOutput(BaseModel):
    detail: str
    manual_entry_permitted: bool = False


class SessionView(BaseModel):
    id: UUID
    started_at: datetime
    expires_at: datetime
    current: bool


class RevokeAllSessionsOutput(BaseModel):
    revoked_sessions: int


# ---------- SPEC-044/045: vínculo entre usuários e divisão de despesas ----------
class SharingInviteInput(BaseModel):
    email: str = Field(min_length=3, max_length=254)


class SharingInviteOutput(BaseModel):
    status: Literal["sent"]


class SharedLinkActiveOutput(BaseModel):
    id: UUID
    partner_name: str
    since: datetime | None


class SharedInvitationReceivedOutput(BaseModel):
    id: UUID
    from_name: str
    expires_at: datetime


class SharedInvitationSentOutput(BaseModel):
    id: UUID
    expires_at: datetime


class SharedLinkHistoryOutput(BaseModel):
    id: UUID
    partner_name: str
    ended_at: datetime | None


class SharingOverviewOutput(BaseModel):
    active: SharedLinkActiveOutput | None
    received: list[SharedInvitationReceivedOutput]
    sent: list[SharedInvitationSentOutput]
    history: list[SharedLinkHistoryOutput]


class ShareSplitInput(BaseModel):
    split: Literal["equal", "custom"] = "equal"
    payer_percent: Decimal | None = Field(default=None, gt=0, lt=100, decimal_places=2)
    partner_percent: Decimal | None = Field(default=None, gt=0, lt=100, decimal_places=2)

    def resolved_payer_percent(self) -> Decimal:
        """50/50 ou percentual customizado que precisa fechar 100%."""
        if self.split == "equal":
            return Decimal("50")
        if self.payer_percent is None or self.partner_percent is None:
            raise ValueError("split_must_total_100")
        if self.payer_percent + self.partner_percent != Decimal("100"):
            raise ValueError("split_must_total_100")
        return self.payer_percent


class ShareExpenseInput(ShareSplitInput):
    expense_id: UUID


class SettlementInput(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    link_id: UUID | None = None


class SharedItemOutput(BaseModel):
    id: UUID
    expense_id: UUID
    description: str
    amount: Decimal
    occurred_on: date
    paid_by: Literal["me", "partner"]
    payer_percent: Decimal
    my_share: Decimal
    partner_share: Decimal


class SettlementOutput(BaseModel):
    id: UUID
    amount: Decimal
    paid_by: Literal["me", "partner"]
    created_at: datetime


class SharedBalanceOutput(BaseModel):
    link_id: UUID
    status: Literal["active", "ended"]
    partner_name: str
    items: list[SharedItemOutput]
    settlements: list[SettlementOutput]
    direction: Literal["settled", "partner_owes_me", "i_owe_partner"]
    amount: Decimal


# ---------- SPEC-046 a SPEC-049: aposentadoria, previdência, IR e resumo anual ----------
class RetirementInput(BaseModel):
    current_age: int = Field(ge=14, le=100)
    target_age: int = Field(ge=15, le=110)
    initial_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    monthly_contribution: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    annual_rate: Decimal = Field(ge=0, le=100, max_digits=10, decimal_places=6)
    withdrawal_rate: Decimal = Field(default=Decimal("4"), gt=0, le=20, decimal_places=4)


class SuggestedRateOutput(BaseModel):
    code: str
    value: Decimal
    stale: bool


class RetirementOutput(BaseModel):
    months: int
    invested: Decimal
    projected_wealth: Decimal
    estimated_monthly_income: Decimal
    withdrawal_rate: Decimal
    suggested_rate: SuggestedRateOutput | None
    assumptions: list[str]
    notice: str


class PensionInput(BaseModel):
    initial_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    monthly_contribution: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    annual_rate: Decimal = Field(ge=0, le=100, max_digits=10, decimal_places=6)
    term_months: int = Field(ge=1, le=720)
    regime: Literal["regressive", "progressive"]
    progressive_rate: Decimal | None = Field(default=None, ge=0, le=Decimal("27.5"))


class PensionModalityOutput(BaseModel):
    modality: Literal["pgbl", "vgbl", "own_portfolio"]
    invested: Decimal
    gross_amount: Decimal
    earnings: Decimal
    tax: Decimal
    net_amount: Decimal
    effective_tax_rate: Decimal


class PensionOutput(BaseModel):
    regime: str
    rule_version: str
    results: list[PensionModalityOutput]
    pgbl_context: str
    notice: str


class TaxEstimateInput(BaseModel):
    regime: Literal["fixed_income", "stock", "fii", "day_trade"]
    competence: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    result: Decimal = Field(max_digits=14, decimal_places=2)
    sales: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    holding_days: int | None = Field(default=None, ge=1, le=36500)


class TaxEstimateOutput(BaseModel):
    id: UUID
    regime: str
    competence: str
    sales: Decimal
    result: Decimal
    tax_rate: Decimal
    tax: Decimal
    exempt: bool
    darf_due_on: date | None
    rule_version: str
    notes: list[str]
    notice: str


class AnnualMonthOutput(BaseModel):
    competence: str
    total: Decimal


class AnnualIncomeOutput(BaseModel):
    monthly: list[AnnualMonthOutput]
    recurring_income: Decimal
    one_time_income: Decimal
    bonus: Decimal
    total: Decimal


class AnnualSimulationOutput(BaseModel):
    label: str
    kind: str
    final_amount: Decimal
    estimated_tax: Decimal
    origin: Literal["simulated"]


class AnnualSummaryOutput(BaseModel):
    year: int
    registered_income: AnnualIncomeOutput
    tax_estimates: list[TaxEstimateOutput]
    estimated_tax_total: Decimal
    simulations: list[AnnualSimulationOutput]
    notice: str


# ---------- SPEC-050/051/052 ----------
class PrivacySettingsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score_benchmark_enabled: bool


class PrivacySettingsOutput(PrivacySettingsInput):
    pass


class ScoreBenchmarkOutput(BaseModel):
    enabled: bool
    available: bool
    reason: Literal["opted_out", "no_profile", "no_score", "insufficient_group"] | None
    profile: str | None
    competence: str | None
    minimum_group_size: int
    my_score: Decimal | None
    group_average_score: Decimal | None
    group_median_score: Decimal | None
    my_savings_rate: Decimal | None
    group_average_savings_rate: Decimal | None
    group_median_savings_rate: Decimal | None


class AchievementOutput(BaseModel):
    code: str
    title: str
    description: str
    unlocked: bool
    unlocked_at: datetime | None
    progress_percent: Decimal


class TourStepOutput(BaseModel):
    key: Literal["first_income", "first_expense", "investor_quiz", "simulator"]
    tab: str
    done: bool


class TourOutput(BaseModel):
    status: Literal["not_started", "in_progress", "completed", "skipped"]
    show: bool
    step: int
    variant: Literal["didactic", "concise"]
    profile: str | None
    steps: list[TourStepOutput]


class TourActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["start", "advance", "complete", "skip", "reopen"]
    step: int | None = Field(default=None, ge=0, le=3)
