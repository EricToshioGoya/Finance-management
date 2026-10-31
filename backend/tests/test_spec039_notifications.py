"""SPEC-039: private in-app history, granular opt-out and deduplicated producer events."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import update

from app.infrastructure.models import NotificationRecord

PREFIX = "/api/v1/notifications"
PASSWORD = "StrongPassword123"


class Delivery:
    def __init__(self):
        self.tokens = []

    def deliver_confirmation(self, *, recipient, token):
        self.tokens.append(token)


def login(client, email):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Alert Owner", "email": email, "password": PASSWORD},
    )
    return {
        "Authorization": "Bearer "
        + client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).json()[
            "access_token"
        ]
    }


def verify(client, headers, delivery):
    client.post("/api/v1/auth/email-confirmation", headers=headers)
    assert (
        client.post(
            "/api/v1/auth/email-confirmation/confirm", json={"token": delivery.tokens[-1]}
        ).status_code
        == 200
    )


def event(client, headers, kind, source_key):
    return client.post(
        f"{PREFIX}/events", headers=headers, json={"kind": kind, "source_key": source_key}
    )


def test_spec039_creates_all_authorized_event_kinds_and_keeps_30_day_history(client, app):
    delivery = Delivery()
    app.state.email_delivery = delivery
    headers = login(client, "alerts@example.com")
    verify(client, headers, delivery)
    for kind in (
        "invoice_due",
        "budget_goal_exceeded",
        "watchlist_document",
        "recurring_expense_due",
    ):
        result = event(client, headers, kind, f"{kind}:2026-10")
        assert result.status_code == 200 and result.json()["created"] is True
    with app.state.engine.begin() as db:
        db.execute(
            update(NotificationRecord).values(created_at=datetime.now(UTC) - timedelta(days=31))
        )
    history = client.get(PREFIX, headers=headers)
    assert history.status_code == 200 and len(history.json()) == 4
    assert {item["kind"] for item in history.json()} == {
        "invoice_due",
        "budget_goal_exceeded",
        "watchlist_document",
        "recurring_expense_due",
    }


def test_spec039_opt_out_deduplication_read_state_and_owner_isolation(client, app):
    delivery = Delivery()
    app.state.email_delivery = delivery
    owner = login(client, "owner-alerts@example.com")
    other = login(client, "other-alerts@example.com")
    verify(client, owner, delivery)
    verify(client, other, delivery)
    disabled = client.put(
        f"{PREFIX}/preferences/budget_goal_exceeded", headers=owner, json={"enabled": False}
    )
    assert disabled.status_code == 200
    assert disabled.json() == {"kind": "budget_goal_exceeded", "enabled": False}
    assert event(client, owner, "budget_goal_exceeded", "goal:october").json() == {
        "created": False,
        "notification": None,
    }
    assert event(client, owner, "invoice_due", "card:october").json()["created"] is True
    repeated = event(client, owner, "invoice_due", "card:october").json()
    assert repeated["created"] is False and repeated["notification"] is not None
    item = client.get(PREFIX, headers=owner).json()[0]
    assert client.patch(f"{PREFIX}/{item['id']}/read", headers=owner).json()["read_at"] is not None
    assert client.get(f"{PREFIX}?unread_only=true", headers=owner).json() == []
    assert client.get(PREFIX, headers=other).json() == []
    assert client.patch(f"{PREFIX}/{item['id']}/read", headers=other).status_code == 404


def test_spec039_requires_authenticated_verified_owner_and_global_in_app_setting(client, app):
    delivery = Delivery()
    app.state.email_delivery = delivery
    headers = login(client, "unverified-alerts@example.com")
    assert event(client, headers, "invoice_due", "card:november").status_code == 403
    verify(client, headers, delivery)
    preferences = client.get("/api/v1/auth/profile", headers=headers).json()["preferences"]
    preferences["in_app_notifications"] = False
    assert (
        client.patch(
            "/api/v1/auth/profile/preferences", headers=headers, json=preferences
        ).status_code
        == 200
    )
    assert event(client, headers, "invoice_due", "card:november").json() == {
        "created": False,
        "notification": None,
    }
    assert client.get(PREFIX).status_code == 401
