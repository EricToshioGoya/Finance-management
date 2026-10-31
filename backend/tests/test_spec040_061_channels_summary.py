"""SPEC-061 (canais externos opcionais) e SPEC-040 (resumo mensal automático optativo)."""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select, update

from app.application.auth import AuthService
from app.application.monthly_summary import MonthlySummaryService, previous_month
from app.infrastructure.channel_delivery import ChannelDeliveryError, UnconfiguredChannelDelivery
from app.infrastructure.models import (
    MonthlySummaryRecord,
    NotificationDeliveryRecord,
    NotificationRecord,
    UserRecord,
)

PREFIX = "/api/v1/auth"
NOTIFY = "/api/v1/notifications"
PASSWORD = "StrongPassword123"


class FakeChannel:
    """Dublê do despachante externo (C-17): registra envios sem rede."""

    def __init__(self, fail=False):
        self.sent, self.fail = [], fail

    def send(self, *, channel, destination, title, message, attachment=None):
        if self.fail:
            raise ChannelDeliveryError("down")
        self.sent.append({"channel": channel, "destination": destination, "attachment": attachment})


def verified(client, app, email="chan@example.com"):
    created = client.post(
        f"{PREFIX}/register", json={"name": "Canal", "email": email, "password": PASSWORD}
    ).json()
    with app.state.engine.begin() as db:
        db.execute(
            update(UserRecord)
            .where(UserRecord.id == uuid.UUID(created["id"]))
            .values(email_verified_at=datetime.now(UTC))
        )
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}, uuid.UUID(created["id"])


def preferences(client, headers, email=False, push=False, in_app=True):
    response = client.patch(
        f"{PREFIX}/profile/preferences",
        headers=headers,
        json={
            "language": "pt",
            "theme": "light",
            "in_app_notifications": in_app,
            "email_notifications": email,
            "push_notifications": push,
        },
    )
    assert response.status_code == 200


def event(client, headers, key="invoice_due:2026-10"):
    return client.post(
        f"{NOTIFY}/events", headers=headers, json={"kind": "invoice_due", "source_key": key}
    )


def deliveries(app):
    with app.state.sessions() as db:
        return [(row.channel, row.status) for row in db.scalars(select(NotificationDeliveryRecord))]


# ---------------- SPEC-061 ----------------
def test_SPEC_061_R01_R03_in_app_is_base_and_channels_are_opt_in(client, app):
    email, push = FakeChannel(), FakeChannel()
    app.state.channel_delivery = {"email": email, "push": push}
    headers, _ = verified(client, app)
    assert event(client, headers).json()["created"] is True
    assert email.sent == push.sent == [] and deliveries(app) == []  # opt-in desligado por padrão
    preferences(client, headers, email=True)
    event(client, headers, "invoice_due:2026-11")
    assert len(email.sent) == 1 and email.sent[0]["destination"] == "chan@example.com"
    assert deliveries(app) == [("email", "sent")]
    assert len(client.get(NOTIFY, headers=headers).json()) == 2  # histórico in-app preservado


def test_SPEC_061_R04_push_uses_configured_adapter_and_registered_device(client, app):
    push = FakeChannel()
    app.state.channel_delivery = {"email": UnconfiguredChannelDelivery(), "push": push}
    headers, _ = verified(client, app)
    preferences(client, headers, push=True)
    event(client, headers, "invoice_due:a")
    assert deliveries(app) == [("push", "no_destination")]
    token = "fcm-device-token-1234567890"
    assert (
        client.post(f"{NOTIFY}/push-devices", headers=headers, json={"token": token}).status_code
        == 201
    )
    event(client, headers, "invoice_due:b")
    assert push.sent[-1]["destination"] == token and ("push", "sent") in deliveries(app)
    listed = client.get(f"{NOTIFY}/deliveries", headers=headers).json()
    assert token not in str(listed) and "message" not in str(listed)  # resultado mínimo


def test_SPEC_061_R02_missing_provider_or_failure_never_records_success(client, app):
    app.state.channel_delivery = {"email": UnconfiguredChannelDelivery(), "push": FakeChannel(True)}
    headers, _ = verified(client, app)
    preferences(client, headers, email=True, push=True)
    client.post(f"{NOTIFY}/push-devices", headers=headers, json={"token": "x" * 20})
    assert event(client, headers).json()["created"] is True  # in-app não depende do canal
    assert sorted(deliveries(app)) == [("email", "provider_unavailable"), ("push", "failed")]
    other, _ = verified(client, app, "other@example.com")
    assert client.get(f"{NOTIFY}/deliveries", headers=other).json() == []


def test_SPEC_061_R03_disabling_channel_stops_delivery(client, app):
    email = FakeChannel()
    app.state.channel_delivery = {"email": email, "push": FakeChannel()}
    headers, _ = verified(client, app)
    preferences(client, headers, email=True)
    event(client, headers, "invoice_due:1")
    preferences(client, headers, email=False)
    event(client, headers, "invoice_due:2")
    assert len(email.sent) == 1
    assert client.delete(f"{NOTIFY}/push-devices", headers=headers).status_code == 204


# ---------------- SPEC-040 ----------------
def run_job(app, clock):
    with app.state.sessions() as db:
        auth = AuthService(
            db,
            None,  # o job não usa configurações de sessão
            app.state.security,
            clock=lambda: clock,
            channel_delivery=app.state.channel_delivery,
        )
        return MonthlySummaryService(db, auth).run()


def test_SPEC_040_R01_R03_R04_sends_previous_month_pdf_by_email(client, app):
    email = FakeChannel()
    app.state.channel_delivery = {"email": email, "push": FakeChannel()}
    headers, user_id = verified(client, app)
    preferences(client, headers, email=True)
    assert client.get(f"{PREFIX}/profile/reports", headers=headers).json() == {
        "monthly_summary_enabled": False
    }
    client.put(f"{PREFIX}/profile/reports", headers=headers, json={"monthly_summary_enabled": True})
    clock = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)  # 06h de 01/11 em São Paulo
    assert run_job(app, clock)["generated"] == 1
    sent = email.sent[0]
    assert sent["attachment"][0] == "resumo-2026-10.pdf"
    assert sent["attachment"][1].startswith(b"%PDF")
    history = client.get(f"{PREFIX}/financial/monthly-summaries", headers=headers).json()
    assert history[0] == {**history[0], "competence": "2026-10", "status": "sent"}
    # Um envio por mês: nova execução não duplica.
    assert run_job(app, clock) == {"generated": 0, "skipped": 1} and len(email.sent) == 1


def test_SPEC_040_R02_failure_is_not_recorded_as_sent(client, app):
    app.state.channel_delivery = {"email": FakeChannel(fail=True), "push": FakeChannel()}
    headers, user_id = verified(client, app)
    preferences(client, headers, email=True)
    client.put(f"{PREFIX}/profile/reports", headers=headers, json={"monthly_summary_enabled": True})
    run_job(app, datetime(2026, 11, 2, 12, tzinfo=UTC))
    with app.state.sessions() as db:
        record = db.scalar(
            select(MonthlySummaryRecord).where(MonthlySummaryRecord.user_id == user_id)
        )
        assert record.status == "failed"
        assert db.scalar(select(NotificationRecord)) is None  # dados financeiros intactos


def test_SPEC_040_R05_opt_out_and_previous_month_only(client, app):
    email = FakeChannel()
    app.state.channel_delivery = {"email": email, "push": FakeChannel()}
    headers, _ = verified(client, app)
    preferences(client, headers, email=True)
    client.put(f"{PREFIX}/profile/reports", headers=headers, json={"monthly_summary_enabled": True})
    client.put(
        f"{PREFIX}/profile/reports", headers=headers, json={"monthly_summary_enabled": False}
    )
    assert run_job(app, datetime(2026, 11, 1, 9, tzinfo=UTC))["generated"] == 0
    # 01/11 às 02h UTC ainda é 31/10 em São Paulo: o mês anterior é setembro.
    assert previous_month(datetime(2026, 11, 1, 2, tzinfo=UTC)) == date(2026, 9, 1)
    current = date.today().strftime("%Y-%m")
    response = client.get(f"{PREFIX}/financial/monthly-summaries/{current}/pdf", headers=headers)
    assert response.status_code == 422
    closed = client.get(f"{PREFIX}/financial/monthly-summaries/2026-01/pdf", headers=headers)
    assert closed.status_code == 200 and closed.content.startswith(b"%PDF")
