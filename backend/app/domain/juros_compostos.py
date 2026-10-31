"""SPEC-002: evolução bruta com aportes no fim do mês, sem I/O (ADR-002)."""

from dataclasses import dataclass
from decimal import (
    ROUND_HALF_UP,
    Context,
    Decimal,
    DecimalException,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    Underflow,
    localcontext,
)
from typing import Literal

PeriodicidadeTaxa = Literal["mensal", "anual"]
UnidadePrazo = Literal["meses", "anos"]

_ZERO = Decimal("0")
_UM = Decimal("1")
_CEM = Decimal("100")
_DOZE = Decimal("12")


def _contexto() -> Context:
    # A fresh context also isolates flags/traps from the caller and other threads.
    return Context(
        prec=50,
        rounding=ROUND_HALF_UP,
        Emin=-999999,
        Emax=999999,
        capitals=1,
        clamp=0,
        flags=[],
        traps=[InvalidOperation, DivisionByZero, Overflow, Underflow],
    )


class ErroCalculo(ValueError):
    """Erro por campo/código; não inclui o valor financeiro informado."""

    def __init__(self, campo: str, codigo: str):
        self.campo, self.codigo = campo, codigo
        super().__init__(f"{campo}: {codigo}")


@dataclass(frozen=True, slots=True)
class ResultadoMensal:
    mes: int
    saldo_inicial: Decimal
    aporte: Decimal
    juros: Decimal
    saldo_final: Decimal


@dataclass(frozen=True, slots=True)
class ResultadoCalculo:
    prazo_meses: int
    taxa_mensal_percentual: Decimal
    total_investido: Decimal
    total_juros: Decimal
    montante: Decimal
    serie: tuple[ResultadoMensal, ...]


def _validar_decimal(valor: Decimal, campo: str) -> None:
    if not isinstance(valor, Decimal):
        raise ErroCalculo(campo, "decimal_obrigatorio")
    if not valor.is_finite():
        raise ErroCalculo(campo, "numero_nao_finito")
    if valor < _ZERO:
        raise ErroCalculo(campo, "valor_negativo")
    if not valor.is_zero() and not -999999 <= valor.adjusted() <= 999999:
        raise ErroCalculo(campo, "limite_numerico")


def _validar_unidade(valor: str, permitidas: tuple[str, ...], campo: str) -> None:
    if not isinstance(valor, str) or valor not in permitidas:
        raise ErroCalculo(campo, "unidade_invalida")


def converter_taxa(
    taxa_percentual: Decimal, origem: PeriodicidadeTaxa, destino: PeriodicidadeTaxa
) -> Decimal:
    """Converte percentuais equivalentes: entrada/saída 12 significa 12%."""
    _validar_decimal(taxa_percentual, "taxa_percentual")
    _validar_unidade(origem, ("mensal", "anual"), "origem")
    _validar_unidade(destino, ("mensal", "anual"), "destino")
    if origem == destino or taxa_percentual.is_zero():
        return taxa_percentual
    try:
        with localcontext(_contexto()):
            base = _UM + taxa_percentual / _CEM
            expoente = _DOZE if origem == "mensal" else _UM / _DOZE
            return (base**expoente - _UM) * _CEM
    except DecimalException as exc:
        raise ErroCalculo("taxa_percentual", "limite_numerico") from exc


def arredondar_moeda(valor: Decimal) -> Decimal:
    """Centavos HALF_UP para consumo; nunca recapitalizar valores exibidos."""
    _validar_decimal(valor, "valor")
    try:
        with localcontext(_contexto()):
            return valor.quantize(Decimal("0.01"))
    except DecimalException as exc:
        raise ErroCalculo("valor", "limite_numerico") from exc


class MotorJurosCompostos:
    @staticmethod
    def calcular(
        *,
        valor_inicial: Decimal,
        aporte_mensal: Decimal,
        taxa_percentual: Decimal,
        periodicidade_taxa: PeriodicidadeTaxa,
        prazo: int,
        unidade_prazo: UnidadePrazo,
    ) -> ResultadoCalculo:
        for campo, valor in (
            ("valor_inicial", valor_inicial),
            ("aporte_mensal", aporte_mensal),
            ("taxa_percentual", taxa_percentual),
        ):
            _validar_decimal(valor, campo)
        if type(prazo) is not int or prazo <= 0:
            raise ErroCalculo("prazo", "prazo_invalido")
        _validar_unidade(periodicidade_taxa, ("mensal", "anual"), "periodicidade_taxa")
        _validar_unidade(unidade_prazo, ("meses", "anos"), "unidade_prazo")
        meses = prazo * 12 if unidade_prazo == "anos" else prazo
        try:
            with localcontext(_contexto()):
                taxa = converter_taxa(taxa_percentual, periodicidade_taxa, "mensal")
                fracao = taxa / _CEM
                saldo = valor_inicial
                serie = []
                for mes in range(1, meses + 1):
                    juros = saldo * fracao
                    saldo_final = saldo + juros + aporte_mensal
                    serie.append(ResultadoMensal(mes, saldo, aporte_mensal, juros, saldo_final))
                    saldo = saldo_final
                investido = valor_inicial + aporte_mensal * meses
                return ResultadoCalculo(
                    meses, taxa, investido, saldo - investido, saldo, tuple(serie)
                )
        except DecimalException as exc:
            raise ErroCalculo("calculo", "limite_numerico") from exc
