"""SPEC-033: real asset goals, current progress and private projected contributions."""

from datetime import date, timedelta

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/auth/financial"


def _future_deadline() -> str:
    return (date.today() + timedelta(days=400)).isoformat()


def _goal(asset_id: str, target: str = "1000.00") -> dict[str, str]:
    return {
        "name": "Viagem",
        "category": "travel",
        "asset_id": asset_id,
        "target_amount": target,
        "deadline": _future_deadline(),
        "annual_rate": "0",
    }


def test_goal_tracks_manual_real_asset_without_duplicating_net_worth(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    owner = login(client, "named-goals-owner@example.com")
    verify(client, owner, delivery)
    asset = client.post(
        f"{PREFIX}/net-worth/items",
        headers=owner,
        json={"kind": "asset", "name": "Poupança para viagem", "value": "250"},
    )
    assert asset.status_code == 201
    asset_id = asset.json()["id"]
    baseline = client.get(f"{PREFIX}/net-worth", headers=owner).json()

    result = client.post(f"{PREFIX}/named-asset-goals", headers=owner, json=_goal(asset_id))
    assert result.status_code == 201, result.text
    goal = result.json()
    assert goal["current_value"] == "250.00"
    assert goal["progress_percent"] == "25.00"
    assert goal["remaining_amount"] == "750.00"
    assert goal["monthly_contribution_needed"] is not None
    assert float(goal["monthly_contribution_needed"]) > 0
    assert goal["asset_name"] == "Poupança para viagem"
    assert goal["projection_status"] == "needs_contribution"
    assert client.get(f"{PREFIX}/net-worth", headers=owner).json() == baseline

    second = client.post(
        f"{PREFIX}/named-asset-goals",
        headers=owner,
        json={**_goal(asset_id, "500"), "name": "Segunda meta"},
    )
    assert second.status_code == 201
    changed = client.patch(
        f"{PREFIX}/net-worth/items/{asset_id}", headers=owner, json={"value": "500"}
    )
    assert changed.status_code == 200
    values = client.get(f"{PREFIX}/named-asset-goals", headers=owner).json()
    assert len(values) == 2
    assert values[0]["current_value"] == "500.00"
    assert values[0]["progress_percent"] == "50.00"
    assert values[1]["progress_percent"] == "100.00"
    assert values[1]["monthly_contribution_needed"] == "0.00"

    removed = client.delete(f"{PREFIX}/named-asset-goals/{goal['id']}", headers=owner)
    assert removed.status_code == 204
    assert len(client.get(f"{PREFIX}/named-asset-goals", headers=owner).json()) == 1
    assert client.get(f"{PREFIX}/net-worth", headers=owner).json()["net_worth"] == "500.00"
    assert client.delete(f"{PREFIX}/net-worth/items/{asset_id}", headers=owner).status_code == 204
    assert client.get(f"{PREFIX}/named-asset-goals", headers=owner).json() == []


def test_goal_rejects_foreign_assets_liabilities_invalid_target_and_unverified(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    assert client.get(f"{PREFIX}/named-asset-goals").status_code == 401
    owner = login(client, "named-goals-private@example.com")
    assert client.get(f"{PREFIX}/named-asset-goals", headers=owner).status_code == 403
    verify(client, owner, delivery)
    asset = client.post(
        f"{PREFIX}/net-worth/items",
        headers=owner,
        json={"kind": "asset", "name": "Patrimônio", "value": "250"},
    ).json()
    debt = client.post(
        f"{PREFIX}/net-worth/items",
        headers=owner,
        json={"kind": "liability", "name": "Empréstimo", "value": "250"},
    ).json()
    assert (
        client.post(
            f"{PREFIX}/named-asset-goals",
            headers=owner,
            json=_goal(debt["id"]),
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"{PREFIX}/named-asset-goals",
            headers=owner,
            json=_goal(asset["id"], "0"),
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"{PREFIX}/named-asset-goals",
            headers=owner,
            json={**_goal(asset["id"]), "deadline": "2000-01-01"},
        ).status_code
        == 422
    )

    other = login(client, "named-goals-stranger@example.com")
    verify(client, other, delivery)
    assert (
        client.post(
            f"{PREFIX}/named-asset-goals", headers=other, json=_goal(asset["id"])
        ).status_code
        == 404
    )
    created = client.post(
        f"{PREFIX}/named-asset-goals", headers=owner, json=_goal(asset["id"])
    ).json()
    assert client.get(f"{PREFIX}/named-asset-goals", headers=other).json() == []
    assert (
        client.delete(f"{PREFIX}/named-asset-goals/{created['id']}", headers=other).status_code
        == 404
    )
    assert len(client.get(f"{PREFIX}/named-asset-goals", headers=owner).json()) == 1
