"""Apoio aos testes por cláusula (C-02): usuário verificado, fontes e lançamentos sintéticos."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import update

from app.infrastructure.models import MarketIndicatorRecord, UserRecord

AUTH = "/api/v1/auth"
FIN = f"{AUTH}/financial"
PASSWORD = "StrongPassword123"


def verified_user(client, app, email="clausula@example.com"):
    created = client.post(
        f"{AUTH}/register", json={"name": "Cláusula", "email": email, "password": PASSWORD}
    ).json()
    with app.state.engine.begin() as db:
        db.execute(
            update(UserRecord)
            .where(UserRecord.id == uuid.UUID(created["id"]))
            .values(email_verified_at=datetime.now(UTC))
        )
    token = client.post(f"{AUTH}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def unverified_user(client, email="pendente@example.com"):
    client.post(f"{AUTH}/register", json={"name": "Pendente", "email": email, "password": PASSWORD})
    token = client.post(f"{AUTH}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}


def account(client, headers, name="Conta", balance="0"):
    return client.post(
        f"{FIN}/accounts",
        headers=headers,
        json={"name": name, "account_type": "checking", "initial_balance": balance},
    ).json()["id"]


def card(client, headers, limit="1000"):
    return client.post(
        f"{FIN}/credit-cards",
        headers=headers,
        json={"name": "Cartão", "credit_limit": limit, "closing_day": 10, "due_day": 20},
    ).json()["id"]


def expense(client, headers, amount, when="2026-03-10", category="standard:alimentacao", **source):
    response = client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={
            "description": "Despesa",
            "amount": amount,
            "category_key": category,
            "occurred_on": when,
            **source,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def one_time_income(client, headers, amount, when="2026-03-05", account_id=None):
    response = client.post(
        f"{FIN}/one-time-incomes",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={
            "description": "Receita",
            "amount": amount,
            "occurred_on": when,
            "account_id": account_id,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def set_indicator(app, code="selic", value="12", reference=date(2026, 10, 30), checked=None):
    with app.state.sessions() as db:
        db.merge(
            MarketIndicatorRecord(
                code=code,
                value=Decimal(value),
                unit="percentual_anual",
                reference_date=reference,
                checked_at=checked or datetime.now(UTC),
                source="BCB_SGS",
            )
        )
        db.commit()


def clear_indicators(app):
    with app.state.sessions() as db:
        for code in ("selic", "cdi", "ipca"):
            record = db.get(MarketIndicatorRecord, code)
            if record is not None:
                db.delete(record)
        db.commit()
