"""Cálculos puros das Specs de expansão (sem I/O, regras C-03, C-04 e C-05).

- SPEC-046: projeção de aposentadoria e renda estimada por taxa de retirada.
- SPEC-047: comparação PGBL x VGBL x carteira própria com tabelas simplificadas.
- SPEC-048: estimativa de IR por regime e data-limite do DARF.

Tabelas internas versionadas ("2026-10"); são simplificações educativas, não apuração oficial.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal

from app.domain.juros_compostos import ErroCalculo, MotorJurosCompostos, converter_taxa

TAX_RULE_VERSION = "2026-10"
CENT = Decimal("0.01")
HUNDRED = Decimal("100")
TWELVE = Decimal("12")


def moeda(valor: Decimal) -> Decimal:
    return valor.quantize(CENT, ROUND_HALF_EVEN)


# ---------------------------------------------------------------- SPEC-046
@dataclass(frozen=True)
class ProjecaoAposentadoria:
    meses: int
    total_investido: Decimal
    patrimonio_projetado: Decimal
    renda_mensal_estimada: Decimal
    taxa_retirada_anual: Decimal


def projetar_aposentadoria(
    *,
    idade_atual: int,
    idade_alvo: int,
    valor_inicial: Decimal,
    aporte_mensal: Decimal,
    taxa_anual: Decimal,
    taxa_retirada_anual: Decimal = Decimal("4"),
) -> ProjecaoAposentadoria:
    """Reaproveita o motor (RF-22/RB-10) até a idade-alvo e aplica a regra de retirada."""
    if idade_alvo <= idade_atual:
        raise ErroCalculo("idade_alvo", "idade_alvo_deve_ser_futura")
    if not Decimal("0") < taxa_retirada_anual <= Decimal("20"):
        raise ErroCalculo("taxa_retirada", "taxa_retirada_invalida")
    meses = (idade_alvo - idade_atual) * 12
    resultado = MotorJurosCompostos.calcular(
        valor_inicial=valor_inicial,
        aporte_mensal=aporte_mensal,
        taxa_percentual=taxa_anual,
        periodicidade_taxa="anual",
        prazo=meses,
        unidade_prazo="meses",
    )
    renda = resultado.montante * taxa_retirada_anual / HUNDRED / TWELVE
    return ProjecaoAposentadoria(
        meses=meses,
        total_investido=moeda(resultado.total_investido),
        patrimonio_projetado=moeda(resultado.montante),
        renda_mensal_estimada=moeda(renda),
        taxa_retirada_anual=taxa_retirada_anual,
    )


# ---------------------------------------------------------------- SPEC-047
def aliquota_previdencia_regressiva(meses_acumulados: int) -> Decimal:
    """Tabela regressiva de previdência por tempo de acumulação de cada aporte."""
    anos = Decimal(meses_acumulados) / TWELVE
    for limite, aliquota in ((2, "35"), (4, "30"), (6, "25"), (8, "20"), (10, "15")):
        if anos <= limite:
            return Decimal(aliquota)
    return Decimal("10")


def aliquota_renda_fixa_por_meses(meses: int) -> Decimal:
    """Tabela regressiva de renda fixa (mesma convenção de 30 dias/mês da SPEC-004)."""
    dias = meses * 30
    if dias <= 180:
        return Decimal("22.5")
    if dias <= 360:
        return Decimal("20")
    if dias <= 720:
        return Decimal("17.5")
    return Decimal("15")


@dataclass(frozen=True)
class ResultadoModalidade:
    modalidade: str
    total_investido: Decimal
    montante_bruto: Decimal
    rendimento: Decimal
    imposto: Decimal
    montante_liquido: Decimal
    aliquota_efetiva: Decimal


def comparar_previdencia(
    *,
    valor_inicial: Decimal,
    aporte_mensal: Decimal,
    taxa_anual: Decimal,
    prazo_meses: int,
    regime: str,
    aliquota_progressiva: Decimal | None = None,
) -> list[ResultadoModalidade]:
    """Mesmos parâmetros para PGBL, VGBL e carteira própria; IR por aporte (PEPS)."""
    if prazo_meses <= 0 or valor_inicial < 0 or aporte_mensal < 0 or taxa_anual < 0:
        raise ErroCalculo("parametros", "entrada_invalida")
    if regime not in ("regressive", "progressive"):
        raise ErroCalculo("regime", "regime_nao_configurado")
    if regime == "progressive" and (
        aliquota_progressiva is None or not Decimal("0") <= aliquota_progressiva <= Decimal("27.5")
    ):
        raise ErroCalculo("aliquota_progressiva", "aliquota_progressiva_obrigatoria")
    taxa_mensal = converter_taxa(taxa_anual, "anual", "mensal") / HUNDRED  # C-04
    # Cada aporte é uma "parcela" com o próprio tempo de acumulação (aporte no fim do mês).
    parcelas = [(valor_inicial, prazo_meses)] if valor_inicial > 0 else []
    parcelas += [(aporte_mensal, prazo_meses - mes) for mes in range(1, prazo_meses + 1)]
    parcelas = [(valor, meses) for valor, meses in parcelas if valor > 0]
    resultados = []
    for modalidade in ("pgbl", "vgbl", "own_portfolio"):
        investido = bruto = imposto = Decimal("0")
        for valor, meses in parcelas:
            final = valor * (1 + taxa_mensal) ** meses
            rendimento = final - valor
            if modalidade == "own_portfolio":
                aliquota, base = aliquota_renda_fixa_por_meses(max(meses, 1)), rendimento
            else:
                aliquota = (
                    aliquota_previdencia_regressiva(meses)
                    if regime == "regressive"
                    else aliquota_progressiva
                )
                # PGBL tributa o valor total resgatado; VGBL apenas o rendimento.
                base = final if modalidade == "pgbl" else rendimento
            investido += valor
            bruto += final
            imposto += base * aliquota / HUNDRED
        bruto, imposto = moeda(bruto), moeda(imposto)
        resultados.append(
            ResultadoModalidade(
                modalidade=modalidade,
                total_investido=moeda(investido),
                montante_bruto=bruto,
                rendimento=moeda(bruto - investido),
                imposto=imposto,
                montante_liquido=bruto - imposto,
                aliquota_efetiva=moeda(imposto / bruto * HUNDRED) if bruto else Decimal("0"),
            )
        )
    return resultados


# ---------------------------------------------------------------- SPEC-048
def pascoa(ano: int) -> date:
    """Domingo de Páscoa (algoritmo gregoriano anônimo)."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    mes, dia = divmod(h + m - 7 * n + 114, 31)
    return date(ano, mes, dia + 1)


def feriados_nacionais(ano: int) -> set[date]:
    """Feriados nacionais fixos e Sexta-feira Santa (recorte aprovado; sem pontos facultativos)."""
    fixos = {(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)}
    return {date(ano, mes, dia) for mes, dia in fixos} | {pascoa(ano) - timedelta(days=2)}


def vencimento_darf(competencia: date) -> date:
    """Último dia útil do mês seguinte ao da operação."""
    ano, mes = (
        (competencia.year + 1, 1)
        if competencia.month == 12
        else (
            competencia.year,
            competencia.month + 1,
        )
    )
    proximo = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
    dia = proximo - timedelta(days=1)
    feriados = feriados_nacionais(ano)
    while dia.weekday() >= 5 or dia in feriados:
        dia -= timedelta(days=1)
    return dia


@dataclass(frozen=True)
class EstimativaIR:
    regime: str
    aliquota: Decimal
    imposto: Decimal
    isento: bool
    vencimento_darf: date | None
    observacoes: tuple[str, ...]


ISENCAO_ACOES_MENSAL = Decimal("20000")


def estimar_ir(
    *,
    regime: str,
    competencia: date,
    resultado: Decimal,
    vendas_no_mes: Decimal = Decimal("0"),
    dias_aplicacao: int | None = None,
) -> EstimativaIR:
    """Estimativa educativa de IR por regime (RF-64), com regra interna versionada."""
    observacoes: list[str] = []
    if regime == "fixed_income":
        if dias_aplicacao is None or dias_aplicacao <= 0:
            raise ErroCalculo("dias_aplicacao", "prazo_obrigatorio")
        aliquota = aliquota_renda_fixa_por_meses(-(-dias_aplicacao // 30))
        observacoes.append("Renda fixa: imposto retido na fonte; não há DARF a emitir.")
        imposto = moeda(max(resultado, Decimal("0")) * aliquota / HUNDRED)
        return EstimativaIR(regime, aliquota, imposto, False, None, tuple(observacoes))
    aliquotas = {"stock": Decimal("15"), "fii": Decimal("20"), "day_trade": Decimal("20")}
    if regime not in aliquotas:
        raise ErroCalculo("regime", "regime_nao_configurado")
    aliquota = aliquotas[regime]
    if resultado <= 0:
        observacoes.append(
            "Sem lucro no mês: nada a recolher. A compensação de prejuízos não é calculada."
        )
        return EstimativaIR(regime, aliquota, Decimal("0.00"), False, None, tuple(observacoes))
    if regime == "stock" and vendas_no_mes <= ISENCAO_ACOES_MENSAL:
        observacoes.append("Vendas de ações no mês até R$ 20.000,00: lucro isento.")
        return EstimativaIR(regime, aliquota, Decimal("0.00"), True, None, tuple(observacoes))
    observacoes.append("Compensação de prejuízos anteriores não aplicada nesta estimativa.")
    imposto = moeda(resultado * aliquota / HUNDRED)
    return EstimativaIR(
        regime, aliquota, imposto, False, vencimento_darf(competencia), tuple(observacoes)
    )
