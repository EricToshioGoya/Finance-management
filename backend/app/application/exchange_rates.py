"""SPEC-026 reads only dated local PTAX references; requests never call Banco Central."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.application.auth import AuthError
from app.infrastructure.models import ExchangeRateRecord

MAX_REFERENCE_AGE = timedelta(hours=24)
SUPPORTED_CURRENCIES = {"BRL", "USD", "EUR"}


class ExchangeRateService:
    def __init__(self, db: Session, clock: Callable[[], datetime]):
        self.db = db
        self.clock = clock

    def rate(self, currency: str) -> dict[str, object]:
        if currency not in SUPPORTED_CURRENCIES:
            raise AuthError("unsupported_currency", 422)
        now = self.clock().astimezone(UTC)
        if currency == "BRL":
            return {
                "currency": "BRL",
                "exchange_rate_to_brl": 1,
                "reference_date": now.date(),
                "referenced_at": now,
                "source": "Paridade BRL",
            }
        record = self.db.get(ExchangeRateRecord, currency)
        if record is None or record.availability != "available":
            raise AuthError("ptax_unavailable", 503)
        if now > record.referenced_at + MAX_REFERENCE_AGE:
            raise AuthError("ptax_stale", 503)
        return {
            "currency": record.currency,
            "exchange_rate_to_brl": record.rate_to_brl,
            "reference_date": record.reference_date,
            "referenced_at": record.referenced_at,
            "source": record.source_name,
        }
