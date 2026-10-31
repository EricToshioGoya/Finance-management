"""SPEC-018 R01..R06: deletion, isolation, failure and restore protection."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.config import Settings
from app.infrastructure.account_deletion import DeletionJournal
from app.infrastructure.models import UserRecord
from app.main import create_app

PREFIX = "/api/v1/auth"
PASSWORD = "StrongPassword123"


def owner(client, email="delete@example.com"):
    registered = client.post(
        f"{PREFIX}/register", json={"name": "Delete Owner", "email": email, "password": PASSWORD}
    )
    assert registered.status_code == 201
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return registered.json(), {"Authorization": f"Bearer {token}"}


def erase(client, headers, **changes):
    return client.request(
        "DELETE",
        f"{PREFIX}/account",
        headers=headers,
        json={"current_password": PASSWORD, "confirmation": "EXCLUIR MINHA CONTA", **changes},
    )


def test_preview_and_authentication(client):
    assert client.get(f"{PREFIX}/account/deletion-preview").status_code == 401
    assert erase(client, {}).status_code == 401
    _, headers = owner(client)
    preview = client.get(f"{PREFIX}/account/deletion-preview", headers=headers)
    assert preview.status_code == 200
    assert set(preview.json()) == {
        "deleted",
        "timing",
        "legal_retention",
        "backups",
        "technical_retention",
    }
    assert len(preview.json()["deleted"]) == 5


@pytest.mark.parametrize(
    "change,status",
    [
        ({"current_password": "wrong"}, 401),
        ({"confirmation": "cancelar"}, 422),
        ({"user_id": str(uuid.uuid4())}, 422),
    ],
)
def test_invalid_confirmation_preserves_account(client, change, status):
    _, headers = owner(client)
    assert erase(client, headers, **change).status_code == status
    assert client.get(f"{PREFIX}/me", headers=headers).status_code == 200


def test_delete_revokes_all_sessions_preserves_other_owner_and_cascades(client, app):
    first, first_headers = owner(client)
    second, second_headers = owner(client, "other@example.com")
    another_token = client.post(
        f"{PREFIX}/login", json={"email": first["email"], "password": PASSWORD}
    ).json()["access_token"]
    with app.state.engine.begin() as db:
        db.execute(
            text(
                "INSERT INTO accounts (id, user_id, name_encrypted, account_type, initial_balance) "
                "VALUES (:id, :user, :name, 'checking', 0)"
            ),
            {
                "id": uuid.uuid4(),
                "user": uuid.UUID(first["id"]),
                "name": app.state.security.encrypt("Account"),
            },
        )
    response = erase(client, first_headers)
    assert response.status_code == 204
    assert "Max-Age=0" in response.headers["set-cookie"]
    for headers in (first_headers, {"Authorization": f"Bearer {another_token}"}):
        assert client.get(f"{PREFIX}/me", headers=headers).status_code == 401
    assert client.post(f"{PREFIX}/refresh").status_code == 401
    assert client.get(f"{PREFIX}/me", headers=second_headers).json()["id"] == second["id"]
    with app.state.sessions() as db:
        assert db.get(UserRecord, uuid.UUID(first["id"])) is None
        assert (
            db.execute(
                text("SELECT count(*) FROM accounts WHERE user_id=:id"),
                {"id": uuid.UUID(first["id"])},
            ).scalar()
            == 0
        )


def test_journal_failure_never_reports_success_or_deletes(client, monkeypatch):
    _, headers = owner(client)

    def fail(*args):
        raise OSError("synthetic journal failure")

    monkeypatch.setattr(DeletionJournal, "record", fail)
    assert erase(client, headers).status_code == 503
    assert client.get(f"{PREFIX}/me", headers=headers).status_code == 200


def test_restore_reapplies_tombstone_before_serving(client, app):
    user, headers = owner(client)
    with app.state.sessions() as db:
        original = db.get(UserRecord, uuid.UUID(user["id"]))
        values = {
            column.name: getattr(original, column.name) for column in UserRecord.__table__.columns
        }
    assert erase(client, headers).status_code == 204
    with app.state.sessions() as db:
        db.add(UserRecord(**values))
        db.commit()
    settings = Settings().model_copy(
        update={
            "database_url": type(Settings().database_url)(
                app.state.engine.url.render_as_string(hide_password=False)
            )
        }
    )
    restored = create_app(settings)
    with TestClient(restored, base_url="https://localhost:8443") as checked:
        assert checked.get("/api/v1/health").status_code == 200
        with app.state.sessions() as db:
            assert db.get(UserRecord, uuid.UUID(user["id"])) is None
    restored.state.engine.dispose()


def test_restore_without_journal_fails_closed(client, app, tmp_path):
    owner(client)
    settings = Settings().model_copy(
        update={
            "database_url": type(Settings().database_url)(
                app.state.engine.url.render_as_string(hide_password=False)
            ),
            "deletion_journal_path": str(tmp_path / "missing.sqlite3"),
        }
    )
    restored = create_app(settings)
    with pytest.raises(OSError, match="Missing independent"):
        with TestClient(restored):
            pass
    restored.state.engine.dispose()


def test_partial_database_failure_is_not_success_and_blocks_access(client, monkeypatch, app):
    from sqlalchemy.exc import SQLAlchemyError

    from app.application import auth

    _, headers = owner(client)
    original = auth.erase_user

    def fail(*args):
        raise SQLAlchemyError("synthetic deletion failure")

    monkeypatch.setattr(auth, "erase_user", fail)
    assert erase(client, headers).status_code == 503
    assert client.get(f"{PREFIX}/me", headers=headers).status_code == 401
    monkeypatch.setattr(auth, "erase_user", original)
    settings = Settings()
    with app.state.sessions() as db:
        DeletionJournal(settings.deletion_journal_path, settings.data_key.get_secret_value()).apply(
            db
        )
        assert (
            db.scalar(
                select(UserRecord).where(
                    UserRecord.email_lookup == app.state.security.lookup("delete@example.com")
                )
            )
            is None
        )


def test_journal_is_idempotent_and_has_no_direct_identifiers(tmp_path):
    journal = DeletionJournal(str(tmp_path / "journal.sqlite3"), "test-key")
    user = uuid.uuid4()
    with pytest.raises(OSError):
        journal.contains(user)
    journal.record(user)
    journal.record(user)
    assert journal.contains(user)
    with journal.connect() as db:
        rows = list(db.execute("SELECT * FROM deletions"))
    assert len(rows) == 1 and len(rows[0][0]) == 64
    assert str(user).encode() not in journal.path.read_bytes()
