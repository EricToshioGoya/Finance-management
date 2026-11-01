"""SPEC-029: historical positions must be persisted, scoped, and idempotent."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"


def test_snapshot_is_real_idempotent_and_not_retroactively_recalculated(client):
    """Cláusulas: SPEC-029-R01, SPEC-029-R02, SPEC-029-R03, SPEC-029-R04, SPEC-029-R05."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "history-owner@example.com")
    verify(client, headers, delivery)

    assert client.get(f"{PREFIX}/net-worth/history", headers=headers).json() == []
    assert client.get(f"{PREFIX}/net-worth/history").status_code == 401
    assert (
        client.post(
            f"{PREFIX}/accounts",
            headers=headers,
            json={"name": "Conta", "account_type": "checking", "initial_balance": "100"},
        ).status_code
        == 201
    )
    debt = client.post(
        f"{PREFIX}/net-worth/items",
        headers=headers,
        json={"kind": "liability", "name": "Dívida", "value": "30"},
    )
    assert debt.status_code == 201
    captured = client.post(f"{PREFIX}/net-worth/history/snapshots", headers=headers)
    assert captured.status_code == 201, captured.text
    assert captured.json()["total_assets"] == "100.00"
    assert captured.json()["total_liabilities"] == "30.00"
    assert captured.json()["net_worth"] == "70.00"
    month = captured.json()["competence"]

    assert (
        client.patch(
            f"{PREFIX}/net-worth/items/{debt.json()['id']}",
            headers=headers,
            json={"value": "20"},
        ).status_code
        == 200
    )
    repeat = client.post(f"{PREFIX}/net-worth/history/snapshots", headers=headers)
    assert repeat.status_code == 201
    assert repeat.json() == captured.json()
    history = client.get(f"{PREFIX}/net-worth/history", headers=headers).json()
    assert len(history) == 1 and history[0]["net_worth"] == "70.00"
    assert (
        client.get(f"{PREFIX}/net-worth/history?start={month}&end={month}", headers=headers).json()
        == history
    )
    assert client.get(f"{PREFIX}/net-worth/history?start=2099-01-01", headers=headers).json() == []
    assert (
        client.get(
            f"{PREFIX}/net-worth/history?start=2026-12-01&end=2026-01-01",
            headers=headers,
        ).status_code
        == 422
    )


def test_history_is_private_and_does_not_backfill_missing_months(client):
    """Cláusulas: SPEC-029-R02."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "history-private@example.com")
    verify(client, owner, delivery)
    first = client.post(f"{PREFIX}/net-worth/history/snapshots", headers=owner)
    assert first.status_code == 201

    other = login(client, "history-other@example.com")
    verify(client, other, delivery)
    assert client.get(f"{PREFIX}/net-worth/history", headers=other).json() == []
    assert client.get(f"{PREFIX}/net-worth/history", headers=owner).json() == [first.json()]
    assert client.post(f"{PREFIX}/net-worth/history/snapshots", headers=other).status_code == 201
    assert len(client.get(f"{PREFIX}/net-worth/history", headers=other).json()) == 1
