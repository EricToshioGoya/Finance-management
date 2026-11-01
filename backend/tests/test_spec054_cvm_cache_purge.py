"""SPEC-054: public CVM cache expires on the calendar boundary and is rebuilt locally."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.application.cvm_cache import CvmCacheService, twelve_calendar_months_before
from app.infrastructure.models import (
    CvmCachePurgeRunRecord,
    FinancialIndicatorRecord,
    OfficialDocumentRecord,
)

COMPANIES = "/api/v1/companies"
PASSWORD = "StrongPassword123"
NOW = datetime(2027, 10, 28, 3, 0, tzinfo=UTC)


def login(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Cache Reader", "email": "cache@example.com", "password": PASSWORD},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cache@example.com", "password": PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def company_id(client, headers, ticker):
    return client.get(f"{COMPANIES}?query={ticker}", headers=headers).json()[0]["id"]


def test_spec054_expunges_at_calendar_limit_and_writes_aggregated_completed_run(client, app):
    """Cláusulas: SPEC-054-R01, SPEC-054-R04, SPEC-054-R07."""
    headers = login(client)
    petr4 = company_id(client, headers, "PETR4")
    vale3 = company_id(client, headers, "VALE3")
    app.state.clock = lambda: NOW
    cutoff = twelve_calendar_months_before(NOW)
    with app.state.sessions() as db:
        for model in (OfficialDocumentRecord, FinancialIndicatorRecord):
            for row in db.scalars(select(model).where(model.company_id == petr4)):
                row.synced_at = cutoff
            for row in db.scalars(select(model).where(model.company_id == vale3)):
                row.synced_at = cutoff + timedelta(microseconds=1)
        db.commit()
    with app.state.sessions() as db:
        result = CvmCacheService(db, clock=app.state.clock).purge_expired()
        run = db.scalars(select(CvmCachePurgeRunRecord)).one()
        assert result["status"] == run.status == "completed"
        assert result["documents_expunged"] == 4
        assert result["indicators_expunged"] == 6
        assert run.occurred_at == NOW
        assert (
            db.scalars(
                select(OfficialDocumentRecord).where(OfficialDocumentRecord.company_id == petr4)
            ).all()
            == []
        )
        assert (
            db.scalars(
                select(FinancialIndicatorRecord).where(FinancialIndicatorRecord.company_id == petr4)
            ).all()
            == []
        )
        assert (
            len(
                db.scalars(
                    select(OfficialDocumentRecord).where(OfficialDocumentRecord.company_id == vale3)
                ).all()
            )
            == 4
        )
        assert (
            len(
                db.scalars(
                    select(FinancialIndicatorRecord).where(
                        FinancialIndicatorRecord.company_id == vale3
                    )
                ).all()
            )
            == 7
        )


def test_spec054_next_company_consultation_rebuilds_only_public_local_cache(client, app):
    """Cláusulas: SPEC-054-R05."""
    now = datetime.now(UTC)
    app.state.clock = lambda: now
    headers = login(client)
    petr4 = company_id(client, headers, "PETR4")
    cutoff = twelve_calendar_months_before(now)
    with app.state.sessions() as db:
        for model in (OfficialDocumentRecord, FinancialIndicatorRecord):
            for row in db.scalars(select(model).where(model.company_id == petr4)):
                row.synced_at = cutoff
        db.commit()
    with app.state.sessions() as db:
        CvmCacheService(db, clock=app.state.clock).purge_expired()
    documents = client.get(f"{COMPANIES}/{petr4}/documents", headers=headers)
    indicators = client.get(f"{COMPANIES}/{petr4}/financial-indicators", headers=headers)
    assert documents.status_code == indicators.status_code == 200
    assert len(documents.json()) == 4
    assert len(indicators.json()) == 6
    assert all(row["synced_at"].startswith(now.date().isoformat()) for row in indicators.json())
    assert all("pdf" not in row for row in indicators.json())


def test_spec054_calendar_boundary_handles_leap_day_without_extending_retention():
    """Cláusulas: SPEC-054-R01, SPEC-054-R04."""
    leap_instant = datetime(2028, 2, 29, 3, 0, tzinfo=UTC)
    assert twelve_calendar_months_before(leap_instant) == datetime(2027, 2, 28, 3, 0, tzinfo=UTC)
