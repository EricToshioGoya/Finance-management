"""SPEC-060 R01..R06: minimal asynchronous events and protected audit trail."""

import uuid

from sqlalchemy import select, text

from app.infrastructure.models import AuditLogRecord, UsageEventRecord

PREFIX = "/api/v1/auth"
PASSWORD = "StrongPassword123"


def owner(client, email="audit@example.com"):
    registered = client.post(
        f"{PREFIX}/register", json={"name": "Audit Owner", "email": email, "password": PASSWORD}
    )
    assert registered.status_code == 201
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return registered.json(), {"Authorization": f"Bearer {token}"}


def test_spec060_r01_r03_r04_minimal_event_is_backgrounded_and_persisted(client, app):
    """Cláusulas: SPEC-060-R01, SPEC-060-R03, SPEC-060-R04."""
    user, headers = owner(client)
    response = client.post(
        f"{PREFIX}/usage-events",
        headers=headers,
        json={"module": "simulator", "action": "opened"},
    )
    assert response.status_code == 202
    with app.state.sessions() as db:
        event = db.scalar(select(UsageEventRecord))
        assert event is not None
        assert event.user_id == uuid.UUID(user["id"])
        assert (event.module, event.action) == ("simulator", "opened")
        assert event.occurred_at.tzinfo is not None
        assert set(UsageEventRecord.__table__.columns.keys()) == {
            "id",
            "user_id",
            "module",
            "action",
            "occurred_at",
        }


def test_spec060_r02_rejects_invalid_or_unauthenticated_event_without_recording(client, app):
    """Cláusulas: SPEC-060-R02."""
    _, headers = owner(client)
    unauthenticated = client.post(
        f"{PREFIX}/usage-events", json={"module": "simulator", "action": "opened"}
    )
    assert unauthenticated.status_code == 401
    assert (
        client.post(
            f"{PREFIX}/usage-events",
            headers=headers,
            json={"module": "financial", "action": "opened", "amount": "1000"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{PREFIX}/usage-events",
            headers=headers,
            json={"module": "financial", "action": "saved"},
        ).status_code
        == 422
    )
    with app.state.sessions() as db:
        assert db.scalar(select(UsageEventRecord)) is None


def test_spec060_r01_audit_is_server_written_and_has_no_mutation_route(client, app):
    """Cláusulas: SPEC-060-R01."""
    user, headers = owner(client)
    changed = client.patch(
        f"{PREFIX}/password",
        headers=headers,
        json={"current_password": PASSWORD, "new_password": "NewStrongPassword123"},
    )
    assert changed.status_code == 204
    mutation = client.patch(f"{PREFIX}/audit-logs/anything", headers=headers, json={})
    assert mutation.status_code == 404
    with app.state.sessions() as db:
        log = db.scalar(select(AuditLogRecord).where(AuditLogRecord.action == "password_changed"))
        assert log is not None
        assert log.user_id == uuid.UUID(user["id"])
        assert set(AuditLogRecord.__table__.columns.keys()) == {
            "id",
            "user_id",
            "action",
            "occurred_at",
        }


def test_spec060_r05_policy_is_public_in_frontend_source():
    """Cláusulas: SPEC-060-R05."""
    source = "../frontend/src/i18n.ts"
    with open(source, encoding="utf-8") as frontend:
        text_source = frontend.read()
    assert "eventos mínimos de uso (módulo e ação), de forma agregada" in text_source
    assert "Administradores não veem o seu conteúdo financeiro" in text_source


def test_spec060_r06_account_deletion_anonymizes_events_and_audit(client, app):
    """Cláusulas: SPEC-060-R06."""
    _, headers = owner(client)
    assert (
        client.post(
            f"{PREFIX}/usage-events",
            headers=headers,
            json={"module": "profile", "action": "viewed"},
        ).status_code
        == 202
    )
    deleted = client.request(
        "DELETE",
        f"{PREFIX}/account",
        headers=headers,
        json={"current_password": PASSWORD, "confirmation": "EXCLUIR MINHA CONTA"},
    )
    assert deleted.status_code == 204
    with app.state.sessions() as db:
        assert db.scalar(select(UsageEventRecord.user_id)) is None
        deleted_log = db.scalar(
            select(AuditLogRecord).where(AuditLogRecord.action == "account_deleted")
        )
        assert deleted_log is not None and deleted_log.user_id is None
        assert db.execute(text("SELECT count(*) FROM users")).scalar() == 0
