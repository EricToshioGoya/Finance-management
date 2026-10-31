"""SPEC-002-R01 a R08 / CA-001 a CA-008 / INV-001 a INV-006.

Referências fechadas usam 80 dígitos e fórmula de anuidade, sem reutilizar
conversão ou recorrência do motor. Nenhuma fixture de banco é solicitada.
"""

import ast
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from decimal import ROUND_DOWN, ROUND_FLOOR, Context, Decimal, Inexact, localcontext
from pathlib import Path

import pytest

from app.domain.juros_compostos import (
    ErroCalculo,
    MotorJurosCompostos,
    arredondar_moeda,
    converter_taxa,
)

D = Decimal


def calcular(**overrides):
    params = dict(
        valor_inicial=D("1000"),
        aporte_mensal=D("0"),
        taxa_percentual=D("12"),
        periodicidade_taxa="anual",
        prazo=12,
        unidade_prazo="meses",
    )
    return MotorJurosCompostos.calcular(**(params | overrides))


def proximo(real, esperado):
    with localcontext(Context(prec=80)):
        assert abs(real - esperado) <= max(D("1e-40"), abs(esperado) * D("1e-40"))


def test_SPEC_002_R01_referencia_anual_e_taxa_mensal():
    result = calcular()
    assert arredondar_moeda(result.montante) == D("1120.00")
    proximo(result.montante, D("1120"))
    assert abs(result.taxa_mensal_percentual - D("0.9488792935")) < D("1e-10")
    assert result.taxa_mensal_percentual != D("1")


def test_SPEC_002_R02_aporte_no_fim_nao_rende_no_mes_de_entrada():
    result = calcular(
        valor_inicial=D("0"),
        aporte_mensal=D("100"),
        taxa_percentual=D("1"),
        periodicidade_taxa="mensal",
        prazo=2,
    )
    assert result.serie[0].saldo_inicial == result.serie[0].juros == D("0")
    assert [m.saldo_final for m in result.serie] == [D("100"), D("201")]
    assert result.total_investido == D("200") and result.total_juros == D("1")


@pytest.mark.parametrize(
    "inicial,aporte,montante",
    [("100", "10", "120"), ("0", "0", "0"), ("100", "0", "100"), ("0", "10", "20")],
)
def test_SPEC_002_R03_taxa_zero_e_valores_zero(inicial, aporte, montante):
    result = calcular(
        valor_inicial=D(inicial), aporte_mensal=D(aporte), taxa_percentual=D("0"), prazo=2
    )
    assert result.total_investido == result.montante == D(montante)
    assert result.total_juros == 0
    assert all(m.juros == 0 for m in result.serie)


@pytest.mark.parametrize("campo", ["valor_inicial", "aporte_mensal", "taxa_percentual"])
@pytest.mark.parametrize(
    "valor,codigo",
    [
        (D("-0.01"), "valor_negativo"),
        (D("NaN"), "numero_nao_finito"),
        (D("sNaN"), "numero_nao_finito"),
        (D("Infinity"), "numero_nao_finito"),
        (D("-Infinity"), "numero_nao_finito"),
        (1.1, "decimal_obrigatorio"),
        ("1.1", "decimal_obrigatorio"),
        (True, "decimal_obrigatorio"),
        (None, "decimal_obrigatorio"),
    ],
)
def test_SPEC_002_R04_valores_invalidos_por_campo(campo, valor, codigo):
    with pytest.raises(ErroCalculo) as error:
        calcular(**{campo: valor})
    assert (error.value.campo, error.value.codigo) == (campo, codigo)
    assert str(error.value) == f"{campo}: {codigo}"


@pytest.mark.parametrize("prazo", [0, -1, 1.5, D("1"), True, False, "12", None])
def test_SPEC_002_R04_prazo_inteiro_positivo_estrito(prazo):
    with pytest.raises(ErroCalculo, match="prazo: prazo_invalido"):
        calcular(prazo=prazo)


@pytest.mark.parametrize("campo", ["periodicidade_taxa", "unidade_prazo"])
@pytest.mark.parametrize("valor", ["dia", "", None, 12, [], True])
def test_SPEC_002_R04_unidades_invalidas_sem_typeerror(campo, valor):
    with pytest.raises(ErroCalculo, match=f"{campo}: unidade_invalida"):
        calcular(**{campo: valor})


def test_SPEC_002_R05_ano_e_doze_meses_identicos():
    assert calcular(prazo=1, unidade_prazo="anos") == calcular(prazo=12)
    assert calcular(prazo=5, unidade_prazo="anos") == calcular(prazo=60)


@pytest.mark.parametrize("mensal", ["0", "0.00001", "1", "5", "12.34"])
def test_SPEC_002_R06_conversao_composta_e_ida_volta(mensal):
    mensal = D(mensal)
    anual = converter_taxa(mensal, "mensal", "anual")
    with localcontext(Context(prec=80)):
        esperado = ((1 + mensal / 100) ** 12 - 1) * 100
    proximo(anual, esperado)
    proximo(converter_taxa(anual, "anual", "mensal"), mensal)
    assert converter_taxa(mensal, "mensal", "mensal") == mensal
    if mensal == 1:
        assert abs(anual - D("12.6825030132")) < D("1e-10")
        assert anual != D("12")


@pytest.mark.parametrize(
    "inicial,aporte,taxa,prazo",
    [
        ("1000", "100", "12", 360),
        ("0", "100", "1", 2),
        ("1234.56", "78.90", "2.5", 120),
        ("0.01", "0.01", "0.00001", 600),
        ("999999999999.99", "1000", "5", 12),
    ],
)
def test_SPEC_002_R07_serie_e_resumo_contra_formula_independente(inicial, aporte, taxa, prazo):
    result = calcular(
        valor_inicial=D(inicial), aporte_mensal=D(aporte), taxa_percentual=D(taxa), prazo=prazo
    )
    assert len(result.serie) == result.prazo_meses == prazo
    with localcontext(Context(prec=80)):
        i = (1 + D(taxa) / 100) ** (D(1) / D(12)) - 1
        for mes, row in enumerate(result.serie, 1):
            fator = (1 + i) ** mes
            esperado = D(inicial) * fator + D(aporte) * (fator - 1) / i
            proximo(row.saldo_final, esperado)
            assert row.mes == mes and row.aporte == D(aporte)
            proximo(row.juros, row.saldo_inicial * i)
            proximo(row.saldo_final, row.saldo_inicial + row.juros + row.aporte)
            if mes > 1:
                assert row.saldo_inicial == result.serie[mes - 2].saldo_final
        assert result.total_investido == D(inicial) + D(aporte) * prazo
        assert result.montante == result.serie[-1].saldo_final
        proximo(result.total_juros, result.montante - result.total_investido)
        proximo(result.total_juros, sum(m.juros for m in result.serie))


def test_SPEC_002_R07_nao_arredonda_saldo_mensal_a_centavos():
    result = calcular(
        valor_inicial=D("0.01"),
        aporte_mensal=D("0"),
        taxa_percentual=D("1"),
        periodicidade_taxa="mensal",
        prazo=120,
    )
    with localcontext(Context(prec=80)):
        proximo(result.montante, D("0.01") * D("1.01") ** 120)
    assert arredondar_moeda(result.montante) == D("0.03")


def test_SPEC_002_R08_determinismo_imutabilidade_contexto_e_flags():
    expected = calcular()
    with localcontext(Context(prec=3, rounding=ROUND_DOWN)) as caller:
        caller.traps[Inexact] = True
        flags = caller.flags.copy()
        assert calcular() == expected
        assert converter_taxa(D("1"), "mensal", "anual") == D("12.682503013196972066120100")
        assert arredondar_moeda(D("1.005")) == D("1.01")
        assert caller.prec == 3 and caller.rounding == ROUND_DOWN
        assert caller.traps[Inexact] and caller.flags == flags
    with pytest.raises(FrozenInstanceError):
        expected.montante = D("0")
    with pytest.raises(FrozenInstanceError):
        expected.serie[0].saldo_final = D("0")
    assert isinstance(expected.serie, tuple)


def test_SPEC_002_R08_contextos_concorrentes_nao_alteram_resultado():
    expected = calcular()

    def execute(precision):
        with localcontext(Context(prec=precision, rounding=ROUND_FLOOR)):
            return calcular()

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(execute, [2, 6, 12, 28])) == [expected] * 4


def test_SPEC_002_R08_importa_e_executa_em_python_isolado_sem_terceiros():
    backend = Path(__file__).resolve().parents[2]
    script = f"""import sys
sys.path.insert(0,{str(backend)!r})
from decimal import Decimal
from app.domain.juros_compostos import MotorJurosCompostos
r=MotorJurosCompostos.calcular(
    valor_inicial=Decimal('100'), aporte_mensal=Decimal('10'),
    taxa_percentual=Decimal('0'), periodicidade_taxa='mensal',
    prazo=2, unidade_prazo='meses')
assert r.montante == Decimal('120')
for module in ('fastapi','sqlalchemy','psycopg','httpx','app.main','app.infrastructure.models'):
    assert module not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", script], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    domain = backend / "app/domain/juros_compostos.py"
    imports = ast.walk(ast.parse(domain.read_text()))
    for node in imports:
        if isinstance(node, ast.Import):
            assert all(n.name in {"decimal", "dataclasses", "typing"} for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.module in {"decimal", "dataclasses", "typing"}
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float)


@pytest.mark.parametrize("origem,destino", [("dia", "mensal"), ("anual", "dia"), ([], None)])
def test_SPEC_002_R04_conversor_rejeita_unidades_invalidas(origem, destino):
    with pytest.raises(ErroCalculo, match="unidade_invalida"):
        converter_taxa(D("1"), origem, destino)


@pytest.mark.parametrize("valor", [D("-1"), D("NaN"), 1.1])
def test_SPEC_002_R04_helpers_validam_decimal(valor):
    for operation in [
        lambda: converter_taxa(valor, "anual", "mensal"),
        lambda: arredondar_moeda(valor),
    ]:
        with pytest.raises(ErroCalculo):
            operation()


def test_SPEC_002_R04_limites_tecnicos_nao_vazam_excecao_decimal():
    for valor in [D("1e1000000"), D("1e-1000000")]:
        with pytest.raises(ErroCalculo, match="valor_inicial: limite_numerico"):
            calcular(valor_inicial=valor)
    with pytest.raises(ErroCalculo, match="taxa_percentual: limite_numerico"):
        converter_taxa(D("1e999999"), "mensal", "anual")
    with pytest.raises(ErroCalculo, match="calculo: limite_numerico"):
        calcular(
            valor_inicial=D("9e999999"),
            taxa_percentual=D("1000"),
            periodicidade_taxa="mensal",
            prazo=1,
        )
    with pytest.raises(ErroCalculo, match="valor: limite_numerico"):
        arredondar_moeda(D("1e50"))


def test_SPEC_002_R03_zero_assinado_valido_e_arredondamento_comercial():
    assert (
        calcular(valor_inicial=D("-0"), aporte_mensal=D("-0"), taxa_percentual=D("-0")).montante
        == 0
    )
    assert converter_taxa(D("0"), "anual", "mensal") == 0
    assert arredondar_moeda(D("1.0049")) == D("1.00")
    assert arredondar_moeda(D("1.005")) == D("1.01")
