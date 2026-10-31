# ruff: noqa: E501

from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Ana Despesa", "email": "ana.expense@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Caio Despesa", "email": "caio.expense@example.com", "password": "SenhaForte456"}


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


def account(client, headers):
    response = client.post(
        f"{PREFIX}/financial/accounts",
        headers=headers,
        json={"name": "Conta principal", "account_type": "checking", "initial_balance": "0"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def expense(client, headers, account_id, key="expense-1", **changes):
    body = {
        "description": "Mercado",
        "amount": "30.00",
        "category_key": "standard:alimentacao",
        "occurred_on": "2026-01-15",
        "account_id": account_id,
        **changes,
    }
    return post(client, f"{PREFIX}/financial/expenses", headers, key, body)


def test_SPEC_059_R01_R03_R04_R05_R06_records_lists_and_retries_expense(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    account_id = account(client, headers)
    created = expense(client, headers, account_id, recurring=True)
    repeated = expense(client, headers, account_id, recurring=True)
    assert created.status_code == repeated.status_code == 201
    assert created.json()["id"] == repeated.json()["id"]
    listed = client.get(f"{PREFIX}/financial/expenses", headers=headers)
    assert listed.status_code == 200 and len(listed.json()) == 1
    assert listed.json()[0]["recurring"] is True and listed.json()[0]["amount"] == "30.00"
    assert COOKIE in client.cookies


def test_SPEC_059_R02_rejects_invalid_or_foreign_source_and_never_persists(client):
    delivery = CaptureDelivery()
    owner = access(client, USER, delivery)
    account_id = account(client, owner)
    invalid_value = expense(client, owner, account_id, "zero", amount="0")
    invalid_source = client.post(
        f"{PREFIX}/financial/expenses",
        headers={**owner, "Idempotency-Key": "two-sources"},
        json={
            "description": "Erro",
            "amount": "1",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-01-15",
            "account_id": account_id,
            "credit_card_id": account_id,
        },
    )
    assert invalid_value.status_code == invalid_source.status_code == 422
    assert client.get(f"{PREFIX}/financial/expenses", headers=owner).json() == []


def test_SPEC_006_R01_R04_R05_recalculates_balance_after_edit_and_delete(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    account_id = account(client, headers)
    income = post(
        client,
        f"{PREFIX}/financial/one-time-incomes",
        headers,
        "income-jan",
        {"description": "Freela", "amount": "100.00", "occurred_on": "2026-01-15"},
    )
    created = expense(client, headers, account_id)
    assert income.status_code == created.status_code == 201
    summary_path = f"{PREFIX}/financial/balance-summary?competence=2026-01"
    assert client.get(summary_path, headers=headers).json()["balance_variation"] == "70.00"
    edited = client.patch(
        f"{PREFIX}/financial/expenses/{created.json()['id']}",
        headers=headers,
        json={"amount": "40.00", "description": "Mercado semanal"},
    )
    assert edited.status_code == 200 and edited.json()["description"] == "Mercado semanal"
    assert client.get(summary_path, headers=headers).json()["balance_variation"] == "60.00"
    assert (
        client.delete(
            f"{PREFIX}/financial/expenses/{created.json()['id']}", headers=headers
        ).status_code
        == 204
    )
    assert client.get(summary_path, headers=headers).json()["balance_variation"] == "100.00"


def test_SPEC_006_R02_R03_edits_all_income_types_and_hides_foreign_records(client):
    delivery = CaptureDelivery()
    owner = access(client, USER, delivery)
    account_id = account(client, owner)
    recurring = post(
        client,
        f"{PREFIX}/financial/recurring-incomes",
        owner,
        "recurring-edit",
        {"description": "Salário", "amount": "100", "starts_on": "2026-01-01"},
    ).json()
    one_time = post(
        client,
        f"{PREFIX}/financial/one-time-incomes",
        owner,
        "income-edit",
        {"description": "Freela", "amount": "50", "occurred_on": "2026-01-15"},
    ).json()
    bonus = post(
        client,
        f"{PREFIX}/financial/bonuses",
        owner,
        "bonus-edit",
        {
            "description": "PLR",
            "amount": "10",
            "periodicity": "annual",
            "reference_month": 1,
            "starts_on": "2026-01-01",
        },
    ).json()
    created_expense = expense(client, owner, account_id).json()
    assert (
        client.patch(
            f"{PREFIX}/financial/recurring-incomes/{recurring['id']}",
            headers=owner,
            json={"amount": "120"},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"{PREFIX}/financial/one-time-incomes/{one_time['id']}",
            headers=owner,
            json={"occurred_on": "2026-02-01"},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"{PREFIX}/financial/bonuses/{bonus['id']}",
            headers=owner,
            json={"periodicity": "monthly"},
        ).status_code
        == 200
    )
    other = access(client, OTHER, delivery)
    foreign = client.patch(
        f"{PREFIX}/financial/expenses/{created_expense['id']}", headers=other, json={"amount": "1"}
    )
    assert foreign.status_code == 404
    assert (
        client.delete(
            f"{PREFIX}/financial/one-time-incomes/{one_time['id']}", headers=owner
        ).status_code
        == 204
    )


def test_SPEC_006_update_and_delete_errors_do_not_expose_other_financial_records(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    recurring = post(
        client,
        f"{PREFIX}/financial/recurring-incomes",
        headers,
        "recurring-delete",
        {"description": "Salário", "amount": "10", "starts_on": "2026-01-01"},
    ).json()
    one_time = post(
        client,
        f"{PREFIX}/financial/one-time-incomes",
        headers,
        "one-delete",
        {"description": "Freela", "amount": "10", "occurred_on": "2026-01-01"},
    ).json()
    bonus = post(
        client,
        f"{PREFIX}/financial/bonuses",
        headers,
        "bonus-delete",
        {
            "description": "Bônus",
            "amount": "1",
            "periodicity": "monthly",
            "starts_on": "2026-01-01",
        },
    ).json()
    for path in ("recurring-incomes", "one-time-incomes", "bonuses"):
        assert (
            client.patch(
                f"{PREFIX}/financial/{path}/00000000-0000-0000-0000-000000000000",
                headers=headers,
                json={"amount": "1"},
            ).status_code
            == 404
        )
    assert (
        client.patch(
            f"{PREFIX}/financial/bonuses/{bonus['id']}",
            headers=headers,
            json={"periodicity": "annual"},
        ).status_code
        == 400
    )
    assert (
        client.delete(
            f"{PREFIX}/financial/recurring-incomes/{recurring['id']}", headers=headers
        ).status_code
        == 204
    )
    assert (
        client.delete(f"{PREFIX}/financial/bonuses/{bonus['id']}", headers=headers).status_code
        == 204
    )
    assert (
        client.delete(
            f"{PREFIX}/financial/one-time-incomes/{one_time['id']}", headers=headers
        ).status_code
        == 204
    )


def test_SPEC_059_category_and_source_are_checked_on_server(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    account_id = account(client, headers)
    bad_category = expense(
        client, headers, account_id, "bad-category", category_key="standard:inexistente"
    )
    other = access(client, OTHER, delivery)
    foreign_source = expense(client, other, account_id, "foreign-source")
    assert bad_category.status_code == foreign_source.status_code == 404
    assert client.get(f"{PREFIX}/financial/expenses", headers=other).json() == []


def test_SPEC_059_accepts_personal_category_and_credit_card_as_exclusive_source(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    category = client.post(
        f"{PREFIX}/categories", headers=headers, json={"name": "Pet", "color": "#112233"}
    )
    card = client.post(
        f"{PREFIX}/financial/credit-cards",
        headers=headers,
        json={"name": "Cartão", "credit_limit": "500", "closing_day": 10, "due_day": 20},
    )
    assert category.status_code == card.status_code == 201
    created = post(
        client,
        f"{PREFIX}/financial/expenses",
        headers,
        "card-expense",
        {
            "description": "Ração",
            "amount": "20",
            "category_key": category.json()["key"],
            "occurred_on": "2026-01-15",
            "credit_card_id": card.json()["id"],
        },
    )
    assert created.status_code == 201 and created.json()["credit_card_id"] == card.json()["id"]


def test_SPEC_006_expense_errors_keep_record_unchanged(client):
    delivery = CaptureDelivery()
    headers = access(client, USER, delivery)
    account_id = account(client, headers)
    created = expense(client, headers, account_id).json()
    assert (
        client.patch(
            f"{PREFIX}/financial/expenses/{created['id']}",
            headers=headers,
            json={"category_key": "personal:not-a-uuid"},
        ).status_code
        == 404
    )
    missing = "00000000-0000-0000-0000-000000000000"
    assert (
        client.patch(
            f"{PREFIX}/financial/expenses/{missing}", headers=headers, json={"amount": "1"}
        ).status_code
        == 404
    )
    assert (
        client.delete(f"{PREFIX}/financial/expenses/{missing}", headers=headers).status_code == 404
    )
    assert (
        client.get(f"{PREFIX}/financial/expenses", headers=headers).json()[0]["amount"] == "30.00"
    )


def test_financial_mutations_require_an_authenticated_session(client):
    missing = "00000000-0000-0000-0000-000000000000"
    paths = (
        ("get", f"{PREFIX}/financial/expenses"),
        ("post", f"{PREFIX}/financial/expenses"),
        ("patch", f"{PREFIX}/financial/expenses/{missing}"),
        ("delete", f"{PREFIX}/financial/expenses/{missing}"),
        ("patch", f"{PREFIX}/financial/recurring-incomes/{missing}"),
        ("delete", f"{PREFIX}/financial/recurring-incomes/{missing}"),
        ("patch", f"{PREFIX}/financial/one-time-incomes/{missing}"),
        ("delete", f"{PREFIX}/financial/one-time-incomes/{missing}"),
        ("patch", f"{PREFIX}/financial/bonuses/{missing}"),
        ("delete", f"{PREFIX}/financial/bonuses/{missing}"),
        ("get", f"{PREFIX}/financial/balance-summary?competence=2026-01"),
    )
    for method, path in paths:
        if method == "post":
            response = getattr(client, method)(
                path,
                headers={"Idempotency-Key": "unauthenticated"},
                json={
                    "description": "Teste",
                    "amount": "1",
                    "category_key": "standard:alimentacao",
                    "occurred_on": "2026-01-01",
                    "account_id": missing,
                },
            )
        elif method == "patch":
            response = getattr(client, method)(path, json={"amount": "1"})
        else:
            response = getattr(client, method)(path)
        assert response.status_code == 401
