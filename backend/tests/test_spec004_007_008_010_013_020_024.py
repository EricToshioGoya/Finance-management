# ruff: noqa: E501

from datetime import UTC, date, datetime

from app.infrastructure.models import MarketIndicatorRecord

PREFIX = "/api/v1/auth/financial"
USER = {"name": "Ana Lote", "email": "ana.lote@example.com", "password": "SenhaForte123"}


class Delivery:
    def __init__(self):
        self.tokens = []

    def deliver_confirmation(self, *, recipient, token):
        self.tokens.append(token)

    def deliver_password_reset(self, *, recipient, token):
        pass


def authenticated(client):
    delivery = Delivery()
    client.app.state.email_delivery = delivery
    assert client.post("/api/v1/auth/register", json=USER).status_code == 201
    login = client.post(
        "/api/v1/auth/login", json={"email": USER["email"], "password": USER["password"]}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.post("/api/v1/auth/email-confirmation", headers=headers).status_code == 204
    assert (
        client.post(
            "/api/v1/auth/email-confirmation/confirm", json={"token": delivery.tokens[-1]}
        ).status_code
        == 200
    )
    return headers


def account_and_card(client, headers):
    account = client.post(
        f"{PREFIX}/accounts",
        headers=headers,
        json={"name": "Conta", "account_type": "checking", "initial_balance": "0"},
    ).json()["id"]
    card = client.post(
        f"{PREFIX}/credit-cards",
        headers=headers,
        json={"name": "Cartão", "credit_limit": "100", "closing_day": 10, "due_day": 20},
    ).json()["id"]
    return account, card


def test_spec_004_013_024_calculator_tax_and_target(client):
    headers = authenticated(client)
    calculation = client.post(
        f"{PREFIX}/calculator",
        headers=headers,
        json={
            "initial_amount": "1000",
            "monthly_contribution": "0",
            "annual_rate": "12",
            "term_months": 12,
        },
    )
    assert calculation.status_code == 200
    assert calculation.json()["gross_amount"] == "1120.00"
    taxed = client.post(
        f"{PREFIX}/fixed-income-projections",
        headers=headers,
        json={
            "initial_amount": "1000",
            "monthly_contribution": "0",
            "annual_rate": "12",
            "term_months": 12,
            "product": "cdb",
        },
    )
    assert taxed.status_code == 200 and taxed.json()["estimated_tax"] == "24.00"
    target = client.post(
        f"{PREFIX}/target-contributions",
        headers=headers,
        json={
            "target_amount": "120",
            "initial_amount": "0",
            "annual_rate": "0",
            "term_months": 12,
            "available_monthly_amount": "9",
        },
    )
    assert target.status_code == 200 and target.json()["feasible"] is False


def test_spec_007_008_009_010_saves_private_simulations_and_indicator(client):
    headers = authenticated(client)
    with client.app.state.sessions() as db:
        db.add(
            MarketIndicatorRecord(
                code="selic",
                value="10.5",
                unit="percentual_anual",
                reference_date=date(2026, 1, 1),
                checked_at=datetime.now(UTC),
                source="BCB_SGS",
            )
        )
        db.commit()
    indicator = client.get(f"{PREFIX}/indicators/selic", headers=headers)
    assert indicator.status_code == 200 and indicator.json()["stale"] is False
    fixed = client.post(
        f"{PREFIX}/simulations/fixed-income",
        headers=headers,
        json={
            "label": "CDB",
            "product": "cdb",
            "initial_amount": "100",
            "monthly_contribution": "0",
            "annual_rate": "12",
            "term_months": 12,
        },
    )
    variable = client.post(
        f"{PREFIX}/simulations/variable-income",
        headers=headers,
        json={
            "label": "Ações",
            "initial_amount": "100",
            "monthly_contribution": "0",
            "expected_annual_return": "15",
            "term_months": 12,
        },
    )
    assert fixed.status_code == variable.status_code == 201
    comparison = client.post(
        f"{PREFIX}/simulations/compare",
        headers=headers,
        json={"simulation_ids": [fixed.json()["id"], variable.json()["id"]]},
    )
    assert comparison.status_code == 200 and len(comparison.json()["simulations"]) == 2


def test_spec_020_021_022_invoice_budget_and_dashboard(client):
    headers = authenticated(client)
    account, card = account_and_card(client, headers)
    created = client.post(
        f"{PREFIX}/expenses",
        headers={**headers, "Idempotency-Key": "card-expense"},
        json={
            "description": "Mercado",
            "amount": "80",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-01-15",
            "credit_card_id": card,
        },
    )
    assert created.status_code == 201
    invoice = client.get(
        f"{PREFIX}/credit-cards/{card}/invoice?competence=2026-01", headers=headers
    )
    assert invoice.status_code == 200 and invoice.json()["near_limit"] is True
    goal = client.put(
        f"{PREFIX}/budget-goals",
        headers=headers,
        json={
            "kind": "category_expense",
            "category_key": "standard:alimentacao",
            "target": "100",
            "alert_threshold": "90",
        },
    )
    assert goal.status_code == 200
    progress = client.get(f"{PREFIX}/budget-progress?competence=2026-01", headers=headers)
    assert progress.status_code == 200 and progress.json()[0]["status"] == "attention"
    dashboard = client.get(f"{PREFIX}/dashboard?start=2026-01&end=2026-02", headers=headers)
    assert dashboard.status_code == 200 and len(dashboard.json()) == 2
    assert account
