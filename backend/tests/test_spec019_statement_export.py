"""SPEC-019: own financial statement downloads, periods, CSV and PDF summaries."""

import csv
import io
import uuid
from datetime import UTC, datetime

import pytest

from app.infrastructure.models import UserRecord

PREFIX = "/api/v1/auth"


def owner(client, app, email="export@example.com"):
    password = "StrongPassword123"
    created = client.post(
        f"{PREFIX}/register", json={"name": "Export Owner", "email": email, "password": password}
    ).json()
    with app.state.sessions() as db:
        db.get(UserRecord, uuid.UUID(created["id"])).email_verified_at = datetime.now(UTC)
        db.commit()
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": password}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def add_data(client, headers):
    account = client.post(
        f"{PREFIX}/financial/accounts",
        headers=headers,
        json={"name": "Conta", "account_type": "checking", "initial_balance": "0"},
    ).json()["id"]
    income = {"description": "=Receita", "amount": "100", "occurred_on": "2026-01-10"}
    expense = {
        "description": "+Mercado",
        "amount": "30",
        "category_key": "standard:alimentacao",
        "occurred_on": "2026-01-12",
        "account_id": account,
    }
    assert (
        client.post(
            f"{PREFIX}/financial/one-time-incomes",
            headers={**headers, "Idempotency-Key": "income"},
            json=income,
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"{PREFIX}/financial/expenses",
            headers={**headers, "Idempotency-Key": "expense"},
            json=expense,
        ).status_code
        == 201
    )


def test_csv_pdf_period_summary_and_formula_safety(client, app):
    """Cláusulas: SPEC-019-R01, SPEC-019-R03, SPEC-019-R05, SPEC-019-R06."""
    headers = owner(client, app)
    add_data(client, headers)
    query = "start=2026-01-01&end=2026-01-31"
    response = client.get(f"{PREFIX}/financial/exports/csv?{query}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=extrato.csv"
    rows = list(csv.reader(io.StringIO(response.text)))
    assert rows[0] == ["data", "tipo", "descrição", "categoria", "valor"]
    assert {row[2] for row in rows[1:]} == {"'=Receita", "'+Mercado"}
    pdf = client.get(f"{PREFIX}/financial/exports/pdf?{query}", headers=headers)
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-1.4")
    assert b"Saldo do per" in pdf.content and b"70.00" in pdf.content
    assert b"alimentacao" in pdf.content and b"receita" in pdf.content


@pytest.mark.parametrize("query", ["month=2026-01", "year=2026", "start=2026-01-01&end=2026-01-31"])
def test_all_supported_period_selectors_return_only_owner_data(client, app, query):
    """Cláusulas: SPEC-019-R04, SPEC-019-R06."""
    own = owner(client, app)
    other = owner(client, app, "other-export@example.com")
    add_data(client, own)
    response = client.get(f"{PREFIX}/financial/exports/csv?{query}", headers=other)
    assert response.status_code == 200 and "Receita" not in response.text
    assert client.get(f"{PREFIX}/financial/exports/csv?{query}", headers=own).status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/financial/exports/csv?start=invalid&end=2026-01-01",
        "/financial/exports/pdf?start=2026-02-01&end=2026-01-01",
        "/financial/exports/csv",
        "/financial/exports/pdf?month=2026-13",
    ],
)
def test_export_rejects_invalid_or_unauthenticated_request(client, app, path):
    """Cláusulas: SPEC-019-R02."""
    headers = owner(client, app)
    assert client.get(f"{PREFIX}{path}").status_code == 401
    assert client.get(f"{PREFIX}{path}", headers=headers).status_code == 400


def test_empty_statement_is_explicit_and_pdf_xref_is_valid(client, app):
    headers = owner(client, app)
    pdf = client.get(f"{PREFIX}/financial/exports/pdf?year=2025", headers=headers)
    assert b"Sem lan" in pdf.content
    xref = int(pdf.content.split(b"startxref\n")[1].splitlines()[0])
    assert pdf.content[xref:].startswith(b"xref\n")
