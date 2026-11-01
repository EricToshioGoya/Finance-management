"""SPEC-034 educational score uses persisted weights and owner-only financial inputs."""

PREFIX = "/api/v1/auth/financial"
PASSWORD = "StrongPassword123"


class Delivery:
    def __init__(self):
        self.confirmations = []

    def deliver_confirmation(self, *, recipient, token):
        self.confirmations.append(token)

    def deliver_password_reset(self, *, recipient, token):
        pass


def login(client, email):
    client.post(
        "/api/v1/auth/register", json={"name": "Score", "email": email, "password": PASSWORD}
    )
    return {
        "Authorization": "Bearer "
        + client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).json()[
            "access_token"
        ]
    }


def verify(client, headers, delivery):
    client.post("/api/v1/auth/email-confirmation", headers=headers)
    client.post(
        "/api/v1/auth/email-confirmation/confirm", json={"token": delivery.confirmations[-1]}
    )


def test_spec034_calculates_educational_score_and_preserves_one_month_history(client):
    """Cláusulas: SPEC-034-R01, SPEC-034-R03, SPEC-034-R06."""
    delivery = Delivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "score@example.com")
    verify(client, headers, delivery)
    account = client.post(
        f"{PREFIX}/accounts",
        headers=headers,
        json={"name": "Reserva", "account_type": "savings", "initial_balance": "6000"},
    ).json()
    client.post(
        f"{PREFIX}/recurring-incomes",
        headers={**headers, "Idempotency-Key": "score-income"},
        json={
            "description": "Salário",
            "amount": "1000",
            "account_id": account["id"],
            "starts_on": "2026-10-01",
        },
    )
    result = client.get(f"{PREFIX}/health-score?competence=2026-10-01", headers=headers)
    assert result.status_code == 200
    payload = result.json()
    assert payload["score"] == "100.00" and payload["classification"] == "excellent"
    assert payload["educational"] is True and len(payload["factors"]) == 2
    repeated = client.get(f"{PREFIX}/health-score?competence=2026-10-01", headers=headers).json()
    assert len(repeated["history"]) == 1


def test_spec034_refuses_arbitrary_score_when_income_is_zero_and_keeps_private(client):
    """Cláusulas: SPEC-034-R02."""
    delivery = Delivery()
    client.app.state.email_delivery = delivery
    first = login(client, "zero-score@example.com")
    verify(client, first, delivery)
    assert (
        client.get(f"{PREFIX}/health-score?competence=2026-10-01", headers=first).json()["detail"]
        == "health_score_income_unavailable"
    )
    assert client.get(f"{PREFIX}/health-score?competence=2026-10-01").status_code == 401
