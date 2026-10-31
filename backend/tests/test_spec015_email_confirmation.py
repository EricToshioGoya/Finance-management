from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.infrastructure.email_delivery import EmailDeliveryError
from app.infrastructure.models import EmailConfirmationTokenRecord, UserRecord
from app.main import COOKIE

PREFIX = "/api/v1/auth"
USER = {"name": "Mariana Souza", "email": "mariana@example.com", "password": "SenhaForte123"}


class CaptureDelivery:
    def __init__(self):
        self.messages: list[tuple[str, str]] = []

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        self.messages.append((recipient, token))


class FailingDelivery:
    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        raise EmailDeliveryError("provider unavailable")


def register_and_login(client):
    assert client.post(f"{PREFIX}/register", json=USER).status_code == 201
    response = client.post(
        f"{PREFIX}/login", json={"email": USER["email"], "password": USER["password"]}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def request_token(client, headers):
    assert client.post(f"{PREFIX}/email-confirmation", headers=headers).status_code == 204
    return client.app.state.email_delivery.messages[-1][1]


def test_SPEC_015_R01_one_time_confirmation_and_pending_profile(client):
    capture = CaptureDelivery()
    client.app.state.email_delivery = capture
    headers = register_and_login(client)
    assert client.get(f"{PREFIX}/me", headers=headers).json()["email_verified"] is False
    token = request_token(client, headers)
    confirmed = client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": token})
    assert confirmed.status_code == 200 and confirmed.json() == {"email_verified": True}
    assert client.get(f"{PREFIX}/me", headers=headers).json()["email_verified"] is True
    repeated = client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": token})
    assert repeated.status_code == 400
    assert repeated.json() == {"detail": "invalid_confirmation_token"}


def test_SPEC_015_R02_expired_tampered_and_cross_account_tokens_do_not_confirm(client, app):
    capture = CaptureDelivery()
    client.app.state.email_delivery = capture
    headers = register_and_login(client)
    token = request_token(client, headers)
    with app.state.sessions() as db:
        record = db.scalar(select(EmailConfirmationTokenRecord))
        record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    assert (
        client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": token}).status_code
        == 400
    )
    assert (
        client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": "x" * 64}).status_code
        == 400
    )
    with app.state.sessions() as db:
        assert db.scalar(select(UserRecord)).email_verified_at is None


def test_SPEC_015_R03_digest_ttl_resend_limit_and_previous_invalidation(client, app):
    capture = CaptureDelivery()
    client.app.state.email_delivery = capture
    start = datetime.now(UTC).replace(microsecond=0)
    app.state.clock = lambda: start
    headers = register_and_login(client)
    first = request_token(client, headers)
    with app.state.sessions() as db:
        stored = db.scalar(select(EmailConfirmationTokenRecord))
        assert stored.digest != first and len(stored.digest) == 64
        assert stored.purpose == "email_confirmation"
        assert stored.expires_at == start + timedelta(hours=24)
    limited = client.post(f"{PREFIX}/email-confirmation", headers=headers)
    assert limited.status_code == 429 and limited.headers["retry-after"] == "60"
    app.state.clock = lambda: start + timedelta(seconds=60)
    second = request_token(client, headers)
    assert second != first
    assert (
        client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": first}).status_code
        == 400
    )
    assert client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": second}).json() == {
        "email_verified": True
    }


def test_email_delivery_failure_keeps_prior_token_usable(client, app):
    capture = CaptureDelivery()
    client.app.state.email_delivery = capture
    start = datetime.now(UTC).replace(microsecond=0)
    app.state.clock = lambda: start
    headers = register_and_login(client)
    token = request_token(client, headers)
    app.state.clock = lambda: start + timedelta(seconds=60)
    client.app.state.email_delivery = FailingDelivery()
    response = client.post(f"{PREFIX}/email-confirmation", headers=headers)
    assert response.status_code == 503 and response.json() == {
        "detail": "email_delivery_unavailable"
    }
    assert client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": token}).json() == {
        "email_verified": True
    }


def test_token_is_bound_to_its_owner_and_confirmation_is_atomic(app, client):
    capture = CaptureDelivery()
    client.app.state.email_delivery = capture
    headers = register_and_login(client)
    token = request_token(client, headers)

    def confirm(_):
        with TestClient(app, base_url="https://localhost:8443") as other:
            return other.post(
                f"{PREFIX}/email-confirmation/confirm", json={"token": token}
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(confirm, range(2))) == [200, 400]
    with app.state.sessions() as db:
        record = db.scalar(select(UserRecord))
        assert record.email_verified_at is not None


def test_unconfigured_delivery_does_not_persist_token_or_expose_it(client, app):
    from app.infrastructure.email_delivery import UnconfiguredEmailConfirmationDelivery

    client.app.state.email_delivery = UnconfiguredEmailConfirmationDelivery()
    headers = register_and_login(client)
    response = client.post(f"{PREFIX}/email-confirmation", headers=headers)
    assert response.status_code == 503 and response.json() == {
        "detail": "email_delivery_unavailable"
    }
    with app.state.sessions() as db:
        assert db.scalar(select(EmailConfirmationTokenRecord)) is None
    assert COOKIE in client.cookies


@pytest.mark.parametrize("body", [{}, {"token": "short"}, {"token": "x" * 513}, {"token": 42}])
def test_confirmation_rejects_malformed_input_without_echoing_token(client, body):
    response = client.post(f"{PREFIX}/email-confirmation/confirm", json=body)
    assert response.status_code == 422 and response.json() == {"detail": "invalid_input"}
