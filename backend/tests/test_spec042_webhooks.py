import hashlib
import hmac

from app.infrastructure.models import WebhookAttemptRecord

PASSWORD = "StrongPassword123"
PREFIX = "/api/v1/auth"


class Delivery:
    def __init__(self, status=204):
        self.status = status
        self.calls = []

    def deliver(self, url, payload, headers):
        self.calls.append((url, payload, headers))
        return self.status


def login_and_verify(client, app, email):
    delivery = app.state.email_delivery
    client.post(
        f"{PREFIX}/register",
        json={"name": "Webhook Owner", "email": email, "password": PASSWORD},
    )
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    headers = {"Authorization": f"Bearer {token}"}
    client.post(f"{PREFIX}/email-confirmation", headers=headers)
    client.post(f"{PREFIX}/email-confirmation/confirm", json={"token": delivery.tokens[-1]})
    return headers


def test_spec042_hmac_history_and_manual_retry(client, app):
    email_delivery = type(
        "Email",
        (),
        {"tokens": [], "deliver_confirmation": lambda self, **x: self.tokens.append(x["token"])},
    )()
    app.state.email_delivery = email_delivery
    outgoing = Delivery(status=503)
    app.state.webhook_delivery = outgoing
    headers = login_and_verify(client, app, "hooks@example.com")

    rejected = client.post(
        f"{PREFIX}/webhooks", headers=headers, json={"url": "http://example.com"}
    )
    assert rejected.status_code == 422
    created = client.post(
        f"{PREFIX}/webhooks", headers=headers, json={"url": "https://example.com/events"}
    )
    assert created.status_code == 201
    subscription = created.json()
    assert "signing_secret" in subscription
    assert "signing_secret" not in client.get(f"{PREFIX}/webhooks", headers=headers).json()[0]

    event = client.post(
        "/api/v1/notifications/events",
        headers=headers,
        json={"kind": "invoice_due", "source_key": "card:2026-10"},
    )
    assert event.status_code == 200 and event.json()["created"] is True
    assert len(outgoing.calls) == 1
    _, body, sent_headers = outgoing.calls[0]
    expected = hmac.new(subscription["signing_secret"].encode(), body, hashlib.sha256).hexdigest()
    assert sent_headers["X-FinNova-Signature"] == f"sha256={expected}"
    assert b"card:2026-10" not in body

    attempts = client.get(
        f"{PREFIX}/webhooks/{subscription['id']}/attempts", headers=headers
    ).json()
    assert attempts[0]["outcome"] == "failed"
    assert "payload" not in attempts[0]
    outgoing.status = 204
    retry = client.post(
        f"{PREFIX}/webhooks/{subscription['id']}/attempts/{attempts[0]['id']}/retry",
        headers=headers,
    )
    assert retry.status_code == 200 and retry.json()["outcome"] == "succeeded"
    with app.state.sessions() as db:
        assert db.query(WebhookAttemptRecord).count() == 2


def test_spec042_owner_isolation(client, app):
    email_delivery = type(
        "Email",
        (),
        {"tokens": [], "deliver_confirmation": lambda self, **x: self.tokens.append(x["token"])},
    )()
    app.state.email_delivery = email_delivery
    first = login_and_verify(client, app, "first-hooks@example.com")
    second = login_and_verify(client, app, "second-hooks@example.com")
    created = client.post(
        f"{PREFIX}/webhooks", headers=first, json={"url": "https://example.com/a"}
    ).json()
    assert client.get(f"{PREFIX}/webhooks/{created['id']}/attempts", headers=second).json() == []
    assert client.delete(f"{PREFIX}/webhooks/{created['id']}", headers=second).status_code == 404
