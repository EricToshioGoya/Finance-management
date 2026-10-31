# ruff: noqa: E501

from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Ana Silva", "email": "ana@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Caio Luz", "email": "caio@example.com", "password": "SenhaForte456"}


class CaptureDelivery:
    def __init__(self):
        self.confirmations: list[str] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.confirmations.append(token)

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        pass


def access(client, user, delivery):
    client.app.state.email_delivery = delivery
    assert client.post(f"{PREFIX}/register", json=user).status_code == 201
    token = client.post(
        f"{PREFIX}/login", json={"email": user["email"], "password": user["password"]}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post(f"{PREFIX}/email-confirmation", headers=headers).status_code == 204
    assert (
        client.post(
            f"{PREFIX}/email-confirmation/confirm", json={"token": delivery.confirmations[-1]}
        ).status_code
        == 200
    )
    return headers


def create_income(client, headers, key, **body):
    values = {"description": "Salário", "amount": "100.00", **body}
    return client.post(
        f"{PREFIX}/financial/recurring-incomes",
        headers={**headers, "Idempotency-Key": key},
        json=values,
    )


def test_SPEC_056_R01_R03_R04_R05_two_sources_count_in_current_competency(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    first = create_income(client, headers, "income-1", description="Emprego", amount="100.00")
    second = create_income(client, headers, "income-2", description="Freela fixo", amount="200.00")
    assert first.status_code == second.status_code == 201
    incomes = client.get(f"{PREFIX}/financial/recurring-incomes", headers=headers)
    assert (
        incomes.status_code == 200 and sum(float(item["amount"]) for item in incomes.json()) == 300
    )
    assert all(item["starts_on"] for item in incomes.json()) and COOKIE in client.cookies


def test_SPEC_056_R02_R06_idempotency_validation_and_owner_isolation(client):
    delivery = CaptureDelivery()
    owner = access(client, USER, delivery)
    first = create_income(client, owner, "same-key")
    repeated = create_income(client, owner, "same-key")
    assert first.status_code == repeated.status_code == 201
    assert first.json()["id"] == repeated.json()["id"]
    assert len(client.get(f"{PREFIX}/financial/recurring-incomes", headers=owner).json()) == 1
    zero = create_income(client, owner, "zero", amount="0")
    assert zero.status_code == 422
    other = access(client, OTHER, delivery)
    assert client.get(f"{PREFIX}/financial/recurring-incomes", headers=other).json() == []
    missing_key = client.post(
        f"{PREFIX}/financial/recurring-incomes",
        headers=owner,
        json={"description": "Salário", "amount": "100"},
    )
    assert missing_key.status_code == 400 and missing_key.json() == {
        "detail": "idempotency_key_required"
    }
