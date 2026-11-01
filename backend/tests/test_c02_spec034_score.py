"""C-02: SPEC-034 — score educativo: pesos configuráveis, recálculo, fatores e histórico."""

from decimal import Decimal

import pytest

from app.application.auth import AuthService
from app.infrastructure.models import HealthScoreRuleRecord
from tests.clause_support import FIN, account, expense, verified_user


def score(client, headers, competence="2026-10-01"):
    response = client.get(f"{FIN}/health-score?competence={competence}", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def baseline(client, app):
    headers = verified_user(client, app)
    account_id = account(client, headers, "Reserva", "1000")
    client.post(
        f"{FIN}/recurring-incomes",
        headers={**headers, "Idempotency-Key": "score-c02-income"},
        json={"description": "Salário", "amount": "1000", "starts_on": "2026-09-01"},
    )
    return headers, account_id


@pytest.fixture
def rule(app):
    with app.state.sessions() as db:
        record = db.get(HealthScoreRuleRecord, "default")
        original = (
            record.spending_weight,
            record.reserve_weight,
            record.debt_weight,
            record.goals_weight,
            record.version,
        )
    yield
    with app.state.sessions() as db:
        record = db.get(HealthScoreRuleRecord, "default")
        (
            record.spending_weight,
            record.reserve_weight,
            record.debt_weight,
            record.goals_weight,
            record.version,
        ) = original
        db.commit()


def test_SPEC_034_R04_weights_are_data_not_code(client, app, baseline, rule):
    headers, account_id = baseline
    expense(client, headers, "500", "2026-10-10", account_id=account_id)
    before = score(client, headers)
    with app.state.sessions() as db:
        record = db.get(HealthScoreRuleRecord, "default")
        record.spending_weight, record.reserve_weight = Decimal("0"), Decimal("60")
        record.version = "teste-pesos"
        db.commit()
    after = score(client, headers)
    assert after["rule_version"] == "teste-pesos" and after["score"] != before["score"]


def test_SPEC_034_R03_R05_recalculated_when_source_data_changes(client, app, baseline):
    headers, account_id = baseline
    calm = score(client, headers)
    expense(client, headers, "950", "2026-10-10", account_id=account_id)
    stressed = score(client, headers)
    assert Decimal(stressed["score"]) < Decimal(calm["score"])
    assert len(stressed["history"]) == 1  # mesma competência: recalcula, não duplica


def test_SPEC_034_R09_two_weakest_factors_with_generic_suggestion(client, app, baseline):
    headers, account_id = baseline
    expense(client, headers, "950", "2026-10-10", account_id=account_id)
    factors = score(client, headers)["factors"]
    assert len(factors) == 2
    assert Decimal(factors[0]["score"]) <= Decimal(factors[1]["score"])
    assert factors[0]["key"] == "spending" and factors[0]["suggestion"]


def test_SPEC_034_R08_monthly_history_in_order(client, app, baseline):
    headers, _ = baseline
    score(client, headers, "2026-09-01")
    history = score(client, headers, "2026-10-01")["history"]
    assert [row["competence"] for row in history] == ["2026-09-01", "2026-10-01"]


@pytest.mark.parametrize(
    ("value", "band"),
    [("39.99", "critical"), ("40", "attention"), ("60", "healthy"), ("80", "excellent")],
)
def test_SPEC_034_R07_classification_bands(value, band):
    assert AuthService._score_band(Decimal(value)) == band
