"""SPEC-026 reads only dated local PTAX references; requests never call Banco Central."""

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.application.auth import AuthError
from app.infrastructure.models import ExchangeRateRecord

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
# OPEN-23 (2026-10-31): PTAX de venda do último dia útil anterior; na falha da fonte,
# usa a última referência com aviso por até 5 dias úteis (C-08) e recusa acima disso.
MAX_BUSINESS_DAYS = 5
SUPPORTED_CURRENCIES = {"BRL", "USD", "EUR"}
STALE_NOTICE = (
    "Última PTAX disponível no cache local, de {date}; a fonte oficial não foi atualizada "
    "e o valor pode estar desatualizado."
)


def business_days_between(start: date, end: date) -> int:
    """Dias úteis (segunda a sexta) após `start` até `end`, inclusive; feriados contam."""
    if end <= start:
        return 0
    total = 0
    current = start
    while current < end:
        current += timedelta(days=1)
        total += current.weekday() < 5
    return total


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
                "stale": False,
                "notice": None,
            }
        record = self.db.get(ExchangeRateRecord, currency)
        if record is None or record.availability != "available":
            raise AuthError("ptax_unavailable", 503)
        age = business_days_between(record.reference_date, now.astimezone(SAO_PAULO).date())
        if age > MAX_BUSINESS_DAYS:
            raise AuthError("ptax_stale", 503)
        stale = age > 1
        return {
            "currency": record.currency,
            "exchange_rate_to_brl": record.rate_to_brl,
            "reference_date": record.reference_date,
            "referenced_at": record.referenced_at,
            "source": record.source_name,
            "stale": stale,
            "notice": STALE_NOTICE.format(date=record.reference_date.strftime("%d/%m/%Y"))
            if stale
            else None,
        }
