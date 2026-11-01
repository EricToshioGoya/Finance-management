"""SPEC-037: private comparison cannot change real net worth."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"
REQUEST = {
    "asset_value": "120.00",
    "down_payment": "0.00",
    "installments": 12,
    "financing_annual_rate": "0",
    "investment_annual_rate": "0",
    "horizon_months": 12,
}


def test_comparison_requires_auth_and_email_verification(client):
    """Cláusulas: SPEC-037-R01, SPEC-037-R02."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    route = f"{PREFIX}/financing/compare"
    assert client.post(route, json=REQUEST).status_code == 401
    headers = login(client, "compare-unverified@example.com")
    assert client.post(route, headers=headers, json=REQUEST).status_code == 403
    verify(client, headers, delivery)
    result = client.post(route, headers=headers, json=REQUEST)
    assert result.status_code == 200, result.text
    data = result.json()
    assert data["simulated_only"] is True
    assert data["monthly_investment"] == "10.00"
    assert data["invest_possession_month"] == 12
    assert data["financing_possession_month"] == 0
    assert data["nominal_cost_difference"] == "0.00"
    assert data["lower_nominal_cost"] == "tie"


def test_comparison_cannot_invent_purchase_or_change_owner_data(client):
    """Cláusulas: SPEC-037-R02, SPEC-037-R05."""
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "compare-owner@example.com")
    verify(client, headers, delivery)
    initial = client.get(f"{PREFIX}/net-worth", headers=headers).json()
    route = f"{PREFIX}/financing/compare"
    short = client.post(route, headers=headers, json={**REQUEST, "horizon_months": 4})
    assert short.status_code == 200
    data = short.json()
    assert data["invest_possession_month"] is None
    assert data["lower_nominal_cost"] == "not_comparable"
    assert data["nominal_cost_difference"] is None
    for bad in (
        {"down_payment": "200"},
        {"horizon_months": 0},
        {"investment_annual_rate": "-1"},
        {"installments": 0},
    ):
        assert client.post(route, headers=headers, json={**REQUEST, **bad}).status_code == 422
    assert client.post(route, headers=headers, json=REQUEST).status_code == 200
    assert client.get(f"{PREFIX}/net-worth", headers=headers).json() == initial
