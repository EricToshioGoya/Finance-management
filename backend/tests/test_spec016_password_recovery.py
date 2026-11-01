from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.infrastructure.models import PasswordResetTokenRecord

PREFIX = "/api/v1/auth"
USER = {"name": "Camila Souza", "email": "camila@example.com", "password": "SenhaForte123"}


class CaptureDelivery:
    def __init__(self):
        self.password_resets: list[tuple[str, str]] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        pass

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        self.password_resets.append((recipient, token))


def register_and_login(client, password=USER["password"]):
    if password == USER["password"]:
        assert client.post(f"{PREFIX}/register", json=USER).status_code == 201
    response = client.post(f"{PREFIX}/login", json={"email": USER["email"], "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_SPEC_016_R01_recovery_changes_password_and_revokes_sessions(client, app):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    old_access = register_and_login(client)

    unknown = client.post(f"{PREFIX}/password-recovery", json={"email": "missing@example.com"})
    requested = client.post(f"{PREFIX}/password-recovery", json={"email": USER["email"]})
    assert unknown.status_code == requested.status_code == 204
    assert len(delivery.password_resets) == 1
    token = delivery.password_resets[-1][1]
    with app.state.sessions() as db:
        stored = db.scalar(select(PasswordResetTokenRecord))
        assert stored.digest != token and len(stored.digest) == 64
        assert stored.expires_at - stored.issued_at == timedelta(minutes=30)

    reset = client.post(
        f"{PREFIX}/password-recovery/confirm",
        json={"token": token, "new_password": "NovaSenhaForte456"},
    )
    assert reset.status_code == 204
    assert client.get(f"{PREFIX}/me", headers=old_access).status_code == 401
    assert (
        client.post(
            f"{PREFIX}/login", json={"email": USER["email"], "password": USER["password"]}
        ).status_code
        == 401
    )
    assert (
        client.post(
            f"{PREFIX}/login", json={"email": USER["email"], "password": "NovaSenhaForte456"}
        ).status_code
        == 200
    )


def test_SPEC_016_R02_invalid_or_expired_token_preserves_credentials(client, app):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    access = register_and_login(client)
    requested = client.post(f"{PREFIX}/password-recovery", json={"email": USER["email"]})
    assert requested.status_code == 204
    token = delivery.password_resets[-1][1]
    with app.state.sessions() as db:
        record = db.scalar(select(PasswordResetTokenRecord))
        record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    result = client.post(
        f"{PREFIX}/password-recovery/confirm",
        json={"token": token, "new_password": "NovaSenhaForte456"},
    )
    assert result.status_code == 400 and result.json() == {"detail": "invalid_password_reset_token"}
    assert client.get(f"{PREFIX}/me", headers=access).status_code == 200
    assert (
        client.post(
            f"{PREFIX}/login", json={"email": USER["email"], "password": USER["password"]}
        ).status_code
        == 200
    )


def test_SPEC_016_R03_authenticated_change_requires_current_password_and_revokes(client):
    """Cláusulas: SPEC-016-R04."""
    access = register_and_login(client)
    failed = client.patch(
        f"{PREFIX}/password",
        headers=access,
        json={"current_password": "OutraSenha123", "new_password": "NovaSenhaForte456"},
    )
    assert failed.status_code == 401 and failed.json() == {"detail": "invalid_current_password"}
    assert client.get(f"{PREFIX}/me", headers=access).status_code == 200
    weak = client.patch(
        f"{PREFIX}/password",
        headers=access,
        json={"current_password": USER["password"], "new_password": "curta"},
    )
    assert weak.status_code == 422 and "curta" not in weak.text
    changed = client.patch(
        f"{PREFIX}/password",
        headers=access,
        json={"current_password": USER["password"], "new_password": "NovaSenhaForte456"},
    )
    assert changed.status_code == 204
    assert client.get(f"{PREFIX}/me", headers=access).status_code == 401
    assert (
        client.post(
            f"{PREFIX}/login", json={"email": USER["email"], "password": "NovaSenhaForte456"}
        ).status_code
        == 200
    )
