"""C-02: testes por cláusula das SPEC-007, 008 (renda fixa), 009 (renda variável) e 010."""

from datetime import UTC, datetime, timedelta

from tests.clause_support import (
    FIN,
    clear_indicators,
    set_indicator,
    unverified_user,
    verified_user,
)

SIM = {
    "label": "CDB",
    "product": "cdb",
    "initial_amount": "1000",
    "monthly_contribution": "100",
    "annual_rate": "10",
    "term_months": 24,
}
VARIABLE = {
    "label": "Ações",
    "initial_amount": "1000",
    "monthly_contribution": "100",
    "expected_annual_return": "12",
    "term_months": 12,
}


# ---------------- SPEC-007 ----------------
def test_SPEC_007_R01_R05_cached_indicator_with_unit_reference_and_timestamp(client, app):
    headers = verified_user(client, app)
    set_indicator(app, "ipca", "4.5")
    data = client.get(f"{FIN}/indicators/ipca", headers=headers).json()
    assert data["code"] == "ipca" and data["value"] == "4.500000"
    assert data["unit"] == "percentual_anual" and data["reference_date"] == "2026-10-30"
    assert data["checked_at"] and data["source"] == "BCB_SGS" and data["stale"] is False
    clear_indicators(app)


def test_SPEC_007_R02_missing_indicator_is_unavailable_never_zero(client, app):
    headers = verified_user(client, app)
    clear_indicators(app)
    response = client.get(f"{FIN}/indicators/selic", headers=headers)
    assert response.status_code == 503 and response.json()["detail"] == "indicator_unavailable"


def test_SPEC_007_R07_source_failure_keeps_last_value_with_warning(client, app):
    headers = verified_user(client, app)
    set_indicator(app, "selic", "11", checked=datetime.now(UTC) - timedelta(days=3))
    data = client.get(f"{FIN}/indicators/selic", headers=headers).json()
    assert data["value"] == "11.000000" and data["stale"] is True
    used = client.post(
        f"{FIN}/simulations/fixed-income", headers=headers, json={**SIM, "indicator_code": "selic"}
    )
    source = used.json()["payload"]["rate_source"]
    assert source["stale"] is True and "Último valor" in source["notice"]
    clear_indicators(app)


def test_SPEC_007_R08_reference_date_shown_when_indicator_is_used(client, app):
    headers = verified_user(client, app)
    set_indicator(app, "cdi", "10")
    payload = client.post(
        f"{FIN}/simulations/fixed-income", headers=headers, json={**SIM, "indicator_code": "cdi"}
    ).json()["payload"]
    assert payload["rate_source"]["reference_date"] == "2026-10-30"
    clear_indicators(app)


# ---------------- SPEC-008 ----------------
def test_SPEC_008_R01_R06_traceable_gross_and_net_projection(client, app):
    headers = verified_user(client, app)
    data = client.post(f"{FIN}/simulations/fixed-income", headers=headers, json=SIM).json()
    payload = data["payload"]
    assert data["kind"] == "fixed_income"
    assert {"gross_amount", "estimated_tax", "net_amount", "tax_rate", "rate_source"} <= set(
        payload
    )
    assert payload["tax_rate"] == "17.5"  # 24 meses na tabela regressiva
    assert data["final_amount"] == payload["net_amount"]


def test_SPEC_008_R02_invalid_or_unauthorized_simulation_is_refused(client, app):
    headers = verified_user(client, app)
    assert (
        client.post(
            f"{FIN}/simulations/fixed-income", headers=headers, json={**SIM, "term_months": 0}
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{FIN}/simulations/fixed-income", headers=unverified_user(client), json=SIM
        ).status_code
        == 403
    )


def test_SPEC_008_R03_cdb_tesouro_and_savings(client, app):
    headers = verified_user(client, app)
    for product in ("cdb", "tesouro", "poupanca"):
        response = client.post(
            f"{FIN}/simulations/fixed-income", headers=headers, json={**SIM, "product": product}
        )
        assert response.status_code == 201
    assert len(client.get(f"{FIN}/simulations", headers=headers).json()) == 3


def test_SPEC_008_R04_engine_fed_by_official_indicator(client, app):
    headers = verified_user(client, app)
    set_indicator(app, "selic", "10")
    official = client.post(
        f"{FIN}/simulations/fixed-income",
        headers=headers,
        json={**SIM, "annual_rate": "0", "indicator_code": "selic"},
    ).json()
    manual = client.post(f"{FIN}/simulations/fixed-income", headers=headers, json=SIM).json()
    assert official["payload"]["gross_amount"] == manual["payload"]["gross_amount"]
    assert official["payload"]["annual_rate"] == "10.000000"
    clear_indicators(app)


def test_SPEC_008_R05_manual_rate_overrides_suggestion(client, app):
    headers = verified_user(client, app)
    data = client.post(
        f"{FIN}/simulations/fixed-income", headers=headers, json={**SIM, "annual_rate": "13"}
    ).json()
    assert data["payload"]["annual_rate"] == "13" and data["payload"]["rate_source"] == {
        "origin": "manual"
    }


def test_SPEC_008_R07_shows_indicator_reference_date(client, app):
    headers = verified_user(client, app)
    set_indicator(app, "cdi", "10", reference=datetime(2026, 9, 30).date())
    source = client.post(
        f"{FIN}/simulations/fixed-income", headers=headers, json={**SIM, "indicator_code": "cdi"}
    ).json()["payload"]["rate_source"]
    assert source["origin"] == "cdi" and source["reference_date"] == "2026-09-30"
    clear_indicators(app)


# ---------------- SPEC-009 ----------------
def test_SPEC_009_R01_R06_projection_with_monthly_evolution(client, app):
    headers = verified_user(client, app)
    data = client.post(f"{FIN}/simulations/variable-income", headers=headers, json=VARIABLE).json()
    series = data["payload"]["monthly_series"]
    assert data["kind"] == "variable_income" and len(series) == 12
    assert series[-1]["closing_balance"] == data["final_amount"]


def test_SPEC_009_R02_invalid_ticker_or_values_are_refused(client, app):
    headers = verified_user(client, app)
    assert (
        client.post(
            f"{FIN}/simulations/variable-income",
            headers=headers,
            json={**VARIABLE, "ticker": "1234"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{FIN}/simulations/variable-income",
            headers=headers,
            json={**VARIABLE, "initial_amount": "-1"},
        ).status_code
        == 422
    )


def test_SPEC_009_R03_R04_ticker_prefills_current_price_and_history(client, app):
    headers = verified_user(client, app)
    app.state.clock = lambda: datetime(2026, 10, 29, 13, tzinfo=UTC)
    data = client.post(
        f"{FIN}/simulations/variable-income", headers=headers, json={**VARIABLE, "ticker": "petr4"}
    ).json()
    quote = data["payload"]["quote"]
    assert data["payload"]["ticker"] == "PETR4"
    assert quote["price"] == "31.2500" and len(quote["history"]) == 4


def test_SPEC_009_R05_projection_is_explicitly_not_a_guarantee(client, app):
    headers = verified_user(client, app)
    payload = client.post(
        f"{FIN}/simulations/variable-income", headers=headers, json=VARIABLE
    ).json()["payload"]
    assert "não é cotação nem garantia" in payload["disclaimer"]


# ---------------- SPEC-010 ----------------
def saved(client, headers, rate, product="cdb"):
    return client.post(
        f"{FIN}/simulations/fixed-income",
        headers=headers,
        json={**SIM, "annual_rate": rate, "product": product, "label": f"{product} {rate}"},
    ).json()["id"]


def test_SPEC_010_R01_R03_R04_R05_side_by_side_percentage_and_best(client, app):
    headers = verified_user(client, app)
    savings, cdb, tesouro = (
        saved(client, headers, "6", "poupanca"),
        saved(client, headers, "12"),
        saved(client, headers, "10", "tesouro"),
    )
    data = client.post(
        f"{FIN}/simulations/compare",
        headers=headers,
        json={"simulation_ids": [savings, cdb, tesouro]},
    ).json()
    assert [item["id"] for item in data["simulations"]] == [savings, cdb, tesouro]
    assert (
        data["difference_from_first"][0] == "0.00"
        and data["difference_percent_from_first"][0] == "0.00"
    )
    assert all(value is not None for value in data["difference_percent_from_first"])
    finals = {item["id"]: float(item["final_amount"]) for item in data["simulations"]}
    assert data["best_simulation_id"] == max(finals, key=finals.get)


def test_SPEC_010_R02_needs_two_owned_simulations(client, app):
    headers = verified_user(client, app)
    own = saved(client, headers, "10")
    other = saved(client, verified_user(client, app, "outro@example.com"), "10")
    assert (
        client.post(
            f"{FIN}/simulations/compare", headers=headers, json={"simulation_ids": [own]}
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{FIN}/simulations/compare", headers=headers, json={"simulation_ids": [own, other]}
        ).status_code
        == 404
    )
