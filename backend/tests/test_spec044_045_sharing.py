"""SPEC-044 (vínculo entre dois usuários) e SPEC-045 (divisão de despesas e acertos)."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.infrastructure.models import SharedLinkRecord, UserRecord

PREFIX = "/api/v1/auth"
SHARING = f"{PREFIX}/sharing"
PASSWORD = "StrongPassword123"


def member(client, app, email, name):
    """Cria titular com e-mail verificado e uma conta própria para lançar despesas."""
    created = client.post(
        f"{PREFIX}/register", json={"name": name, "email": email, "password": PASSWORD}
    ).json()
    with app.state.engine.begin() as db:
        db.execute(
            update(UserRecord)
            .where(UserRecord.id == uuid.UUID(created["id"]))
            .values(email_verified_at=datetime.now(UTC))
        )
    token = client.post(f"{PREFIX}/login", json={"email": email, "password": PASSWORD}).json()[
        "access_token"
    ]
    headers = {"Authorization": f"Bearer {token}"}
    account = client.post(
        f"{PREFIX}/financial/accounts",
        headers=headers,
        json={"name": "Conta", "account_type": "checking", "initial_balance": "0"},
    ).json()
    return headers, account["id"]


def expense(client, headers, account, amount, description="Mercado"):
    response = client.post(
        f"{PREFIX}/financial/expenses",
        headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
        json={
            "description": description,
            "amount": amount,
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-10-10",
            "account_id": account,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def linked_pair(client, app):
    ana, ana_account = member(client, app, "ana@example.com", "Ana")
    beto, beto_account = member(client, app, "beto@example.com", "Beto")
    assert client.post(
        f"{SHARING}/invitations", headers=ana, json={"email": "beto@example.com"}
    ).json() == {"status": "sent"}
    invitation = client.get(SHARING, headers=beto).json()["received"][0]
    assert invitation["from_name"] == "Ana"
    accepted = client.post(f"{SHARING}/invitations/{invitation['id']}/accept", headers=beto)
    assert accepted.status_code == 200
    return ana, ana_account, beto, beto_account, accepted.json()["active"]["id"]


# ---------------- SPEC-044 ----------------
def test_SPEC_044_R01_R03_R04_link_is_created_only_after_acceptance(client, app):
    ana, _ = member(client, app, "ana@example.com", "Ana")
    beto, _ = member(client, app, "beto@example.com", "Beto")
    client.post(f"{SHARING}/invitations", headers=ana, json={"email": "BETO@example.com"})
    # Antes do aceite não há vínculo nem acesso compartilhado.
    assert client.get(SHARING, headers=ana).json()["active"] is None
    assert client.get(f"{SHARING}/balance", headers=ana).status_code == 409
    sent = client.get(SHARING, headers=ana).json()["sent"]
    assert len(sent) == 1 and "name" not in str(sent)
    received = client.get(SHARING, headers=beto).json()["received"]
    overview = client.post(f"{SHARING}/invitations/{received[0]['id']}/accept", headers=beto).json()
    assert overview["active"]["partner_name"] == "Ana"
    assert client.get(SHARING, headers=ana).json()["active"]["partner_name"] == "Beto"


def test_SPEC_044_R02_self_unknown_and_third_party_never_create_link(client, app):
    ana, _ = member(client, app, "ana@example.com", "Ana")
    beto, _ = member(client, app, "beto@example.com", "Beto")
    carla, _ = member(client, app, "carla@example.com", "Carla")
    assert (
        client.post(
            f"{SHARING}/invitations", headers=ana, json={"email": "ana@example.com"}
        ).status_code
        == 422
    )
    # Convite para inexistente: resposta idêntica, sem registro criado (sem enumeração).
    unknown = client.post(f"{SHARING}/invitations", headers=ana, json={"email": "nobody@x.com"})
    assert unknown.status_code == 202 and unknown.json() == {"status": "sent"}
    with app.state.engine.connect() as db:
        assert db.scalar(select(SharedLinkRecord.id)) is None
    client.post(f"{SHARING}/invitations", headers=ana, json={"email": "beto@example.com"})
    invitation = client.get(SHARING, headers=beto).json()["received"][0]["id"]
    # Terceiro (e o próprio convidante) não aceitam o convite de outra pessoa.
    assert (
        client.post(f"{SHARING}/invitations/{invitation}/accept", headers=carla).status_code == 404
    )
    assert client.post(f"{SHARING}/invitations/{invitation}/accept", headers=ana).status_code == 404
    assert client.get(SHARING, headers=beto).json()["active"] is None


def test_SPEC_044_R02_invitation_expires_and_single_active_link(client, app):
    ana, _ = member(client, app, "ana@example.com", "Ana")
    beto, _ = member(client, app, "beto@example.com", "Beto")
    carla, _ = member(client, app, "carla@example.com", "Carla")
    client.post(f"{SHARING}/invitations", headers=ana, json={"email": "beto@example.com"})
    invitation = client.get(SHARING, headers=beto).json()["received"][0]["id"]
    with app.state.engine.begin() as db:
        db.execute(
            update(SharedLinkRecord).values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
    response = client.post(f"{SHARING}/invitations/{invitation}/accept", headers=beto)
    assert response.status_code == 409 and response.json()["detail"] == "invitation_expired"
    # Novo convite aceito; com vínculo ativo, nenhum dos dois pode iniciar outro.
    client.post(f"{SHARING}/invitations", headers=ana, json={"email": "beto@example.com"})
    fresh = client.get(SHARING, headers=beto).json()["received"][0]["id"]
    assert client.post(f"{SHARING}/invitations/{fresh}/accept", headers=beto).status_code == 200
    assert (
        client.post(
            f"{SHARING}/invitations", headers=carla, json={"email": "ana@example.com"}
        ).status_code
        == 202
    )
    assert client.get(SHARING, headers=ana).json()["received"] == []
    blocked = client.post(f"{SHARING}/invitations", headers=ana, json={"email": "carla@x.com"})
    assert blocked.status_code == 409


def test_SPEC_044_R02_decline_and_cancel(client, app):
    ana, _ = member(client, app, "ana@example.com", "Ana")
    beto, _ = member(client, app, "beto@example.com", "Beto")
    client.post(f"{SHARING}/invitations", headers=ana, json={"email": "beto@example.com"})
    first = client.get(SHARING, headers=beto).json()["received"][0]["id"]
    assert client.post(f"{SHARING}/invitations/{first}/decline", headers=beto).status_code == 204
    client.post(f"{SHARING}/invitations", headers=ana, json={"email": "beto@example.com"})
    second = client.get(SHARING, headers=ana).json()["sent"][0]["id"]
    assert client.post(f"{SHARING}/invitations/{second}/cancel", headers=beto).status_code == 404
    assert client.post(f"{SHARING}/invitations/{second}/cancel", headers=ana).status_code == 204
    assert client.get(SHARING, headers=beto).json()["received"] == []


def test_SPEC_044_R05_either_member_ends_link_preserving_history(client, app):
    ana, ana_account, beto, _, link = linked_pair(client, app)
    shared = expense(client, ana, ana_account, "100.00")
    client.post(f"{SHARING}/expenses", headers=ana, json={"expense_id": shared})
    assert client.post(f"{SHARING}/links/{link}/end", headers=beto).status_code == 204
    assert client.get(SHARING, headers=ana).json()["active"] is None
    history = client.get(f"{SHARING}/balance", headers=beto, params={"link_id": link}).json()
    assert history["status"] == "ended" and len(history["items"]) == 1
    assert history["direction"] == "i_owe_partner" and history["amount"] == "50.00"
    # Histórico somente leitura: novo compartilhamento exige vínculo ativo.
    other = expense(client, ana, ana_account, "10.00")
    assert (
        client.post(f"{SHARING}/expenses", headers=ana, json={"expense_id": other}).status_code
        == 409
    )


def test_SPEC_044_R06_individual_data_stays_private(client, app):
    ana, ana_account, beto, _, link = linked_pair(client, app)
    expense(client, ana, ana_account, "999.00", "Privada")
    balance = client.get(f"{SHARING}/balance", headers=beto).json()
    assert balance["items"] == [] and "Privada" not in str(balance)
    # O parceiro continua sem acesso direto às despesas individuais da Ana.
    assert "Privada" not in str(client.get(f"{PREFIX}/financial/expenses", headers=beto).json())
    outsider, _ = member(client, app, "zeca@example.com", "Zeca")
    response = client.get(f"{SHARING}/balance", headers=outsider, params={"link_id": link})
    assert response.status_code == 404


# ---------------- SPEC-045 ----------------
def test_SPEC_045_R01_R03_equal_and_custom_split(client, app):
    ana, ana_account, beto, _, _ = linked_pair(client, app)
    first = expense(client, ana, ana_account, "100.01", "Luz")
    data = client.post(f"{SHARING}/expenses", headers=ana, json={"expense_id": first}).json()
    item = data["items"][0]
    # 50/50 de R$ 100,01: o centavo restante fica com quem pagou.
    assert item["my_share"] == "50.01" and item["partner_share"] == "50.00"
    second = expense(client, ana, ana_account, "200.00", "Internet")
    custom = client.post(
        f"{SHARING}/expenses",
        headers=ana,
        json={
            "expense_id": second,
            "split": "custom",
            "payer_percent": "70",
            "partner_percent": "30",
        },
    ).json()
    assert custom["direction"] == "partner_owes_me" and custom["amount"] == "110.00"


def test_SPEC_045_R02_invalid_split_or_non_member_does_not_change_balance(client, app):
    ana, ana_account, beto, beto_account, _ = linked_pair(client, app)
    shared = expense(client, ana, ana_account, "100.00")
    wrong = client.post(
        f"{SHARING}/expenses",
        headers=ana,
        json={
            "expense_id": shared,
            "split": "custom",
            "payer_percent": "60",
            "partner_percent": "30",
        },
    )
    assert wrong.status_code == 422 and wrong.json()["detail"] == "split_must_total_100"
    # Beto não pode compartilhar a despesa da Ana.
    stolen = client.post(f"{SHARING}/expenses", headers=beto, json={"expense_id": shared})
    assert stolen.status_code == 404
    assert client.get(f"{SHARING}/balance", headers=ana).json()["items"] == []


def test_SPEC_045_R04_balance_updates_on_edit_and_delete(client, app):
    ana, ana_account, beto, _, _ = linked_pair(client, app)
    shared = expense(client, ana, ana_account, "80.00")
    share = client.post(f"{SHARING}/expenses", headers=ana, json={"expense_id": shared}).json()
    assert client.get(f"{SHARING}/balance", headers=beto).json()["amount"] == "40.00"
    client.patch(f"{PREFIX}/financial/expenses/{shared}", headers=ana, json={"amount": "120.00"})
    assert client.get(f"{SHARING}/balance", headers=beto).json()["amount"] == "60.00"
    share_id = share["items"][0]["id"]
    updated = client.patch(
        f"{SHARING}/expenses/{share_id}",
        headers=ana,
        json={"split": "custom", "payer_percent": "25", "partner_percent": "75"},
    ).json()
    assert updated["amount"] == "90.00"
    client.delete(f"{PREFIX}/financial/expenses/{shared}", headers=ana)
    assert client.get(f"{SHARING}/balance", headers=beto).json()["direction"] == "settled"


def test_SPEC_045_R05_settlement_reduces_balance_idempotently(client, app):
    ana, ana_account, beto, _, _ = linked_pair(client, app)
    shared = expense(client, ana, ana_account, "100.00")
    client.post(f"{SHARING}/expenses", headers=ana, json={"expense_id": shared})
    key = {"Idempotency-Key": "acerto-1"}
    first = client.post(f"{SHARING}/settlements", headers={**beto, **key}, json={"amount": "20"})
    again = client.post(f"{SHARING}/settlements", headers={**beto, **key}, json={"amount": "20"})
    assert first.status_code == again.status_code == 201
    assert again.json()["amount"] == "30.00" and len(again.json()["settlements"]) == 1
    too_much = client.post(
        f"{SHARING}/settlements",
        headers={**beto, "Idempotency-Key": "acerto-2"},
        json={"amount": "31"},
    )
    assert too_much.status_code == 422
    creditor = client.post(
        f"{SHARING}/settlements",
        headers={**ana, "Idempotency-Key": "acerto-3"},
        json={"amount": "1"},
    )
    assert creditor.status_code == 409 and creditor.json()["detail"] == "nothing_to_settle"
    final = client.post(
        f"{SHARING}/settlements",
        headers={**beto, "Idempotency-Key": "acerto-4"},
        json={"amount": "30"},
    ).json()
    assert final["direction"] == "settled" and final["amount"] == "0.00"


def test_SPEC_045_R06_both_members_see_composition(client, app):
    ana, ana_account, beto, beto_account, _ = linked_pair(client, app)
    client.post(
        f"{SHARING}/expenses",
        headers=ana,
        json={"expense_id": expense(client, ana, ana_account, "60.00", "Gás")},
    )
    client.post(
        f"{SHARING}/expenses",
        headers=beto,
        json={"expense_id": expense(client, beto, beto_account, "20.00", "Pão")},
    )
    ana_view = client.get(f"{SHARING}/balance", headers=ana).json()
    beto_view = client.get(f"{SHARING}/balance", headers=beto).json()
    assert {item["description"] for item in ana_view["items"]} == {"Gás", "Pão"}
    assert {item["description"] for item in beto_view["items"]} == {"Gás", "Pão"}
    assert ana_view["direction"] == "partner_owes_me" and ana_view["amount"] == "20.00"
    assert beto_view["direction"] == "i_owe_partner" and beto_view["amount"] == "20.00"
    assert beto_view["partner_name"] == "Ana"


def test_SPEC_044_045_require_verified_email(client):
    client.post(
        f"{PREFIX}/register",
        json={"name": "Sem", "email": "sem@example.com", "password": PASSWORD},
    )
    token = client.post(
        f"{PREFIX}/login", json={"email": "sem@example.com", "password": PASSWORD}
    ).json()["access_token"]
    response = client.get(SHARING, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert client.get(SHARING).status_code == 401
