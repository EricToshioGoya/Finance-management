"""SPEC-011 R01..R11: backend RBAC and metadata-only paginated admin listing."""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings
from app.infrastructure.models import AuditLogRecord, UserRecord
from app.main import create_app

PREFIX = "/api/v1/auth"
ADMIN_PREFIX = "/api/v1/admin"
PASSWORD = "StrongPassword123"


class CaptureDelivery:
    def __init__(self):
        self.tokens: list[str] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.tokens.append(token)


def register_and_login(client, name: str, email: str):
    assert (
        client.post(
            f"{PREFIX}/register", json={"name": name, "email": email, "password": PASSWORD}
        ).status_code
        == 201
    )
    response = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_spec011_r03_r06_first_admin_requires_configured_email_confirmation(client, app):
    """Cláusulas: SPEC-011-R03, SPEC-011-R06."""
    configured = "admin@example.com"
    settings = Settings().model_copy(
        update={
            "database_url": type(Settings().database_url)(
                app.state.engine.url.render_as_string(hide_password=False)
            ),
            "initial_admin_email": configured,
        }
    )
    delivery = CaptureDelivery()
    bootstrapped = create_app(settings, email_delivery=delivery)
    with TestClient(bootstrapped, base_url="https://localhost:8443") as admin_client:
        headers = register_and_login(admin_client, "Configured Admin", configured)
        assert admin_client.get(f"{ADMIN_PREFIX}/users", headers=headers).status_code == 403
        assert admin_client.post(f"{PREFIX}/email-confirmation", headers=headers).status_code == 204
        assert (
            admin_client.post(
                f"{PREFIX}/email-confirmation/confirm", json={"token": delivery.tokens[-1]}
            ).status_code
            == 200
        )
        assert admin_client.get(f"{PREFIX}/me", headers=headers).json()["role"] == "administrador"


def test_spec011_r04_r05_r08_r10_r11_admin_endpoint_is_server_protected_paginated_and_safe(
    client, app
):
    """Cláusulas: SPEC-011-R01, SPEC-011-R04, SPEC-011-R05, SPEC-011-R08, SPEC-011-R10,
    SPEC-011-R11.
    """
    common = register_and_login(client, "Common User", "common@example.com")
    with app.state.sessions() as db:
        first = db.scalar(select(UserRecord).where(UserRecord.role == "usuario"))
        first.role = "administrador"
        db.commit()
    admin = common
    for index in range(3):
        register_and_login(client, f"Member {index}", f"member{index}@example.com")
    assert client.get(f"{ADMIN_PREFIX}/users").status_code == 401
    other = register_and_login(client, "Common Other", "other@example.com")
    assert client.get(f"{ADMIN_PREFIX}/users", headers=other).status_code == 403

    page = client.get(f"{ADMIN_PREFIX}/users?page=2&page_size=2&query=member", headers=admin)
    assert page.status_code == 200
    body = page.json()
    assert body["page"] == 2 and body["page_size"] == 2 and body["total"] == 3
    assert len(body["items"]) == 1
    assert set(body["items"][0]) == {
        "id",
        "name",
        "email",
        "created_at",
        "investor_profile",
        "status",
    }
    assert body["items"][0]["investor_profile"] is None and body["items"][0]["status"] == "active"
    assert "amount" not in str(body) and "password" not in str(body)


def test_spec011_r07_r09_filters_and_audits_access(client, app):
    """Cláusulas: SPEC-011-R01, SPEC-011-R07, SPEC-011-R09."""
    headers = register_and_login(client, "Admin Filter", "filter@example.com")
    with app.state.sessions() as db:
        user = db.scalar(
            select(UserRecord).where(
                UserRecord.email_lookup == app.state.security.lookup("filter@example.com")
            )
        )
        user.role = "administrador"
        db.commit()
    register_and_login(client, "Alice Silva", "alice@example.com")
    matching = client.get(
        f"{ADMIN_PREFIX}/users?query=ALICE&status=active&profile=unassigned", headers=headers
    )
    assert matching.status_code == 200 and matching.json()["total"] == 1
    assert client.get(f"{ADMIN_PREFIX}/users?status=disabled", headers=headers).json()["total"] == 0
    with app.state.sessions() as db:
        assert (
            db.scalar(select(AuditLogRecord).where(AuditLogRecord.action == "admin_users_listed"))
            is not None
        )


def test_spec011_r02_public_registration_cannot_set_role(client):
    """Cláusulas: SPEC-011-R02, SPEC-011-R06."""
    response = client.post(
        f"{PREFIX}/register",
        json={
            "name": "No Admin",
            "email": "no-admin@example.com",
            "password": PASSWORD,
            "role": "administrador",
        },
    )
    assert response.status_code == 422
