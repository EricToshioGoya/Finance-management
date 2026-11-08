"""Intervalo de datas suportado e parsing de competência (regras puras, sem I/O)."""

from datetime import date

# Datas de lançamentos, competências e períodos ficam neste intervalo; fora dele a
# aritmética de meses (parcelas, ciclos, séries) pode estourar o calendário.
DATA_MINIMA = date(1900, 1, 1)
DATA_MAXIMA = date(2100, 12, 31)
# Períodos consultados de uma vez (dashboards, gastos por categoria e exportações).
MAXIMO_COMPETENCIAS = 120


def data_suportada(valor: date) -> bool:
    return DATA_MINIMA <= valor <= DATA_MAXIMA


def competencia(texto: str) -> date:
    """`AAAA-MM` → primeiro dia do mês; ValueError se inválida ou fora do intervalo."""
    inicio = date.fromisoformat(f"{texto}-01")
    if inicio.strftime("%Y-%m") != texto or not data_suportada(inicio):
        raise ValueError("competência inválida")
    return inicio


def competencias_no_periodo(inicio: date, fim: date) -> int:
    """Quantidade de competências entre os meses de `inicio` e `fim`, inclusive."""
    return (fim.year - inicio.year) * 12 + fim.month - inicio.month + 1
