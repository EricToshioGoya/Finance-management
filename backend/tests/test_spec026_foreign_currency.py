"""SPEC-026: projections use dated local PTAX and separate asset/currency hypotheses."""

from datetime import UTC, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.infrastructure.models import ExchangeRateRecord, UserRecord

PASSWORD = "StrongPassword123"
PREFIX = "/api/v1/auth/financial/simulations/foreign-currency"


def confirmed_headers(client, email):
    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Cambio", "email": email, "password": PASSWORD},
    )
    assert registered.status_code == 201
    with client.app.state.sessions() as db:
        user = db.get(UserRecord, registered.json()["id"])
        assert user is not None
        user.email_verified_at = datetime.now(UTC)
        db.commit()
    token = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {token.json()['access_token']}"}


def seed_usd(app):
    now = datetime.now(UTC)
    with app.state.sessions() as db:
        db.merge(
            ExchangeRateRecord(
                currency="USD",
                rate_to_brl=Decimal("5"),
                reference_date=now.astimezone(ZoneInfo("America/Sao_Paulo")).date(),
                referenced_at=now,
                source_name="PTAX venda BCB (fixture)",
                availability="available",
            )
        )
        db.commit()


def payload(currency="USD"):
    return {
        "label": f"Carteira {currency}",
        "currency": currency,
        "initial_amount": "100",
        "monthly_contribution": "0",
        "asset_annual_return": "0",
        "expected_exchange_annual_change": "0",
        "term_months": 12,
    }


def test_spec026_projects_usd_in_original_and_brl_with_dated_ptax(client, app):
    headers = confirmed_headers(client, "usd@example.com")
    seed_usd(app)
    response = client.post(PREFIX, headers=headers, json=payload())
    assert response.status_code == 201
    foreign = response.json()["foreign_currency"]
    assert foreign["final_amount_original"] == "100"
    assert foreign["final_amount_brl"] == "500.000000"
    assert foreign["currency"] == "USD"
    assert foreign["exchange_rate_to_brl"] == "5.000000"
    assert "cambial" in foreign["risk_notice"]


def test_spec026_accepts_brl_parity_and_rejects_missing_or_invalid_ptax(client, app):
    headers = confirmed_headers(client, "brl@example.com")
    brl = client.post(PREFIX, headers=headers, json=payload("BRL"))
    assert brl.status_code == 201
    assert brl.json()["foreign_currency"]["final_amount_brl"] == "100"
    assert client.post(PREFIX, headers=headers, json=payload("EUR")).status_code == 503
    invalid = payload("GBP")
    assert client.post(PREFIX, headers=headers, json=invalid).status_code == 422
