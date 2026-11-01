"""SPEC-003: five-answer investor profile quiz, redo and simulator guidance."""

from sqlalchemy import select

from app.infrastructure.models import UserRecord

PREFIX = "/api/v1/auth"
PASSWORD = "StrongPassword123"


def register_and_login(client, name="Quiz User", email="quiz@example.com"):
    assert (
        client.post(
            f"{PREFIX}/register", json={"name": name, "email": email, "password": PASSWORD}
        ).status_code
        == 201
    )
    response = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_spec003_quiz_has_only_five_safe_questions_and_requires_session(client):
    """Cláusulas: SPEC-003-R02, SPEC-003-R03."""
    assert client.get(f"{PREFIX}/investor-profile/quiz").status_code == 401
    headers = register_and_login(client)
    response = client.get(f"{PREFIX}/investor-profile/quiz", headers=headers)
    assert response.status_code == 200
    questions = response.json()
    assert [question["id"] for question in questions] == [
        "knowledge",
        "loss",
        "horizon",
        "liquidity",
        "volatility",
    ]
    assert all(
        len(question["options"]) == 3 and set(question) == {"id", "prompt", "options"}
        for question in questions
    )


def test_spec003_validates_answers_persists_and_allows_redo(client):
    """Cláusulas: SPEC-003-R01, SPEC-003-R02, SPEC-003-R04, SPEC-003-R05, SPEC-003-R06."""
    headers = register_and_login(client)
    assert client.get(f"{PREFIX}/investor-profile", headers=headers).json()["profile"] is None
    assert (
        client.put(
            f"{PREFIX}/investor-profile", headers=headers, json={"answers": [0, 0]}
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"{PREFIX}/investor-profile", headers=headers, json={"answers": [0, 0, 0, 0, 3]}
        ).status_code
        == 422
    )
    conservative = client.put(
        f"{PREFIX}/investor-profile", headers=headers, json={"answers": [0] * 5}
    )
    assert conservative.status_code == 200
    assert conservative.json()["profile"] == "conservador" and conservative.json()["score"] == 0
    moderate = client.put(f"{PREFIX}/investor-profile", headers=headers, json={"answers": [1] * 5})
    assert moderate.json()["profile"] == "moderado" and moderate.json()["score"] == 5
    bold = client.put(f"{PREFIX}/investor-profile", headers=headers, json={"answers": [2] * 5})
    assert bold.json()["profile"] == "arrojado" and bold.json()["score"] == 10
    assert client.get(f"{PREFIX}/investor-profile", headers=headers).json()["profile"] == "arrojado"


def test_spec003_profile_is_private_and_guides_authenticated_simulator(client, app):
    """Cláusulas: SPEC-003-R01, SPEC-003-R05."""
    first = register_and_login(client, "First", "first@example.com")
    second = register_and_login(client, "Second", "second@example.com")
    assert (
        client.put(
            f"{PREFIX}/investor-profile", headers=first, json={"answers": [0] * 5}
        ).status_code
        == 200
    )
    assert client.get(f"{PREFIX}/investor-profile", headers=second).json()["profile"] is None
    with app.state.sessions() as db:
        record = db.scalar(
            select(UserRecord).where(
                UserRecord.email_lookup == app.state.security.lookup("first@example.com")
            )
        )
        record.email_verified_at = app.state.clock()
        db.commit()
    calculation = client.post(
        f"{PREFIX}/financial/calculator",
        headers=first,
        json={
            "initial_amount": "100",
            "monthly_contribution": "10",
            "annual_rate": "0.1",
            "term_months": 12,
        },
    )
    assert calculation.status_code == 200
    assert "liquidez" in calculation.json()["investor_guidance"].casefold()
