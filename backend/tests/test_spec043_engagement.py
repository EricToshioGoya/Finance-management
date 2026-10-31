from sqlalchemy import update

from app.infrastructure.models import UserRecord

PASSWORD = "StrongPassword123"


def headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Administrator", "email": "admin@example.com", "password": PASSWORD},
    )
    token = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_spec043_admin_aggregate_report_and_inactivity(client, app):
    admin = headers(client)
    with app.state.engine.begin() as db:
        db.execute(update(UserRecord).values(role="administrador"))
    for module in ("dashboard", "dashboard", "simulator"):
        assert (
            client.post(
                "/api/v1/auth/usage-events",
                headers=admin,
                json={"module": module, "action": "opened"},
            ).status_code
            == 202
        )

    report = client.get("/api/v1/admin/engagement?inactive_days=30", headers=admin)
    assert report.status_code == 200
    data = report.json()
    assert data["dau"] == 1 and data["mau"] == 1
    assert data["most_used_module"] == "dashboard"
    assert data["average_frequency"] == 3
    assert data["recurring_modules"] == [{"module": "dashboard", "recurring_users": 1}]
    assert "email" not in str(data) and "id" not in str(data)


def test_spec043_requires_admin(client):
    assert client.get("/api/v1/admin/engagement").status_code == 401
    ordinary = headers(client)
    assert client.get("/api/v1/admin/engagement", headers=ordinary).status_code == 403
