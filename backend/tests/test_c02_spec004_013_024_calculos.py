"""C-02: um teste por cláusula das SPEC-004, SPEC-013 (calculadora) e SPEC-024 (objetivo)."""

from decimal import Decimal

from tests.clause_support import (
    FIN,
    clear_indicators,
    set_indicator,
    unverified_user,
    verified_user,
)

BASE = {
    "initial_amount": "1000",
    "monthly_contribution": "0",
    "annual_rate": "12",
    "term_months": 12,
}


# ---------------- SPEC-004 ----------------
def test_SPEC_004_R01_R03_gross_tax_and_net_are_identified(client, app):
    headers = verified_user(client, app)
    data = client.post(
        f"{FIN}/fixed-income-projections", headers=headers, json={**BASE, "product": "cdb"}
    ).json()
    assert data["gross_amount"] == "1120.00" and data["tax_rate"] == "20"
    assert data["estimated_tax"] == "24.00" and data["net_amount"] == "1096.00"


def test_SPEC_004_R02_unknown_product_or_session_is_refused(client, app):
    headers = verified_user(client, app)
    invalid = client.post(
        f"{FIN}/fixed-income-projections", headers=headers, json={**BASE, "product": "acoes"}
    )
    assert invalid.status_code == 422
    assert (
        client.post(f"{FIN}/fixed-income-projections", json={**BASE, "product": "cdb"}).status_code
        == 401
    )


def test_SPEC_004_R04_internal_versioned_rule_by_term_and_exempt_savings(client, app):
    headers = verified_user(client, app)
    rates = {
        months: client.post(
            f"{FIN}/fixed-income-projections",
            headers=headers,
            json={**BASE, "term_months": months, "product": "tesouro"},
        ).json()["tax_rate"]
        for months in (6, 12, 24, 25)
    }
    assert rates == {6: "22.5", 12: "20", 24: "17.5", 25: "15"}
    savings = client.post(
        f"{FIN}/fixed-income-projections", headers=headers, json={**BASE, "product": "poupanca"}
    ).json()
    assert savings["estimated_tax"] == "0.00"


# ---------------- SPEC-013 ----------------
def test_SPEC_013_R01_R07_R08_R09_monthly_table_chart_data_and_summary(client, app):
    headers = verified_user(client, app)
    data = client.post(
        f"{FIN}/calculator", headers=headers, json={**BASE, "monthly_contribution": "100"}
    ).json()
    series = data["monthly_series"]
    assert len(series) == 12 and series[0]["month"] == 1
    assert set(series[0]) == {
        "month",
        "opening_balance",
        "contribution",
        "interest",
        "closing_balance",
    }
    assert data["invested"] == "2200.00"
    assert Decimal(data["gross_amount"]) == Decimal(series[-1]["closing_balance"])
    assert Decimal(data["interest"]) == Decimal(data["gross_amount"]) - Decimal(data["invested"])


def test_SPEC_013_R02_invalid_inputs_are_refused(client, app):
    headers = verified_user(client, app)
    negative = client.post(f"{FIN}/calculator", headers=headers, json={**BASE, "annual_rate": "-1"})
    zero_term = client.post(f"{FIN}/calculator", headers=headers, json={**BASE, "term_months": 0})
    assert negative.status_code == zero_term.status_code == 422
    assert (
        client.post(f"{FIN}/calculator", headers=unverified_user(client), json=BASE).status_code
        == 403
    )


def test_SPEC_013_R03_rate_period_selector_monthly_or_annual(client, app):
    headers = verified_user(client, app)
    monthly = client.post(
        f"{FIN}/calculator",
        headers=headers,
        json={**BASE, "annual_rate": "1", "rate_period": "monthly"},
    ).json()
    # 1% a.m. por 12 meses = 1,01^12 ≈ 1,126825 (sem dividir taxa anual por 12, C-04).
    assert monthly["gross_amount"] == "1126.83"
    assert "já é mensal" in monthly["rate_explanation"]


def test_SPEC_013_R04_term_unit_selector_months_or_years(client, app):
    headers = verified_user(client, app)
    years = client.post(
        f"{FIN}/calculator", headers=headers, json={**BASE, "term_months": 1, "term_unit": "years"}
    ).json()
    assert years["gross_amount"] == "1120.00" and len(years["monthly_series"]) == 12
    too_long = client.post(
        f"{FIN}/calculator", headers=headers, json={**BASE, "term_months": 61, "term_unit": "years"}
    )
    assert too_long.status_code == 422


def test_SPEC_013_R05_R10_rate_help_explains_in_plain_language(client, app):
    headers = verified_user(client, app)
    data = client.post(f"{FIN}/calculator", headers=headers, json=BASE).json()
    assert "taxa mensal equivalente" in data["rate_explanation"]
    assert "fim de cada mês" in data["rate_explanation"]


def test_SPEC_013_R06_rate_from_official_indicator_or_manual(client, app):
    headers = verified_user(client, app)
    clear_indicators(app)
    manual = client.post(f"{FIN}/calculator", headers=headers, json=BASE).json()
    assert manual["rate_source"] == {"origin": "manual"}
    missing = client.post(
        f"{FIN}/calculator", headers=headers, json={**BASE, "indicator_code": "cdi"}
    )
    assert missing.status_code == 503 and missing.json()["detail"] == "indicator_unavailable"
    set_indicator(app, "cdi", "12")
    official = client.post(
        f"{FIN}/calculator",
        headers=headers,
        json={**BASE, "annual_rate": "1", "indicator_code": "cdi"},
    ).json()
    assert official["gross_amount"] == "1120.00"
    assert official["rate_source"]["origin"] == "cdi"
    assert official["rate_source"]["reference_date"] == "2026-10-30"
    clear_indicators(app)


# ---------------- SPEC-024 ----------------
TARGET = {"target_amount": "1200", "initial_amount": "0", "annual_rate": "0", "term_months": 12}


def test_SPEC_024_R01_R03_R04_monthly_contribution_for_target(client, app):
    headers = verified_user(client, app)
    data = client.post(f"{FIN}/target-contributions", headers=headers, json=TARGET).json()
    assert data == {"monthly_contribution_needed": "100.00", "feasible": True, "warning": None}
    with_return = client.post(
        f"{FIN}/target-contributions", headers=headers, json={**TARGET, "annual_rate": "12"}
    ).json()
    assert Decimal(with_return["monthly_contribution_needed"]) < Decimal("100")


def test_SPEC_024_R02_invalid_target_is_refused(client, app):
    headers = verified_user(client, app)
    response = client.post(
        f"{FIN}/target-contributions", headers=headers, json={**TARGET, "target_amount": "0"}
    )
    assert response.status_code == 422


def test_SPEC_024_R05_warns_when_target_is_not_feasible(client, app):
    headers = verified_user(client, app)
    data = client.post(
        f"{FIN}/target-contributions",
        headers=headers,
        json={**TARGET, "available_monthly_amount": "50"},
    ).json()
    assert data["feasible"] is False and "supera" in data["warning"]
