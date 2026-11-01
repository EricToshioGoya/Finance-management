"""SPEC-032: authorized, non-mutating financial stress API."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"
INPUT = {
    "minimum_reserve_months": 3,
    "first": {"kind": "income_loss", "months": 12},
    "second": {
        "kind": "income_reduction",
        "months": 12,
        "reduction_percent": "50",
        "expense_cut_percent": "30",
    },
}


def test_stress_requires_verified_account_and_actual_expense_history(client):
    """Cláusulas: SPEC-032-R02."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    assert client.post(f"{PREFIX}/stress/compare", json=INPUT).status_code == 401
    headers = login(client, "stress-no-data@example.com")
    assert client.post(f"{PREFIX}/stress/compare", headers=headers, json=INPUT).status_code == 403
    verify(client, headers, delivery)
    failed = client.post(f"{PREFIX}/stress/compare", headers=headers, json=INPUT)
    assert failed.status_code == 422
    assert failed.json()["detail"] == "stress_expense_history_required"
    invalid = client.post(
        f"{PREFIX}/stress/compare",
        headers=headers,
        json={**INPUT, "minimum_reserve_months": 7},
    )
    assert invalid.status_code == 422


def test_stress_reads_real_ledger_but_never_changes_it(client):
    """Cláusulas: SPEC-032-R01, SPEC-032-R04, SPEC-032-R06, SPEC-032-R07."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "stress-real-user@example.com")
    verify(client, headers, delivery)
    account = client.post(
        f"{PREFIX}/accounts",
        headers=headers,
        json={"name": "Reserva", "account_type": "savings", "initial_balance": "900"},
    )
    assert account.status_code == 201
    card = client.post(
        f"{PREFIX}/credit-cards",
        headers=headers,
        json={"name": "Despesas", "credit_limit": "1000", "closing_day": 10, "due_day": 17},
    )
    assert card.status_code == 201
    recurring = client.post(
        f"{PREFIX}/expenses",
        headers={**headers, "Idempotency-Key": "stress-monthly-expense"},
        json={
            "description": "Despesa mensal",
            "amount": "100",
            "occurred_on": "2026-01-01",
            "credit_card_id": card.json()["id"],
            "category_key": "standard:alimentacao",
            "recurring": True,
        },
    )
    assert recurring.status_code == 201, recurring.text
    prior_worth = client.get(f"{PREFIX}/net-worth", headers=headers).json()
    first = client.post(f"{PREFIX}/stress/compare", headers=headers, json=INPUT)
    assert first.status_code == 200, first.text
    data = first.json()
    assert data["rule_version"] == "stress-v1"
    assert data["window_months"] == 3
    assert data["average_monthly_expenses"] == "100.00"
    assert data["reserve"] == "900.00"
    assert data["first"]["months_supported"] == "9.00"
    assert data["second"]["months_supported"] == "12.86"
    assert client.get(f"{PREFIX}/net-worth", headers=headers).json() == prior_worth
    assert client.post(f"{PREFIX}/stress/compare", headers=headers, json=INPUT).json() == data

    other = login(client, "stress-other-user@example.com")
    verify(client, other, delivery)
    other_result = client.post(f"{PREFIX}/stress/compare", headers=other, json=INPUT)
    assert other_result.status_code == 422
    assert other_result.json()["detail"] == "stress_expense_history_required"
