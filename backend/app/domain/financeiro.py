"""Cálculos puros usados pelas Specs financeiras posteriores ao motor base."""

from decimal import Decimal

from app.domain.juros_compostos import ErroCalculo, MotorJurosCompostos, converter_taxa


def aliquota_ir_renda_fixa(prazo_meses: int, produto: str) -> Decimal:
    """Tabela regressiva interna, versionada para cenários de simulação."""
    if produto == "poupanca":
        return Decimal("0")
    if produto not in {"cdb", "tesouro"} or prazo_meses <= 0:
        raise ErroCalculo("produto", "regra_tributaria_indisponivel")
    dias_estimados = prazo_meses * 30
    if dias_estimados <= 180:
        return Decimal("22.5")
    if dias_estimados <= 360:
        return Decimal("20")
    if dias_estimados <= 720:
        return Decimal("17.5")
    return Decimal("15")


def resultado_liquido(
    bruto: Decimal, investido: Decimal, prazo_meses: int, produto: str
) -> tuple[Decimal, Decimal]:
    if bruto < investido:
        raise ErroCalculo("montante", "resultado_invalido")
    aliquota = aliquota_ir_renda_fixa(prazo_meses, produto)
    imposto = (bruto - investido) * aliquota / Decimal("100")
    return imposto, bruto - imposto


def aporte_necessario(
    *, alvo: Decimal, inicial: Decimal, taxa_percentual: Decimal, prazo_meses: int
) -> Decimal:
    if alvo <= 0 or inicial < 0 or prazo_meses <= 0:
        raise ErroCalculo("objetivo", "entrada_invalida")
    taxa = converter_taxa(taxa_percentual, "anual", "mensal") / Decimal("100")
    if taxa == 0:
        return max(Decimal("0"), (alvo - inicial) / prazo_meses)
    fator = (Decimal("1") + taxa) ** prazo_meses
    necessario = (alvo - inicial * fator) * taxa / (fator - Decimal("1"))
    return max(Decimal("0"), necessario)


def projetar(*, inicial: Decimal, aporte: Decimal, taxa: Decimal, prazo: int):
    return MotorJurosCompostos.calcular(
        valor_inicial=inicial,
        aporte_mensal=aporte,
        taxa_percentual=taxa,
        periodicidade_taxa="anual",
        prazo=prazo,
        unidade_prazo="meses",
    )
