from app.main import COOKIE
from tests.clause_support import FIN, account, verified_user

PREFIX = "/api/v1/auth"
USER = {"name": "Larissa Alves", "email": "larissa@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Rafael Lima", "email": "rafael@example.com", "password": "SenhaForte456"}
DEFAULT_NAMES = [
    "Moradia",
    "Custos básicos",
    "Alimentação",
    "Locomoção",
    "Saúde",
    "Educação",
    "Lazer",
    "Investimentos",
    "Doações",
]


class CaptureDelivery:
    def __init__(self):
        self.confirmations: list[str] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.confirmations.append(token)

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        pass


def headers_for(client, user):
    assert client.post(f"{PREFIX}/register", json=user).status_code == 201
    response = client.post(
        f"{PREFIX}/login", json={"email": user["email"], "password": user["password"]}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def confirm_email(client, headers, delivery):
    assert client.post(f"{PREFIX}/email-confirmation", headers=headers).status_code == 204
    assert (
        client.post(
            f"{PREFIX}/email-confirmation/confirm", json={"token": delivery.confirmations[-1]}
        ).status_code
        == 200
    )


def test_SPEC_055_R01_defaults_and_personal_category_with_stable_color(client):
    """Cláusulas: SPEC-055-R03, SPEC-055-R04, SPEC-055-R07."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = headers_for(client, USER)
    defaults = client.get(f"{PREFIX}/categories", headers=headers)
    assert defaults.status_code == 200
    assert [item["name"] for item in defaults.json()] == DEFAULT_NAMES
    assert all(item["active"] and item["kind"] == "standard" for item in defaults.json())

    unverified = client.post(
        f"{PREFIX}/categories", headers=headers, json={"name": "Viagem", "color": "#8a2be2"}
    )
    assert unverified.status_code == 403 and unverified.json() == {"detail": "email_not_verified"}
    confirm_email(client, headers, delivery)
    created = client.post(
        f"{PREFIX}/categories", headers=headers, json={"name": "Viagem", "color": "#8a2be2"}
    )
    assert created.status_code == 201
    assert created.json() == {
        "key": created.json()["key"],
        "name": "Viagem",
        "color": "#8A2BE2",
        "kind": "personal",
        "active": True,
    }
    categories = client.get(f"{PREFIX}/categories", headers=headers).json()
    assert categories[-1]["name"] == "Viagem" and categories[-1]["color"] == "#8A2BE2"


def test_SPEC_055_R02_hiding_default_is_per_owner_and_preserves_category(client):
    """Cláusulas: SPEC-055-R05."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    first = headers_for(client, USER)
    confirm_email(client, first, delivery)
    hidden = client.patch(
        f"{PREFIX}/categories/standard/lazer", headers=first, json={"active": False}
    )
    assert hidden.status_code == 200 and hidden.json()["active"] is False
    own_lazer = next(
        item
        for item in client.get(f"{PREFIX}/categories", headers=first).json()
        if item["name"] == "Lazer"
    )
    assert own_lazer["key"] == "standard:lazer" and own_lazer["active"] is False

    other = headers_for(client, OTHER)
    other_lazer = next(
        item
        for item in client.get(f"{PREFIX}/categories", headers=other).json()
        if item["name"] == "Lazer"
    )
    assert other_lazer["active"] is True
    assert COOKIE in client.cookies


def test_SPEC_055_R03_custom_categories_are_private_and_names_are_unique(client):
    """Cláusulas: SPEC-055-R02, SPEC-055-R04."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    first = headers_for(client, USER)
    confirm_email(client, first, delivery)
    assert (
        client.post(
            f"{PREFIX}/categories", headers=first, json={"name": "Projetos", "color": "#123456"}
        ).status_code
        == 201
    )
    duplicate = client.post(
        f"{PREFIX}/categories", headers=first, json={"name": " projetos ", "color": "#654321"}
    )
    assert duplicate.status_code == 409 and duplicate.json() == {"detail": "category_exists"}

    other = headers_for(client, OTHER)
    names = [item["name"] for item in client.get(f"{PREFIX}/categories", headers=other).json()]
    assert "Projetos" not in names
    missing = client.patch(
        f"{PREFIX}/categories/standard/inexistente", headers=other, json={"active": False}
    )
    assert missing.status_code == 403


def test_SPEC_055_R06_each_expense_belongs_to_exactly_one_category(client, app):
    headers = verified_user(client, app, "categoria-unica@example.com")
    body = {
        "description": "Sem categoria",
        "amount": "10",
        "occurred_on": "2026-03-10",
        "account_id": account(client, headers),
    }
    missing = client.post(
        f"{FIN}/expenses", headers={**headers, "Idempotency-Key": "sem-categoria"}, json=body
    )
    many = client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": "duas-categorias"},
        json={**body, "category_key": ["standard:lazer", "standard:moradia"]},
    )
    assert missing.status_code == many.status_code == 422
    created = client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": "uma-categoria"},
        json={**body, "category_key": "standard:lazer"},
    ).json()
    assert created["category_key"] == "standard:lazer"
