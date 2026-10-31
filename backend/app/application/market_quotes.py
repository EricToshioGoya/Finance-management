"""SPEC-023 local market-reference queries; no live provider is called by requests."""

import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.auth import AuthError
from app.domain.market_metrics import MetricInputError, calculate_historical_metrics
from app.infrastructure.models import MarketQuoteHistoryRecord, MarketQuoteRecord

MAX_REFERENCE_AGE = timedelta(hours=24)
TICKER_PATTERN = re.compile(r"^[A-Z]{4,5}[0-9]{1,2}$")


class MarketQuoteService:
    def __init__(self, db: Session, clock: Callable[[], datetime] | None = None):
        self.db = db
        self.clock = clock or (lambda: datetime.now(UTC))

    @staticmethod
    def normalized_ticker(value: str) -> str:
        ticker = value.strip().upper()
        if not TICKER_PATTERN.fullmatch(ticker):
            raise AuthError("invalid_market_ticker", 422)
        return ticker

    def metrics(self, requested_ticker: str, annual_selic_percent: Decimal) -> dict[str, object]:
        quote = self.quote(requested_ticker)
        observations = [(row["quoted_on"], row["close_price"]) for row in quote["history"]]
        try:
            metrics = calculate_historical_metrics(observations, annual_selic_percent)
        except MetricInputError as error:
            raise AuthError(str(error), 422) from error
        return {"ticker": quote["ticker"], **metrics}

    def quote(self, requested_ticker: str) -> dict[str, object]:
        ticker = self.normalized_ticker(requested_ticker)
        record = self.db.get(MarketQuoteRecord, ticker)
        if record is None:
            raise AuthError("market_ticker_not_found", 404)
        if record.availability != "available":
            raise AuthError("market_reference_unavailable", 503, manual_entry_permitted=True)
        now = self.clock().astimezone(UTC)
        fresh_until = record.referenced_at + MAX_REFERENCE_AGE
        if now > fresh_until:
            raise AuthError("market_reference_stale", 503, manual_entry_permitted=True)
        history = self.db.scalars(
            select(MarketQuoteHistoryRecord)
            .where(MarketQuoteHistoryRecord.ticker == ticker)
            .order_by(MarketQuoteHistoryRecord.quoted_on)
        )
        variation = (record.price - record.previous_close) / record.previous_close * Decimal("100")
        return {
            "ticker": record.ticker,
            "asset_kind": record.asset_kind,
            "price": record.price,
            "daily_change_percent": variation.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            "referenced_at": record.referenced_at,
            "fresh_until": fresh_until,
            "source_name": record.source_name,
            "catalogue_type": "local_reference",
            "history": [
                {"quoted_on": row.quoted_on, "close_price": row.close_price} for row in history
            ],
        }
