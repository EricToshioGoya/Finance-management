# ruff: noqa: E501

from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Larissa Alves", "email": "larissa@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Rafael Lima", "email": "rafael@example.com", "password": "SenhaForte456"}


class CaptureDelivery:
    def __init__(self):
        self.confirmations: list[str] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.confirmations.append(token)

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        pass


def authenticated(client, user):
    assert client.post(f"{PREFIX}/register", json=user).status_code == 201
    response = client.post(
        f"{PREFIX}/login", json={"email": user["email"], "password": user["password"]}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def verified(client, headers, delivery):
    assert client.post(f"{PREFIX}/email-confirmation", headers=headers).status_code == 204
    assert (
        client.post(
            f"{PREFIX}/email-confirmation/confirm", json={"token": delivery.confirmations[-1]}
        ).status_code
        == 200
    )


def test_SPEC_005_R01_R03_R04_registers_multiple_owned_accounts_and_cards(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = authenticated(client, USER)
    assert (
        client.post(
            f"{PREFIX}/financial/accounts",
            headers=headers,
            json={"name": "Nubank", "account_type": "checking", "initial_balance": "100.00"},
        ).status_code
        == 403
    )
    verified(client, headers, delivery)
    first = client.post(
        f"{PREFIX}/financial/accounts",
        headers=headers,
        json={"name": "Nubank", "account_type": "checking", "initial_balance": "100.00"},
    )
    second = client.post(
        f"{PREFIX}/financial/accounts",
        headers=headers,
        json={"name": "Reserva", "account_type": "savings", "initial_balance": "250.50"},
    )
    card = client.post(
        f"{PREFIX}/financial/credit-cards",
        headers=headers,
        json={"name": "Cartão azul", "credit_limit": "1200.00", "closing_day": 10, "due_day": 17},
    )
    assert first.status_code == second.status_code == card.status_code == 201
    sources = client.get(f"{PREFIX}/financial/sources", headers=headers)
    assert sources.status_code == 200 and sorted(
        item["initial_balance"] for item in sources.json()["accounts"]
    ) == ["100.00", "250.50"]
    assert sources.json()["credit_cards"][0]["credit_limit"] == "1200.00"
    assert COOKIE in client.cookies


def test_SPEC_005_R02_keeps_sources_private_and_rejects_invalid_card(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = authenticated(client, USER)
    verified(client, owner, delivery)
    created = client.post(
        f"{PREFIX}/financial/accounts",
        headers=owner,
        json={"name": "Pessoal", "account_type": "cash", "initial_balance": "12.00"},
    )
    assert created.status_code == 201
    other = authenticated(client, OTHER)
    assert client.get(f"{PREFIX}/financial/sources", headers=other).json() == {
        "accounts": [],
        "credit_cards": [],
    }
    invalid = client.post(
        f"{PREFIX}/financial/credit-cards",
        headers=owner,
        json={"name": "Inválido", "credit_limit": "0", "closing_day": 0, "due_day": 40},
    )
    assert invalid.status_code == 422 and invalid.json() == {"detail": "invalid_input"}
