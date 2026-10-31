"""SPEC-053: structured CVM values are sourced, unit-labelled and never summed by revision."""

COMPANIES = "/api/v1/companies"
PASSWORD = "StrongPassword123"


def login(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Indicator Reader", "email": "indicators@example.com", "password": PASSWORD},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "indicators@example.com", "password": PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def company_id(client, headers, ticker):
    response = client.get(f"{COMPANIES}?query={ticker}", headers=headers)
    assert response.status_code == 200
    return response.json()[0]["id"]


def test_spec053_returns_three_structured_metrics_in_two_periods_with_source_and_unit(client):
    headers = login(client)
    petr4 = company_id(client, headers, "PETR4")
    denied = client.get(f"{COMPANIES}/{petr4}/financial-indicators")
    response = client.get(f"{COMPANIES}/{petr4}/financial-indicators", headers=headers)
    assert denied.status_code == 401
    assert response.status_code == 200
    rows = response.json()
    assert {row["metric"] for row in rows} == {"net_revenue", "net_income", "equity"}
    assert {row["reference_period"] for row in rows} == {"Exercício 2025", "2º trimestre de 2026"}
    assert {row["unit"] for row in rows} == {"BRL_THOUSANDS"}
    assert all(row["source_name"].startswith("Dados Abertos CVM") for row in rows)
    assert all(row["source_url"].startswith("https://dados.cvm.gov.br/") for row in rows)
    assert all(row["reference_date"] and row["synced_at"] for row in rows)
    assert all("pdf" not in row and "content" not in row for row in rows)


def test_spec053_filters_only_known_metric_and_period_kinds(client):
    headers = login(client)
    petr4 = company_id(client, headers, "PETR4")
    revenue = client.get(
        f"{COMPANIES}/{petr4}/financial-indicators?metric=net_revenue&period_kind=annual",
        headers=headers,
    )
    invalid_metric = client.get(
        f"{COMPANIES}/{petr4}/financial-indicators?metric=market_price", headers=headers
    )
    assert revenue.status_code == 200
    assert len(revenue.json()) == 1
    assert revenue.json()[0]["metric"] == "net_revenue"
    assert revenue.json()[0]["period_kind"] == "annual"
    assert invalid_metric.status_code == 422


def test_spec053_restatement_remains_visible_but_only_latest_revision_is_effective(client):
    headers = login(client)
    vale3 = company_id(client, headers, "VALE3")
    response = client.get(
        f"{COMPANIES}/{vale3}/financial-indicators?metric=net_income&period_kind=quarterly",
        headers=headers,
    )
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 2
    assert {row["status"] for row in rows} == {"active", "restated"}
    assert sum(row["effective"] for row in rows) == 1
    effective = next(row for row in rows if row["effective"])
    restated = next(row for row in rows if not row["effective"])
    assert effective["status"] == "active"
    assert effective["value"] != restated["value"]


def test_spec053_unknown_company_is_not_confirmed_as_data(client):
    headers = login(client)
    response = client.get(
        f"{COMPANIES}/00000000-0000-0000-0000-000000000000/financial-indicators",
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "company_not_found"
