"""SPEC-032: isolated financial stress engine and its numeric boundaries."""

from decimal import Decimal

import pytest

from app.domain.financial_stress import StressScenario, simulate_stress


def test_loss_of_income_600_reserve_100_expenses_supports_six_months():
    """Cláusulas: SPEC-032-R03, SPEC-032-R04."""
    result = simulate_stress(
        Decimal("600"),
        Decimal("0"),
        Decimal("100"),
        StressScenario(kind="income_loss", months=12),
        6,
    )
    assert result["months_supported"] == Decimal("6.00")
    assert result["reserve_months_before_shock"] == Decimal("6.00")
    assert result["low_reserve"] is False
    assert result["falls_below_threshold"] is False


def test_income_reduction_versus_cutting_spending_changes_runway():
    """Cláusulas: SPEC-032-R03, SPEC-032-R06."""
    without_cut = simulate_stress(
        Decimal("600"),
        Decimal("80"),
        Decimal("100"),
        StressScenario(kind="income_reduction", months=100, reduction_percent=Decimal("50")),
        3,
    )
    with_cut = simulate_stress(
        Decimal("600"),
        Decimal("80"),
        Decimal("100"),
        StressScenario(
            kind="income_reduction",
            months=100,
            reduction_percent=Decimal("50"),
            expense_cut_percent=Decimal("30"),
        ),
        3,
    )
    assert without_cut["months_supported"] == Decimal("10.00")
    assert with_cut["months_supported"] == Decimal("20.00")


def test_emergency_is_one_time_and_unknown_runway_is_not_infinite():
    """Cláusulas: SPEC-032-R03."""
    exhausted = simulate_stress(
        Decimal("600"),
        Decimal("0"),
        Decimal("100"),
        StressScenario(kind="emergency_expense", months=1, emergency_amount=Decimal("500")),
        3,
    )
    assert exhausted["months_supported"] == Decimal("1.00")
    stable = simulate_stress(
        Decimal("600"),
        Decimal("150"),
        Decimal("100"),
        StressScenario(kind="income_loss", months=1),
        3,
    )
    assert stable["months_supported"] is None
    assert stable["horizon_reached"] is True


@pytest.mark.parametrize(
    ("reserve", "income", "expenses", "scenario", "threshold"),
    [
        (Decimal("-1"), Decimal("0"), Decimal("100"), StressScenario("income_loss", 1), 3),
        (Decimal("100"), Decimal("0"), Decimal("0"), StressScenario("income_loss", 1), 3),
        (Decimal("100"), Decimal("0"), Decimal("100"), StressScenario("income_loss", 0), 3),
        (Decimal("100"), Decimal("0"), Decimal("100"), StressScenario("income_loss", 1), 7),
        (
            Decimal("100"),
            Decimal("0"),
            Decimal("100"),
            StressScenario("income_reduction", 1, reduction_percent=Decimal("150")),
            3,
        ),
        (
            Decimal("100"),
            Decimal("0"),
            Decimal("100"),
            StressScenario("emergency_expense", 1, emergency_amount=Decimal("-1")),
            3,
        ),
    ],
)
def test_rejects_invalid_values(reserve, income, expenses, scenario, threshold):
    """Cláusulas: SPEC-032-R02."""
    with pytest.raises(ValueError):
        simulate_stress(reserve, income, expenses, scenario, threshold)


def test_SPEC_032_R05_alert_when_reserve_does_not_cover_configured_months():
    """Reserva 200 e gasto 100: cobre 2 meses, abaixo do mínimo configurado (3 ou 6)."""
    for minimum in (3, 6):
        result = simulate_stress(
            Decimal("200"),
            Decimal("100"),
            Decimal("100"),
            StressScenario(kind="income_loss", months=12),
            minimum,
        )
        assert result["low_reserve"] is True and result["falls_below_threshold"] is True
        assert result["months_supported"] == Decimal("2.00")
    healthy = simulate_stress(
        Decimal("600"),
        Decimal("100"),
        Decimal("100"),
        StressScenario(kind="income_loss", months=12),
        6,
    )
    assert healthy["low_reserve"] is False and healthy["falls_below_threshold"] is False
