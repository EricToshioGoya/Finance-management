"""SPEC-012: local CVM metadata catalogue, filters and safe official-link checks."""

from unittest.mock import MagicMock

from app.infrastructure.models import OfficialDocumentRecord

PREFIX = "/api/v1/auth"
COMPANIES = "/api/v1/companies"
PASSWORD = "StrongPassword123"


def login(client):
    assert (
        client.post(
            f"{PREFIX}/register",
            json={"name": "Company Reader", "email": "companies@example.com", "password": PASSWORD},
        ).status_code
        == 201
    )
    response = client.post(
        f"{PREFIX}/login", json={"email": "companies@example.com", "password": PASSWORD}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_spec012_searches_ticker_cnpj_and_name_with_no_private_payload(client):
    headers = login(client)
    assert client.get(COMPANIES).status_code == 401
    by_ticker = client.get(f"{COMPANIES}?query=PETR4", headers=headers)
    by_cnpj = client.get(f"{COMPANIES}?query=33.592.510", headers=headers)
    by_name = client.get(f"{COMPANIES}?query=petroleo", headers=headers)
    assert by_ticker.status_code == by_cnpj.status_code == by_name.status_code == 200
    assert by_ticker.json()[0]["ticker"] == "PETR4"
    assert by_cnpj.json()[0]["ticker"] == "VALE3"
    assert by_name.json()[0]["legal_name"].startswith("PETRÓLEO")
    assert set(by_ticker.json()[0]) == {"id", "ticker", "cnpj", "legal_name", "sector"}
    assert client.get(f"{COMPANIES}?query=does-not-exist", headers=headers).json() == []


def test_spec012_lists_metadata_filters_and_never_returns_document_binary(client):
    headers = login(client)
    company = client.get(f"{COMPANIES}?query=PETR4", headers=headers).json()[0]
    documents = client.get(f"{COMPANIES}/{company['id']}/documents", headers=headers)
    assert documents.status_code == 200
    rows = documents.json()
    assert {row["document_type"] for row in rows} == {"DFP", "ITR", "FRE", "IPE"}
    assert all(row["official_url"].startswith("https://www.rad.cvm.gov.br/") for row in rows)
    assert all("pdf" not in row and "content" not in row for row in rows)
    only_itr = client.get(
        f"{COMPANIES}/{company['id']}/documents?document_type=ITR", headers=headers
    )
    assert len(only_itr.json()) == 1 and only_itr.json()[0]["document_type"] == "ITR"
    after_august = client.get(
        f"{COMPANIES}/{company['id']}/documents?starts_on=2026-08-01", headers=headers
    )
    assert {row["document_type"] for row in after_august.json()} == {"ITR", "IPE"}
    assert (
        client.get(
            f"{COMPANIES}/{company['id']}/documents?starts_on=2026-09-01&ends_on=2026-08-01",
            headers=headers,
        ).status_code
        == 422
    )


def test_spec012_checks_only_official_host_and_records_link_status(client, app, monkeypatch):
    headers = login(client)
    company = client.get(f"{COMPANIES}?query=VALE3", headers=headers).json()[0]
    document = client.get(
        f"{COMPANIES}/{company['id']}/documents?document_type=DFP", headers=headers
    ).json()[0]
    response = MagicMock()
    response.status = 200
    opener = MagicMock()
    opener.__enter__.return_value = response
    monkeypatch.setattr("app.application.companies.urlopen", MagicMock(return_value=opener))
    checked = client.post(f"{COMPANIES}/documents/{document['id']}/link-check", headers=headers)
    assert checked.status_code == 200
    assert checked.json()["link_status"] == "available" and checked.json()["last_checked_at"]
    with app.state.sessions() as db:
        record = db.get(OfficialDocumentRecord, document["id"])
        record.official_url = "https://example.invalid/document"
        db.commit()
    unsafe = client.post(f"{COMPANIES}/documents/{document['id']}/link-check", headers=headers)
    assert unsafe.json()["link_status"] == "broken"
    assert (
        client.get(f"{COMPANIES}/00000000-0000-0000-0000-000000000000", headers=headers).status_code
        == 404
    )
