"""Motor de juros compostos (SPEC-002).

Implementação pura da operação ``Simulacao.calcularEvolucao()`` do modelo de domínio (ADR-002):
Python puro, sem I/O, com ``Decimal`` em todos os valores monetários e taxas (INV-02).
"""

from dataclasses import dataclass
from decimal import (
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    Context,
    Decimal,
    DivisionByZero,
    FloatOperation,
    InvalidOperation,
    Overflow,
    localcontext,
)
from enum import Enum

__all__ = [
    "EvolucaoMensal",
    "ResultadoEvolucao",
    "TipoPeriodo",
    "TipoTaxa",
    "calcular_evolucao",
    "converter_taxa_anual_para_mensal",
]

_MESES_POR_ANO = 12
_CENTAVOS = Decimal("0.01")

# PLAN-002, decisão 2: contexto local com 34 dígitos significativos (decimal128), aplicado com
# ``localcontext`` para não alterar o contexto global. FloatOperation interceptado: criar um
# Decimal a partir de float, ou compará-lo com float, gera erro (INV-02).
_CONTEXTO = Context(
    prec=34,
    rounding=ROUND_HALF_EVEN,
    traps=[InvalidOperation, DivisionByZero, Overflow, FloatOperation],
)


class TipoTaxa(Enum):
    """Periodicidade da taxa de juros informada (SPEC-002, seção 4)."""

    MENSAL = "MENSAL"
    ANUAL = "ANUAL"


class TipoPeriodo(Enum):
    """Unidade do período informado (SPEC-002, seção 4)."""

    MESES = "MESES"
    ANOS = "ANOS"


@dataclass(frozen=True, slots=True)
class EvolucaoMensal:
    """Linha imutável da evolução mensal (R04), com valores em centavos (R08)."""

    mes: int
    saldo_inicial: Decimal
    aporte: Decimal
    juros: Decimal
    saldo_final: Decimal


@dataclass(frozen=True, slots=True)
class ResultadoEvolucao:
    """Resultado imutável do cálculo: evolução mensal (R04) e totais (R05).

    Valores monetários em centavos (R08). ``taxa_mensal`` é a taxa usada no cálculo, sem
    arredondamento (PLAN-002, decisão 4).
    """

    taxa_mensal: Decimal
    meses: int
    evolucao: tuple[EvolucaoMensal, ...]
    valor_total_investido: Decimal
    total_juros: Decimal
    montante_final_bruto: Decimal


def converter_taxa_anual_para_mensal(taxa_anual: Decimal | int) -> Decimal:
    """Converte taxa anual em mensal por equivalência composta (R02, INV-01).

    ``i_mensal = (1 + i_anual) ** (1/12) - 1``, com a taxa na forma unitária (12% = 0.12).
    A taxa nunca é dividida por 12: o 1/12 é o expoente da fórmula.
    """
    taxa = _validar_valor("taxa_anual", taxa_anual)
    with localcontext(_CONTEXTO):
        return (1 + taxa) ** (Decimal(1) / _MESES_POR_ANO) - 1


def calcular_evolucao(
    valor_inicial: Decimal | int,
    aporte_mensal: Decimal | int,
    taxa_juros: Decimal | int,
    tipo_taxa: TipoTaxa,
    periodo: int,
    tipo_periodo: TipoPeriodo,
) -> ResultadoEvolucao:
    """Calcula a evolução mensal por juros compostos (SPEC-002-R01 a R08).

    Valida todas as entradas antes de calcular (R06, R07), converte taxa e período para a base
    mensal (R02, R03), itera mês a mês com o aporte no fim do período (R01) e arredonda os
    valores monetários para centavos só na montagem do resultado (R08).

    Raises:
        TypeError: valor monetário ou taxa que não seja ``Decimal`` ou ``int`` (``float`` e
            ``bool`` incluídos), período que não seja ``int`` ou tipo fora dos ``Enum``.
        ValueError: valor monetário ou taxa negativos ou não finitos, ou período <= 0.
    """
    inicial = _validar_valor("valor_inicial", valor_inicial)
    aporte = _validar_valor("aporte_mensal", aporte_mensal)
    taxa = _validar_valor("taxa_juros", taxa_juros)
    _validar_enum("tipo_taxa", tipo_taxa, TipoTaxa)
    _validar_periodo(periodo)
    _validar_enum("tipo_periodo", tipo_periodo, TipoPeriodo)

    taxa_mensal = converter_taxa_anual_para_mensal(taxa) if tipo_taxa is TipoTaxa.ANUAL else taxa
    meses = periodo * _MESES_POR_ANO if tipo_periodo is TipoPeriodo.ANOS else periodo

    with localcontext(_CONTEXTO):
        # Cálculo sem arredondamento intermediário (R01, R05).
        serie: list[tuple[int, Decimal, Decimal, Decimal]] = []
        saldo = inicial
        for mes in range(1, meses + 1):
            juros = saldo * taxa_mensal
            saldo_final = saldo + juros + aporte
            serie.append((mes, saldo, juros, saldo_final))
            saldo = saldo_final
        valor_total_investido = inicial + meses * aporte
        total_juros = saldo - valor_total_investido

        # Montagem do resultado: único ponto de arredondamento (R08).
        return ResultadoEvolucao(
            taxa_mensal=taxa_mensal,
            meses=meses,
            evolucao=tuple(
                EvolucaoMensal(
                    mes=mes,
                    saldo_inicial=_arredondar(saldo_inicial),
                    aporte=_arredondar(aporte),
                    juros=_arredondar(juros),
                    saldo_final=_arredondar(saldo_final),
                )
                for mes, saldo_inicial, juros, saldo_final in serie
            ),
            valor_total_investido=_arredondar(valor_total_investido),
            total_juros=_arredondar(total_juros),
            montante_final_bruto=_arredondar(saldo),
        )


def _validar_valor(campo: str, valor: object) -> Decimal:
    """Aceita valor monetário ou taxa em ``Decimal`` ou ``int``, finito e >= 0 (R06, R07)."""
    if isinstance(valor, bool) or not isinstance(valor, Decimal | int):
        raise TypeError(f"{campo} deve ser Decimal ou int, não {type(valor).__name__}.")
    numero = Decimal(valor)
    if not numero.is_finite():
        raise ValueError(f"{campo} deve ser um número finito.")
    if numero < 0:
        raise ValueError(f"{campo} não pode ser negativo.")
    return numero.copy_abs()  # -0 vale zero; evita exibir "-0.00".


def _validar_periodo(periodo: object) -> None:
    """Aceita apenas ``int`` maior que zero (R06; PLAN-002, decisão 3)."""
    if isinstance(periodo, bool) or not isinstance(periodo, int):
        raise TypeError(f"periodo deve ser int, não {type(periodo).__name__}.")
    if periodo <= 0:
        raise ValueError("periodo deve ser maior que zero.")


def _validar_enum(campo: str, valor: object, tipo: type[Enum]) -> None:
    """Aceita apenas membros do ``Enum`` esperado."""
    if not isinstance(valor, tipo):
        raise TypeError(f"{campo} deve ser {tipo.__name__}, não {type(valor).__name__}.")


def _arredondar(valor: Decimal) -> Decimal:
    """Arredonda valor monetário para centavos com ROUND_HALF_UP (R08)."""
    return valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
