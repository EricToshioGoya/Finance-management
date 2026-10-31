"""Pure foreign-currency projection rules for SPEC-026."""

from decimal import Decimal, localcontext

from app.domain.financeiro import projetar
from app.domain.juros_compostos import ErroCalculo

RULE_VERSION = "spec-026-ptax-cache-v1"


def calcular_projecao_moeda_estrangeira(
    *,
    initial_amount: Decimal,
    monthly_contribution: Decimal,
    asset_annual_return: Decimal,
    expected_exchange_annual_change: Decimal,
    term_months: int,
    exchange_rate_to_brl: Decimal,
) -> dict[str, Decimal | int | str]:
    """Project asset and currency components independently, without financial operations."""
    if (
        initial_amount < 0
        or monthly_contribution < 0
        or term_months <= 0
        or exchange_rate_to_brl <= 0
        or expected_exchange_annual_change <= Decimal("-100")
    ):
        raise ErroCalculo("foreign_currency", "entrada_invalida")
    original = projetar(
        inicial=initial_amount,
        aporte=monthly_contribution,
        taxa=asset_annual_return,
        prazo=term_months,
    ).montante
    with localcontext() as context:
        context.prec = 50
        projected_rate = exchange_rate_to_brl * (
            Decimal("1") + expected_exchange_annual_change / Decimal("100")
        ) ** (Decimal(term_months) / Decimal("12"))
        return {
            "final_amount_original": original,
            "exchange_rate_to_brl": exchange_rate_to_brl,
            "projected_exchange_rate_to_brl": projected_rate,
            "final_amount_brl": original * projected_rate,
            "rule_version": RULE_VERSION,
        }
