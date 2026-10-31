"""SPEC-036: authenticated simulations never create financial records."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"
INPUT = {
    "asset_value": "120.00",
    "down_payment": "0.00",
    "installments": 12,
    "annual_rate": "0",
}


def test_financing_requires_session_and_confirmed_email(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    route = f"{PREFIX}/financing/simulate"
    assert client.post(route, json=INPUT).status_code == 401
    headers = login(client, "financing-unverified@example.com")
    assert client.post(route, json=INPUT, headers=headers).status_code == 403
    verify(client, headers, delivery)
    result = client.post(route, json=INPUT, headers=headers)
    assert result.status_code == 200, result.text
    payload = result.json()
    assert payload["total_paid"] == "120.00"
    assert payload["installment_amount"] == "10.00"
    assert payload["schedule"][-1]["remaining_balance"] == "0.00"
    assert payload["amortization_system"] == "price"
    assert payload["simulated_only"] is True
    assert payload["includes_fees"] is False


def test_financing_refuses_invalid_and_is_side_effect_free(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "financing-no-debt@example.com")
    verify(client, headers, delivery)
    route = f"{PREFIX}/financing/simulate"
    baseline = client.get(f"{PREFIX}/net-worth", headers=headers).json()
    for changes in (
        {"down_payment": "121"},
        {"installments": 0},
        {"annual_rate": "-1"},
        {"annual_rate": "101"},
    ):
        response = client.post(route, headers=headers, json={**INPUT, **changes})
        assert response.status_code == 422
    first = client.post(route, headers=headers, json=INPUT)
    second = client.post(route, headers=headers, json=INPUT)
    assert first.status_code == 200
    assert second.json() == first.json()
    assert client.get(f"{PREFIX}/net-worth", headers=headers).json() == baseline
