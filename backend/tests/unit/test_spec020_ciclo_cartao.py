"""SPEC-020 (OPEN-12): ciclo da fatura e parcelamento no domínio puro, sem banco."""

from datetime import date
from decimal import Decimal

import pytest

from app.domain.cartao import (
    competencia_da_fatura,
    dia_de_fechamento,
    dividir_parcelas,
    somar_meses,
)


@pytest.mark.parametrize(
    ("ano", "mes", "configurado", "esperado"),
    [(2026, 3, 10, 10), (2026, 2, 31, 28), (2024, 2, 30, 29), (2026, 4, 31, 30)],
)
def test_SPEC_020_R03_fechamento_em_dia_inexistente_usa_ultimo_dia(ano, mes, configurado, esperado):
    """Cláusulas: SPEC-020-R03 — fechamento 29 a 31 vira o último dia do mês."""
    assert dia_de_fechamento(ano, mes, configurado) == esperado


@pytest.mark.parametrize(
    ("base", "meses", "esperado"),
    [
        (date(2026, 1, 31), 1, date(2026, 2, 28)),
        (date(2026, 11, 15), 3, date(2027, 2, 15)),
        (date(2024, 1, 31), 1, date(2024, 2, 29)),
        (date(2026, 5, 10), 0, date(2026, 5, 10)),
    ],
)
def test_SPEC_020_R03_somar_meses_preserva_dia_ou_usa_ultimo(base, meses, esperado):
    """Cláusulas: SPEC-020-R03."""
    assert somar_meses(base, meses) == esperado


@pytest.mark.parametrize(
    ("compra", "fechamento", "fatura"),
    [
        (date(2026, 3, 10), 10, date(2026, 3, 1)),  # no dia do fechamento: fatura do mês
        (date(2026, 3, 11), 10, date(2026, 4, 1)),  # depois do fechamento: próxima fatura
        (date(2026, 12, 20), 10, date(2027, 1, 1)),  # virada de ano
        (date(2026, 2, 28), 31, date(2026, 2, 1)),  # fechamento 31 em fevereiro = dia 28
    ],
)
def test_SPEC_020_R03_compra_entra_na_fatura_do_ciclo(compra, fechamento, fatura):
    """Cláusulas: SPEC-020-R03 — soma no ciclo da fatura atual."""
    assert competencia_da_fatura(compra, fechamento) == fatura


def test_SPEC_020_R03_parcelas_somam_o_total_e_residuo_fica_na_primeira():
    """Cláusulas: SPEC-020-R03 — 100,00 em 3x = 33,34 + 33,33 + 33,33."""
    parcelas = dividir_parcelas(Decimal("100.00"), 3)
    assert parcelas == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    assert sum(parcelas) == Decimal("100.00")
    assert all(isinstance(valor, Decimal) for valor in parcelas)


@pytest.mark.parametrize(
    ("total", "quantidade"),
    [
        (Decimal("100.00"), 0),
        (Decimal("100.00"), 49),
        (Decimal("0"), 2),
        (Decimal("-10.00"), 2),
        (Decimal("10.001"), 2),
        (Decimal("0.01"), 2),
    ],
)
def test_SPEC_020_R02_parcelamento_invalido_e_recusado(total, quantidade):
    """Cláusulas: SPEC-020-R02 — fora de 1–48, sem centavos inteiros ou parcela zero."""
    with pytest.raises(ValueError):
        dividir_parcelas(total, quantidade)
