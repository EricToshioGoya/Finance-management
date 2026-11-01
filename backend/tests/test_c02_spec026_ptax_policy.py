"""SPEC-026-R04 e política OPEN-23: PTAX D-1 útil, aviso e limite de 5 dias úteis."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.application.exchange_rates import business_days_between
from app.infrastructure.models import ExchangeRateRecord
from tests.clause_support import FIN, verified_user

BODY = {
    "label": "Carteira USD",
    "currency": "USD",
    "initial_amount": "100",
    "monthly_contribution": "0",
    "asset_annual_return": "0",
    "expected_exchange_annual_change": "0",
    "term_months": 12,
}


def seed(app, reference: date):
    with app.state.sessions() as db:
        db.merge(
            ExchangeRateRecord(
                currency="USD",
                rate_to_brl=Decimal("5"),
                reference_date=reference,
                referenced_at=datetime.combine(reference, datetime.min.time(), tzinfo=UTC),
                source_name="PTAX venda BCB (dublê)",
                availability="available",
            )
        )
        db.commit()


def simulate(client, app, headers, now: datetime):
    app.state.clock = lambda: now
    return client.post(f"{FIN}/simulations/foreign-currency", headers=headers, json=BODY)


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (date(2026, 10, 30), date(2026, 11, 2), 1),  # sexta → segunda
        (date(2026, 10, 30), date(2026, 10, 31), 0),  # sexta → sábado
        (date(2026, 10, 26), date(2026, 11, 2), 5),
        (date(2026, 11, 2), date(2026, 10, 30), 0),
    ],
)
def test_SPEC_026_R04_business_days_skip_weekends(start, end, expected):
    assert business_days_between(start, end) == expected


def test_SPEC_026_R04_previous_business_day_ptax_is_current(client, app):
    headers = verified_user(client, app)
    seed(app, date(2026, 10, 30))  # sexta-feira
    monday = datetime(2026, 11, 2, 13, 0, tzinfo=UTC)  # 10h em São Paulo
    data = simulate(client, app, headers, monday).json()["payload"]["foreign_currency"]
    assert data["stale"] is False and data["notice"] is None
    assert data["final_amount_brl"] == "500.000000"


def test_SPEC_026_R04_source_failure_uses_last_ptax_with_notice(client, app):
    headers = verified_user(client, app)
    seed(app, date(2026, 10, 27))
    friday = datetime(2026, 10, 30, 13, 0, tzinfo=UTC)
    data = simulate(client, app, headers, friday).json()["payload"]["foreign_currency"]
    assert data["stale"] is True and "27/10/2026" in data["notice"]
    assert Decimal(data["exchange_rate_to_brl"]) == Decimal("5")


def test_SPEC_026_R02_ptax_older_than_five_business_days_is_refused(client, app):
    headers = verified_user(client, app)
    seed(app, date(2026, 10, 23))
    six_days = datetime(2026, 11, 2, 13, 0, tzinfo=UTC)
    response = simulate(client, app, headers, six_days)
    assert response.status_code == 503 and response.json()["detail"] == "ptax_stale"
    five_days = datetime(2026, 10, 30, 13, 0, tzinfo=UTC)
    assert simulate(client, app, headers, five_days).status_code == 201


def test_SPEC_026_R03_R05_R06_R07_asset_return_and_exchange_change_are_separate(client, app):
    headers = verified_user(client, app)
    seed(app, date(2026, 10, 30))
    app.state.clock = lambda: datetime(2026, 11, 2, 13, 0, tzinfo=UTC)
    body = {**BODY, "asset_annual_return": "12", "expected_exchange_annual_change": "10"}
    response = client.post(f"{FIN}/simulations/foreign-currency", headers=headers, json=body)
    assert response.status_code == 201, response.text
    data = response.json()["payload"]["foreign_currency"]
    # R05: rentabilidade do ativo (12% a.a.) e câmbio esperado (10% a.a.) compõem-se à parte.
    assert Decimal(data["final_amount_original"]).quantize(Decimal("0.01")) == Decimal("112.00")
    assert Decimal(data["projected_exchange_rate_to_brl"]).quantize(Decimal("0.0001")) == Decimal(
        "5.5000"
    )
    # R03/R07: resultado na moeda original e convertido para BRL pela PTAX oficial.
    assert Decimal(data["final_amount_brl"]).quantize(Decimal("0.01")) == Decimal("616.00")
    assert data["currency"] == "USD" and data["source"].startswith("PTAX venda")
    # R06: variação cambial explicitada como risco distinto da rentabilidade do ativo.
    assert "variação cambial" in data["risk_notice"] and "distinta" in data["risk_notice"]
