"""C-02: um teste por cláusula das SPEC-005-R05, SPEC-020 (fatura), SPEC-021 (metas) e SPEC-022."""

import uuid
from decimal import Decimal

from tests.clause_support import FIN, account, card, expense, one_time_income, verified_user


def progress(client, headers, competence="2026-03"):
    return client.get(f"{FIN}/budget-progress?competence={competence}", headers=headers).json()


def goal(client, headers, kind, target, category=None, threshold="90"):
    body = {"kind": kind, "target": target, "category_key": category, "alert_threshold": threshold}
    response = client.put(f"{FIN}/budget-goals", headers=headers, json=body)
    assert response.status_code == 200, response.text
    return response.json()


def by_kind(items, kind, category=None):
    return next(i for i in items if i["kind"] == kind and i["category_key"] == category)


def invoice(client, headers, card_id, competence="2026-03"):
    return client.get(
        f"{FIN}/credit-cards/{card_id}/invoice?competence={competence}", headers=headers
    )


def dashboard(client, headers, start, end):
    return client.get(f"{FIN}/dashboard?start={start}&end={end}", headers=headers)


def spending(client, headers, start, end):
    return client.get(f"{FIN}/spending-by-category?start={start}&end={end}", headers=headers)


# ---------------- SPEC-005 ----------------
def test_SPEC_005_R05_each_entry_links_to_one_account_or_card(client, app):
    headers = verified_user(client, app)
    account_id, card_id = account(client, headers), card(client, headers)
    expense(client, headers, "10", account_id=account_id)
    expense(client, headers, "20", credit_card_id=card_id)
    one_time_income(client, headers, "30", account_id=account_id)
    items = client.get(f"{FIN}/expenses", headers=headers).json()
    assert {(i["account_id"], i["credit_card_id"]) for i in items} == {
        (account_id, None),
        (None, card_id),
    }
    both = client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={
            "description": "Ambos",
            "amount": "5",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-03-10",
            "account_id": account_id,
            "credit_card_id": card_id,
        },
    )
    assert both.status_code == 422


# ---------------- SPEC-020 ----------------
def test_SPEC_020_R01_R03_invoice_sums_card_entries_of_the_cycle(client, app):
    headers = verified_user(client, app)
    card_id = card(client, headers, "1000")
    # Fechamento no dia 10 (OPEN-12): até o dia 10 entra na fatura de março; depois, abril.
    expense(client, headers, "100", "2026-02-11", credit_card_id=card_id)
    expense(client, headers, "200", "2026-03-10", credit_card_id=card_id)
    expense(client, headers, "999", "2026-03-11", credit_card_id=card_id)
    data = invoice(client, headers, card_id).json()
    assert Decimal(data["invoice_total"]) == Decimal("300")
    assert data["competence"] == "2026-03" and data["due_day"] == 20


def test_SPEC_020_R02_other_card_or_owner_does_not_enter_the_invoice(client, app):
    headers = verified_user(client, app)
    card_id, other_card = card(client, headers), card(client, headers)
    account_id = account(client, headers)
    expense(client, headers, "50", credit_card_id=other_card)
    expense(client, headers, "70", account_id=account_id)
    assert Decimal(invoice(client, headers, card_id).json()["invoice_total"]) == 0
    intruder = verified_user(client, app, "intruso@example.com")
    assert invoice(client, intruder, card_id).status_code == 404
    assert invoice(client, headers, card_id, "2026-13").status_code == 400


def test_SPEC_020_R04_available_limit_is_limit_minus_invoice(client, app):
    headers = verified_user(client, app)
    card_id = card(client, headers, "1000")
    expense(client, headers, "300", credit_card_id=card_id)
    data = invoice(client, headers, card_id).json()
    assert Decimal(data["available_limit"]) == Decimal("700")
    assert Decimal(data["credit_limit"]) == Decimal("1000")


def test_SPEC_020_R05_near_limit_flag_from_80_percent(client, app):
    headers = verified_user(client, app)
    card_id = card(client, headers, "1000")
    expense(client, headers, "799.99", credit_card_id=card_id)
    assert invoice(client, headers, card_id).json()["near_limit"] is False
    expense(client, headers, "0.01", credit_card_id=card_id)
    assert invoice(client, headers, card_id).json()["near_limit"] is True


# ---------------- SPEC-021 ----------------
def test_SPEC_021_R01_goals_progress_and_overrun_signal(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "expense_total", "100")
    expense(client, headers, "120", account_id=account_id)
    item = by_kind(progress(client, headers), "expense_total")
    assert Decimal(item["percentage"]) == Decimal("120") and item["status"] == "exceeded"


def test_SPEC_021_R02_invalid_goals_are_refused(client, app):
    headers = verified_user(client, app)
    for body in (
        {"kind": "expense_total", "target": "0"},
        {"kind": "expense_total", "target": "-5"},
        {"kind": "category_expense", "target": "10"},
        {"kind": "expense_total", "target": "10", "category_key": "standard:lazer"},
        {"kind": "expense_total", "target": "10", "alert_threshold": "60"},
    ):
        assert client.put(f"{FIN}/budget-goals", headers=headers, json=body).status_code == 422
    unknown = client.put(
        f"{FIN}/budget-goals",
        headers=headers,
        json={"kind": "category_expense", "target": "10", "category_key": "standard:inexistente"},
    )
    assert unknown.status_code == 404


def test_SPEC_021_R03_monthly_expense_ceiling(client, app):
    headers = verified_user(client, app)
    created = goal(client, headers, "expense_total", "1500")
    assert created["kind"] == "expense_total" and Decimal(created["target"]) == Decimal("1500")


def test_SPEC_021_R04_monthly_income_floor(client, app):
    headers = verified_user(client, app)
    created = goal(client, headers, "income_total", "5000")
    assert created["kind"] == "income_total" and Decimal(created["target"]) == Decimal("5000")


def test_SPEC_021_R05_goal_can_be_edited_without_duplicating(client, app):
    headers = verified_user(client, app)
    first = goal(client, headers, "expense_total", "100")
    edited = goal(client, headers, "expense_total", "250")
    assert edited["id"] == first["id"] and Decimal(edited["target"]) == Decimal("250")
    assert len(progress(client, headers)) == 1


def test_SPEC_021_R06_signals_overrun_and_income_below_floor(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "expense_total", "100")
    goal(client, headers, "income_total", "1000")
    expense(client, headers, "150", account_id=account_id)
    one_time_income(client, headers, "400", account_id=account_id)
    items = progress(client, headers)
    assert by_kind(items, "expense_total")["status"] == "exceeded"
    assert by_kind(items, "income_total")["status"] == "below_target"
    one_time_income(client, headers, "600", account_id=account_id)
    assert by_kind(progress(client, headers), "income_total")["status"] == "reached"


def test_SPEC_021_R07_category_monthly_ceiling(client, app):
    headers = verified_user(client, app)
    created = goal(client, headers, "category_expense", "500", "standard:lazer")
    assert created["category_key"] == "standard:lazer"


def test_SPEC_021_R08_category_alert_at_threshold_and_over_100(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "category_expense", "100", "standard:lazer", threshold="85")
    expense(client, headers, "85", category="standard:lazer", account_id=account_id)
    assert by_kind(progress(client, headers), "category_expense", "standard:lazer")["status"] == (
        "alert"
    )
    expense(client, headers, "20", category="standard:lazer", account_id=account_id)
    assert by_kind(progress(client, headers), "category_expense", "standard:lazer")["status"] == (
        "exceeded"
    )


def test_SPEC_021_R09_categories_without_goal_have_no_alert(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "category_expense", "100", "standard:lazer")
    expense(client, headers, "999", category="standard:alimentacao", account_id=account_id)
    items = progress(client, headers)
    assert [i["category_key"] for i in items] == ["standard:lazer"]
    assert items[0]["status"] == "on_track"


def test_SPEC_021_R10_progress_for_general_expense_and_income_goals(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "expense_total", "200")
    goal(client, headers, "income_total", "400")
    expense(client, headers, "50", account_id=account_id)
    one_time_income(client, headers, "100", account_id=account_id)
    items = progress(client, headers)
    assert Decimal(by_kind(items, "expense_total")["percentage"]) == Decimal("25")
    assert Decimal(by_kind(items, "income_total")["percentage"]) == Decimal("25")


def test_SPEC_021_R11_one_progress_bar_per_category_goal(client, app):
    headers = verified_user(client, app)
    goal(client, headers, "category_expense", "100", "standard:lazer")
    goal(client, headers, "category_expense", "300", "standard:moradia")
    keys = {i["category_key"] for i in progress(client, headers)}
    assert keys == {"standard:lazer", "standard:moradia"}


def test_SPEC_021_R12_color_band_follows_proximity(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "expense_total", "100")
    statuses = []
    for amount in ("60", "15", "15", "20"):  # 60%, 75%, 90%, 110%
        expense(client, headers, amount, account_id=account_id)
        statuses.append(by_kind(progress(client, headers), "expense_total")["status"])
    assert statuses == ["on_track", "attention", "alert", "exceeded"]


def test_SPEC_021_R13_progress_recalculated_on_new_entry(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    goal(client, headers, "expense_total", "100")
    assert Decimal(by_kind(progress(client, headers), "expense_total")["actual"]) == 0
    expense(client, headers, "40", account_id=account_id)
    assert Decimal(by_kind(progress(client, headers), "expense_total")["actual"]) == Decimal("40")


# ---------------- SPEC-022 ----------------
def test_SPEC_022_R01_R11_income_composition_without_diluting_plr(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    client.post(
        f"{FIN}/recurring-incomes",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={"description": "Salário", "amount": "100", "starts_on": "2026-01-01"},
    )
    client.post(
        f"{FIN}/bonuses",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={
            "description": "PLR",
            "amount": "50",
            "periodicity": "annual",
            "reference_month": 3,
            "starts_on": "2026-01-01",
        },
    )
    expense(client, headers, "40", account_id=account_id)
    months = dashboard(client, headers, "2026-02", "2026-03").json()
    march = months[-1]
    assert Decimal(march["total"]) == Decimal("150") and Decimal(march["bonus"]) == Decimal("50")
    assert Decimal(march["balance_variation"]) == Decimal("110")
    assert Decimal(months[0]["bonus"]) == 0


def test_SPEC_022_R02_invalid_period_and_foreign_data(client, app):
    headers = verified_user(client, app)
    assert dashboard(client, headers, "2026-13", "2026-03").status_code == 400
    assert spending(client, headers, "x", "2026-03").status_code == 400
    assert spending(client, headers, "2026-03", "2026-03").json() == []
    other = verified_user(client, app, "outro@example.com")
    expense(client, other, "77", account_id=account(client, other))
    assert spending(client, headers, "2026-03", "2026-03").json() == []


def test_SPEC_022_R03_R06_total_and_share_per_category(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    expense(client, headers, "75", category="standard:moradia", account_id=account_id)
    expense(client, headers, "25", category="standard:lazer", account_id=account_id)
    data = spending(client, headers, "2026-03", "2026-03").json()
    assert [(i["category_key"], Decimal(i["total"]), Decimal(i["percentage"])) for i in data] == [
        ("standard:moradia", Decimal("75"), Decimal("75")),
        ("standard:lazer", Decimal("25"), Decimal("25")),
    ]


def test_SPEC_022_R04_filter_by_month(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    expense(client, headers, "10", "2026-03-10", account_id=account_id)
    expense(client, headers, "90", "2026-04-10", account_id=account_id)
    march = spending(client, headers, "2026-03", "2026-03").json()
    assert [Decimal(i["total"]) for i in march] == [Decimal("10")]


def test_SPEC_022_R05_categories_without_spending_do_not_appear(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    expense(client, headers, "10", category="standard:lazer", account_id=account_id)
    keys = [i["category_key"] for i in spending(client, headers, "2026-03", "2026-03").json()]
    assert keys == ["standard:lazer"]


def test_SPEC_022_R07_consolidated_balance_month_by_month(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    one_time_income(client, headers, "100", "2026-02-05", account_id=account_id)
    expense(client, headers, "30", "2026-02-10", account_id=account_id)
    expense(client, headers, "20", "2026-03-10", account_id=account_id)
    months = dashboard(client, headers, "2026-02", "2026-03").json()
    assert [Decimal(m["balance_variation"]) for m in months] == [Decimal("70"), Decimal("-20")]


def test_SPEC_022_R08_R12_selectable_month_interval(client, app):
    headers = verified_user(client, app)
    six = dashboard(client, headers, "2026-01", "2026-06").json()
    twelve = dashboard(client, headers, "2025-07", "2026-06").json()
    assert len(six) == 6 and len(twelve) == 12
    assert [m["competence"] for m in six][:2] == ["2026-01", "2026-02"]


def test_SPEC_022_R09_dashboard_updates_after_new_entry(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    before = dashboard(client, headers, "2026-03", "2026-03").json()[0]
    expense(client, headers, "15", account_id=account_id)
    after = dashboard(client, headers, "2026-03", "2026-03").json()[0]
    assert Decimal(after["expenses"]) - Decimal(before["expenses"]) == Decimal("15")


def test_SPEC_022_R10_income_and_expense_side_by_side_per_month(client, app):
    headers = verified_user(client, app)
    months = dashboard(client, headers, "2026-01", "2026-03").json()
    assert all({"competence", "total", "expenses"} <= set(m) for m in months)


def test_SPEC_022_R13_months_with_spending_above_income_are_identifiable(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers)
    one_time_income(client, headers, "50", "2026-03-05", account_id=account_id)
    expense(client, headers, "80", "2026-03-10", account_id=account_id)
    march = dashboard(client, headers, "2026-03", "2026-03").json()[0]
    # O cliente web destaca o mês em vermelho quando despesas > receitas (Overview.tsx).
    assert Decimal(march["expenses"]) > Decimal(march["total"])
    assert Decimal(march["balance_variation"]) < 0
