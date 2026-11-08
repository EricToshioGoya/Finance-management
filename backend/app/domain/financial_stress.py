"""Pure, non-mutating stress calculations under documented SPEC-032 assumptions."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

Kind = Literal["income_loss", "income_reduction", "emergency_expense"]
CENT = Decimal("0.01")
HORIZON = 120


@dataclass(frozen=True)
class StressScenario:
    kind: Kind
    months: int
    reduction_percent: Decimal = Decimal("0")
    emergency_amount: Decimal = Decimal("0")
    expense_cut_percent: Decimal = Decimal("0")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def simulate_stress(
    reserve: Decimal,
    average_income: Decimal,
    average_expenses: Decimal,
    scenario: StressScenario,
    minimum_reserve_months: int,
) -> dict[str, object]:
    """Estimate reserve-based runway, without assuming investments are liquid.

    Loss/reduction applies for scenario.months, then baseline income resumes.
    Emergency is a one-time debit at month 0; optional spending cut persists.
    Beyond 120 months the runway is unknown, never claimed infinite.
    """
    _validate(reserve, average_income, average_expenses, scenario, minimum_reserve_months)
    monthly_outflow = average_expenses * (
        Decimal("1") - scenario.expense_cut_percent / Decimal("100")
    )
    reduced_income = _income_during_shock(average_income, scenario)

    available = reserve - (
        scenario.emergency_amount if scenario.kind == "emergency_expense" else Decimal("0")
    )
    baseline_runway = reserve / average_expenses
    shortage = baseline_runway < minimum_reserve_months

    if available <= 0:
        return {
            "months_supported": Decimal("0.00"),
            "remaining_reserve": Decimal("0.00"),
            "reserve_months_before_shock": _money(baseline_runway),
            "low_reserve": shortage,
            "falls_below_threshold": True,
            "horizon_reached": False,
        }

    elapsed, available, exhausted = _run_reserve(
        available, monthly_outflow, reduced_income, average_income, scenario.months
    )

    return {
        "months_supported": _money(elapsed) if exhausted else None,
        "remaining_reserve": _money(max(available, Decimal("0"))),
        "reserve_months_before_shock": _money(baseline_runway),
        "low_reserve": shortage,
        "falls_below_threshold": (exhausted and elapsed < minimum_reserve_months),
        "horizon_reached": not exhausted,
    }


def _validate(
    reserve: Decimal,
    average_income: Decimal,
    average_expenses: Decimal,
    scenario: StressScenario,
    minimum_reserve_months: int,
) -> None:
    if average_expenses <= 0 or average_income < 0 or reserve < 0:
        raise ValueError("invalid_financial_baseline")
    if minimum_reserve_months < 3 or minimum_reserve_months > 6:
        raise ValueError("invalid_reserve_threshold")
    if scenario.months < 1 or scenario.months > 120:
        raise ValueError("invalid_stress_duration")
    if not Decimal("0") <= scenario.reduction_percent <= Decimal("100"):
        raise ValueError("invalid_income_reduction")
    if not Decimal("0") <= scenario.expense_cut_percent <= Decimal("100"):
        raise ValueError("invalid_expense_cut")
    if scenario.emergency_amount < 0:
        raise ValueError("invalid_emergency_amount")


def _income_during_shock(average_income: Decimal, scenario: StressScenario) -> Decimal:
    if scenario.kind == "income_loss":
        return Decimal("0")
    if scenario.kind == "income_reduction":
        return average_income * (Decimal("1") - scenario.reduction_percent / Decimal("100"))
    if scenario.kind != "emergency_expense":
        raise ValueError("invalid_stress_kind")
    return average_income


def _run_reserve(
    available: Decimal,
    monthly_outflow: Decimal,
    reduced_income: Decimal,
    average_income: Decimal,
    shock_months: int,
) -> tuple[Decimal, Decimal, bool]:
    """Consome a reserva mês a mês até esgotar ou atingir o horizonte (fração no último mês)."""
    elapsed = Decimal("0")
    for month in range(1, HORIZON + 1):
        income = reduced_income if month <= shock_months else average_income
        deficit = monthly_outflow - income
        # A reserva é sempre positiva aqui; déficit maior ou igual a ela a esgota no mês.
        if deficit >= available:
            return elapsed + available / deficit, Decimal("0"), True
        available -= deficit
        elapsed += 1
    return elapsed, available, False
