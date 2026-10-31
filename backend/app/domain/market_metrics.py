"""Deterministic historical-risk metrics for SPEC-025; no market I/O lives here."""

from collections.abc import Sequence
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, localcontext

TRADING_DAYS_PER_YEAR = Decimal("252")
DISPLAY_SCALE = Decimal("0.0001")


class MetricInputError(ValueError):
    pass


def _display(value: Decimal) -> Decimal:
    return value.quantize(DISPLAY_SCALE, rounding=ROUND_HALF_UP)


def calculate_historical_metrics(
    observations: Sequence[tuple[date, Decimal]], annual_selic_percent: Decimal
) -> dict[str, object]:
    if len(observations) < 3:
        raise MetricInputError("market_history_insufficient")
    previous_date, previous_price = observations[0]
    if previous_price <= 0:
        raise MetricInputError("market_history_invalid")
    returns: list[Decimal] = []
    for quoted_on, close_price in observations[1:]:
        if close_price <= 0 or (quoted_on - previous_date).days > 3:
            raise MetricInputError("market_history_incompatible")
        returns.append(close_price / previous_price - Decimal("1"))
        previous_date, previous_price = quoted_on, close_price
    mean_return = sum(returns, Decimal("0")) / Decimal(len(returns))
    variance = sum((value - mean_return) ** 2 for value in returns) / Decimal(len(returns) - 1)
    with localcontext() as context:
        context.prec = 50
        daily_volatility = variance.sqrt()
        annual_factor = TRADING_DAYS_PER_YEAR.sqrt()
        daily_selic = (Decimal("1") + annual_selic_percent / Decimal("100")) ** (
            Decimal("1") / TRADING_DAYS_PER_YEAR
        ) - Decimal("1")
        annualized_volatility = daily_volatility * annual_factor
        if daily_volatility == 0:
            sharpe = None
            status = "zero_volatility"
        else:
            sharpe = (mean_return - daily_selic) / daily_volatility * annual_factor
            status = "available"
    return {
        "period_start": observations[0][0],
        "period_end": observations[-1][0],
        "observations": len(observations),
        "volatility_annualized": _display(annualized_volatility),
        "sharpe": _display(sharpe) if sharpe is not None else None,
        "status": status,
        "disclaimer": "Métricas históricas não garantem comportamento ou retorno futuro.",
        "rule_version": "spec-025-local-v1",
    }
