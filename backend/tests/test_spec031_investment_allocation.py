"""SPEC-031: only real classified investments enter owner-scoped allocation."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial/investment-allocation"
FIN = "/api/v1/auth/financial"
HALF = {
    "fixed_income": "50.00",
    "stocks": "50.00",
    "fiis": "0.00",
    "savings": "0.00",
    "other": "0.00",
}


def test_allocation_calculates_25_75_and_target_deviations(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "allocation-owner@example.com")
    assert client.get(PREFIX).status_code == 401
    assert client.get(PREFIX, headers=owner).status_code == 403
    verify(client, owner, delivery)

    ids = []
    for label, amount, category in (
        ("Título real", "25", "fixed_income"),
        ("Ação real", "75", "stocks"),
    ):
        created = client.post(
            f"{FIN}/net-worth/items",
            headers=owner,
            json={"kind": "asset", "name": label, "value": amount},
        )
        assert created.status_code == 201
        ids.append(created.json()["id"])
        classified = client.put(
            f"{PREFIX}/assets/{ids[-1]}",
            headers=owner,
            json={"asset_class": category},
        )
        assert classified.status_code == 200, classified.text

    projection = client.post(
        f"{FIN}/calculator",
        headers=owner,
        json={
            "initial_amount": "100000",
            "monthly_contribution": "0",
            "annual_rate": "12",
            "term_months": 12,
        },
    )
    assert projection.status_code == 200
    before = client.get(PREFIX, headers=owner).json()
    assert before["total_invested"] == "100.00"
    assert before["has_targets"] is False
    assert len(before["classified"]) == 2
    assert before["unclassified"] == []
    assert before["classes"][0]["actual_percent"] == "25.00"
    assert before["classes"][1]["actual_percent"] == "75.00"
    assert before["classes"][0]["deviation_points"] is None

    saved = client.put(f"{PREFIX}/targets", headers=owner, json={"targets": HALF})
    assert saved.status_code == 200, saved.text
    data = saved.json()
    assert data["has_targets"] is True
    assert data["classes"][0]["deviation_points"] == "-25.00"
    assert data["classes"][1]["deviation_points"] == "25.00"
    assert client.get(PREFIX, headers=owner).json() == data

    changed = client.patch(
        f"{FIN}/net-worth/items/{ids[0]}",
        headers=owner,
        json={"value": "75"},
    )
    assert changed.status_code == 200
    recalculated = client.get(PREFIX, headers=owner).json()
    assert recalculated["total_invested"] == "150.00"
    assert recalculated["classes"][0]["actual_percent"] == "50.00"
    assert recalculated["classes"][0]["deviation_points"] == "0.00"


def test_allocation_rejects_invalid_targets_and_cross_owner_access(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "allocation-private@example.com")
    verify(client, owner, delivery)
    manual = client.post(
        f"{FIN}/net-worth/items",
        headers=owner,
        json={"kind": "asset", "name": "Investimento", "value": "100"},
    )
    assert manual.status_code == 201
    id_ = manual.json()["id"]
    assert (
        client.put(
            f"{PREFIX}/targets",
            headers=owner,
            json={"targets": {**HALF, "fixed_income": "49"}},
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"{PREFIX}/targets",
            headers=owner,
            json={"targets": {"fixed_income": "100"}},
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"{PREFIX}/targets",
            headers=owner,
            json={"targets": {**HALF, "fixed_income": "-1"}},
        ).status_code
        == 422
    )
    assert client.get(PREFIX, headers=owner).json()["has_targets"] is False

    other = login(client, "allocation-other@example.com")
    verify(client, other, delivery)
    assert (
        client.put(
            f"{PREFIX}/assets/{id_}",
            headers=other,
            json={"asset_class": "stocks"},
        ).status_code
        == 404
    )
    assert client.delete(f"{PREFIX}/assets/{id_}", headers=other).status_code == 200
    assert client.get(PREFIX, headers=other).json()["total_invested"] == "0"
    assert client.get(PREFIX, headers=owner).json()["unclassified"][0]["id"] == id_

    assert (
        client.put(
            f"{PREFIX}/assets/{id_}",
            headers=owner,
            json={"asset_class": "stocks"},
        ).status_code
        == 200
    )
    assigned = client.put(
        f"{PREFIX}/assets/{id_}",
        headers=owner,
        json={"asset_class": "fixed_income"},
    )
    assert assigned.status_code == 200
    assert assigned.json()["classified"][0]["asset_class"] == "fixed_income"
    assert client.delete(f"{PREFIX}/assets/{id_}", headers=owner).status_code == 200
    assert len(client.get(PREFIX, headers=owner).json()["unclassified"]) == 1


def test_zero_investments_and_savings_do_not_invent_percentages(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "allocation-savings@example.com")
    verify(client, owner, delivery)
    empty = client.get(PREFIX, headers=owner).json()
    assert empty["total_invested"] == "0"
    assert all(row["actual_percent"] is None for row in empty["classes"])
    assert client.put(f"{PREFIX}/targets", headers=owner, json={"targets": HALF}).status_code == 200
    empty_goals = client.get(PREFIX, headers=owner).json()
    assert all(row["deviation_points"] is None for row in empty_goals["classes"])

    for name, account_type, amount in (
        ("Reserva", "savings", "200"),
        ("Dia a dia", "checking", "500"),
        ("Corretora", "investment", "100"),
    ):
        response = client.post(
            f"{FIN}/accounts",
            headers=owner,
            json={"name": name, "account_type": account_type, "initial_balance": amount},
        )
        assert response.status_code == 201
    view = client.get(PREFIX, headers=owner).json()
    assert view["total_invested"] == "300.00"
    assert view["classes"][3]["amount"] == "200.00"
    assert view["classes"][4]["amount"] == "100.00"
    assert view["classes"][3]["actual_percent"] == "66.67"
    assert view["classes"][4]["actual_percent"] == "33.33"
