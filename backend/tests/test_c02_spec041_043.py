"""C-02: SPEC-041-R05 (documentação pública da API externa) e SPEC-043 (uso por módulo)."""

from datetime import timedelta

from app.infrastructure.models import UserRecord
from tests.clause_support import verified_user


def test_SPEC_041_R05_external_api_is_in_public_openapi(client):
    schema = client.get("/api/v1/openapi.json").json()
    for path in ("/api/v1/external/balance", "/api/v1/external/net-worth"):
        assert path in schema["paths"]
        assert schema["paths"][path]["get"]["summary"]


def admin_with_usage(client, app):
    headers = verified_user(client, app, "admin-uso@example.com")
    other = verified_user(client, app, "membro-uso@example.com")
    with app.state.sessions() as db:
        for user in db.query(UserRecord):
            if app.state.security.decrypt(user.email_encrypted) == "admin-uso@example.com":
                user.role = "administrador"
        db.commit()
    for who, module in ((headers, "dashboard"), (other, "dashboard"), (headers, "simulator")):
        response = client.post(
            "/api/v1/auth/usage-events", headers=who, json={"module": module, "action": "opened"}
        )
        assert response.status_code == 202
    return headers


def test_SPEC_043_R03_R04_R05_accesses_and_unique_users_per_module_in_period(client, app):
    headers = admin_with_usage(client, app)
    today = app.state.clock().date()
    report = client.get(
        f"/api/v1/admin/engagement?start={today - timedelta(days=7)}&end={today}", headers=headers
    ).json()
    modules = {row["module"]: row for row in report["modules"]}
    assert modules["dashboard"] == {"module": "dashboard", "accesses": 2, "unique_users": 2}
    assert modules["simulator"]["accesses"] == 1
    assert report["most_used_module"] == "dashboard"
    assert report["least_used_module"] == "simulator"
    assert "membro-uso" not in str(report) and "email" not in str(report)
    empty = client.get(
        f"/api/v1/admin/engagement?start={today - timedelta(days=60)}"
        f"&end={today - timedelta(days=30)}",
        headers=headers,
    ).json()
    assert all(row["accesses"] == 0 for row in empty["modules"]) or empty["modules"] == []


def test_SPEC_043_R06_R08_engagement_metrics_and_trend_over_time(client, app):
    headers = admin_with_usage(client, app)
    report = client.get("/api/v1/admin/engagement?inactive_days=1", headers=headers).json()
    assert report["dau"] == report["wau"] == report["mau"] == 2
    assert report["inactive_days"] == 1 and report["inactive_users"] == 0
    today = str(app.state.clock().date())
    assert any(point["date"] == today and point["accesses"] == 3 for point in report["trend"])
