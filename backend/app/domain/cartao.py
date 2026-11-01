"""Ciclo da fatura e parcelamento do cartão (OPEN-12, aprovada em 2026-10-31); sem I/O (ADR-002).

- Compra com data até o dia de fechamento entra na fatura que fecha naquele mês; depois do
  fechamento, na fatura seguinte. Fechamento em dia inexistente (29 a 31) usa o último dia.
- Compra parcelada gera N parcelas mensais; o resíduo de centavos fica na 1ª parcela.
"""

import calendar
from datetime import date
from decimal import ROUND_DOWN, Decimal

CENTAVO = Decimal("0.01")
MAX_PARCELAS = 48


def dia_de_fechamento(ano: int, mes: int, dia_configurado: int) -> int:
    return min(dia_configurado, calendar.monthrange(ano, mes)[1])


def somar_meses(base: date, meses: int) -> date:
    """Mesmo dia `meses` depois; dia inexistente no mês de destino vira o último dia."""
    indice = base.year * 12 + base.month - 1 + meses
    ano, mes = divmod(indice, 12)
    mes += 1
    return date(ano, mes, min(base.day, calendar.monthrange(ano, mes)[1]))


def competencia_da_fatura(data_compra: date, dia_configurado: int) -> date:
    """Primeiro dia do mês em que fecha a fatura que recebe a compra."""
    fechamento = dia_de_fechamento(data_compra.year, data_compra.month, dia_configurado)
    mes_da_compra = data_compra.replace(day=1)
    return mes_da_compra if data_compra.day <= fechamento else somar_meses(mes_da_compra, 1)


def dividir_parcelas(total: Decimal, quantidade: int) -> list[Decimal]:
    """Divide em parcelas de centavos inteiros; a soma é exatamente `total`."""
    if quantidade < 1 or quantidade > MAX_PARCELAS:
        raise ValueError("Quantidade de parcelas fora do intervalo 1–48")
    if total <= 0 or total != total.quantize(CENTAVO):
        raise ValueError("Total deve ser positivo e em centavos")
    base = (total / quantidade).quantize(CENTAVO, rounding=ROUND_DOWN)
    if base <= 0:
        raise ValueError("Cada parcela deve ter ao menos um centavo")
    return [total - base * (quantidade - 1), *([base] * (quantidade - 1))]
