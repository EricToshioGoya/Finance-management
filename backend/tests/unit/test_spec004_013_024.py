from decimal import Decimal

import pytest

from app.domain.financeiro import aliquota_ir_renda_fixa, aporte_necessario, resultado_liquido
from app.domain.juros_compostos import ErroCalculo


@pytest.mark.parametrize(
    ("months", "expected"),
    [(1, "22.5"), (6, "22.5"), (7, "20"), (12, "20"), (13, "17.5"), (25, "15")],
)
def test_regressive_income_tax_table(months, expected):
    assert aliquota_ir_renda_fixa(months, "cdb") == Decimal(expected)


def test_poupanca_has_no_income_tax_and_net_projection_uses_only_gain():
    assert aliquota_ir_renda_fixa(12, "poupanca") == Decimal("0")
    tax, net = resultado_liquido(Decimal("1120"), Decimal("1000"), 12, "cdb")
    assert tax == Decimal("24")
    assert net == Decimal("1096")


def test_tax_rejects_unknown_product_and_negative_result():
    with pytest.raises(ErroCalculo):
        aliquota_ir_renda_fixa(12, "crypto")
    with pytest.raises(ErroCalculo):
        resultado_liquido(Decimal("99"), Decimal("100"), 12, "cdb")


def test_target_contribution_supports_zero_rate_and_already_reached_target():
    assert aporte_necessario(
        alvo=Decimal("120"), inicial=Decimal("0"), taxa_percentual=Decimal("0"), prazo_meses=12
    ) == Decimal("10")
    assert aporte_necessario(
        alvo=Decimal("100"), inicial=Decimal("200"), taxa_percentual=Decimal("12"), prazo_meses=12
    ) == Decimal("0")


def test_target_contribution_rejects_invalid_goal_inputs():
    with pytest.raises(ErroCalculo):
        aporte_necessario(
            alvo=Decimal("0"), inicial=Decimal("0"), taxa_percentual=Decimal("0"), prazo_meses=12
        )
