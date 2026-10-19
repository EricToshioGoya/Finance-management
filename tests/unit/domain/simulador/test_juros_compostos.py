"""Testes unitários do motor de juros compostos (SPEC-002).

Cada teste cita no nome e na docstring a cláusula que verifica. Os valores esperados vêm dos
Cenários 1 a 5 da spec ou de referência independente registrada na docstring; nunca são
recalculados com a fórmula da implementação.
"""

import dataclasses
from decimal import Decimal, getcontext

import pytest

from finnova.domain.simulador import (
    EvolucaoMensal,
    ResultadoEvolucao,
    TipoPeriodo,
    TipoTaxa,
    calcular_evolucao,
    converter_taxa_anual_para_mensal,
    juros_compostos,
)

# Cenário 1: R$ 1.000,00, sem aportes, 12% a.a., 12 meses.
CENARIO_1 = {
    "valor_inicial": Decimal("1000.00"),
    "aporte_mensal": Decimal(0),
    "taxa_juros": Decimal("0.12"),
    "tipo_taxa": TipoTaxa.ANUAL,
    "periodo": 12,
    "tipo_periodo": TipoPeriodo.MESES,
}

# Cenário 2: R$ 0,00 inicial, aporte de R$ 100,00, 1% a.m., 2 meses.
CENARIO_2 = {
    "valor_inicial": Decimal("0.00"),
    "aporte_mensal": Decimal("100.00"),
    "taxa_juros": Decimal("0.01"),
    "tipo_taxa": TipoTaxa.MENSAL,
    "periodo": 2,
    "tipo_periodo": TipoPeriodo.MESES,
}

# Cenário 4: R$ 1.000,00 inicial, aporte de R$ 100,00, 1% a.m., 2 meses.
CENARIO_4 = {**CENARIO_2, "valor_inicial": Decimal("1000.00")}

# Cenário 5: R$ 12,50 inicial, sem aportes, 1% a.m., 2 meses.
CENARIO_5 = {**CENARIO_2, "valor_inicial": Decimal("12.50"), "aporte_mensal": Decimal(0)}


def _valores_monetarios(resultado: ResultadoEvolucao) -> list[Decimal]:
    """Todos os valores monetários do resultado: série mensal e totais."""
    valores = [
        resultado.valor_total_investido,
        resultado.total_juros,
        resultado.montante_final_bruto,
    ]
    for linha in resultado.evolucao:
        valores += [linha.saldo_inicial, linha.aporte, linha.juros, linha.saldo_final]
    return valores


# --- SPEC-002-R01: saldo mensal com aporte no fim do período -------------------------------


def test_spec002_r01_saldo_mensal_com_aporte_no_fim_do_periodo():
    """SPEC-002-R01 — Cenário 2: o aporte entra no fim do mês e só rende no mês seguinte."""
    resultado = calcular_evolucao(**CENARIO_2)

    mes_1, mes_2 = resultado.evolucao
    assert mes_1.juros == Decimal("0.00")
    assert mes_1.saldo_final == Decimal("100.00")
    assert mes_2.juros == Decimal("1.00")
    assert mes_2.saldo_final == Decimal("201.00")


def test_spec002_r01_juros_incidem_sobre_o_saldo_do_mes_anterior():
    """SPEC-002-R01 — Cenário 4: Saldo_k = Saldo_{k-1} + Saldo_{k-1} x i + AporteMensal."""
    resultado = calcular_evolucao(**CENARIO_4)

    mes_1, mes_2 = resultado.evolucao
    assert mes_1.juros == Decimal("10.00")
    assert mes_1.saldo_final == Decimal("1110.00")
    assert mes_2.juros == Decimal("11.10")
    assert mes_2.saldo_final == Decimal("1221.10")


# --- SPEC-002-R02: taxa anual convertida por equivalência composta --------------------------


def test_spec002_r02_converte_taxa_anual_por_equivalencia_composta():
    """SPEC-002-R02 — Cenário 1: 12% a.a. equivale a ~0,948879% a.m."""
    taxa_mensal = converter_taxa_anual_para_mensal(Decimal("0.12"))

    taxa_mensal_percentual = taxa_mensal * 100
    assert abs(taxa_mensal_percentual - Decimal("0.948879")) <= Decimal("0.0000005")


def test_spec002_r02_calculo_com_taxa_anual_usa_taxa_mensal_equivalente():
    """SPEC-002-R02 — Cenário 1: o motor usa a taxa mensal equivalente e chega a R$ 1.120,00."""
    resultado = calcular_evolucao(**CENARIO_1)

    assert abs(resultado.taxa_mensal * 100 - Decimal("0.948879")) <= Decimal("0.0000005")
    assert resultado.montante_final_bruto == Decimal("1120.00")


def test_spec002_r02_taxa_mensal_informada_nao_e_convertida():
    """SPEC-002-R02 — só a taxa anual é convertida; a taxa mensal é usada como informada."""
    resultado = calcular_evolucao(**CENARIO_2)

    assert resultado.taxa_mensal == Decimal("0.01")


# --- SPEC-002-R03: período em anos convertido para meses ------------------------------------


def test_spec002_r03_converte_um_ano_em_doze_meses():
    """SPEC-002-R03 — Cenário 1 com período em anos: 1 ano dá o mesmo resultado que 12 meses."""
    em_anos = calcular_evolucao(**{**CENARIO_1, "periodo": 1, "tipo_periodo": TipoPeriodo.ANOS})
    em_meses = calcular_evolucao(**CENARIO_1)

    assert em_anos.meses == 12
    assert len(em_anos.evolucao) == 12
    assert em_anos.evolucao[-1].mes == 12
    assert em_anos.montante_final_bruto == Decimal("1120.00")
    assert em_anos == em_meses


def test_spec002_r03_converte_dois_anos_em_vinte_e_quatro_meses():
    """SPEC-002-R03 — 2 anos = 24 meses; referência: 1000 x 1,12^2 = R$ 1.254,40."""
    resultado = calcular_evolucao(**{**CENARIO_1, "periodo": 2, "tipo_periodo": TipoPeriodo.ANOS})

    assert resultado.meses == 24
    assert len(resultado.evolucao) == 24
    assert resultado.montante_final_bruto == Decimal("1254.40")


def test_spec002_r03_horizonte_de_trinta_anos():
    """SPEC-002-R02/R03 — 30 anos = 360 meses; precisão em horizonte longo (PLAN-002, risco 1).

    Referência independente: 1000 x 1,12^30 = 29.959,9221... (potência inteira em aritmética
    racional exata), ou seja, R$ 29.959,92.
    """
    resultado = calcular_evolucao(**{**CENARIO_1, "periodo": 30, "tipo_periodo": TipoPeriodo.ANOS})

    assert resultado.meses == 360
    assert len(resultado.evolucao) == 360
    assert resultado.montante_final_bruto == Decimal("29959.92")


# --- SPEC-002-R04: série mensal ------------------------------------------------------------


def test_spec002_r04_serie_mensal_com_saldo_inicial_aporte_juros_e_saldo_final():
    """SPEC-002-R04 — Cenário 2: cada mês traz saldo inicial, aporte, juros e saldo final."""
    resultado = calcular_evolucao(**CENARIO_2)

    assert resultado.evolucao == (
        EvolucaoMensal(
            mes=1,
            saldo_inicial=Decimal("0.00"),
            aporte=Decimal("100.00"),
            juros=Decimal("0.00"),
            saldo_final=Decimal("100.00"),
        ),
        EvolucaoMensal(
            mes=2,
            saldo_inicial=Decimal("100.00"),
            aporte=Decimal("100.00"),
            juros=Decimal("1.00"),
            saldo_final=Decimal("201.00"),
        ),
    )


def test_spec002_r04_saldo_inicial_do_mes_e_o_saldo_final_do_mes_anterior():
    """SPEC-002-R04 — Cenário 4: a série começa no valor inicial e é contínua mês a mês."""
    resultado = calcular_evolucao(**CENARIO_4)

    mes_1, mes_2 = resultado.evolucao
    assert mes_1.saldo_inicial == Decimal("1000.00")
    assert mes_2.saldo_inicial == Decimal("1110.00")
    assert [linha.mes for linha in resultado.evolucao] == [1, 2]


# --- SPEC-002-R05: totais ------------------------------------------------------------------


def test_spec002_r05_totais_sem_aporte_mensal():
    """SPEC-002-R05 — Cenário 1: investido R$ 1.000,00; juros R$ 120,00; montante R$ 1.120,00."""
    resultado = calcular_evolucao(**CENARIO_1)

    assert resultado.valor_total_investido == Decimal("1000.00")
    assert resultado.total_juros == Decimal("120.00")
    assert resultado.montante_final_bruto == Decimal("1120.00")


def test_spec002_r05_totais_com_aportes_mensais():
    """SPEC-002-R05 — Cenário 2: investido R$ 200,00; juros R$ 1,00; montante R$ 201,00."""
    resultado = calcular_evolucao(**CENARIO_2)

    assert resultado.valor_total_investido == Decimal("200.00")
    assert resultado.total_juros == Decimal("1.00")
    assert resultado.montante_final_bruto == Decimal("201.00")


def test_spec002_r05_valor_total_investido_inclui_valor_inicial():
    """SPEC-002-R05 — Cenário 4 (OPEN-02): o valor total investido inclui o valor inicial.

    Investido R$ 1.200,00 (1.000,00 + 2 x 100,00); juros R$ 21,10; montante R$ 1.221,10.
    """
    resultado = calcular_evolucao(**CENARIO_4)

    assert resultado.valor_total_investido == Decimal("1200.00")
    assert resultado.total_juros == Decimal("21.10")
    assert resultado.montante_final_bruto == Decimal("1221.10")


def test_spec002_r04_r05_resultado_e_imutavel():
    """SPEC-002-R04/R05 — o resultado é uma estrutura imutável (seção 4, passo 6)."""
    resultado = calcular_evolucao(**CENARIO_2)

    assert isinstance(resultado.evolucao, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        resultado.montante_final_bruto = Decimal(0)  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        resultado.evolucao[0].saldo_final = Decimal(0)  # type: ignore[misc]


# --- SPEC-002-R06: entradas inválidas -------------------------------------------------------


def test_spec002_r06_rejeita_valor_inicial_negativo():
    """SPEC-002-R06 — Cenário 3: valor inicial negativo gera ValueError que indica o campo."""
    with pytest.raises(ValueError, match="valor_inicial"):
        calcular_evolucao(**{**CENARIO_4, "valor_inicial": Decimal("-0.01")})


def test_spec002_r06_rejeita_aporte_mensal_negativo():
    """SPEC-002-R06 — aporte mensal negativo gera ValueError que indica o campo."""
    with pytest.raises(ValueError, match="aporte_mensal"):
        calcular_evolucao(**{**CENARIO_4, "aporte_mensal": Decimal("-100.00")})


def test_spec002_r06_rejeita_taxa_juros_negativa():
    """SPEC-002-R06 — Cenário 3: taxa negativa gera ValueError que indica o campo."""
    with pytest.raises(ValueError, match="taxa_juros"):
        calcular_evolucao(**{**CENARIO_4, "taxa_juros": Decimal("-0.01")})


def test_spec002_r06_rejeita_periodo_zero():
    """SPEC-002-R06 — Cenário 3: período de 0 meses gera ValueError que indica o campo."""
    with pytest.raises(ValueError, match="periodo"):
        calcular_evolucao(**{**CENARIO_4, "periodo": 0})


def test_spec002_r06_rejeita_periodo_negativo():
    """SPEC-002-R06 — período negativo gera ValueError que indica o campo."""
    with pytest.raises(ValueError, match="periodo"):
        calcular_evolucao(**{**CENARIO_4, "periodo": -1, "tipo_periodo": TipoPeriodo.ANOS})


def test_spec002_r06_rejeita_taxa_anual_negativa_na_conversao():
    """SPEC-002-R06 — a conversão de taxa também recusa taxa negativa."""
    with pytest.raises(ValueError, match="taxa_anual"):
        converter_taxa_anual_para_mensal(Decimal("-0.12"))


@pytest.mark.parametrize("valor", [Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity")])
def test_spec002_r06_rejeita_valor_nao_finito(valor):
    """SPEC-002-R06 — valor não finito não atende a ">= 0" da seção 4 e gera ValueError."""
    with pytest.raises(ValueError, match="valor_inicial"):
        calcular_evolucao(**{**CENARIO_4, "valor_inicial": valor})


def test_spec002_r06_valida_entradas_antes_de_calcular(monkeypatch):
    """SPEC-002-R06 — a entrada inválida é recusada sem executar o cálculo (nem a conversão)."""
    chamadas = []
    monkeypatch.setattr(
        juros_compostos,
        "converter_taxa_anual_para_mensal",
        lambda taxa: chamadas.append(taxa),
    )

    with pytest.raises(ValueError, match="periodo"):
        calcular_evolucao(**{**CENARIO_1, "periodo": 0})
    assert chamadas == []


def test_spec002_r06_aceita_zero_nos_valores_e_na_taxa():
    """SPEC-002-R06 — zero é válido em valor inicial, aporte e taxa (">= 0"; RF-22 "aceita 0")."""
    resultado = calcular_evolucao(
        valor_inicial=Decimal(0),
        aporte_mensal=Decimal(0),
        taxa_juros=Decimal(0),
        tipo_taxa=TipoTaxa.ANUAL,
        periodo=1,
        tipo_periodo=TipoPeriodo.MESES,
    )

    assert resultado.taxa_mensal == 0
    assert resultado.montante_final_bruto == Decimal("0.00")
    assert resultado.total_juros == Decimal("0.00")


def test_spec002_r06_zero_negativo_nao_e_negativo():
    """SPEC-002-R06 — Decimal("-0") vale zero: é aceito e exibido como 0.00, nunca -0.00."""
    resultado = calcular_evolucao(**{**CENARIO_4, "valor_inicial": Decimal("-0")})

    assert str(resultado.evolucao[0].saldo_inicial) == "0.00"


# --- SPEC-002-R07: Decimal, nunca float ----------------------------------------------------


def test_spec002_r07_resultado_usa_somente_decimal():
    """SPEC-002-R07 — taxa e todos os valores monetários do resultado são Decimal."""
    resultado = calcular_evolucao(**CENARIO_1)

    assert type(resultado.taxa_mensal) is Decimal
    for valor in _valores_monetarios(resultado):
        assert type(valor) is Decimal
    assert type(resultado.meses) is int
    assert all(type(linha.mes) is int for linha in resultado.evolucao)


@pytest.mark.parametrize("campo", ["valor_inicial", "aporte_mensal", "taxa_juros"])
def test_spec002_r07_float_na_entrada_gera_type_error(campo):
    """SPEC-002-R07 — float em valor monetário ou taxa gera TypeError (PLAN-002, decisão 3)."""
    with pytest.raises(TypeError, match=campo):
        calcular_evolucao(**{**CENARIO_4, campo: 0.01})


@pytest.mark.parametrize("campo", ["valor_inicial", "aporte_mensal", "taxa_juros"])
def test_spec002_r07_bool_na_entrada_gera_type_error(campo):
    """SPEC-002-R07 — bool não é aceito como valor monetário ou taxa (PLAN-002, decisão 3)."""
    with pytest.raises(TypeError, match=campo):
        calcular_evolucao(**{**CENARIO_4, campo: True})


@pytest.mark.parametrize("periodo", [2.0, Decimal(2), True])
def test_spec002_r07_periodo_aceita_apenas_int(periodo):
    """SPEC-002-R07 — período em float, Decimal ou bool gera TypeError (PLAN-002, decisão 3)."""
    with pytest.raises(TypeError, match="periodo"):
        calcular_evolucao(**{**CENARIO_4, "periodo": periodo})


def test_spec002_r07_conversao_de_taxa_recusa_float():
    """SPEC-002-R07 — a conversão de taxa recusa float com TypeError."""
    with pytest.raises(TypeError, match="taxa_anual"):
        converter_taxa_anual_para_mensal(0.12)


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("tipo_taxa", "ANUAL"), ("tipo_periodo", "MESES"), ("tipo_taxa", TipoPeriodo.MESES)],
)
def test_spec002_r07_tipo_de_taxa_e_de_periodo_exigem_enum(campo, valor):
    """SPEC-002-R07 — tipo de taxa e de período só aceitam os Enum da seção 4."""
    with pytest.raises(TypeError, match=campo):
        calcular_evolucao(**{**CENARIO_4, campo: valor})


def test_spec002_r07_aceita_int_nos_valores_monetarios():
    """SPEC-002-R07 — int é aceito e convertido para Decimal (PLAN-002, decisão 3); Cenário 4."""
    resultado = calcular_evolucao(**{**CENARIO_4, "valor_inicial": 1000, "aporte_mensal": 100})

    assert resultado.montante_final_bruto == Decimal("1221.10")
    assert type(resultado.montante_final_bruto) is Decimal


def test_spec002_r07_nao_altera_o_contexto_decimal_global():
    """SPEC-002-R07 — o cálculo usa contexto decimal local (PLAN-002, decisão 2)."""
    precisao_antes = getcontext().prec

    calcular_evolucao(**CENARIO_1)

    assert getcontext().prec == precisao_antes


# --- SPEC-002-R08: arredondamento apenas na saída -------------------------------------------


def test_spec002_r08_arredonda_apenas_na_saida():
    """SPEC-002-R08 — Cenário 5: o mês 2 é calculado sobre 12,625 (exato), não sobre 12,63.

    Valores exatos: mês 1 juros 0,125 e saldo 12,625; mês 2 juros 0,12625 e saldo 12,75125;
    total de juros 0,25125. Com arredondamento intermediário o mês 2 daria R$ 12,76.
    """
    resultado = calcular_evolucao(**CENARIO_5)

    mes_1, mes_2 = resultado.evolucao
    assert mes_1.juros == Decimal("0.13")
    assert mes_1.saldo_final == Decimal("12.63")
    assert mes_2.saldo_inicial == Decimal("12.63")
    assert mes_2.juros == Decimal("0.13")
    assert mes_2.saldo_final == Decimal("12.75")
    assert resultado.montante_final_bruto == Decimal("12.75")
    assert resultado.total_juros == Decimal("0.25")
    assert resultado.valor_total_investido == Decimal("12.50")


def test_spec002_r08_usa_round_half_up():
    """SPEC-002-R08 — Cenário 5: 0,125 vira 0,13 (ROUND_HALF_UP), e não 0,12 (ROUND_HALF_EVEN)."""
    resultado = calcular_evolucao(**CENARIO_5)

    assert resultado.evolucao[0].juros == Decimal("0.13")


def test_spec002_r08_soma_exibida_pode_diferir_do_total():
    """SPEC-002-R08 — Cenário 5 (OPEN-01): consequência aceita do arredondamento independente.

    Saldo inicial exibido do mês 2 (12,63) + juros exibidos (0,13) = 12,76, mas o saldo final
    exibido é 12,75.
    """
    resultado = calcular_evolucao(**CENARIO_5)

    mes_2 = resultado.evolucao[1]
    assert mes_2.saldo_inicial + mes_2.juros + mes_2.aporte == Decimal("12.76")
    assert mes_2.saldo_final == Decimal("12.75")


def test_spec002_r08_valores_monetarios_com_duas_casas_decimais():
    """SPEC-002-R08 — Cenário 1: todo valor monetário da série e dos totais tem 2 casas."""
    resultado = calcular_evolucao(**CENARIO_1)

    assert str(resultado.montante_final_bruto) == "1120.00"
    for valor in _valores_monetarios(resultado):
        assert valor.as_tuple().exponent == -2


def test_spec002_r08_taxa_mensal_nao_e_arredondada():
    """SPEC-002-R08 — a taxa não é valor monetário e não é arredondada (PLAN-002, decisão 4)."""
    resultado = calcular_evolucao(**{**CENARIO_5, "taxa_juros": Decimal("0.00125")})

    assert resultado.taxa_mensal == Decimal("0.00125")


# --- Invariantes ---------------------------------------------------------------------------


def test_spec002_inv01_taxa_anual_nao_e_convertida_por_divisao_simples():
    """SPEC-002-INV-01 — 12% a.a. não vira 1% a.m. (12 / 12).

    Referências independentes: com 1% a.m. o montante seria 1000 x 1,01^12 = R$ 1.126,83;
    com a taxa equivalente composta é 1000 x 1,12 = R$ 1.120,00.
    """
    taxa_mensal = converter_taxa_anual_para_mensal(Decimal("0.12"))
    resultado = calcular_evolucao(**CENARIO_1)

    assert taxa_mensal < Decimal("0.01")
    assert resultado.montante_final_bruto != Decimal("1126.83")
    assert resultado.montante_final_bruto == Decimal("1120.00")


def test_spec002_inv01_taxa_mensal_recompoe_a_taxa_anual():
    """SPEC-002-INV-01 — conversão inversa do RF-22: (1 + i_mensal)^12 - 1 = i_anual."""
    taxa_mensal = converter_taxa_anual_para_mensal(Decimal("0.12"))

    taxa_anual = (1 + taxa_mensal) ** 12 - 1
    assert abs(taxa_anual - Decimal("0.12")) < Decimal("1e-20")


def test_spec002_inv02_calculo_em_decimal_exato_sem_float():
    """SPEC-002-INV-02 — R$ 1,005 arredonda para R$ 1,01 em Decimal exato.

    Referência: em float, 1.005 vale 1,00499999999999989... e arredondaria para R$ 1,00.
    """
    resultado = calcular_evolucao(
        valor_inicial=Decimal("1.005"),
        aporte_mensal=Decimal(0),
        taxa_juros=Decimal(0),
        tipo_taxa=TipoTaxa.MENSAL,
        periodo=1,
        tipo_periodo=TipoPeriodo.MESES,
    )

    assert resultado.montante_final_bruto == Decimal("1.01")
    assert resultado.valor_total_investido == Decimal("1.01")


def test_spec002_inv02_valores_do_resultado_nao_sao_float():
    """SPEC-002-INV-02 — nenhum valor do resultado é float (Cenário 4)."""
    resultado = calcular_evolucao(**CENARIO_4)

    assert not isinstance(resultado.taxa_mensal, float)
    assert not any(isinstance(valor, float) for valor in _valores_monetarios(resultado))
