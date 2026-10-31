"""SPEC-037: pure comparison of Price financing versus investing its payment."""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.financing import simulate_financing
from app.domain.juros_compostos import (
    ErroCalculo,
    MotorJurosCompostos,
    arredondar_moeda,
)


@dataclass(frozen=True, slots=True)
class FinancingComparison:
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
    lower_nominal_cost: str
    assumptions: tuple[str, ...]


def compare_financing_and_investing(
    *,
    asset_value: Decimal,
    down_payment: Decimal,
    installments: int,
    financing_annual_rate: Decimal,
    investment_annual_rate: Decimal,
    horizon_months: int,
) -> FinancingComparison:
    """Invest the same down payment and monthly Price installment.

    The first month to reach the fixed cash price is searched within the
    specified horizon. Contributions occur at month end, as in SPEC-002.
    The comparison of nominal prices is only reported if possession is possible.
    """
    if not isinstance(investment_annual_rate, Decimal) or not investment_annual_rate.is_finite():
        raise ErroCalculo("investment_annual_rate", "taxa_invalida")
    if investment_annual_rate < 0 or investment_annual_rate > 100:
        raise ErroCalculo("investment_annual_rate", "taxa_nao_suportada")
    if type(horizon_months) is not int or not 1 <= horizon_months <= 600:
        raise ErroCalculo("horizon_months", "prazo_invalido")

    financing = simulate_financing(asset_value, down_payment, installments, financing_annual_rate)
    projection = MotorJurosCompostos.calcular(
        valor_inicial=down_payment,
        aporte_mensal=financing.installment_amount,
        taxa_percentual=investment_annual_rate,
        periodicidade_taxa="anual",
        prazo=horizon_months,
        unidade_prazo="meses",
    )
    possession = 0 if down_payment >= asset_value else None
    balance_at_possession = down_payment if possession == 0 else None
    for month in projection.serie:
        if possession is None and month.saldo_final >= asset_value:
            possession = month.mes
            balance_at_possession = month.saldo_final
    cost_to_possession = (
        down_payment + financing.installment_amount * possession if possession is not None else None
    )
    difference = financing.total_paid - asset_value if possession is not None else None
    if difference is None:
        cheaper = "not_comparable"
    elif difference > 0:
        cheaper = "invest_then_buy"
    elif difference < 0:
        cheaper = "finance_now"
    else:
        cheaper = "tie"
    return FinancingComparison(
        asset_value=financing.asset_value,
        down_payment=financing.down_payment,
        financing_months=installments,
        comparison_horizon_months=horizon_months,
        financing_annual_rate=financing_annual_rate,
        investment_annual_rate=investment_annual_rate,
        monthly_investment=financing.installment_amount,
        financing_total_paid=financing.total_paid,
        financing_total_interest=financing.total_interest,
        financing_possession_month=0,
        invest_possession_month=possession,
        invested_by_horizon=arredondar_moeda(
            down_payment + financing.installment_amount * horizon_months
        ),
        investment_balance_at_horizon=arredondar_moeda(projection.montante),
        invest_cost_to_possession=(
            arredondar_moeda(cost_to_possession) if cost_to_possession is not None else None
        ),
        invest_balance_at_possession=(
            arredondar_moeda(balance_at_possession) if balance_at_possession is not None else None
        ),
        nominal_purchase_price=financing.asset_value,
        nominal_cost_difference=(arredondar_moeda(difference) if difference is not None else None),
        lower_nominal_cost=cheaper,
        assumptions=(
            "fixed_nominal_asset_price",
            "price_amortization_no_fees",
            "effective_annual_rates",
            "investment_contributions_at_month_end",
            "invested_down_payment_not_spent",
            "no_investment_taxes_fees_or_risk",
            "comparison_of_nominal_cash_outlays_not_risk_adjusted_wealth",
            "possession_now_vs_after_target",
        ),
    )
