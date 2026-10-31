"""SPEC-046 (aposentadoria), SPEC-047 (previdência), SPEC-048 (IR/DARF) e SPEC-049 (resumo anual)."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import update

from app.domain.expansion import (
    aliquota_previdencia_regressiva,
    comparar_previdencia,
    estimar_ir,
    pascoa,
    projetar_aposentadoria,
    vencimento_darf,
)
from app.domain.juros_compostos import ErroCalculo
from app.infrastructure.models import MarketIndicatorRecord, UserRecord

PREFIX = "/api/v1/auth"
FIN = f"{PREFIX}/financial"
PASSWORD = "StrongPassword123"


def verified(client, app, email="tax@example.com"):
    created = client.post(
        f"{PREFIX}/register", json={"name": "Taxa", "email": email, "password": PASSWORD}
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
    return {"Authorization": f"Bearer {token}"}


RETIREMENT = {
    "current_age": 30,
    "target_age": 31,
    "monthly_contribution": "100",
    "annual_rate": "0",
}


# ---------------- SPEC-046 ----------------
def test_SPEC_046_R01_R03_R04_projects_wealth_with_engine(client, app):
    headers = verified(client, app)
    body = {**RETIREMENT, "initial_amount": "1000", "annual_rate": "12"}
    data = client.post(f"{FIN}/retirement-projections", headers=headers, json=body).json()
    engine = projetar_aposentadoria(
        idade_atual=30,
        idade_alvo=31,
        valor_inicial=Decimal("1000"),
        aporte_mensal=Decimal("100"),
        taxa_anual=Decimal("12"),
    )
    assert data["months"] == 12 and data["invested"] == "2200.00"
    assert Decimal(data["projected_wealth"]) == engine.patrimonio_projetado
    # 12% a.a. sobre R$ 1.000 em 12 meses = R$ 1.120 (equivalência composta, RB-10).
    only_initial = projetar_aposentadoria(
        idade_atual=30,
        idade_alvo=31,
        valor_inicial=Decimal("1000"),
        aporte_mensal=Decimal("0"),
        taxa_anual=Decimal("12"),
    )
    assert only_initial.patrimonio_projetado == Decimal("1120.00")


def test_SPEC_046_R02_target_age_must_be_future(client, app):
    headers = verified(client, app)
    response = client.post(
        f"{FIN}/retirement-projections", headers=headers, json={**RETIREMENT, "target_age": 30}
    )
    assert response.status_code == 422 and response.json()["detail"] == "idade_alvo_deve_ser_futura"
    with pytest.raises(ErroCalculo):
        projetar_aposentadoria(
            idade_atual=40,
            idade_alvo=41,
            valor_inicial=Decimal("0"),
            aporte_mensal=Decimal("1"),
            taxa_anual=Decimal("1"),
            taxa_retirada_anual=Decimal("0"),
        )


def test_SPEC_046_R05_income_uses_configurable_withdrawal_rate(client, app):
    headers = verified(client, app)
    body = {**RETIREMENT, "monthly_contribution": "1000", "withdrawal_rate": "6"}
    data = client.post(f"{FIN}/retirement-projections", headers=headers, json=body).json()
    # Taxa zero: R$ 12.000 acumulados; 6% a.a. / 12 = R$ 60,00 por mês.
    assert data["projected_wealth"] == "12000.00" and data["estimated_monthly_income"] == "60.00"
    default = client.post(f"{FIN}/retirement-projections", headers=headers, json=RETIREMENT).json()
    assert default["withdrawal_rate"] == "4"


def test_SPEC_046_R03_suggests_cached_indicator_without_inventing(client, app):
    headers = verified(client, app)
    with app.state.sessions() as db:  # outros testes podem ter deixado o cache preenchido
        existing = db.get(MarketIndicatorRecord, "selic")
        if existing is not None:
            db.delete(existing)
            db.commit()
    first = client.post(f"{FIN}/retirement-projections", headers=headers, json=RETIREMENT).json()
    assert first["suggested_rate"] is None
    with app.state.sessions() as db:
        db.merge(
            MarketIndicatorRecord(
                code="selic",
                value=Decimal("10.5"),
                unit="percent_year",
                reference_date=date(2026, 10, 30),
                checked_at=datetime.now(UTC),
                source="BCB",
            )
        )
        db.commit()
    second = client.post(f"{FIN}/retirement-projections", headers=headers, json=RETIREMENT).json()
    assert second["suggested_rate"]["code"] == "selic"
    assert Decimal(second["suggested_rate"]["value"]) == Decimal("10.5")
    with app.state.sessions() as db:  # a tabela de cache não é truncada entre testes
        db.delete(db.get(MarketIndicatorRecord, "selic"))
        db.commit()


def test_SPEC_046_R06_educational_notice_and_no_persistence(client, app):
    headers = verified(client, app)
    data = client.post(f"{FIN}/retirement-projections", headers=headers, json=RETIREMENT).json()
    assert "educativa" in data["notice"] and "inflação" in data["notice"]
    assert client.get(f"{FIN}/simulations", headers=headers).json() == []


# ---------------- SPEC-047 ----------------
PENSION = {"monthly_contribution": "500", "annual_rate": "8", "term_months": 120}


def test_SPEC_047_R01_R03_same_parameters_for_three_modalities(client, app):
    headers = verified(client, app)
    data = client.post(
        f"{FIN}/pension-comparisons", headers=headers, json={**PENSION, "regime": "regressive"}
    ).json()
    results = {item["modality"]: item for item in data["results"]}
    assert set(results) == {"pgbl", "vgbl", "own_portfolio"}
    assert len({item["gross_amount"] for item in data["results"]}) == 1
    assert len({item["invested"] for item in data["results"]}) == 1
    # PGBL tributa o total; VGBL só o rendimento: o líquido do VGBL é maior.
    assert Decimal(results["vgbl"]["net_amount"]) > Decimal(results["pgbl"]["net_amount"])


def test_SPEC_047_R04_simplified_configurable_tables():
    assert aliquota_previdencia_regressiva(24) == Decimal("35")
    assert aliquota_previdencia_regressiva(25) == Decimal("30")
    assert aliquota_previdencia_regressiva(121) == Decimal("10")
    progressive = comparar_previdencia(
        valor_inicial=Decimal("1000"),
        aporte_mensal=Decimal("0"),
        taxa_anual=Decimal("0"),
        prazo_meses=12,
        regime="progressive",
        aliquota_progressiva=Decimal("15"),
    )
    pgbl = next(item for item in progressive if item.modalidade == "pgbl")
    assert pgbl.imposto == Decimal("150.00")  # 15% sobre o total resgatado


def test_SPEC_047_R02_regime_not_configured_is_not_replaced(client, app):
    headers = verified(client, app)
    response = client.post(
        f"{FIN}/pension-comparisons", headers=headers, json={**PENSION, "regime": "progressive"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "aliquota_progressiva_obrigatoria"


def test_SPEC_047_R05_explains_pgbl_context_without_recommendation(client, app):
    headers = verified(client, app)
    data = client.post(
        f"{FIN}/pension-comparisons", headers=headers, json={**PENSION, "regime": "regressive"}
    ).json()
    assert "declaração completa" in data["pgbl_context"]
    assert "não é recomendação" in data["notice"] and data["rule_version"] == "2026-10"


# ---------------- SPEC-048 ----------------
def test_SPEC_048_R03_regimes_and_stock_exemption():
    month = date(2026, 3, 1)
    exempt = estimar_ir(
        regime="stock", competencia=month, resultado=Decimal("1000"), vendas_no_mes=Decimal("15000")
    )
    assert exempt.isento and exempt.imposto == Decimal("0.00") and exempt.vencimento_darf is None
    taxed = estimar_ir(
        regime="stock", competencia=month, resultado=Decimal("1000"), vendas_no_mes=Decimal("25000")
    )
    assert taxed.imposto == Decimal("150.00")
    assert estimar_ir(regime="fii", competencia=month, resultado=Decimal("100")).imposto == Decimal(
        "20.00"
    )
    day_trade = estimar_ir(
        regime="day_trade", competencia=month, resultado=Decimal("100"), vendas_no_mes=Decimal("1")
    )
    assert day_trade.imposto == Decimal("20.00") and not day_trade.isento
    fixed = estimar_ir(
        regime="fixed_income", competencia=month, resultado=Decimal("100"), dias_aplicacao=200
    )
    assert fixed.aliquota == Decimal("20") and fixed.vencimento_darf is None


def test_SPEC_048_R04_R05_darf_due_last_business_day_of_next_month():
    assert pascoa(2027) == date(2027, 3, 28)
    # Operação em fev/2026 → vence em 31/03/2026 (terça-feira).
    assert vencimento_darf(date(2026, 2, 1)) == date(2026, 3, 31)
    # Operação em out/2026 → 30/11/2026 (segunda-feira).
    assert vencimento_darf(date(2026, 10, 1)) == date(2026, 11, 30)
    # Operação em jul/2026 → 31/08/2026 (segunda); em mai/2027 → 30/06/2027.
    assert vencimento_darf(date(2026, 7, 1)) == date(2026, 8, 31)
    # Operação em fev/2027 → 31/03/2027 (quarta).
    assert vencimento_darf(date(2027, 2, 1)) == date(2027, 3, 31)
    # Operação em nov/2026 → 31/12/2026 (quinta).
    assert vencimento_darf(date(2026, 11, 1)) == date(2026, 12, 31)
    # Operação em dez/2026 → janeiro/2027: 31/01 é domingo, então 29/01 (sexta).
    assert vencimento_darf(date(2026, 12, 1)) == date(2027, 1, 29)


def test_SPEC_048_R01_R06_api_persists_estimate_with_notice(client, app):
    headers = verified(client, app)
    response = client.post(
        f"{FIN}/tax-estimates",
        headers=headers,
        json={"regime": "fii", "competence": "2026-10", "result": "500.00"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tax"] == "100.00" and data["darf_due_on"] == "2026-11-30"
    assert "e-CAC" in data["notice"] and "não gera nem envia DARF" in data["notice"]
    assert len(client.get(f"{FIN}/tax-estimates", headers=headers).json()) == 1
    other = verified(client, app, "other@example.com")
    assert client.get(f"{FIN}/tax-estimates", headers=other).json() == []
    assert client.delete(f"{FIN}/tax-estimates/{data['id']}", headers=other).status_code == 404


def test_SPEC_048_R02_losses_and_unknown_rules_are_not_invented(client, app):
    headers = verified(client, app)
    loss = client.post(
        f"{FIN}/tax-estimates",
        headers=headers,
        json={"regime": "stock", "competence": "2026-10", "result": "-50", "sales": "30000"},
    ).json()
    assert loss["tax"] == "0.00" and "compensação" in loss["notes"][0]
    missing = client.post(
        f"{FIN}/tax-estimates",
        headers=headers,
        json={"regime": "fixed_income", "competence": "2026-10", "result": "10"},
    )
    assert missing.status_code == 422


# ---------------- SPEC-049 ----------------
def test_SPEC_049_R01_R03_consolidates_registered_and_simulated(client, app):
    headers = verified(client, app)
    account = client.post(
        f"{FIN}/accounts",
        headers=headers,
        json={"name": "Conta", "account_type": "checking", "initial_balance": "0"},
    ).json()["id"]
    client.post(
        f"{FIN}/one-time-incomes",
        headers={**headers, "Idempotency-Key": "freela"},
        json={
            "description": "Freela",
            "amount": "1500.00",
            "occurred_on": "2026-05-10",
            "account_id": account,
        },
    )
    client.post(
        f"{FIN}/tax-estimates",
        headers=headers,
        json={"regime": "fii", "competence": "2026-06", "result": "100"},
    )
    client.post(
        f"{FIN}/simulations/fixed-income",
        headers=headers,
        json={
            "label": "CDB",
            "product": "cdb",
            "initial_amount": "1000",
            "monthly_contribution": "0",
            "annual_rate": "12",
            "term_months": 12,
        },
    )
    year = datetime.now(UTC).year
    data = client.get(f"{FIN}/annual-summary", headers=headers, params={"year": 2026}).json()
    assert data["registered_income"]["one_time_income"] == "1500.00"
    assert data["estimated_tax_total"] == "20.00"
    if year == 2026:
        assert data["simulations"][0]["origin"] == "simulated"
    csv = client.get(f"{FIN}/annual-summary/csv", headers=headers, params={"year": 2026})
    assert csv.status_code == 200 and "registrado" in csv.text
    pdf = client.get(f"{FIN}/annual-summary/pdf", headers=headers, params={"year": 2026})
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")


def test_SPEC_049_R04_document_is_not_official(client, app):
    headers = verified(client, app)
    client.post(
        f"{FIN}/tax-estimates",
        headers=headers,
        json={"regime": "fii", "competence": "2026-06", "result": "100"},
    )
    data = client.get(f"{FIN}/annual-summary", headers=headers, params={"year": 2026}).json()
    assert "Não é informe de rendimentos oficial" in data["notice"]
    csv = client.get(f"{FIN}/annual-summary/csv", headers=headers, params={"year": 2026}).text
    assert csv.startswith("# Resumo auxiliar gerado pelo FinNova")


def test_SPEC_049_R02_year_without_data_and_other_owner(client, app):
    headers = verified(client, app)
    empty = client.get(f"{FIN}/annual-summary", headers=headers, params={"year": 2015})
    assert empty.status_code == 404 and empty.json()["detail"] == "no_data_for_year"
    assert client.get(f"{FIN}/annual-summary", params={"year": 2026}).status_code == 401
