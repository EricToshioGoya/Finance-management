"""Sincronização diária das fontes oficiais (SPEC-007-R03/R04/R06, SPEC-026-R04; ADR-009).

Regras (OPEN-04/10/23, aprovadas em 2026-10-31):
- cada item é independente: a falha de um não impede os demais;
- o cache só é substituído por referência igual ou mais recente;
- na falha da fonte, o último valor permanece (C-08) e o item é repetido após 5, 15 e 45 min.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infrastructure.models import (
    ExchangeRateRecord,
    MarketIndicatorRecord,
    TreasuryBondRateRecord,
)
from app.infrastructure.official_sources import OfficialSources, SourceError

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
INDICATORS = ("selic", "cdi", "ipca")
CURRENCIES = ("USD", "EUR")
ITEMS = (*INDICATORS, "ptax_usd", "ptax_eur", "tesouro")
RETRY_DELAYS = (timedelta(minutes=5), timedelta(minutes=15), timedelta(minutes=45))
PTAX_LOOKBACK_BUSINESS_DAYS = 5
PTAX_SOURCE = "PTAX venda BCB (Olinda)"

logger = logging.getLogger("finnova.indicator_sync")


def previous_business_days(today: date, count: int) -> list[date]:
    """Dias úteis (segunda a sexta) anteriores a `today`, do mais recente ao mais antigo."""
    days: list[date] = []
    current = today
    while len(days) < count:
        current -= timedelta(days=1)
        if current.weekday() < 5:
            days.append(current)
    return days


class IndicatorSyncService:
    def __init__(self, db: Session, clock: Callable[[], datetime], sources: OfficialSources):
        self.db = db
        self.clock = clock
        self.sources = sources

    def sync_indicator(self, code: str) -> str:
        observation = self.sources.sgs_latest(code)
        record = self.db.get(MarketIndicatorRecord, code)
        if record is not None and observation.reference_date < record.reference_date:
            return "kept"
        if record is None:
            record = MarketIndicatorRecord(code=code)
            self.db.add(record)
        record.value = observation.value
        record.unit = "percentual_anual"
        record.reference_date = observation.reference_date
        record.checked_at = self.clock()
        record.source = "BCB_SGS"
        self.db.commit()
        return "updated"

    def sync_ptax(self, currency: str) -> str:
        today = self.clock().astimezone(SAO_PAULO).date()
        for day in previous_business_days(today, PTAX_LOOKBACK_BUSINESS_DAYS):
            quote = self.sources.ptax_sell(currency, day)
            if quote is None:
                continue  # feriado ou boletim ainda não publicado
            record = self.db.get(ExchangeRateRecord, currency)
            if record is not None and quote.reference_date < record.reference_date:
                return "kept"
            if record is None:
                record = ExchangeRateRecord(currency=currency)
                self.db.add(record)
            record.rate_to_brl = quote.sell_rate
            record.reference_date = quote.reference_date
            record.referenced_at = quote.quoted_at
            record.source_name = PTAX_SOURCE
            record.availability = "available"
            self.db.commit()
            return "updated"
        raise SourceError("ptax_not_published")

    def sync_treasury(self) -> str:
        rates = self.sources.treasury_rates()
        if not rates:
            raise SourceError("empty_source")
        reference = rates[0].reference_date
        current = self.db.scalar(select(func.max(TreasuryBondRateRecord.reference_date)))
        if current is not None and reference < current:
            return "kept"
        now = self.clock()
        self.db.execute(delete(TreasuryBondRateRecord))
        self.db.add_all(
            TreasuryBondRateRecord(
                bond_type=rate.bond_type,
                maturity=rate.maturity,
                buy_rate=rate.buy_rate,
                reference_date=rate.reference_date,
                checked_at=now,
                source="Tesouro Transparente",
            )
            for rate in rates
        )
        self.db.commit()
        return "updated"

    def sync_item(self, item: str) -> str:
        try:
            if item in INDICATORS:
                return self.sync_indicator(item)
            if item.startswith("ptax_"):
                return self.sync_ptax(item.removeprefix("ptax_").upper())
            return self.sync_treasury()
        except (SourceError, SQLAlchemyError) as exc:
            self.db.rollback()
            logger.warning("indicator_sync_failed item=%s reason=%s", item, exc)
            return "failed"

    def run(self, items: tuple[str, ...] = ITEMS) -> dict[str, str]:
        result = {item: self.sync_item(item) for item in items}
        logger.info("indicator_sync_run %s", result)
        return result


async def run_with_retries(
    run_once: Callable[[tuple[str, ...]], Awaitable[dict[str, str]]],
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> dict[str, str]:
    """Executa todos os itens e repete apenas os que falharam (OPEN-04: 5, 15 e 45 min)."""
    result = await run_once(ITEMS)
    for delay in RETRY_DELAYS:
        failed = tuple(item for item, status in result.items() if status == "failed")
        if not failed:
            break
        await sleep(delay.total_seconds())
        result.update(await run_once(failed))
    return result
