"""SPEC-017 integration checks against PostgreSQL, with no real external service."""

from fastapi.testclient import TestClient

from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Mariana Souza", "email": "mariana@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Lucas Lima", "email": "lucas@example.com", "password": "SenhaForte123"}


def authorize(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register(client: TestClient, user: dict[str, str]) -> None:
    assert client.post(f"{PREFIX}/register", json=user).status_code == 201


def login(client: TestClient, user: dict[str, str]) -> str:
    response = client.post(
        f"{PREFIX}/login", json={"email": user["email"], "password": user["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_SPEC_017_R01_lists_only_owned_sessions_without_tokens(client):
    register(client, USER)
    first = login(client, USER)
    second = login(client, USER)

    response = client.get(f"{PREFIX}/sessions", headers=authorize(second))

    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 2
    assert {item["current"] for item in sessions} == {False, True}
    assert all(set(item) == {"id", "started_at", "expires_at", "current"} for item in sessions)
    assert all(
        "token" not in str(item).lower() and "digest" not in str(item).lower() for item in sessions
    )
    assert client.get(f"{PREFIX}/me", headers=authorize(first)).status_code == 200


def test_SPEC_017_R02_rejects_foreign_or_malformed_session_without_revocation(client, app):
    register(client, USER)
    owner_access = login(client, USER)
    owner_session = client.get(f"{PREFIX}/sessions", headers=authorize(owner_access)).json()[0][
        "id"
    ]

    with TestClient(app, base_url="https://localhost:8443") as other:
        register(other, OTHER)
        other_access = login(other, OTHER)
        foreign = other.post(
            f"{PREFIX}/sessions/{owner_session}/revoke", headers=authorize(other_access)
        )
        malformed = other.post(
            f"{PREFIX}/sessions/not-a-session/revoke", headers=authorize(other_access)
        )

    assert foreign.status_code == malformed.status_code == 404
    assert foreign.json() == malformed.json() == {"detail": "session_not_found"}
    assert client.get(f"{PREFIX}/me", headers=authorize(owner_access)).status_code == 200


def test_SPEC_017_R03_selected_revocation_is_idempotent_and_isolated(client):
    register(client, USER)
    first = login(client, USER)
    first_refresh = client.cookies.get(COOKIE)
    second = login(client, USER)
    sessions = client.get(f"{PREFIX}/sessions", headers=authorize(second)).json()
    first_id = next(item["id"] for item in sessions if not item["current"])

    revoked = client.post(f"{PREFIX}/sessions/{first_id}/revoke", headers=authorize(second))
    repeated = client.post(f"{PREFIX}/sessions/{first_id}/revoke", headers=authorize(second))

    assert revoked.status_code == repeated.status_code == 204
    assert client.get(f"{PREFIX}/me", headers=authorize(first)).status_code == 401
    assert (
        client.post(
            f"{PREFIX}/refresh", headers={"Cookie": f"{COOKIE}={first_refresh}"}
        ).status_code
        == 401
    )
    assert client.get(f"{PREFIX}/me", headers=authorize(second)).status_code == 200
    assert all(
        item["id"] != first_id
        for item in client.get(f"{PREFIX}/sessions", headers=authorize(second)).json()
    )


def test_SPEC_017_R04_revoking_all_invalidates_every_device_and_clears_cookie(client, app):
    register(client, USER)
    first = login(client, USER)
    with TestClient(app, base_url="https://localhost:8443") as other:
        second = login(other, USER)
        response = other.post(f"{PREFIX}/sessions/revoke-all", headers=authorize(second))
        assert response.status_code == 200
        assert response.json() == {"revoked_sessions": 2}
        assert "Max-Age=0" in response.headers["set-cookie"]

    assert client.get(f"{PREFIX}/me", headers=authorize(first)).status_code == 401
    assert client.get(f"{PREFIX}/me", headers=authorize(second)).status_code == 401
