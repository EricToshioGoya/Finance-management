"""C-15/ADR-006: a data padrão de início usa America/Sao_Paulo e o relógio injetado."""

from datetime import UTC, datetime

from tests.clause_support import FIN, verified_user

# 01:30 UTC de 15/01 = 22:30 de 14/01 em São Paulo: o dia civil local ainda é 14.
LATE_EVENING_SAO_PAULO = datetime(2026, 1, 15, 1, 30, tzinfo=UTC)


def test_SPEC_056_R01_default_start_date_is_sao_paulo_calendar_day(client):
    headers = verified_user(client, client.app)
    client.app.state.clock = lambda: LATE_EVENING_SAO_PAULO
    response = client.post(
        f"{FIN}/recurring-incomes",
        headers={**headers, "Idempotency-Key": "income-late-evening"},
        json={"description": "Salário", "amount": "100.00"},
    )
    assert response.status_code == 201
    assert response.json()["starts_on"] == "2026-01-14"


def test_SPEC_058_R01_default_bonus_start_date_is_sao_paulo_calendar_day(client):
    headers = verified_user(client, client.app)
    client.app.state.clock = lambda: LATE_EVENING_SAO_PAULO
    response = client.post(
        f"{FIN}/bonuses",
        headers={**headers, "Idempotency-Key": "bonus-late-evening"},
        json={"description": "Bônus", "amount": "50.00", "periodicity": "monthly"},
    )
    assert response.status_code == 201
    assert response.json()["starts_on"] == "2026-01-14"
