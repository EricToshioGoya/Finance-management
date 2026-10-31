"""SPEC-062: distribuição de perfis de investidor no painel administrativo."""

from datetime import UTC, datetime

from sqlalchemy import update

from app.infrastructure.models import UserRecord

PREFIX = "/api/v1/auth"
URL = "/api/v1/admin/investor-profiles"
PASSWORD = "StrongPassword123"
# Respostas do quiz (SPEC-003) que produzem cada perfil.
ANSWERS = {"conservador": [0, 0, 0, 0, 0], "arrojado": [2, 2, 2, 2, 2]}


def login(client, email, name="Pessoa"):
    client.post(f"{PREFIX}/register", json={"name": name, "email": email, "password": PASSWORD})
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def admin_headers(client, app):
    headers = login(client, "admin@example.com", "Admin")
    with app.state.engine.begin() as db:
        db.execute(update(UserRecord).values(role="administrador"))  # único usuário até aqui
    return headers


def answer_quiz(client, headers, profile):
    response = client.put(
        f"{PREFIX}/investor-profile", headers=headers, json={"answers": ANSWERS[profile]}
    )
    assert response.status_code == 200 and response.json()["profile"] == profile


def test_SPEC_062_R01_R03_aggregated_distribution_by_quiz_result(client, app):
    admin = admin_headers(client, app)
    answer_quiz(client, login(client, "a@example.com"), "conservador")
    answer_quiz(client, login(client, "b@example.com"), "conservador")
    answer_quiz(client, login(client, "c@example.com"), "arrojado")
    data = client.get(URL, headers=admin).json()
    by_profile = {item["profile"]: item for item in data["items"]}
    assert data["profiled_users"] == 3 and data["without_profile"] == 1  # admin sem quiz
    assert by_profile["conservador"]["count"] == 2
    assert by_profile["conservador"]["percentage"] == "66.67"
    assert by_profile["moderado"]["count"] == 0
    assert by_profile["arrojado"]["percentage"] == "33.33"
    # INV-001: nenhum identificador, e-mail ou resposta individual na saída.
    assert "@" not in str(data) and "answers" not in str(data)


def test_SPEC_062_R02_only_administrators_receive_the_chart(client, app):
    assert client.get(URL).status_code == 401
    ordinary = login(client, "ordinary@example.com")
    response = client.get(URL, headers=ordinary)
    assert response.status_code == 403 and response.json()["detail"] == "admin_access_denied"


def test_SPEC_062_R04_filters_by_registration_period(client, app):
    admin = admin_headers(client, app)
    old = login(client, "old@example.com")
    answer_quiz(client, old, "arrojado")
    with app.state.engine.begin() as db:
        # 10/01/2025 às 23h30 em São Paulo = 11/01/2025 02h30 UTC: conta no dia local 10.
        db.execute(
            update(UserRecord)
            .where(UserRecord.investor_profile.isnot(None))
            .values(created_at=datetime(2025, 1, 11, 2, 30, tzinfo=UTC))
        )
    recent = client.get(URL, headers=admin, params={"start": "2026-01-01"}).json()
    assert recent["profiled_users"] == 0
    period = client.get(
        URL, headers=admin, params={"start": "2025-01-10", "end": "2025-01-10"}
    ).json()
    assert period["profiled_users"] == 1 and period["total_users"] == 1
    invalid = client.get(URL, headers=admin, params={"start": "2025-02-01", "end": "2025-01-01"})
    assert invalid.status_code == 422


def test_SPEC_062_R05_updates_when_a_new_user_completes_the_quiz(client, app):
    admin = admin_headers(client, app)
    newcomer = login(client, "new@example.com")
    before = client.get(URL, headers=admin).json()
    assert before["profiled_users"] == 0 and before["without_profile"] == 2
    answer_quiz(client, newcomer, "conservador")
    after = client.get(URL, headers=admin).json()
    assert after["profiled_users"] == 1 and after["without_profile"] == 1
