from datetime import UTC, datetime

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"


def test_monthly_capture_uses_sao_paulo_and_verified_email(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "month-boundary@example.com")
    assert client.post(f"{PREFIX}/net-worth/history/snapshots").status_code == 401
    assert client.get(f"{PREFIX}/net-worth").status_code == 401
    invalid = client.get(f"{PREFIX}/net-worth/history", headers={"Authorization": "Bearer invalid"})
    assert invalid.status_code == 401
    assert client.get(f"{PREFIX}/net-worth/history", headers=headers).status_code == 403
    assert client.post(f"{PREFIX}/net-worth/history/snapshots", headers=headers).status_code == 403
    verify(client, headers, delivery)
    client.app.state.clock = lambda: datetime(2026, 11, 1, 0, 30, tzinfo=UTC)
    october = client.post(f"{PREFIX}/net-worth/history/snapshots", headers=headers)
    assert october.status_code == 201
    assert october.json()["competence"] == "2026-10-01"
    client.app.state.clock = lambda: datetime(2026, 11, 1, 3, 30, tzinfo=UTC)
    november = client.post(f"{PREFIX}/net-worth/history/snapshots", headers=headers)
    assert november.status_code == 201
    assert november.json()["competence"] == "2026-11-01"
    assert len(client.get(f"{PREFIX}/net-worth/history", headers=headers).json()) == 2
