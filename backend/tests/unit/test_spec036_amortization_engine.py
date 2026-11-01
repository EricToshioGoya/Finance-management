"""SPEC-036: pure amortization semantics and safe financial boundaries."""

from decimal import Decimal

import pytest

from app.domain.financing import simulate_financing
from app.domain.juros_compostos import ErroCalculo


def test_zero_rate_120_brl_twelve_installments_exact():
    """Cláusulas: SPEC-036-R04, SPEC-036-R05."""
    plan = simulate_financing(Decimal("120"), Decimal("0"), 12, Decimal("0"))
    assert plan.financed_amount == Decimal("120.00")
    assert plan.total_paid == Decimal("120.00")
    assert plan.total_interest == Decimal("0.00")
    assert plan.installment_amount == Decimal("10.00")
    assert len(plan.schedule) == 12
    assert all(item.payment == Decimal("10.00") for item in plan.schedule)
    assert plan.schedule[-1].remaining_balance == Decimal("0.00")


def test_price_and_down_payment_keep_totals_consistent():
    """Cláusulas: SPEC-036-R03, SPEC-036-R04."""
    plan = simulate_financing(Decimal("1000"), Decimal("200"), 12, Decimal("12"))
    assert plan.financed_amount == Decimal("800.00")
    assert plan.total_paid > Decimal("1000")
    assert plan.total_interest > 0
    assert plan.schedule[0].interest > 0
    assert plan.schedule[-1].remaining_balance == 0
    assert plan.schedule[0].remaining_balance > plan.schedule[-1].remaining_balance
    assert plan.total_paid == plan.down_payment + plan.total_installments
    displayed_interest = sum((row.interest for row in plan.schedule), Decimal(0))
    assert abs(displayed_interest - plan.total_interest) <= Decimal("0.06")


def test_down_payment_can_cover_full_price_without_debt():
    plan = simulate_financing(Decimal("120"), Decimal("120"), 12, Decimal("20"))
    assert plan.financed_amount == 0
    assert plan.total_paid == Decimal("120.00")
    assert all(row.payment == 0 and row.remaining_balance == 0 for row in plan.schedule)


@pytest.mark.parametrize(
    ("asset", "down", "months", "rate"),
    [
        ("120", "121", 12, "0"),
        ("120", "0", 0, "0"),
        ("120", "0", 601, "0"),
        ("120", "0", 12, "-1"),
        ("120", "0", 12, "101"),
        ("0", "0", 12, "0"),
        ("NaN", "0", 12, "0"),
    ],
)
def test_invalid_financing_is_rejected(asset, down, months, rate):
    """Cláusulas: SPEC-036-R02."""
    with pytest.raises(ErroCalculo):
        simulate_financing(Decimal(asset), Decimal(down), months, Decimal(rate))
