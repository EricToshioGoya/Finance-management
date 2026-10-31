"""SPEC-050 (score por grupo anônimo), SPEC-051 (conquistas) e SPEC-052 (tour opcional)."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select, update

from app.infrastructure.models import (
    AchievementRecord,
    HealthScoreRecord,
    NotificationRecord,
    UserRecord,
)

PREFIX = "/api/v1/auth"
FIN = f"{PREFIX}/financial"
PASSWORD = "StrongPassword123"
MONTH = date(2026, 9, 1)


def verified(client, app, email="me@example.com", profile="moderado"):
    created = client.post(
        f"{PREFIX}/register", json={"name": "Eu", "email": email, "password": PASSWORD}
    ).json()
    with app.state.engine.begin() as db:
        db.execute(
            update(UserRecord)
            .where(UserRecord.id == uuid.UUID(created["id"]))
            .values(email_verified_at=datetime.now(UTC), investor_profile=profile)
        )
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}, uuid.UUID(created["id"])


def peers(app, count, profile="moderado", score="50", start=0):
    """Insere usuários sintéticos com score na competência (sem dados individuais expostos)."""
    security = app.state.security
    with app.state.sessions() as db:
        for index in range(start, start + count):
            email = f"peer{index}@example.com"
            user = UserRecord(
                name_encrypted=security.encrypt(f"Peer {index}"),
                email_encrypted=security.encrypt(email),
                email_lookup=security.lookup(email),
                password_hash="x",
                email_verified_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                investor_profile=profile,
            )
            db.add(user)
            db.flush()
            db.add(
                HealthScoreRecord(
                    user_id=user.id,
                    competence=MONTH,
                    score=Decimal(score),
                    classification="Atenção",
                    factors={},
                    rule_version="test",
                )
            )
        db.commit()


def my_score(app, user_id, score="80"):
    with app.state.sessions() as db:
        db.add(
            HealthScoreRecord(
                user_id=user_id,
                competence=MONTH,
                score=Decimal(score),
                classification="Saudável",
                factors={},
                rule_version="test",
            )
        )
        db.commit()


BENCH = f"{FIN}/health-score/benchmark"


# ---------------- SPEC-050 ----------------
def test_SPEC_050_R01_R03_aggregated_comparison_for_same_profile(client, app):
    headers, me = verified(client, app)
    my_score(app, me)
    peers(app, 29, score="50")
    peers(app, 5, profile="arrojado", score="10", start=100)  # outro perfil não entra
    data = client.get(BENCH, headers=headers).json()
    assert data["available"] is True and data["competence"] == "2026-09"
    # 29 pares com 50 + eu com 80 → média 51,00; mediana 50,00.
    assert data["group_average_score"] == "51.00" and data["group_median_score"] == "50.00"
    assert data["my_score"] == "80.00"


def test_SPEC_050_R02_R04_group_below_minimum_shows_nothing(client, app):
    headers, me = verified(client, app)
    my_score(app, me)
    peers(app, 28)
    data = client.get(BENCH, headers=headers).json()
    assert data["available"] is False and data["reason"] == "insufficient_group"
    assert data["group_average_score"] is None and "29" not in str(data)
    # Sem perfil: nenhuma classificação inventada.
    no_profile, _ = verified(client, app, "noprofile@example.com", profile=None)
    assert client.get(BENCH, headers=no_profile).json()["reason"] == "no_profile"


def test_SPEC_050_R05_opt_out_keeps_score_and_leaves_group(client, app):
    headers, me = verified(client, app)
    my_score(app, me)
    peers(app, 29)
    assert client.get(BENCH, headers=headers).json()["available"] is True
    other, other_id = verified(client, app, "other@example.com")
    my_score(app, other_id)
    off = client.put(
        f"{PREFIX}/profile/privacy", headers=headers, json={"score_benchmark_enabled": False}
    )
    assert off.json() == {"score_benchmark_enabled": False}
    hidden = client.get(BENCH, headers=headers).json()
    assert hidden["enabled"] is False and hidden["reason"] == "opted_out"
    # Quem desativou também sai do grupo: o outro usuário fica com 29 pares + ele mesmo = 30.
    assert client.get(BENCH, headers=other).json()["available"] is True
    with app.state.sessions() as db:
        assert db.scalar(select(HealthScoreRecord).where(HealthScoreRecord.user_id == me))
    assert client.get(f"{PREFIX}/profile/privacy", headers=headers).json() == {
        "score_benchmark_enabled": False
    }


# ---------------- SPEC-051 ----------------
def account_and_goal(client, headers, target="1000", value="1500"):
    asset = client.post(
        f"{FIN}/net-worth/items",
        headers=headers,
        json={"kind": "asset", "name": "Reserva", "value": value},
    ).json()
    goal = client.post(
        f"{FIN}/named-asset-goals",
        headers=headers,
        json={
            "name": "Reserva",
            "category": "emergency",
            "asset_id": asset["id"],
            "target_amount": target,
            "deadline": "2030-01-01",
        },
    )
    assert goal.status_code == 201


def test_SPEC_051_R01_R03_R05_grants_once_and_notifies(client, app):
    headers, me = verified(client, app)
    account_and_goal(client, headers)
    first = {
        item["code"]: item for item in client.get(f"{FIN}/achievements", headers=headers).json()
    }
    assert first["named_goal_reached"]["unlocked"] is True
    client.get(f"{FIN}/achievements", headers=headers)
    with app.state.sessions() as db:
        assert len(db.scalars(select(AchievementRecord)).all()) == 1
        notes = db.scalars(
            select(NotificationRecord).where(NotificationRecord.kind == "achievement_unlocked")
        ).all()
        assert len(notes) == 1 and notes[0].user_id == me


def test_SPEC_051_R04_shows_progress_of_next_achievements(client, app):
    headers, _ = verified(client, app)
    account_and_goal(client, headers, target="1000", value="250")
    items = {
        item["code"]: item for item in client.get(f"{FIN}/achievements", headers=headers).json()
    }
    assert set(items) == {"named_goal_reached", "budget_month_on_track", "three_months_on_budget"}
    assert items["named_goal_reached"]["unlocked"] is False
    assert items["named_goal_reached"]["progress_percent"] == "25.00"
    # Sem meta de orçamento, o marco de uso não é concedido.
    assert items["budget_month_on_track"]["progress_percent"] == "0"


def test_SPEC_051_R03_three_months_within_budget(client, app):
    headers, _ = verified(client, app)
    client.put(
        f"{FIN}/budget-goals", headers=headers, json={"kind": "expense_total", "target": "1000"}
    )
    items = {
        item["code"]: item for item in client.get(f"{FIN}/achievements", headers=headers).json()
    }
    assert items["budget_month_on_track"]["unlocked"] is True
    assert items["three_months_on_budget"]["unlocked"] is True


def test_SPEC_051_R02_R06_cosmetic_only_and_respects_preferences(client, app):
    headers, me = verified(client, app)
    client.put(
        "/api/v1/notifications/preferences/achievement_unlocked",
        headers=headers,
        json={"enabled": False},
    )
    before = client.get(f"{PREFIX}/me", headers=headers).json()
    account_and_goal(client, headers)
    client.get(f"{FIN}/achievements", headers=headers)
    after = client.get(f"{PREFIX}/me", headers=headers).json()
    assert before["role"] == after["role"] == "usuario"
    with app.state.sessions() as db:
        assert db.scalar(select(NotificationRecord)) is None  # tipo desativado pelo titular
        assert db.scalar(select(HealthScoreRecord).where(HealthScoreRecord.user_id == me)) is None
    # Evento manual não pode forjar conquista.
    forged = client.post(
        "/api/v1/notifications/events",
        headers=headers,
        json={"kind": "achievement_unlocked", "source_key": "x"},
    )
    assert forged.status_code == 422


# ---------------- SPEC-052 ----------------
def test_SPEC_052_R01_R03_first_access_tour_covers_core_steps(client, app):
    headers, _ = verified(client, app, profile=None)
    tour = client.get(f"{PREFIX}/profile/tour", headers=headers).json()
    assert tour["show"] is True and tour["status"] == "not_started"
    assert [step["key"] for step in tour["steps"]] == [
        "first_income",
        "first_expense",
        "investor_quiz",
        "simulator",
    ]
    assert not any(step["done"] for step in tour["steps"])


def test_SPEC_052_R04_skip_at_any_point_without_creating_data(client, app):
    headers, _ = verified(client, app)
    client.put(f"{PREFIX}/profile/tour", headers=headers, json={"action": "start"})
    client.put(f"{PREFIX}/profile/tour", headers=headers, json={"action": "advance"})
    skipped = client.put(f"{PREFIX}/profile/tour", headers=headers, json={"action": "skip"}).json()
    assert skipped["status"] == "skipped" and skipped["show"] is False
    assert client.get(f"{FIN}/expenses", headers=headers).json() == []
    assert client.get(f"{FIN}/one-time-incomes", headers=headers).json() == []


def test_SPEC_052_R05_reopen_from_help(client, app):
    headers, _ = verified(client, app)
    client.put(f"{PREFIX}/profile/tour", headers=headers, json={"action": "complete"})
    reopened = client.put(f"{PREFIX}/profile/tour", headers=headers, json={"action": "reopen"})
    assert reopened.json()["status"] == "in_progress" and reopened.json()["step"] == 0


def test_SPEC_052_R02_R06_adapts_to_profile_without_inventing(client, app):
    beginner, _ = verified(client, app, "b@example.com", profile=None)
    advanced, _ = verified(client, app, "a@example.com", profile="arrojado")
    conservative, _ = verified(client, app, "c@example.com", profile="conservador")
    assert client.get(f"{PREFIX}/profile/tour", headers=beginner).json()["variant"] == "didactic"
    assert client.get(f"{PREFIX}/profile/tour", headers=beginner).json()["profile"] is None
    assert (
        client.get(f"{PREFIX}/profile/tour", headers=conservative).json()["variant"] == "didactic"
    )
    advanced_tour = client.get(f"{PREFIX}/profile/tour", headers=advanced).json()
    assert advanced_tour["variant"] == "concise"
    assert next(s for s in advanced_tour["steps"] if s["key"] == "investor_quiz")["done"] is True
    assert client.get(f"{PREFIX}/profile/tour").status_code == 401
