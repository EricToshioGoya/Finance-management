"""SPEC-046/047/048: aposentadoria, previdência e IR no domínio puro, sem banco.

Valores de referência calculados à mão: 10% a.a. por 12 meses gera 1.100,00 por
equivalência composta (C-04); alíquotas conforme as tabelas versionadas "2026-10".
"""

from datetime import date
from decimal import Decimal

import pytest

from app.domain.expansion import (
    aliquota_previdencia_regressiva,
    aliquota_renda_fixa_por_meses,
    comparar_previdencia,
    estimar_ir,
    pascoa,
    projetar_aposentadoria,
    vencimento_darf,
)
from app.domain.juros_compostos import ErroCalculo


# ------------------------------------------------------------------ SPEC-046
def test_SPEC_046_R04_R05_patrimonio_e_renda_pela_regra_de_retirada():
    """Cláusulas: SPEC-046-R04, SPEC-046-R05 — 1.100,00 × 4% ÷ 12 = 3,67/mês."""
    result = projetar_aposentadoria(
        idade_atual=30,
        idade_alvo=31,
        valor_inicial=Decimal("1000"),
        aporte_mensal=Decimal("0"),
        taxa_anual=Decimal("10"),
    )
    assert result.meses == 12
    assert result.total_investido == Decimal("1000.00")
    assert result.patrimonio_projetado == Decimal("1100.00")
    assert result.renda_mensal_estimada == Decimal("3.67")
    assert result.taxa_retirada_anual == Decimal("4")


@pytest.mark.parametrize(
    ("idade_alvo", "retirada"), [(30, Decimal("4")), (29, Decimal("4")), (40, Decimal("0"))]
)
def test_SPEC_046_R02_idade_passada_ou_retirada_invalida_e_recusada(idade_alvo, retirada):
    """Cláusulas: SPEC-046-R02."""
    with pytest.raises(ErroCalculo):
        projetar_aposentadoria(
            idade_atual=30,
            idade_alvo=idade_alvo,
            valor_inicial=Decimal("1000"),
            aporte_mensal=Decimal("0"),
            taxa_anual=Decimal("10"),
            taxa_retirada_anual=retirada,
        )


# ------------------------------------------------------------------ SPEC-047
@pytest.mark.parametrize(
    ("meses", "aliquota"),
    [(24, "35"), (25, "30"), (48, "30"), (49, "25"), (120, "15"), (121, "10")],
)
def test_SPEC_047_R04_tabela_regressiva_de_previdencia_nas_fronteiras(meses, aliquota):
    """Cláusulas: SPEC-047-R04."""
    assert aliquota_previdencia_regressiva(meses) == Decimal(aliquota)


@pytest.mark.parametrize(
    ("meses", "aliquota"),
    [(6, "22.5"), (7, "20"), (12, "20"), (13, "17.5"), (24, "17.5"), (25, "15")],
)
def test_SPEC_047_R04_tabela_regressiva_de_renda_fixa_nas_fronteiras(meses, aliquota):
    """Cláusulas: SPEC-047-R04."""
    assert aliquota_renda_fixa_por_meses(meses) == Decimal(aliquota)


def test_SPEC_047_R03_R04_compara_tres_modalidades_com_os_mesmos_parametros():
    """Cláusulas: SPEC-047-R03, SPEC-047-R04.

    1.000 a 10% a.a. por 12 meses → bruto 1.100,00 em todas.
    PGBL (35% sobre o total) = 385,00; VGBL (35% sobre 100) = 35,00;
    carteira (20% sobre 100) = 20,00.
    """
    result = {
        item.modalidade: item
        for item in comparar_previdencia(
            valor_inicial=Decimal("1000"),
            aporte_mensal=Decimal("0"),
            taxa_anual=Decimal("10"),
            prazo_meses=12,
            regime="regressive",
        )
    }
    assert list(result) == ["pgbl", "vgbl", "own_portfolio"]
    assert {item.montante_bruto for item in result.values()} == {Decimal("1100.00")}
    assert result["pgbl"].imposto == Decimal("385.00")
    assert result["vgbl"].imposto == Decimal("35.00")
    assert result["own_portfolio"].imposto == Decimal("20.00")
    assert result["own_portfolio"].montante_liquido == Decimal("1080.00")
    assert result["pgbl"].aliquota_efetiva == Decimal("35.00")


def test_SPEC_047_R04_regime_progressivo_usa_aliquota_informada():
    """Cláusulas: SPEC-047-R04 — PGBL a 27,5% sobre 1.100,00 = 302,50."""
    pgbl = comparar_previdencia(
        valor_inicial=Decimal("1000"),
        aporte_mensal=Decimal("0"),
        taxa_anual=Decimal("10"),
        prazo_meses=12,
        regime="progressive",
        aliquota_progressiva=Decimal("27.5"),
    )[0]
    assert pgbl.imposto == Decimal("302.50")


@pytest.mark.parametrize(
    "ajuste",
    [
        {"prazo_meses": 0},
        {"taxa_anual": Decimal("-1")},
        {"regime": "outro"},
        {"regime": "progressive"},
        {"regime": "progressive", "aliquota_progressiva": Decimal("30")},
    ],
)
def test_SPEC_047_R02_parametros_invalidos_sao_recusados(ajuste):
    """Cláusulas: SPEC-047-R02."""
    entrada = {
        "valor_inicial": Decimal("1000"),
        "aporte_mensal": Decimal("0"),
        "taxa_anual": Decimal("10"),
        "prazo_meses": 12,
        "regime": "regressive",
        **ajuste,
    }
    with pytest.raises(ErroCalculo):
        comparar_previdencia(**entrada)


# ------------------------------------------------------------------ SPEC-048
@pytest.mark.parametrize(
    ("ano", "domingo"),
    [(2024, date(2024, 3, 31)), (2026, date(2026, 4, 5)), (2018, date(2018, 4, 1))],
)
def test_SPEC_048_R05_pascoa_pelo_algoritmo_gregoriano(ano, domingo):
    """Cláusulas: SPEC-048-R05 — base da Sexta-feira Santa no calendário do DARF."""
    assert pascoa(ano) == domingo


@pytest.mark.parametrize(
    ("competencia", "vencimento"),
    [
        (date(2026, 3, 15), date(2026, 4, 30)),  # 30/04/2026 é quinta-feira
        (date(2026, 12, 10), date(2027, 1, 29)),  # 31/01/2027 é domingo → sexta 29
        (date(2018, 2, 10), date(2018, 3, 29)),  # 31/03 sábado; 30/03 Sexta-feira Santa
    ],
)
def test_SPEC_048_R05_darf_vence_no_ultimo_dia_util_do_mes_seguinte(competencia, vencimento):
    """Cláusulas: SPEC-048-R05."""
    assert vencimento_darf(competencia) == vencimento


def test_SPEC_048_R03_acoes_ate_20_mil_em_vendas_sao_isentas():
    """Cláusulas: SPEC-048-R03."""
    isento = estimar_ir(
        regime="stock",
        competencia=date(2026, 3, 1),
        resultado=Decimal("1000"),
        vendas_no_mes=Decimal("20000"),
    )
    tributado = estimar_ir(
        regime="stock",
        competencia=date(2026, 3, 1),
        resultado=Decimal("1000"),
        vendas_no_mes=Decimal("20000.01"),
    )
    assert (isento.isento, isento.imposto, isento.vencimento_darf) == (
        True,
        Decimal("0.00"),
        None,
    )
    assert (tributado.imposto, tributado.vencimento_darf) == (
        Decimal("150.00"),
        date(2026, 4, 30),
    )


@pytest.mark.parametrize(
    ("regime", "resultado", "imposto"),
    [
        ("fii", Decimal("100"), Decimal("20.00")),
        ("day_trade", Decimal("100"), Decimal("20.00")),
        ("fii", Decimal("-50"), Decimal("0.00")),
    ],
)
def test_SPEC_048_R03_R04_aliquotas_internas_por_regime(regime, resultado, imposto):
    """Cláusulas: SPEC-048-R03, SPEC-048-R04 — prejuízo não gera imposto."""
    result = estimar_ir(regime=regime, competencia=date(2026, 3, 1), resultado=resultado)
    assert result.imposto == imposto


@pytest.mark.parametrize(
    ("dias", "aliquota", "imposto"), [(180, "22.5", "22.50"), (181, "20", "20.00")]
)
def test_SPEC_048_R03_renda_fixa_e_retida_na_fonte_sem_darf(dias, aliquota, imposto):
    """Cláusulas: SPEC-048-R03 — 181 dias arredonda para 7 meses (210 dias → 20%)."""
    result = estimar_ir(
        regime="fixed_income",
        competencia=date(2026, 3, 1),
        resultado=Decimal("100"),
        dias_aplicacao=dias,
    )
    assert (result.aliquota, result.imposto, result.vencimento_darf) == (
        Decimal(aliquota),
        Decimal(imposto),
        None,
    )


@pytest.mark.parametrize(
    "entrada",
    [
        {"regime": "fixed_income"},
        {"regime": "fixed_income", "dias_aplicacao": 0},
        {"regime": "crypto"},
    ],
)
def test_SPEC_048_R02_regime_ou_prazo_invalido_e_recusado(entrada):
    """Cláusulas: SPEC-048-R02."""
    with pytest.raises(ErroCalculo):
        estimar_ir(competencia=date(2026, 3, 1), resultado=Decimal("100"), **entrada)
