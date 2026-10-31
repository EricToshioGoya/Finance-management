"""SPEC-034: contract for the score panel and its private monthly history."""

from datetime import date

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"


def test_score_history_is_private_and_recalculation_is_idempotent(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "healthscore-ui-owner@example.com")
    verify(client, owner, delivery)
    other = login(client, "healthscore-ui-other@example.com")
    verify(client, other, delivery)

    account = client.post(
        f"{PREFIX}/accounts",
        headers=owner,
        json={"name": "Conta salário", "account_type": "savings", "initial_balance": "600"},
    )
    assert account.status_code == 201

    month = date.today().replace(day=1).isoformat()
    income = client.post(
        f"{PREFIX}/recurring-incomes",
        headers={**owner, "Idempotency-Key": "healthscore-ui-income"},
        json={
            "description": "Salário",
            "amount": "1000",
            "account_id": account.json()["id"],
            "starts_on": month,
        },
    )
    assert income.status_code == 201
    first = client.get(f"{PREFIX}/health-score?competence={month}", headers=owner)
    assert first.status_code == 200
    result = first.json()
    assert result["educational"] is True
    assert 0 <= float(result["score"]) <= 100
    assert len(result["factors"]) == 2
    assert len(result["history"]) == 1
    assert result["history"][0]["competence"] == month

    repeated = client.get(f"{PREFIX}/health-score?competence={month}", headers=owner)
    assert repeated.status_code == 200
    assert repeated.json() == result

    outsider = client.get(f"{PREFIX}/health-score?competence={month}", headers=other)
    assert outsider.status_code == 422
    assert outsider.json()["detail"] == "health_score_income_unavailable"


def test_score_requires_session_and_confirmed_email(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    month = date.today().replace(day=1).isoformat()
    assert client.get(f"{PREFIX}/health-score?competence={month}").status_code == 401
    headers = login(client, "healthscore-ui-unverified@example.com")
    denied = client.get(f"{PREFIX}/health-score?competence={month}", headers=headers)
    assert denied.status_code == 403
    assert denied.json()["detail"] == "email_not_verified"
