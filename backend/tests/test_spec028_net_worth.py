"""SPEC-028: real sources and owner-scoped manual patrimony are consolidated server-side."""

PREFIX = "/api/v1/auth/financial"
PASSWORD = "StrongPassword123"


class CaptureDelivery:
    def __init__(self):
        self.confirmations: list[str] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.confirmations.append(token)

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        pass


def login(client, email: str):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Patrimônio", "email": email, "password": PASSWORD},
    )
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def verify(client, headers, delivery):
    assert client.post("/api/v1/auth/email-confirmation", headers=headers).status_code == 204
    assert (
        client.post(
            "/api/v1/auth/email-confirmation/confirm", json={"token": delivery.confirmations[-1]}
        ).status_code
        == 200
    )


def test_spec028_consolidates_real_account_manual_debt_and_excludes_projection(client):
    """Cláusulas: SPEC-028-R01, SPEC-028-R03, SPEC-028-R05, SPEC-028-R06, SPEC-028-R07."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "worth@example.com")
    verify(client, headers, delivery)
    assert (
        client.post(
            f"{PREFIX}/accounts",
            headers=headers,
            json={"name": "Conta real", "account_type": "checking", "initial_balance": "100.00"},
        ).status_code
        == 201
    )
    debt = client.post(
        f"{PREFIX}/net-worth/items",
        headers=headers,
        json={"kind": "liability", "name": "Empréstimo", "value": "30.00", "annual_rate": "12.5"},
    )
    assert debt.status_code == 201
    # A calculator projection is not a real asset and must not alter the consolidated result.
    assert (
        client.post(
            f"{PREFIX}/calculator",
            headers=headers,
            json={
                "initial_amount": "1000",
                "monthly_contribution": "0",
                "annual_rate": "10",
                "term_months": 12,
            },
        ).status_code
        == 200
    )
    summary = client.get(f"{PREFIX}/net-worth", headers=headers)
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["total_assets"] == "100.00"
    assert payload["total_liabilities"] == "30.00"
    assert payload["net_worth"] == "70.00"
    assert payload["assets"][0]["origin"] == "account"
    assert payload["liabilities"][0]["origin"] == "manual"


def test_spec028_manual_items_require_verified_owner_and_are_private(client):
    """Cláusulas: SPEC-028-R02, SPEC-028-R05, SPEC-028-R06."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "owner-worth@example.com")
    forbidden = client.post(
        f"{PREFIX}/net-worth/items",
        headers=owner,
        json={"kind": "asset", "name": "Veículo", "value": "50000"},
    )
    assert forbidden.status_code == 403
    verify(client, owner, delivery)
    created = client.post(
        f"{PREFIX}/net-worth/items",
        headers=owner,
        json={"kind": "asset", "name": "Veículo", "value": "50000"},
    )
    assert created.status_code == 201
    item_id = created.json()["id"]
    other = login(client, "other-worth@example.com")
    assert (
        client.patch(
            f"{PREFIX}/net-worth/items/{item_id}", headers=other, json={"value": "1"}
        ).status_code
        == 403
    )
    verify(client, other, delivery)
    assert (
        client.patch(
            f"{PREFIX}/net-worth/items/{item_id}", headers=other, json={"value": "1"}
        ).status_code
        == 404
    )
    updated = client.patch(
        f"{PREFIX}/net-worth/items/{item_id}", headers=owner, json={"value": "45000"}
    )
    assert updated.status_code == 200 and updated.json()["value"] == "45000"
    assert client.delete(f"{PREFIX}/net-worth/items/{item_id}", headers=owner).status_code == 204


def test_spec028_card_invoice_is_real_liability_and_values_are_validated(client):
    """Cláusulas: SPEC-028-R02, SPEC-028-R04."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "card-worth@example.com")
    verify(client, headers, delivery)
    card = client.post(
        f"{PREFIX}/credit-cards",
        headers=headers,
        json={"name": "Cartão", "credit_limit": "1000", "closing_day": 10, "due_day": 17},
    ).json()
    assert (
        client.post(
            f"{PREFIX}/expenses",
            headers={**headers, "Idempotency-Key": "worth-expense"},
            json={
                "description": "Mercado",
                "amount": "80",
                "occurred_on": "2026-10-29",
                "credit_card_id": card["id"],
                "category_key": "standard:alimentacao",
                "recurring": False,
            },
        ).status_code
        == 201
    )
    summary = client.get(f"{PREFIX}/net-worth?as_of=2026-10-29", headers=headers).json()
    assert summary["total_liabilities"] == "80.00"
    assert summary["liabilities"][0]["origin"] == "credit_card_invoice"
    invalid = client.post(
        f"{PREFIX}/net-worth/items",
        headers=headers,
        json={"kind": "asset", "name": "", "value": "0"},
    )
    assert invalid.status_code == 422
