"""SPEC-038: explicit real confirmation, idempotency, owner isolation, atomic expense."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"
DATA = {
    "name": "Veículo financiado",
    "asset_value": "1200.00",
    "down_payment": "200.00",
    "installments": 10,
    "annual_rate": "0",
    "confirmation": "CONFIRMAR FINANCIAMENTO REAL",
    "create_recurring_expense": False,
}


def test_financing_confirmation_is_explicit_once_and_real(client):
    """Cláusulas: SPEC-028-R04.

    Cláusulas: SPEC-038-R01, SPEC-038-R02, SPEC-038-R03.
    """
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    route = f"{PREFIX}/financing/confirm"
    assert client.post(route, json=DATA).status_code == 401
    owner = login(client, "real-financing-owner@example.com")
    assert (
        client.post(
            route, json=DATA, headers={**owner, "Idempotency-Key": "unverified-attempt"}
        ).status_code
        == 403
    )
    verify(client, owner, delivery)
    header = {**owner, "Idempotency-Key": "real-confirmation-123"}
    baseline = client.get(f"{PREFIX}/net-worth", headers=owner).json()
    simulated = client.post(
        f"{PREFIX}/financing/simulate",
        headers=owner,
        json={"asset_value": "1200", "down_payment": "200", "installments": 10, "annual_rate": "0"},
    )
    assert simulated.status_code == 200
    assert client.get(f"{PREFIX}/net-worth", headers=owner).json() == baseline
    invalid = client.post(route, headers=header, json={**DATA, "confirmation": "YES"})
    assert invalid.status_code == 422
    assert client.get(f"{PREFIX}/net-worth", headers=owner).json() == baseline
    created = client.post(route, headers=header, json=DATA)
    assert created.status_code == 201, created.text
    real = created.json()
    assert real["principal"] == "1000.00"
    assert real["installment_amount"] == "100.00"
    assert real["expense_id"] is None
    again = client.post(route, headers=header, json=DATA)
    assert again.status_code == 201
    assert again.json()["id"] == real["id"]
    assert client.post(route, headers=header, json={**DATA, "name": "Outro"}).status_code == 409
    worth = client.get(f"{PREFIX}/net-worth", headers=owner).json()
    assert worth["total_liabilities"] == "1000.00"
    assert len([x for x in worth["liabilities"] if x["origin"] == "financing"]) == 1
    assert worth["liabilities"][0]["id"] == real["id"]
    assert client.get(f"{PREFIX}/financing/confirmed", headers=owner).json()[0]["id"] == real["id"]
    other = login(client, "real-financing-other@example.com")
    verify(client, other, delivery)
    assert client.get(f"{PREFIX}/financing/confirmed", headers=other).json() == []
    assert client.get(f"{PREFIX}/net-worth", headers=other).json()["total_liabilities"] == "0"


def test_real_financing_recurring_expense_is_atomic_and_linked(client):
    """Cláusulas: SPEC-038-R01, SPEC-038-R04."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "real-financing-expense@example.com")
    verify(client, owner, delivery)
    account = client.post(
        f"{PREFIX}/accounts",
        headers=owner,
        json={"name": "Conta pagamento", "account_type": "checking", "initial_balance": "3000"},
    )
    assert account.status_code == 201
    with_expense = {
        **DATA,
        "create_recurring_expense": True,
        "expense_account_id": account.json()["id"],
        "expense_category_key": "standard:moradia",
        "first_payment_on": "2027-02-10",
    }
    route = f"{PREFIX}/financing/confirm"
    header = {**owner, "Idempotency-Key": "real-expense-123"}
    failed = client.post(
        route, headers=header, json={**with_expense, "expense_category_key": "standard:invalid"}
    )
    assert failed.status_code == 404
    assert client.get(f"{PREFIX}/financing/confirmed", headers=owner).json() == []
    assert client.get(f"{PREFIX}/expenses", headers=owner).json() == []
    created = client.post(route, headers=header, json=with_expense)
    assert created.status_code == 201, created.text
    expense_id = created.json()["expense_id"]
    assert expense_id is not None
    expense = client.get(f"{PREFIX}/expenses", headers=owner).json()
    assert len(expense) == 1
    assert expense[0]["id"] == expense_id
    assert expense[0]["recurring"] is True
    assert expense[0]["amount"] == created.json()["installment_amount"]
    again = client.post(route, headers=header, json=with_expense)
    assert again.status_code == 201
    assert len(client.get(f"{PREFIX}/expenses", headers=owner).json()) == 1
    assert len(client.get(f"{PREFIX}/financing/confirmed", headers=owner).json()) == 1
