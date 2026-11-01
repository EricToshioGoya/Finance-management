"""SPEC-037: deterministic cost and possession comparison of two alternatives."""

from decimal import Decimal

import pytest

from app.domain.financing_comparison import compare_financing_and_investing
from app.domain.juros_compostos import ErroCalculo


def compare(**overrides):
    params = {
        "asset_value": Decimal("120"),
        "down_payment": Decimal("0"),
        "installments": 12,
        "financing_annual_rate": Decimal("0"),
        "investment_annual_rate": Decimal("0"),
        "horizon_months": 12,
    }
    return compare_financing_and_investing(**(params | overrides))


def test_zero_rates_and_fixed_price_have_no_fictitious_return():
    """Cláusulas: SPEC-037-R03, SPEC-037-R04."""
    result = compare()
    assert result.monthly_investment == Decimal("10.00")
    assert result.financing_possession_month == 0
    assert result.invest_possession_month == 12
    assert result.financing_total_paid == Decimal("120.00")
    assert result.investment_balance_at_horizon == Decimal("120.00")
    assert result.invested_by_horizon == Decimal("120.00")
    assert result.invest_cost_to_possession == Decimal("120.00")
    assert result.nominal_cost_difference == Decimal("0.00")
    assert result.lower_nominal_cost == "tie"


def test_not_reaching_target_is_not_reported_as_purchase_or_winner():
    """Cláusulas: SPEC-037-R05."""
    result = compare(horizon_months=11)
    assert result.invest_possession_month is None
    assert result.invest_cost_to_possession is None
    assert result.invest_balance_at_possession is None
    assert result.nominal_cost_difference is None
    assert result.lower_nominal_cost == "not_comparable"
    assert result.investment_balance_at_horizon == Decimal("110.00")


def test_interest_on_financing_and_investment_changes_observable_results():
    """Cláusulas: SPEC-037-R03, SPEC-037-R04, SPEC-037-R05."""
    result = compare(
        asset_value=Decimal("1000"),
        down_payment=Decimal("200"),
        financing_annual_rate=Decimal("12"),
        investment_annual_rate=Decimal("8"),
        horizon_months=24,
    )
    assert result.financing_total_paid > Decimal("1000")
    assert result.investment_balance_at_horizon > result.invested_by_horizon
    assert result.invest_possession_month is not None
    assert result.invest_possession_month > 0
    assert result.lower_nominal_cost == "invest_then_buy"
    assert result.nominal_cost_difference == result.financing_total_paid - Decimal("1000")


def test_full_down_payment_means_immediate_cash_possession():
    result = compare(down_payment=Decimal("120"))
    assert result.invest_possession_month == 0
    assert result.invest_cost_to_possession == Decimal("120.00")
    assert result.financing_total_paid == Decimal("120.00")


@pytest.mark.parametrize(
    "changes",
    [
        {"down_payment": Decimal("121")},
        {"installments": 0},
        {"financing_annual_rate": Decimal("-1")},
        {"investment_annual_rate": Decimal("-1")},
        {"investment_annual_rate": Decimal("101")},
        {"horizon_months": 0},
        {"horizon_months": 601},
        {"investment_annual_rate": Decimal("NaN")},
    ],
)
def test_invalid_input_cannot_produce_comparison(changes):
    """Cláusulas: SPEC-037-R02."""
    with pytest.raises(ErroCalculo):
        compare(**changes)
