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
    """Cláusulas: SPEC-025-R01, SPEC-025-R05, SPEC-025-R06, SPEC-025-R07."""
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
    other = client.post(
        f"{FINANCIAL}/simulations/variable-income",
        headers=headers,
        json={
            "label": "PETR4 alternativa",
            "ticker": "PETR4",
            "initial_amount": "200",
            "monthly_contribution": "0",
            "expected_annual_return": "10",
            "term_months": 12,
        },
    ).json()
    compared = client.post(
        f"{FINANCIAL}/simulations/compare",
        headers=headers,
        json={"simulation_ids": [simulation.json()["id"], other["id"]]},
    ).json()
    # R05: as métricas acompanham cada simulação também no comparador (RF-25).
    assert all(item["risk_metrics"]["status"] == "available" for item in compared["simulations"])


def test_spec025_arrojado_has_default_access_and_history_errors_are_explicit(client, app):
    """Cláusulas: SPEC-025-R02, SPEC-025-R07."""
    advanced = login(client, "advanced@example.com", answers=[2, 2, 2, 2, 2])
    seed_selic(app)
    assert client.get(MARKET, headers=advanced).status_code == 200
    unknown = client.get("/api/v1/market/quotes/ABCD11/metrics", headers=advanced)
    assert unknown.status_code == 404


def test_spec025_zero_volatility_is_never_infinite_or_nan():
    """Cláusulas: SPEC-025-R02, SPEC-025-R03."""
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


def test_SPEC_025_R03_R04_volatility_and_simplified_sharpe_formula():
    """Retornos +10% e −10%: média 0; desvio amostral √0,02; Selic anual composta ao dia útil."""
    result = calculate_historical_metrics(
        [
            (date(2026, 1, 5), Decimal("10")),
            (date(2026, 1, 6), Decimal("11")),
            (date(2026, 1, 7), Decimal("9.9")),
        ],
        Decimal("10"),
    )
    daily_volatility = Decimal("0.02").sqrt()
    factor = Decimal("252").sqrt()
    daily_selic = Decimal("1.1") ** (Decimal("1") / Decimal("252")) - Decimal("1")
    expected_volatility = (daily_volatility * factor).quantize(Decimal("0.0001"))
    expected_sharpe = ((Decimal("0") - daily_selic) / daily_volatility * factor).quantize(
        Decimal("0.0001")
    )
    assert result["volatility_annualized"] == expected_volatility == Decimal("2.2450")
    assert result["sharpe"] == expected_sharpe
    assert result["period_start"] == date(2026, 1, 5) and result["observations"] == 3
