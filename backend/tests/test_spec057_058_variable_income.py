# ruff: noqa: E501

from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Ana Silva", "email": "ana.variable@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Caio Luz", "email": "caio.variable@example.com", "password": "SenhaForte456"}


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


def post(client, path, headers, key, body):
    return client.post(path, headers={**headers, "Idempotency-Key": key}, json=body)


def test_SPEC_057_R01_R03_R04_R05_records_only_its_competence_and_is_idempotent(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    created = post(
        client,
        f"{PREFIX}/financial/one-time-incomes",
        headers,
        "variable-jan",
        {"description": "Freela", "amount": "100.00", "occurred_on": "2026-01-15"},
    )
    repeated = post(
        client,
        f"{PREFIX}/financial/one-time-incomes",
        headers,
        "variable-jan",
        {"description": "Freela", "amount": "100.00", "occurred_on": "2026-01-15"},
    )
    assert created.status_code == repeated.status_code == 201
    assert created.json()["id"] == repeated.json()["id"]
    january = client.get(
        f"{PREFIX}/financial/income-summary?competence=2026-01", headers=headers
    ).json()
    february = client.get(
        f"{PREFIX}/financial/income-summary?competence=2026-02", headers=headers
    ).json()
    assert january["one_time_income"] == "100.00" and february["one_time_income"] == "0"


def test_SPEC_057_R02_R06_rejects_invalid_value_and_foreign_source(client):
    delivery = CaptureDelivery()
    owner = access(client, USER, delivery)
    invalid = post(
        client,
        f"{PREFIX}/financial/one-time-incomes",
        owner,
        "invalid",
        {"description": "Freela", "amount": "0", "occurred_on": "2026-01-15"},
    )
    assert invalid.status_code == 422
    other = access(client, OTHER, delivery)
    assert client.get(f"{PREFIX}/financial/one-time-incomes", headers=other).json() == []
    assert COOKIE in client.cookies


def test_SPEC_058_R01_R03_R04_R05_R06_annual_bonus_is_not_diluted_and_zero_is_valid(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    annual = post(
        client,
        f"{PREFIX}/financial/bonuses",
        headers,
        "plr-jun",
        {
            "description": "PLR",
            "amount": "120.00",
            "periodicity": "annual",
            "reference_month": 6,
            "starts_on": "2026-01-01",
        },
    )
    zero = post(
        client,
        f"{PREFIX}/financial/bonuses",
        headers,
        "bonus-zero",
        {
            "description": "Bônus simbólico",
            "amount": "0",
            "periodicity": "monthly",
            "starts_on": "2026-01-01",
        },
    )
    assert annual.status_code == zero.status_code == 201
    june = client.get(
        f"{PREFIX}/financial/income-summary?competence=2026-06", headers=headers
    ).json()
    july = client.get(
        f"{PREFIX}/financial/income-summary?competence=2026-07", headers=headers
    ).json()
    assert june["bonus"] == "120.00" and july["bonus"] == "0.00"


def test_SPEC_058_R02_R07_requires_month_for_annual_and_rejects_negative(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    missing_month = post(
        client,
        f"{PREFIX}/financial/bonuses",
        headers,
        "missing-month",
        {"description": "PLR", "amount": "100", "periodicity": "annual"},
    )
    negative = post(
        client,
        f"{PREFIX}/financial/bonuses",
        headers,
        "negative",
        {"description": "PLR", "amount": "-1", "periodicity": "monthly"},
    )
    assert missing_month.status_code == negative.status_code == 422


def test_variable_income_lists_are_private_and_bonus_retries_do_not_duplicate(client):
    delivery = CaptureDelivery()
    owner = access(client, USER, delivery)
    first = post(
        client,
        f"{PREFIX}/financial/bonuses",
        owner,
        "same-bonus",
        {
            "description": "Bônus",
            "amount": "50",
            "periodicity": "monthly",
            "starts_on": "2026-02-01",
        },
    )
    repeated = post(
        client,
        f"{PREFIX}/financial/bonuses",
        owner,
        "same-bonus",
        {
            "description": "Bônus",
            "amount": "50",
            "periodicity": "monthly",
            "starts_on": "2026-02-01",
        },
    )
    assert first.status_code == repeated.status_code == 201
    assert first.json()["id"] == repeated.json()["id"]
    assert len(client.get(f"{PREFIX}/financial/bonuses", headers=owner).json()) == 1
    assert client.get(f"{PREFIX}/financial/one-time-incomes", headers=owner).json() == []
    other = access(client, OTHER, delivery)
    assert client.get(f"{PREFIX}/financial/bonuses", headers=other).json() == []
    invalid_competence = client.get(
        f"{PREFIX}/financial/income-summary?competence=nope", headers=owner
    )
    assert invalid_competence.status_code == 400
