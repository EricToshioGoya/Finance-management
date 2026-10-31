"""C-02: SPEC-007-R03/R04/R06 e SPEC-026-R04 — sincronização com fontes oficiais (ADR-009).

Nenhum teste chama a fonte real (C-17): o transporte é um dublê com respostas no formato
público documentado de cada provedor.
"""

import asyncio
import json
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.application.indicator_sync import (
    ITEMS,
    IndicatorSyncService,
    previous_business_days,
    run_with_retries,
)
from app.infrastructure.models import (
    ExchangeRateRecord,
    MarketIndicatorRecord,
    TreasuryBondRateRecord,
)
from app.infrastructure.official_sources import (
    PTAX_URL,
    SGS_URL,
    TREASURY_URL,
    OfficialSources,
    SourceError,
    https_get,
)
from tests.clause_support import FIN, verified_user

NOW = datetime(2026, 11, 3, 10, 0, tzinfo=UTC)  # terça-feira, 07h em São Paulo

TREASURY_CSV = (
    "Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha;"
    "PU Compra Manha;PU Venda Manha;PU Base Manha\n"
    "Tesouro Selic;01/03/2031;30/10/2026;0,0812;0,0912;17000,10;16990,00;16980,00\n"
    "Tesouro IPCA+;15/05/2035;30/10/2026;7,12;7,24;2500,00;2490,00;2480,00\n"
    "Tesouro Prefixado;01/01/2027;30/10/2026;0,00;14,10;0,00;980,00;975,00\n"
    "Tesouro IPCA+;15/05/2035;29/10/2026;7,05;7,17;2501,00;2491,00;2481,00\n"
).encode("latin-1")


def sgs(value: str, day: str) -> bytes:
    return json.dumps([{"data": day, "valor": value}]).encode()


def ptax(rate: float, when: str) -> bytes:
    rows = [
        {"cotacaoVenda": rate - 0.01, "dataHoraCotacao": when, "tipoBoletim": "Abertura"},
        {"cotacaoVenda": rate, "dataHoraCotacao": when, "tipoBoletim": "Fechamento PTAX"},
    ]
    return json.dumps({"value": rows}).encode()


class FakeTransport:
    """Responde por URL exata; URLs ausentes simulam falha da fonte."""

    def __init__(self, responses: dict[str, bytes]):
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if url not in self.responses:
            raise SourceError("transport_failure")
        return self.responses[url]


def ptax_url(currency: str, day: date) -> str:
    return PTAX_URL.format(currency=currency, day=day.strftime("%m-%d-%Y"))


def full_responses() -> dict[str, bytes]:
    return {
        SGS_URL.format(series=432): sgs("15.00", "03/11/2026"),
        SGS_URL.format(series=4389): sgs("14.90", "31/10/2026"),
        SGS_URL.format(series=13522): sgs("4.85", "01/09/2026"),
        ptax_url("USD", date(2026, 11, 2)): ptax(5.4321, "2026-11-02 13:08:21.000"),
        ptax_url("EUR", date(2026, 11, 2)): ptax(6.1234, "2026-11-02 13:08:21.000"),
        TREASURY_URL: TREASURY_CSV,
    }


def service(app, transport):
    db = app.state.sessions()
    return db, IndicatorSyncService(db, lambda: NOW, OfficialSources(transport))


def test_SPEC_007_R03_sgs_series_432_4389_13522_fill_local_cache(app):
    db, sync = service(app, FakeTransport(full_responses()))
    with db:
        result = sync.run(("selic", "cdi", "ipca"))
        assert result == {"selic": "updated", "cdi": "updated", "ipca": "updated"}
        selic = db.get(MarketIndicatorRecord, "selic")
        assert selic.value == Decimal("15.000000") and selic.source == "BCB_SGS"
        assert selic.reference_date == date(2026, 11, 3) and selic.unit == "percentual_anual"
        assert db.get(MarketIndicatorRecord, "ipca").reference_date == date(2026, 9, 1)


def test_SPEC_007_R04_treasury_buy_rates_from_latest_base_date(app, client):
    db, sync = service(app, FakeTransport(full_responses()))
    with db:
        assert sync.run(("tesouro",)) == {"tesouro": "updated"}
        rows = db.query(TreasuryBondRateRecord).all()
    # Data-base mais recente apenas; taxa zero (fora de venda) nunca é publicada.
    assert {(r.bond_type, r.buy_rate) for r in rows} == {
        ("Tesouro Selic", Decimal("0.0812")),
        ("Tesouro IPCA+", Decimal("7.1200")),
    }
    headers = verified_user(client, app)
    app.state.clock = lambda: NOW
    response = client.get(f"{FIN}/treasury-bonds", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert [item["bond_type"] for item in data] == ["Tesouro IPCA+", "Tesouro Selic"]
    assert data[0]["reference_date"] == "2026-10-30" and data[0]["stale"] is False


def test_SPEC_007_R05_cache_keeps_reference_and_last_check(app):
    db, sync = service(app, FakeTransport(full_responses()))
    with db:
        sync.run(("cdi",))
        record = db.get(MarketIndicatorRecord, "cdi")
        assert record.checked_at == NOW and record.reference_date == date(2026, 10, 31)


def test_SPEC_007_R06_older_reference_never_replaces_cache(app):
    responses = full_responses()
    db, sync = service(app, FakeTransport(responses))
    with db:
        sync.run(("selic",))
        responses[SGS_URL.format(series=432)] = sgs("9.00", "01/01/2026")
        assert sync.run(("selic",)) == {"selic": "kept"}
        assert db.get(MarketIndicatorRecord, "selic").value == Decimal("15.000000")


def test_SPEC_007_R06_source_failure_keeps_last_value(app):
    responses = full_responses()
    db, sync = service(app, FakeTransport(responses))
    with db:
        sync.run(("selic", "tesouro"))
        responses.clear()
        assert sync.run(("selic", "tesouro")) == {"selic": "failed", "tesouro": "failed"}
        assert db.get(MarketIndicatorRecord, "selic").value == Decimal("15.000000")
        assert db.query(TreasuryBondRateRecord).count() == 2


def test_SPEC_007_R06_unexpected_format_is_a_failure_not_zero(app):
    responses = full_responses()
    responses[SGS_URL.format(series=432)] = b'{"erro": "manutencao"}'
    db, sync = service(app, FakeTransport(responses))
    with db:
        assert sync.run(("selic",)) == {"selic": "failed"}
        assert db.get(MarketIndicatorRecord, "selic") is None


def test_SPEC_007_R06_failed_items_retry_after_5_15_45_minutes():
    attempts: list[tuple[str, ...]] = []
    waits: list[float] = []

    async def run_once(items):
        attempts.append(items)
        return {
            item: "failed" if item == "cdi" and len(attempts) < 3 else "updated" for item in items
        }

    async def sleep(seconds):
        waits.append(seconds)

    result = asyncio.run(run_with_retries(run_once, sleep))
    assert attempts[0] == ITEMS and attempts[1:] == [("cdi",), ("cdi",)]
    assert waits == [300, 900] and result["cdi"] == "updated"


def test_SPEC_007_R06_retries_stop_after_three_attempts():
    waits: list[float] = []

    async def run_once(items):
        return {item: "failed" for item in items}

    async def sleep(seconds):
        waits.append(seconds)

    result = asyncio.run(run_with_retries(run_once, sleep))
    assert waits == [300, 900, 2700] and set(result.values()) == {"failed"}


def test_SPEC_026_R04_ptax_sell_closing_of_previous_business_day(app):
    db, sync = service(app, FakeTransport(full_responses()))
    with db:
        assert sync.run(("ptax_usd", "ptax_eur")) == {"ptax_usd": "updated", "ptax_eur": "updated"}
        usd = db.get(ExchangeRateRecord, "USD")
        assert usd.rate_to_brl == Decimal("5.432100")
        assert usd.reference_date == date(2026, 11, 2) and usd.source_name.startswith("PTAX venda")


def test_SPEC_026_R04_ptax_holiday_falls_back_to_earlier_business_day(app):
    responses = full_responses()
    responses[ptax_url("USD", date(2026, 11, 2))] = json.dumps({"value": []}).encode()
    responses[ptax_url("USD", date(2026, 10, 30))] = ptax(5.40, "2026-10-30 13:10:00.000")
    db, sync = service(app, FakeTransport(responses))
    with db:
        assert sync.run(("ptax_usd",)) == {"ptax_usd": "updated"}
        assert db.get(ExchangeRateRecord, "USD").reference_date == date(2026, 10, 30)


def test_previous_business_days_skip_weekend():
    assert previous_business_days(date(2026, 11, 2), 2) == [date(2026, 10, 30), date(2026, 10, 29)]


@pytest.mark.parametrize(
    "url",
    ["http://api.bcb.gov.br/dados", "https://example.com/dados", "file:///etc/passwd"],
)
def test_https_get_only_reaches_allowed_official_hosts(url):
    with pytest.raises(SourceError, match="host_not_allowed"):
        https_get(url)
