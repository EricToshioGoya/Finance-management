from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.config import Settings
from app.infrastructure.models import SessionRecord, UserRecord
from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Mariana Souza", "email": "mariana@example.com", "password": "SenhaForte123"}


def register(client, **overrides):
    return client.post(f"{PREFIX}/register", json={**USER, **overrides})


def login(client, **overrides):
    return client.post(
        f"{PREFIX}/login",
        json={
            "email": USER["email"],
            "password": USER["password"],
            **overrides,
        },
    )


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_login_identity_and_logout(client, app):
    registered = register(client)
    assert registered.status_code == 201
    user = registered.json()
    assert set(user) == {
        "id",
        "name",
        "email",
        "role",
        "email_verified",
        "investor_profile",
    }
    assert user["investor_profile"] is None
    assert user["email_verified"] is False
    assert user["role"] == "usuario"
    response = login(client)
    assert response.status_code == 200
    assert response.json()["expires_in"] == 900
    access = response.json()["access_token"]
    assert client.get(f"{PREFIX}/me", headers=headers(access)).json() == user
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=strict" in cookie
    assert "Path=/api/v1/auth" in cookie
    assert client.post(f"{PREFIX}/logout", headers=headers(access)).status_code == 204
    assert client.get(f"{PREFIX}/me", headers=headers(access)).status_code == 401
    assert client.post(f"{PREFIX}/refresh").status_code == 401


@pytest.mark.parametrize(
    "override",
    [
        {"name": ""},
        {"name": "   "},
        {"email": "invalid"},
        {"password": "short"},
        {"password": "x" * 129},
        {"role": "administrador"},
    ],
)
def test_reject_invalid_input_without_echoing_password(client, app, override):
    response = register(client, **override)
    assert response.status_code == 422
    assert response.json() == {"detail": "invalid_input"}
    with app.state.sessions() as db:
        assert db.scalar(select(UserRecord)) is None


@pytest.mark.parametrize("field", ["name", "email", "password"])
def test_required_fields(client, field):
    data = {k: v for k, v in USER.items() if k != field}
    assert client.post(f"{PREFIX}/register", json=data).status_code == 422


def test_minimum_password_and_case_insensitive_email(client):
    assert register(client, password="12345678").status_code == 201
    assert register(client, email="MARIANA@EXAMPLE.COM").status_code == 409
    assert login(client, email="MARIANA@EXAMPLE.COM", password="12345678").status_code == 200


def test_generic_login_error(client):
    register(client)
    wrong_password = login(client, password="WrongPassword123")
    absent_email = login(client, email="absent@example.com")
    assert wrong_password.status_code == absent_email.status_code == 401
    assert wrong_password.json() == absent_email.json() == {"detail": "invalid_credentials"}
    assert "set-cookie" not in wrong_password.headers


def test_duplicate_registration_concurrently(app):
    def create(_):
        with TestClient(app, base_url="https://localhost:8443") as client:
            return register(client).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(create, range(2))) == [201, 409]
    with app.state.engine.connect() as db:
        assert db.scalar(text("SELECT COUNT(*) FROM users")) == 1


def test_encrypted_data_and_salted_passwords(client, app, caplog):
    register(client)
    register(client, email="other@example.com")
    with app.state.sessions() as db:
        users = db.scalars(select(UserRecord)).all()
        assert len(users) == 2
        assert users[0].password_hash.startswith("$argon2id$")
        assert users[0].password_hash != users[1].password_hash
        assert USER["name"].encode() not in users[0].name_encrypted
        assert USER["email"].encode() not in users[0].email_encrypted
        assert app.state.security.decrypt(users[0].name_encrypted) == USER["name"]
    assert USER["password"] not in caplog.text


def test_refresh_rotates_and_replay_revokes_family(client):
    register(client)
    first = login(client)
    old_cookie = client.cookies.get(COOKIE)
    refreshed = client.post(f"{PREFIX}/refresh")
    assert refreshed.status_code == 200
    assert client.cookies.get(COOKIE) != old_cookie
    token = refreshed.json()["access_token"]
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 200
    replay = client.post(f"{PREFIX}/refresh", headers={"Cookie": f"{COOKIE}={old_cookie}"})
    assert replay.status_code == 401
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 401
    assert first.json()["access_token"] != token


def test_logout_works_after_access_expires_using_refresh_cookie(client):
    register(client)
    login(client)
    assert client.post(f"{PREFIX}/logout").status_code == 204
    assert client.post(f"{PREFIX}/refresh").status_code == 401


@pytest.mark.parametrize("kind", ["expired", "tampered", "wrong_audience", "wrong_type"])
def test_invalid_jwt(client, kind):
    register(client)
    token = login(client).json()["access_token"]
    settings = Settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=["HS256"],
        audience="finnova-clients",
    )
    if kind == "expired":
        payload["exp"] = datetime.now(UTC) - timedelta(seconds=1)
    elif kind == "wrong_audience":
        payload["aud"] = "other-service"
    elif kind == "wrong_type":
        payload["type"] = "refresh"
    token = jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value()
        if kind != "tampered"
        else "another-signing-key-at-least-32-bytes",
        algorithm="HS256",
    )
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 401


def test_session_expiration_and_missing_credentials(client, app):
    register(client)
    token = login(client).json()["access_token"]
    with app.state.sessions() as db:
        session = db.scalar(select(SessionRecord))
        session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    assert client.get(f"{PREFIX}/me", headers=headers(token)).status_code == 401
    assert client.get(f"{PREFIX}/me").status_code == 401
    assert client.post(f"{PREFIX}/refresh").status_code == 401


def test_limit_per_endpoint_and_client_and_window(client, app, monkeypatch):
    # Malformed payload avoids expensive hashing; all sensitive requests count.
    monkeypatch.setattr("app.main.time.time", lambda: 1000.0)
    for _ in range(100):
        assert client.post(f"{PREFIX}/login", json={}).status_code == 422
    response = client.post(f"{PREFIX}/login", json={})
    assert response.status_code == 429 and response.headers["retry-after"] == "20"
    assert client.post(f"{PREFIX}/register", json={}).status_code == 422
    with TestClient(
        app, base_url="https://localhost:8443", client=("another-client", 123)
    ) as other:
        assert other.post(f"{PREFIX}/login", json={}).status_code == 422
    monkeypatch.setattr("app.main.time.time", lambda: 1020.0)
    assert client.post(f"{PREFIX}/login", json={}).status_code == 422


def test_https_origin_and_contract(client):
    assert (
        client.post(
            f"{PREFIX}/register", json=USER, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"{PREFIX}/register", json=USER, headers={"Sec-Fetch-Site": "cross-site"}
        ).status_code
        == 403
    )
    assert client.get("http://localhost/api/v1/health").status_code == 400
    schema = client.get("/api/v1/openapi.json").json()
    assert all(path.startswith("/api/v1/") for path in schema["paths"])
    assert f"{PREFIX}/login" in schema["paths"]
    assert f"{PREFIX}/sessions" in schema["paths"]
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_mobile_and_web_can_consume_same_api(client, app):
    register(client)
    web = login(client).json()["access_token"]
    with TestClient(
        app, base_url="https://localhost:8443", headers={"User-Agent": "FinNova-Mobile"}
    ) as mobile:
        token = login(mobile).json()["access_token"]
        assert (
            mobile.get(f"{PREFIX}/me", headers=headers(token)).json()
            == client.get(f"{PREFIX}/me", headers=headers(web)).json()
        )
        client.post(f"{PREFIX}/logout", headers=headers(web))
        assert mobile.get(f"{PREFIX}/me", headers=headers(token)).status_code == 200


def test_logout_rejects_mismatched_cookie_and_bearer_without_revoking_other_session(client):
    register(client)
    first = login(client).json()["access_token"]
    second = login(client).json()["access_token"]
    assert client.post(f"{PREFIX}/logout", headers=headers(first)).status_code == 401
    assert client.get(f"{PREFIX}/me", headers=headers(first)).status_code == 200
    assert client.get(f"{PREFIX}/me", headers=headers(second)).status_code == 200


def test_concurrent_refresh_detects_replay(app, client):
    register(client)
    access = login(client).json()["access_token"]
    cookie = client.cookies.get(COOKIE)

    def refresh(_):
        with TestClient(app, base_url="https://localhost:8443") as other:
            return other.post(f"{PREFIX}/refresh", headers={"Cookie": f"{COOKIE}={cookie}"})

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(refresh, range(2)))
    assert sorted(response.status_code for response in responses) == [200, 401]
    assert client.get(f"{PREFIX}/me", headers=headers(access)).status_code == 401


def test_login_cleans_expired_session_records(client, app):
    register(client)
    login(client)
    with app.state.sessions() as db:
        db.scalar(select(SessionRecord)).expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    assert login(client).status_code == 200
    with app.state.sessions() as db:
        assert len(db.scalars(select(SessionRecord)).all()) == 1


def test_database_error_is_generic_without_secret_details(client, app, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    def unavailable():
        raise SQLAlchemyError(USER["password"])

    monkeypatch.setattr(app.state.engine, "connect", unavailable)
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "service_unavailable"}


def test_forwarded_headers_do_not_bypass_https(client):
    response = client.get("http://localhost/api/v1/health", headers={"X-Forwarded-Proto": "https"})
    assert response.status_code == 400


def test_rate_limit_state_is_shared_by_application_instances(app, client, monkeypatch):
    from app.main import create_app

    monkeypatch.setattr("app.main.time.time", lambda: 2000.0)
    for _ in range(100):
        client.post(f"{PREFIX}/login", json={})
    settings = Settings().model_copy(
        update={
            "database_url": type(Settings().database_url)(
                app.state.engine.url.render_as_string(hide_password=False)
            ),
        }
    )
    another_app = create_app(settings)
    try:
        with TestClient(another_app, base_url="https://localhost:8443") as other:
            assert other.post(f"{PREFIX}/login", json={}).status_code == 429
    finally:
        another_app.state.engine.dispose()
