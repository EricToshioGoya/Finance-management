"""SPEC-035 (catálogo educativo) e SPEC-001 (normalização de e-mail) no domínio puro."""

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.domain.education import ARTICLES, CATALOG_VERSION, get_article, search_articles
from app.domain.identity import User, normalize_email


def test_SPEC_035_R03_verbete_existe_nos_dois_idiomas():
    """Cláusulas: SPEC-035-R03."""
    pt = get_article("sharpe", "pt")
    en = get_article("sharpe", "en")
    assert (pt["title"], pt["language"]) == ("Índice de Sharpe", "pt")
    assert (en["title"], en["language"]) == ("Sharpe ratio", "en")
    assert pt["version"] == en["version"] == CATALOG_VERSION
    assert get_article("inexistente", "pt") is None


def test_SPEC_035_R05_busca_por_termo_ordena_por_relevancia():
    """Cláusulas: SPEC-035-R05 — "juros" casa no título de dois verbetes."""
    keys = [item["key"] for item in search_articles("juros", "pt", None)]
    assert keys == ["compound-interest", "interest-rate"]


def test_SPEC_035_R05_busca_ignora_acentos_e_maiusculas():
    """Cláusulas: SPEC-035-R05."""
    keys = [item["key"] for item in search_articles("  PATRIMONIO ", "pt", None)]
    assert keys[0] == "net-worth"


def test_SPEC_035_R04_sugestao_sem_termo_varia_conforme_perfil():
    """Cláusulas: SPEC-035-R04 — perfil arrojado prioriza nível 2; conservador, nível 0."""
    arrojado = [item["key"] for item in search_articles("", "pt", "arrojado")]
    conservador = [item["key"] for item in search_articles("", "pt", None)]
    assert arrojado[:2] == ["sharpe", "volatility"]
    assert conservador[0] == "cdi"
    assert len(arrojado) == len(ARTICLES)


def test_SPEC_035_R02_termo_longo_demais_e_recusado():
    """Cláusulas: SPEC-035-R02."""
    with pytest.raises(ValueError, match="search_term_too_long"):
        search_articles("x" * 101, "pt", None)


def test_SPEC_001_R02_email_normalizado_para_comparar_duplicidade():
    """Cláusulas: SPEC-001-R02 — o mesmo e-mail com caixa e espaços diferentes é igual."""
    assert normalize_email("  Ana@Example.COM ") == normalize_email("ana@example.com")
    assert normalize_email("Ana@Example.COM") == "ana@example.com"


def test_SPEC_001_R01_usuario_novo_e_comum_e_imutavel():
    """Cláusulas: SPEC-001-R01 — papel padrão "usuario" e e-mail não verificado."""
    user = User(id=uuid4(), name="Ana", email="ana@example.com")
    assert (user.role, user.email_verified, user.investor_profile) == ("usuario", False, None)
    with pytest.raises(FrozenInstanceError):
        user.role = "administrador"
