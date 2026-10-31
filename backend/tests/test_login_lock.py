"""SPEC-001-R11 / CA-011 / INV-007: persistent 5 failures / 15 minutes."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from test_auth import PREFIX, headers, login, register

from app.config import Settings
from app.infrastructure.models import LoginAttemptRecord
from app.main import create_app


def freeze(app):
    instant = [datetime.now(UTC)]
    app.state.clock = lambda: instant[0]
    return instant


def test_fifth_failure_locks_even_correct_password_and_expires_exactly(client, app):
    """T-011: fifth failure, before/exact boundary; requests do not extend lock."""
    register(client)
    clock = freeze(app)
    for _ in range(4):
        assert login(client, password="WrongPassword123").status_code == 401
    response = login(client, password="WrongPassword123")
    assert response.status_code == 429
    assert response.json() == {"detail": "login_temporarily_unavailable"}
    assert response.headers["retry-after"] == "900"
    assert "set-cookie" not in response.headers
    assert login(client).status_code == 429
    clock[0] += timedelta(minutes=15) - timedelta(microseconds=1)
    assert login(client).headers["retry-after"] == "1"
    clock[0] += timedelta(microseconds=1)
    assert login(client).status_code == 200
    with app.state.sessions() as db:
        record = db.scalar(select(LoginAttemptRecord))
        assert record.failures == 0 and record.blocked_until is None


def test_success_resets_consecutive_failures(client, app):
    register(client)
    for _ in range(4):
        assert login(client, password="WrongPassword123").status_code == 401
    assert login(client).status_code == 200
    for _ in range(4):
        assert login(client, password="WrongPassword123").status_code == 401
    assert login(client).status_code == 200


def test_expiry_starts_a_fresh_failure_sequence(client, app):
    register(client)
    clock = freeze(app)
    for _ in range(5):
        login(client, password="WrongPassword123")
    clock[0] += timedelta(minutes=15)
    assert login(client, password="WrongPassword123").status_code == 401
    with app.state.sessions() as db:
        record = db.scalar(select(LoginAttemptRecord))
        assert record.failures == 1 and record.blocked_until is None


def test_unknown_email_has_identical_lock_responses_and_no_email_in_state(client, app):
    register(client)
    freeze(app)
    for _ in range(6):
        existing = login(client, password="WrongPassword123")
        missing = login(client, email="absent@example.com", password="WrongPassword123")
        assert existing.status_code == missing.status_code
        assert existing.json() == missing.json()
        assert existing.headers.get("retry-after") == missing.headers.get("retry-after")
    with app.state.sessions() as db:
        records = db.scalars(select(LoginAttemptRecord)).all()
        assert len(records) == 2
        assert all(len(r.email_key) == 64 and "@" not in r.email_key for r in records)


def test_account_lock_is_shared_across_ips_normalization_and_instances(client, app):
    register(client)
    freeze(app)
    settings = Settings().model_copy(
        update={
            "database_url": type(Settings().database_url)(
                app.state.engine.url.render_as_string(hide_password=False)
            )
        }
    )
    other_app = create_app(settings)
    other_app.state.clock = app.state.clock
    try:
        with TestClient(
            other_app, base_url="https://localhost:8443", client=("other-ip", 1)
        ) as other:
            for i in range(5):
                requester = client if i % 2 else other
                response = login(
                    requester, email="MARIANA@EXAMPLE.COM", password="WrongPassword123"
                )
            assert response.status_code == 429
            assert login(client).status_code == login(other).status_code == 429
            assert login(other, email="another@example.com").status_code == 401
    finally:
        other_app.state.engine.dispose()


def test_concurrent_failures_cannot_lose_increments(client, app):
    register(client)
    freeze(app)

    def fail(i):
        with TestClient(app, base_url="https://localhost:8443", client=(f"client-{i}", 1)) as other:
            return login(other, password="WrongPassword123").status_code

    with ThreadPoolExecutor(max_workers=5) as pool:
        assert sorted(pool.map(fail, range(5))) == [401, 401, 401, 401, 429]
    with app.state.sessions() as db:
        assert db.scalar(select(LoginAttemptRecord)).failures == 5
    assert login(client).status_code == 429


def test_new_login_lock_does_not_revoke_existing_sessions(client, app):
    register(client)
    access = login(client).json()["access_token"]
    for _ in range(5):
        login(client, password="WrongPassword123")
    assert client.get(f"{PREFIX}/me", headers=headers(access)).status_code == 200


def test_cleanup_removes_stale_inactive_records_but_preserves_active_lock(client, app):
    register(client)
    clock = freeze(app)
    with app.state.sessions() as db:
        for key, blocked in [("a" * 64, None), ("b" * 64, clock[0] + timedelta(minutes=5))]:
            db.add(
                LoginAttemptRecord(
                    email_key=key,
                    failures=5,
                    blocked_until=blocked,
                    touched_at=clock[0] - timedelta(days=2),
                )
            )
        db.commit()
    login(client)
    with app.state.sessions() as db:
        assert db.get(LoginAttemptRecord, "a" * 64) is None
        assert db.get(LoginAttemptRecord, "b" * 64) is not None
