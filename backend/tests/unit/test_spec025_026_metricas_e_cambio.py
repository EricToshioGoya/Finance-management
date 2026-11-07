"""SPEC-025 (métricas históricas) e SPEC-026 (projeção cambial) no domínio puro, sem banco."""

from datetime import date
from decimal import Decimal

import pytest

from app.domain.foreign_currency import calcular_projecao_moeda_estrangeira
from app.domain.juros_compostos import ErroCalculo
from app.domain.market_metrics import MetricInputError, calculate_historical_metrics

D1, D2, D3 = date(2026, 3, 2), date(2026, 3, 3), date(2026, 3, 4)


def test_SPEC_025_R03_R04_volatilidade_e_sharpe_contra_referencia_independente():
    """Cláusulas: SPEC-025-R03, SPEC-025-R04.

    Preços 100 → 110 → 99: retornos +0,10 e −0,10, média 0, variância amostral 0,02.
    Volatilidade anualizada = √(0,02 × 252) = √5,04 = 2,2450. Com Selic 0, Sharpe = 0.
    """
    result = calculate_historical_metrics(
        [(D1, Decimal("100")), (D2, Decimal("110")), (D3, Decimal("99"))], Decimal("0")
    )
    assert result["volatility_annualized"] == Decimal("2.2450")
    assert result["sharpe"] == Decimal("0.0000")
    assert result["status"] == "available"
    assert (result["period_start"], result["period_end"], result["observations"]) == (D1, D3, 3)


def test_SPEC_025_R06_ressalva_historica_sempre_presente():
    """Cláusulas: SPEC-025-R06."""
    result = calculate_historical_metrics(
        [(D1, Decimal("10")), (D2, Decimal("11")), (D3, Decimal("12"))], Decimal("10")
    )
    assert "não garantem" in result["disclaimer"]


def test_SPEC_025_R04_volatilidade_zero_nao_divide_por_zero():
    """Cláusulas: SPEC-025-R04 — Sharpe indisponível quando não há oscilação."""
    result = calculate_historical_metrics(
        [(D1, Decimal("50")), (D2, Decimal("50")), (D3, Decimal("50"))], Decimal("10")
    )
    assert result["sharpe"] is None
    assert result["status"] == "zero_volatility"
    assert result["volatility_annualized"] == Decimal("0.0000")


@pytest.mark.parametrize(
    ("observacoes", "erro"),
    [
        ([(D1, Decimal("10")), (D2, Decimal("11"))], "market_history_insufficient"),
        ([(D1, Decimal("0")), (D2, Decimal("11")), (D3, Decimal("12"))], "market_history_invalid"),
        (
            [(D1, Decimal("10")), (D2, Decimal("-1")), (D3, Decimal("12"))],
            "market_history_incompatible",
        ),
        (
            [(D1, Decimal("10")), (date(2026, 3, 9), Decimal("11")), (date(2026, 3, 10), 12)],
            "market_history_incompatible",
        ),
    ],
)
def test_SPEC_025_R02_historico_insuficiente_ou_incompativel_e_recusado(observacoes, erro):
    """Cláusulas: SPEC-025-R02 — menos de 3 pontos, preço não positivo ou lacuna > 3 dias."""
    with pytest.raises(MetricInputError, match=erro):
        calculate_historical_metrics(observacoes, Decimal("10"))


def test_SPEC_026_R05_R07_projecao_na_moeda_original_e_em_reais():
    """Cláusulas: SPEC-026-R05, SPEC-026-R07.

    Referência: US$ 1.000 sem rendimento por 12 meses; PTAX 5,00 com variação de +10% a.a.
    → cotação projetada 5,50 e R$ 5.500,00.
    """
    result = calcular_projecao_moeda_estrangeira(
        initial_amount=Decimal("1000"),
        monthly_contribution=Decimal("0"),
        asset_annual_return=Decimal("0"),
        expected_exchange_annual_change=Decimal("10"),
        term_months=12,
        exchange_rate_to_brl=Decimal("5.00"),
    )
    assert result["final_amount_original"] == Decimal("1000")
    assert result["projected_exchange_rate_to_brl"] == Decimal("5.5")
    assert result["final_amount_brl"].quantize(Decimal("0.01")) == Decimal("5500.00")
    assert result["exchange_rate_to_brl"] == Decimal("5.00")


def test_SPEC_026_R05_rendimento_do_ativo_usa_equivalencia_composta():
    """Cláusulas: SPEC-026-R05 — 10% a.a. em 12 meses = 1.100 (C-04), câmbio estável."""
    result = calcular_projecao_moeda_estrangeira(
        initial_amount=Decimal("1000"),
        monthly_contribution=Decimal("0"),
        asset_annual_return=Decimal("10"),
        expected_exchange_annual_change=Decimal("0"),
        term_months=12,
        exchange_rate_to_brl=Decimal("1"),
    )
    assert result["final_amount_original"].quantize(Decimal("0.01")) == Decimal("1100.00")


@pytest.mark.parametrize(
    "ajuste",
    [
        {"initial_amount": Decimal("-1")},
        {"monthly_contribution": Decimal("-1")},
        {"term_months": 0},
        {"exchange_rate_to_brl": Decimal("0")},
        {"expected_exchange_annual_change": Decimal("-100")},
    ],
)
def test_SPEC_026_R02_entrada_invalida_e_recusada(ajuste):
    """Cláusulas: SPEC-026-R02."""
    entrada = {
        "initial_amount": Decimal("1000"),
        "monthly_contribution": Decimal("0"),
        "asset_annual_return": Decimal("5"),
        "expected_exchange_annual_change": Decimal("0"),
        "term_months": 12,
        "exchange_rate_to_brl": Decimal("5"),
        **ajuste,
    }
    with pytest.raises(ErroCalculo):
        calcular_projecao_moeda_estrangeira(**entrada)
