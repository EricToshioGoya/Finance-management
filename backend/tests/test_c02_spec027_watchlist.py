"""C-02: SPEC-027 — watchlist pessoal de empresas (limite de 50) e aviso de documento novo."""

import uuid

import pytest
from sqlalchemy import delete

from app.infrastructure.cvm_catalogue import PETR4, VALE3
from app.infrastructure.models import PublicCompanyRecord
from tests.clause_support import unverified_user, verified_user

COMPANIES = "/api/v1/companies"


def watch(client, headers, company_id):
    return client.post(f"{COMPANIES}/{company_id}/watchlist", headers=headers)


def listed(client, headers):
    return [
        item["company"]["ticker"]
        for item in client.get(f"{COMPANIES}/watchlist", headers=headers).json()
    ]


def test_SPEC_027_R01_R03_R04_favorite_list_and_unfavorite(client, app):
    headers = verified_user(client, app)
    first = watch(client, headers, PETR4)
    assert first.status_code == 200 and first.json()["created"] is True
    assert watch(client, headers, PETR4).json()["created"] is False  # idempotente
    watch(client, headers, VALE3)
    assert sorted(listed(client, headers)) == ["PETR4", "VALE3"]
    assert client.delete(f"{COMPANIES}/{PETR4}/watchlist", headers=headers).status_code == 204
    assert listed(client, headers) == ["VALE3"]


def test_SPEC_027_R02_invalid_company_foreign_list_and_unverified_are_refused(client, app):
    headers = verified_user(client, app)
    assert watch(client, headers, uuid.uuid4()).status_code == 404
    assert client.delete(f"{COMPANIES}/{PETR4}/watchlist", headers=headers).status_code == 404
    assert watch(client, unverified_user(client), PETR4).status_code == 403
    assert client.get(f"{COMPANIES}/watchlist").status_code == 401


def test_SPEC_027_R06_watchlist_is_personal(client, app):
    owner = verified_user(client, app)
    other = verified_user(client, app, "outra-watchlist@example.com")
    watch(client, owner, PETR4)
    assert listed(client, other) == []
    assert client.delete(f"{COMPANIES}/{PETR4}/watchlist", headers=other).status_code == 404
    assert listed(client, owner) == ["PETR4"]


@pytest.fixture
def many_companies(app):
    ids = [uuid.uuid4() for _ in range(51)]
    with app.state.sessions() as db:
        db.add_all(
            PublicCompanyRecord(
                id=company_id,
                ticker=f"TST{index:02d}3",
                cnpj=f"99.999.{index:03d}/0001-00",
                legal_name=f"Companhia de Teste {index}",
                sector="Teste",
            )
            for index, company_id in enumerate(ids)
        )
        db.commit()
    yield ids
    with app.state.sessions() as db:
        db.execute(delete(PublicCompanyRecord).where(PublicCompanyRecord.id.in_(ids)))
        db.commit()


def test_SPEC_027_R06_maximum_of_50_companies(client, app, many_companies):
    headers = verified_user(client, app)
    for company_id in many_companies[:50]:
        assert watch(client, headers, company_id).status_code == 200
    refused = watch(client, headers, many_companies[50])
    assert refused.status_code == 422 and refused.json()["detail"] == "watchlist_limit_reached"
    assert len(listed(client, headers)) == 50
