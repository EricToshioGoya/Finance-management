"""C-02: SPEC-020 com a política OPEN-12 (2026-10-31): ciclo por fechamento, parcelas e alerta."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.domain.cartao import competencia_da_fatura, dividir_parcelas, somar_meses
from tests.clause_support import FIN, account, verified_user


def new_card(client, headers, limit="1000", closing=10, **extra):
    response = client.post(
        f"{FIN}/credit-cards",
        headers=headers,
        json={"name": "Cartão", "credit_limit": limit, "closing_day": closing, "due_day": 20}
        | extra,
    )
    assert response.status_code == 201, response.text
    return response.json()


def buy(client, headers, card_id, amount, when, installments=1, key=None):
    return client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": key or str(uuid.uuid4())},
        json={
            "description": "Compra",
            "amount": amount,
            "category_key": "standard:alimentacao",
            "occurred_on": when,
            "credit_card_id": card_id,
            "installments": installments,
        },
    )


def invoice(client, headers, card_id, competence):
    return client.get(
        f"{FIN}/credit-cards/{card_id}/invoice?competence={competence}", headers=headers
    ).json()


# ---------------- domínio puro ----------------
@pytest.mark.parametrize(
    ("purchase", "closing", "expected"),
    [
        (date(2026, 3, 10), 10, date(2026, 3, 1)),
        (date(2026, 3, 11), 10, date(2026, 4, 1)),
        (date(2026, 2, 28), 31, date(2026, 2, 1)),  # 31 → último dia de fevereiro
        (date(2026, 12, 15), 10, date(2027, 1, 1)),
    ],
)
def test_SPEC_020_R03_invoice_cycle_by_closing_day(purchase, closing, expected):
    assert competencia_da_fatura(purchase, closing) == expected


def test_SPEC_020_R03_installments_keep_cents_residue_on_first():
    assert dividir_parcelas(Decimal("100.00"), 3) == [
        Decimal("33.34"),
        Decimal("33.33"),
        Decimal("33.33"),
    ]
    assert sum(dividir_parcelas(Decimal("0.05"), 4)) == Decimal("0.05")
    with pytest.raises(ValueError):
        dividir_parcelas(Decimal("0.03"), 4)
    assert somar_meses(date(2026, 1, 31), 1) == date(2026, 2, 28)


# ---------------- API ----------------
def test_SPEC_020_R03_purchase_after_closing_goes_to_next_invoice(client, app):
    headers = verified_user(client, app)
    card = new_card(client, headers)
    buy(client, headers, card["id"], "100", "2026-03-10")
    buy(client, headers, card["id"], "50", "2026-03-11")
    assert Decimal(invoice(client, headers, card["id"], "2026-03")["invoice_total"]) == 100
    assert Decimal(invoice(client, headers, card["id"], "2026-04")["invoice_total"]) == 50


def test_SPEC_020_R03_installments_spread_over_following_invoices(client, app):
    headers = verified_user(client, app)
    card = new_card(client, headers)
    first = buy(client, headers, card["id"], "100.00", "2026-03-05", installments=3)
    assert first.status_code == 201
    body = first.json()
    assert body["installment_number"] == 1 and body["installment_count"] == 3
    assert body["amount"] == "33.34"
    totals = [
        Decimal(invoice(client, headers, card["id"], month)["invoice_total"])
        for month in ("2026-03", "2026-04", "2026-05", "2026-06")
    ]
    assert totals == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33"), 0]
    items = client.get(f"{FIN}/expenses", headers=headers).json()
    assert {i["installment_group"] for i in items} == {body["installment_group"]}


def test_SPEC_020_R04_available_limit_discounts_future_installments(client, app):
    headers = verified_user(client, app)
    card = new_card(client, headers, limit="1000")
    buy(client, headers, card["id"], "600.00", "2026-03-05", installments=3)
    buy(client, headers, card["id"], "100", "2026-03-06")
    march = invoice(client, headers, card["id"], "2026-03")
    assert Decimal(march["invoice_total"]) == Decimal("300")
    assert Decimal(march["future_installments"]) == Decimal("400")
    assert Decimal(march["available_limit"]) == Decimal("300")


def test_SPEC_020_R05_alert_threshold_is_configurable_per_card(client, app):
    headers = verified_user(client, app)
    default = new_card(client, headers)
    strict = new_card(client, headers, alert_threshold="70")
    assert Decimal(default["alert_threshold"]) == 80 and Decimal(strict["alert_threshold"]) == 70
    for card in (default, strict):
        buy(client, headers, card["id"], "750", "2026-03-05")
    assert invoice(client, headers, default["id"], "2026-03")["near_limit"] is False
    assert invoice(client, headers, strict["id"], "2026-03")["near_limit"] is True
    updated = client.patch(
        f"{FIN}/credit-cards/{default['id']}", headers=headers, json={"alert_threshold": "75"}
    )
    assert updated.status_code == 200 and Decimal(updated.json()["alert_threshold"]) == 75
    assert invoice(client, headers, default["id"], "2026-03")["near_limit"] is True


def test_SPEC_020_R02_invalid_threshold_installments_and_foreign_card_are_refused(client, app):
    headers = verified_user(client, app)
    card = new_card(client, headers)
    assert (
        client.patch(
            f"{FIN}/credit-cards/{card['id']}", headers=headers, json={"alert_threshold": "60"}
        ).status_code
        == 422
    )
    invalid = client.post(
        f"{FIN}/credit-cards",
        headers=headers,
        json={
            "name": "X",
            "credit_limit": "10",
            "closing_day": 1,
            "due_day": 2,
            "alert_threshold": "101",
        },
    )
    assert invalid.status_code == 422
    on_account = client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={
            "description": "Conta",
            "amount": "10",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-03-05",
            "account_id": account(client, headers),
            "installments": 2,
        },
    )
    assert on_account.status_code == 422
    assert buy(client, headers, card["id"], "0.03", "2026-03-05", installments=4).status_code == 422
    intruder = verified_user(client, app, "intruso-cartao@example.com")
    assert (
        client.patch(
            f"{FIN}/credit-cards/{card['id']}", headers=intruder, json={"alert_threshold": "90"}
        ).status_code
        == 404
    )


def test_SPEC_020_installment_resend_with_same_key_does_not_duplicate(client, app):
    headers = verified_user(client, app)
    card = new_card(client, headers)
    first = buy(client, headers, card["id"], "90", "2026-03-05", installments=3, key="parcelado-1")
    again = buy(client, headers, card["id"], "90", "2026-03-05", installments=3, key="parcelado-1")
    assert first.json()["id"] == again.json()["id"]
    assert len(client.get(f"{FIN}/expenses", headers=headers).json()) == 3
