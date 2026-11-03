"""Cobertura dos adaptadores de e-mail/canais e dos jobs manuais (varredura de QA 2026-11-03).

Dublês substituem `urlopen` e os serviços de sincronização: nenhum serviço externo é chamado
(C-17). Cláusulas citadas: SPEC-015 (confirmação), SPEC-016 (recuperação), SPEC-061 (canais),
SPEC-007/SPEC-027/SPEC-040 (rotinas).
"""

import json

import pytest

from app.infrastructure import channel_delivery, email_delivery
from app.infrastructure.channel_delivery import (
    ChannelDeliveryError,
    ChannelUnavailable,
    HttpsChannelDelivery,
    UnconfiguredChannelDelivery,
)
from app.infrastructure.email_delivery import (
    EmailDeliveryError,
    UnconfiguredEmailConfirmationDelivery,
    WebhookEmailConfirmationDelivery,
)


class FakeResponse:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def fake_urlopen(status=204, error=None, sent=None):
    def opener(request, timeout):
        if sent is not None:
            sent.append((request.full_url, json.loads(request.data), timeout))
        if error is not None:
            raise error
        return FakeResponse(status)

    return opener


def test_SPEC_015_R01_SPEC_016_R01_webhook_email_builds_links_and_maps_failures(monkeypatch):
    sent = []
    monkeypatch.setattr(email_delivery, "urlopen", fake_urlopen(sent=sent))
    delivery = WebhookEmailConfirmationDelivery("https://mail.example/send", "https://app.example")
    delivery.deliver_confirmation(recipient="a@example.com", token="tok")
    delivery.deliver_password_reset(recipient="a@example.com", token="tok2")
    assert sent[0][1]["confirmation_url"] == "https://app.example/#/confirmar-email?token=tok"
    assert sent[1][1]["password_reset_url"].endswith("redefinir-senha?token=tok2")
    assert all(timeout == 5 for *_, timeout in sent)

    monkeypatch.setattr(email_delivery, "urlopen", fake_urlopen(status=500))
    with pytest.raises(EmailDeliveryError):
        delivery.deliver_confirmation(recipient="a@example.com", token="tok")
    with pytest.raises(EmailDeliveryError):
        delivery.deliver_password_reset(recipient="a@example.com", token="tok")
    monkeypatch.setattr(email_delivery, "urlopen", fake_urlopen(error=OSError("down")))
    with pytest.raises(EmailDeliveryError):
        delivery.deliver_confirmation(recipient="a@example.com", token="tok")
    with pytest.raises(EmailDeliveryError):
        delivery.deliver_password_reset(recipient="a@example.com", token="tok")
    unconfigured = UnconfiguredEmailConfirmationDelivery()
    with pytest.raises(EmailDeliveryError):
        unconfigured.deliver_confirmation(recipient="a@example.com", token="tok")
    with pytest.raises(EmailDeliveryError):
        unconfigured.deliver_password_reset(recipient="a@example.com", token="tok")


def test_SPEC_061_R01_https_channel_sends_attachment_and_maps_failures(monkeypatch):
    sent = []
    monkeypatch.setattr(channel_delivery, "urlopen", fake_urlopen(sent=sent))
    delivery = HttpsChannelDelivery("https://push.example/send")
    delivery.send(
        channel="email",
        destination="a@example.com",
        title="Resumo",
        message="Seu resumo",
        attachment=("resumo.pdf", b"%PDF"),
    )
    payload = sent[0][1]
    assert payload["attachment"] == {"filename": "resumo.pdf", "content_base64": "JVBERg=="}
    delivery.send(channel="push", destination="device", title="t", message="m")
    assert "attachment" not in sent[1][1]
    monkeypatch.setattr(channel_delivery, "urlopen", fake_urlopen(status=503))
    with pytest.raises(ChannelDeliveryError):
        delivery.send(channel="push", destination="d", title="t", message="m")
    monkeypatch.setattr(channel_delivery, "urlopen", fake_urlopen(error=OSError("down")))
    with pytest.raises(ChannelDeliveryError):
        delivery.send(channel="push", destination="d", title="t", message="m")
    with pytest.raises(ChannelUnavailable):
        UnconfiguredChannelDelivery().send(channel="push")


def test_SPEC_007_R06_SPEC_027_R05_SPEC_040_R01_manual_jobs_use_configured_services(
    app, monkeypatch
):
    from app.jobs import cvm_sync, indicator_sync, monthly_summary

    settings = app.state.settings
    for module in (cvm_sync, indicator_sync, monthly_summary):
        monkeypatch.setattr(module, "get_settings", lambda: settings)
    calls = []
    monkeypatch.setattr(
        indicator_sync.IndicatorSyncService,
        "run",
        lambda self, items=None: calls.append("indicadores") or {"selic": "kept"},
    )
    monkeypatch.setattr(
        cvm_sync.CvmSyncService,
        "run",
        lambda self, items=None: calls.append("cvm") or {"cadastro": "updated"},
    )
    monkeypatch.setattr(
        monthly_summary.MonthlySummaryService,
        "run",
        lambda self: calls.append("resumo") or {"generated": 0},
    )
    assert indicator_sync.main() == {"selic": "kept"}
    assert cvm_sync.main() == {"cadastro": "updated"}
    assert monthly_summary.main() == {"generated": 0}
    assert calls == ["indicadores", "cvm", "resumo"]
    configured = settings.model_copy(
        update={"email_webhook_url": type(settings.jwt_secret)("https://mail.example/send")}
    )
    monkeypatch.setattr(monthly_summary, "get_settings", lambda: configured)
    assert monthly_summary.main() == {"generated": 0}
