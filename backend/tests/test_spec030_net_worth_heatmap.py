"""SPEC-030: heatmap contains only real owned positions and preserves reported rates."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"


def test_heatmap_requires_verified_session_and_starts_empty(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    assert client.get(f"{PREFIX}/net-worth/heatmap").status_code == 401
    headers = login(client, "heatmap-unverified@example.com")
    assert client.get(f"{PREFIX}/net-worth/heatmap", headers=headers).status_code == 403
    verify(client, headers, delivery)
    result = client.get(f"{PREFIX}/net-worth/heatmap", headers=headers)
    assert result.status_code == 200
    assert result.json()["items"] == []
    assert result.json()["total_absolute"] == "0"


def test_heatmap_preserves_relative_values_rates_and_privacy(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "heatmap-owner@example.com")
    verify(client, owner, delivery)
    for name, value, rate in (
        ("Investimento menor", "100", "0"),
        ("Investimento maior", "300", "12"),
    ):
        created = client.post(
            f"{PREFIX}/net-worth/items",
            headers=owner,
            json={"kind": "asset", "name": name, "value": value, "annual_rate": rate},
        )
        assert created.status_code == 201
    liability = client.post(
        f"{PREFIX}/net-worth/items",
        headers=owner,
        json={"kind": "liability", "name": "Empréstimo", "value": "50", "annual_rate": "20"},
    )
    assert liability.status_code == 201
    assert (
        client.post(
            f"{PREFIX}/calculator",
            headers=owner,
            json={
                "initial_amount": "50000",
                "monthly_contribution": "0",
                "annual_rate": "10",
                "term_months": 12,
            },
        ).status_code
        == 200
    )
    response = client.get(f"{PREFIX}/net-worth/heatmap", headers=owner)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total_absolute"] == "450.00"
    by_name = {item["name"]: item for item in data["items"]}
    assert by_name["Investimento menor"]["value"] == "100.00"
    assert by_name["Investimento maior"]["value"] == "300.00"
    assert by_name["Investimento maior"]["annual_rate"] == "12.0000"
    assert by_name["Empréstimo"]["kind"] == "liability"
    assert by_name["Empréstimo"]["annual_rate"] == "20.0000"

    other = login(client, "heatmap-other@example.com")
    verify(client, other, delivery)
    assert client.get(f"{PREFIX}/net-worth/heatmap", headers=other).json()["items"] == []

    changed = client.patch(
        f"{PREFIX}/net-worth/items/{liability.json()['id']}",
        headers=owner,
        json={"value": "70"},
    )
    assert changed.status_code == 200
    refreshed = client.get(f"{PREFIX}/net-worth/heatmap", headers=owner).json()
    assert refreshed["total_absolute"] == "470.00"
    assert len(refreshed["items"]) == 3


def test_heatmap_missing_rate_is_not_invented(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "heatmap-missing-rate@example.com")
    verify(client, owner, delivery)
    assert (
        client.post(
            f"{PREFIX}/accounts",
            headers=owner,
            json={"name": "Conta real", "account_type": "checking", "initial_balance": "75"},
        ).status_code
        == 201
    )
    data = client.get(f"{PREFIX}/net-worth/heatmap", headers=owner).json()
    assert data["total_absolute"] == "75.00"
    assert data["items"][0]["annual_rate"] is None
    assert data["items"][0]["origin"] == "account"
