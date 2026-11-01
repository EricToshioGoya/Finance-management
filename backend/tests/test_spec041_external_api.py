"""SPEC-041: token isolation, scopes, quotas, revocation and minimized output."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from test_spec028_net_worth import CaptureDelivery, login, verify

from app.infrastructure.models import ExternalApiKeyRecord

ROOT = "/api/v1/external"


def registered(client, delivery, email):
    owner = login(client, email)
    verify(client, owner, delivery)
    return owner


def grant(client, owner, name, scopes):
    return client.post(
        ROOT + "/grants",
        headers=owner,
        json={"name": name, "scopes": scopes},
    )


def test_external_credential_is_separate_scoped_and_owner_only(client):
    """Cláusulas: SPEC-041-R01, SPEC-041-R03, SPEC-041-R04."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = registered(client, delivery, "api-grant-owner@example.com")
    other = registered(client, delivery, "api-grant-other@example.com")
    assert client.get(ROOT + "/grants").status_code == 401
    invalid = grant(client, owner, "Bad", ["balance:read", "balance:read"])
    assert invalid.status_code == 422
    invalid = grant(client, owner, "Bad", ["expenses:write"])
    assert invalid.status_code == 422

    account = client.post(
        "/api/v1/auth/financial/accounts",
        headers=owner,
        json={"name": "Private account", "account_type": "checking", "initial_balance": "350"},
    )
    assert account.status_code == 201
    created = grant(client, owner, "App de saldo", ["balance:read"])
    assert created.status_code == 201, created.text
    payload = created.json()
    key = payload["api_key"]
    assert key.startswith("fnv_")
    assert "api_key" not in client.get(ROOT + "/grants", headers=owner).json()[0]
    assert client.get(ROOT + "/grants", headers=other).json() == []
    assert client.delete(ROOT + f"/grants/{payload['id']}", headers=other).status_code == 404

    target = ROOT + "/balance?competence=2026-10"
    assert client.get(target, headers=owner).status_code == 401
    assert client.get(target, headers={"X-FinNova-API-Key": "fake"}).status_code == 401
    response = client.get(target, headers={"X-FinNova-API-Key": key})
    assert response.status_code == 200, response.text
    data = response.json()
    assert set(data) == {"competence", "income", "expenses", "balance_variation"}
    assert "Private account" not in str(data)
    assert client.get(ROOT + "/net-worth", headers={"X-FinNova-API-Key": key}).status_code == 403

    assert client.delete(ROOT + f"/grants/{payload['id']}", headers=owner).status_code == 204
    assert client.get(target, headers={"X-FinNova-API-Key": key}).status_code == 401


def test_external_read_net_worth_exposes_only_totals_and_isolated_owner(client):
    """Cláusulas: SPEC-041-R01, SPEC-041-R03."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = registered(client, delivery, "api-worth-owner@example.com")
    other = registered(client, delivery, "api-worth-other@example.com")
    a = grant(client, owner, "Agregados", ["net_worth:read"])
    b = grant(client, other, "Outro", ["net_worth:read"])
    assert a.status_code == b.status_code == 201
    client.post(
        "/api/v1/auth/financial/accounts",
        headers=owner,
        json={"name": "Private investment", "account_type": "savings", "initial_balance": "127"},
    )
    route = ROOT + "/net-worth"
    own = client.get(route, headers={"X-FinNova-API-Key": a.json()["api_key"]})
    foreign = client.get(route, headers={"X-FinNova-API-Key": b.json()["api_key"]})
    assert own.status_code == foreign.status_code == 200
    assert own.json()["total_assets"] == "127.00"
    assert foreign.json()["total_assets"] == "0"
    assert set(own.json()) == {"as_of", "total_assets", "total_liabilities", "net_worth"}
    assert "Private investment" not in str(own.json())


def test_external_grant_expires_and_rate_limits_are_persistent(client):
    """Cláusulas: SPEC-041-R02, SPEC-041-R06."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = registered(client, delivery, "api-quota-owner@example.com")
    created = grant(client, owner, "Quota", ["balance:read"])
    assert created.status_code == 201
    key = created.json()["api_key"]
    headers = {"X-FinNova-API-Key": key}
    endpoint = ROOT + "/balance?competence=2026-10"
    for _ in range(30):
        assert client.get(endpoint, headers=headers).status_code == 200
    rejected = client.get(endpoint, headers=headers)
    assert rejected.status_code == 429
    assert rejected.headers["retry-after"] == "60"

    grant_id = uuid.UUID(created.json()["id"])
    with client.app.state.sessions() as db:
        record = db.scalar(select(ExternalApiKeyRecord).where(ExternalApiKeyRecord.id == grant_id))
        record.window_started_at = datetime.now(UTC) - timedelta(minutes=2)
        db.commit()
    assert client.get(endpoint, headers=headers).status_code == 200
    with client.app.state.sessions() as db:
        record = db.scalar(select(ExternalApiKeyRecord).where(ExternalApiKeyRecord.id == grant_id))
        record.expires_at = datetime.now(UTC) - timedelta(seconds=2)
        db.commit()
    assert client.get(endpoint, headers=headers).status_code == 401


def test_no_unverified_user_can_issue_external_key(client):
    """Cláusulas: SPEC-041-R02."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "api-no-email@example.com")
    assert grant(client, headers, "App", ["balance:read"]).status_code == 403
