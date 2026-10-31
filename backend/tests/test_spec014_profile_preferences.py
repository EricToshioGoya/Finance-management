"""SPEC-014 integration tests with PostgreSQL and a fake confirmation delivery."""

from fastapi.testclient import TestClient

from app.infrastructure.email_delivery import EmailDeliveryError

PREFIX = "/api/v1/auth"
USER = {"name": "Mariana Souza", "email": "mariana@example.com", "password": "SenhaForte123"}
OTHER = {"name": "Lucas Lima", "email": "lucas@example.com", "password": "SenhaForte123"}


class CaptureDelivery:
    def __init__(self):
        self.messages: list[tuple[str, str]] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.messages.append((recipient, token))


class FailingDelivery:
    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        raise EmailDeliveryError("provider unavailable")


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_and_login(client: TestClient, user: dict[str, str] = USER) -> str:
    assert client.post(f"{PREFIX}/register", json=user).status_code == 201
    response = client.post(
        f"{PREFIX}/login", json={"email": user["email"], "password": user["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def preferences(language: str = "en", theme: str = "dark") -> dict[str, bool | str]:
    return {
        "language": language,
        "theme": theme,
        "in_app_notifications": True,
        "email_notifications": True,
        "push_notifications": False,
    }


def test_SPEC_014_R01_profile_and_preferences_persist_across_sessions(client, app):
    first = register_and_login(client)
    assert (
        client.patch(
            f"{PREFIX}/profile", json={"name": "Mariana Costa"}, headers=auth(first)
        ).status_code
        == 200
    )
    saved = client.patch(f"{PREFIX}/profile/preferences", json=preferences(), headers=auth(first))
    assert saved.status_code == 200 and saved.json() == preferences()

    with TestClient(app, base_url="https://localhost:8443") as another:
        second = another.post(
            f"{PREFIX}/login", json={"email": USER["email"], "password": USER["password"]}
        ).json()["access_token"]
        profile = another.get(f"{PREFIX}/profile", headers=auth(second))

    assert profile.status_code == 200
    assert profile.json()["user"]["name"] == "Mariana Costa"
    assert profile.json()["preferences"] == preferences()
    assert profile.json()["pending_email"] is None


def test_SPEC_014_R02_email_change_requires_reauthentication_and_promotes_only_on_confirmation(
    client, app
):
    capture = CaptureDelivery()
    app.state.email_delivery = capture
    token = register_and_login(client)
    denied = client.patch(
        f"{PREFIX}/profile",
        json={"email": "novo@example.com", "current_password": "SenhaErrada123"},
        headers=auth(token),
    )
    assert denied.status_code == 401 and denied.json() == {"detail": "invalid_current_password"}

    pending = client.patch(
        f"{PREFIX}/profile",
        json={"email": "novo@example.com", "current_password": USER["password"]},
        headers=auth(token),
    )
    assert pending.status_code == 200
    assert pending.json()["user"]["email"] == USER["email"]
    assert pending.json()["pending_email"] == "novo@example.com"
    assert capture.messages[-1][0] == "novo@example.com"

    confirmed = client.post(
        f"{PREFIX}/email-confirmation/confirm", json={"token": capture.messages[-1][1]}
    )
    assert confirmed.status_code == 200 and confirmed.json() == {"email_verified": True}
    assert client.get(f"{PREFIX}/me", headers=auth(token)).json()["email"] == "novo@example.com"
    assert (
        client.post(
            f"{PREFIX}/login", json={"email": USER["email"], "password": USER["password"]}
        ).status_code
        == 401
    )
    assert (
        client.post(
            f"{PREFIX}/login", json={"email": "novo@example.com", "password": USER["password"]}
        ).status_code
        == 200
    )


def test_SPEC_014_R03_duplicate_or_failed_delivery_keeps_valid_profile_data(client, app):
    capture = CaptureDelivery()
    app.state.email_delivery = capture
    token = register_and_login(client)
    with TestClient(app, base_url="https://localhost:8443") as other:
        register_and_login(other, OTHER)
    duplicate = client.patch(
        f"{PREFIX}/profile",
        json={"email": OTHER["email"], "current_password": USER["password"]},
        headers=auth(token),
    )
    assert duplicate.status_code == 409 and duplicate.json() == {"detail": "email_exists"}

    app.state.email_delivery = FailingDelivery()
    unavailable = client.patch(
        f"{PREFIX}/profile",
        json={
            "name": "Nome Não Salvo",
            "email": "falha@example.com",
            "current_password": USER["password"],
        },
        headers=auth(token),
    )
    assert unavailable.status_code == 503
    profile = client.get(f"{PREFIX}/profile", headers=auth(token)).json()
    assert profile["user"]["name"] == USER["name"]
    assert profile["pending_email"] is None


def test_SPEC_014_R04_profiles_are_isolated_and_invalid_input_is_generic(client, app):
    first = register_and_login(client)
    with TestClient(app, base_url="https://localhost:8443") as other:
        second = register_and_login(other, OTHER)
        assert (
            other.patch(
                f"{PREFIX}/profile/preferences",
                json=preferences("en", "dark"),
                headers=auth(second),
            ).status_code
            == 200
        )
    own = client.get(f"{PREFIX}/profile", headers=auth(first)).json()
    assert own["user"]["email"] == USER["email"]
    assert own["preferences"]["language"] == "pt"
    assert client.patch(f"{PREFIX}/profile", json={}, headers=auth(first)).json() == {
        "detail": "invalid_input"
    }
