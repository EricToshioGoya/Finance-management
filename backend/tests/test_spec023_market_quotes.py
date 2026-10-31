"""SPEC-023: local references expose historical data and never masquerade as live quotes."""

from datetime import UTC, datetime, timedelta

PREFIX = "/api/v1/market/quotes"
PASSWORD = "StrongPassword123"


def login(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Market Reader", "email": "market@example.com", "password": PASSWORD},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "market@example.com", "password": PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_spec023_returns_dated_local_stock_and_fii_history(client, app):
    headers = login(client)
    app.state.clock = lambda: datetime(2026, 10, 29, 13, tzinfo=UTC)
    petr4 = client.get(f"{PREFIX}/petr4", headers=headers)
    mxrf11 = client.get(f"{PREFIX}/MXRF11", headers=headers)
    assert petr4.status_code == mxrf11.status_code == 200
    payload = petr4.json()
    assert payload["ticker"] == "PETR4"
    assert payload["asset_kind"] == "stock"
    assert payload["catalogue_type"] == "local_reference"
    assert payload["price"] == "31.2500"
    assert payload["daily_change_percent"] == "1.4610"
    assert len(payload["history"]) == 4
    assert payload["history"][-1] == {"quoted_on": "2026-10-29", "close_price": "31.2500"}
    assert mxrf11.json()["asset_kind"] == "fii"


def test_spec023_requires_authenticated_valid_ticker_and_identifies_unknown(client):
    assert client.get(f"{PREFIX}/PETR4").status_code == 401
    headers = login(client)
    assert client.get(f"{PREFIX}/PETR", headers=headers).json()["detail"] == "invalid_market_ticker"
    unknown = client.get(f"{PREFIX}/ABCD11", headers=headers)
    assert unknown.status_code == 404
    assert unknown.json()["detail"] == "market_ticker_not_found"


def test_spec023_stale_or_unavailable_reference_permits_explicit_manual_entry(client, app):
    headers = login(client)
    app.state.clock = lambda: datetime(2026, 10, 30, 12, 0, 1, tzinfo=UTC)
    stale = client.get(f"{PREFIX}/PETR4", headers=headers)
    assert stale.status_code == 503
    assert stale.json() == {"detail": "market_reference_stale", "manual_entry_permitted": True}
    app.state.clock = lambda: datetime(2026, 10, 29, 12, 0, tzinfo=UTC) + timedelta(hours=1)
    unavailable = client.get(f"{PREFIX}/FAIL11", headers=headers)
    assert unavailable.status_code == 503
    assert unavailable.json() == {
        "detail": "market_reference_unavailable",
        "manual_entry_permitted": True,
    }
