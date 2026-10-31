"""SPEC-025: historical volatility and Sharpe are private, dated and never predictive."""

from datetime import UTC, date, datetime
from decimal import Decimal

from app.domain.market_metrics import calculate_historical_metrics
from app.infrastructure.models import MarketIndicatorRecord, UserRecord

PASSWORD = "StrongPassword123"
MARKET = "/api/v1/market/quotes/PETR4/metrics"
FINANCIAL = "/api/v1/auth/financial"


class Delivery:
    def __init__(self):
        self.tokens = []

    def deliver_confirmation(self, *, recipient, token):
        self.tokens.append(token)


def login(client, email, answers=None):
    registered = client.post(
        "/api/v1/auth/register",
        json={"name": "Metrics", "email": email, "password": PASSWORD},
    )
    assert registered.status_code == 201
    with client.app.state.sessions() as db:
        user = db.get(UserRecord, registered.json()["id"])
        assert user is not None
        user.email_verified_at = datetime.now(UTC)
        db.commit()
    token = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    headers = {"Authorization": f"Bearer {token}"}
    if answers is not None:
        client.put("/api/v1/auth/investor-profile", headers=headers, json={"answers": answers})
    return headers


def seed_selic(app):
    app.state.clock = lambda: datetime(2026, 10, 29, 13, tzinfo=UTC)
    with app.state.sessions() as db:
        db.merge(
            MarketIndicatorRecord(
                code="selic",
                value=Decimal("10.50"),
                unit="percentual_anual",
                reference_date=date(2026, 10, 29),
                checked_at=app.state.clock(),
                source="local test",
            )
        )
        db.commit()


def test_spec025_metrics_require_opt_in_for_non_arrojado_and_enrich_variable_simulation(
    client, app
):
    headers = login(client, "metrics@example.com", answers=[1, 1, 1, 1, 1])
    seed_selic(app)
    assert client.get(MARKET, headers=headers).status_code == 403
    preference = client.put(
        "/api/v1/auth/profile/advanced-metrics", headers=headers, json={"enabled": True}
    )
    assert preference.status_code == 200
    metric = client.get(MARKET, headers=headers)
    assert metric.status_code == 200
    assert metric.json()["ticker"] == "PETR4"
    assert metric.json()["status"] == "available"
    assert metric.json()["sharpe"] is not None
    assert "não garantem" in metric.json()["disclaimer"]
    simulation = client.post(
        f"{FINANCIAL}/simulations/variable-income",
        headers=headers,
        json={
            "label": "PETR4 local",
            "ticker": "petr4",
            "initial_amount": "100",
            "monthly_contribution": "0",
            "expected_annual_return": "12",
            "term_months": 12,
        },
    )
    assert simulation.status_code == 201
    assert simulation.json()["risk_metrics"]["ticker"] == "PETR4"


def test_spec025_arrojado_has_default_access_and_history_errors_are_explicit(client, app):
    advanced = login(client, "advanced@example.com", answers=[2, 2, 2, 2, 2])
    seed_selic(app)
    assert client.get(MARKET, headers=advanced).status_code == 200
    unknown = client.get("/api/v1/market/quotes/ABCD11/metrics", headers=advanced)
    assert unknown.status_code == 404


def test_spec025_zero_volatility_is_never_infinite_or_nan():
    result = calculate_historical_metrics(
        [
            (date(2026, 1, 2), Decimal("10")),
            (date(2026, 1, 3), Decimal("10")),
            (date(2026, 1, 4), Decimal("10")),
        ],
        Decimal("10"),
    )
    assert result["status"] == "zero_volatility"
    assert result["sharpe"] is None
    assert result["volatility_annualized"] == Decimal("0.0000")
