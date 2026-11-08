"""SPEC-001-R08: sessão ausente ou inválida é recusada antes da validação do corpo.

Desde a dependência CurrentUser, o cliente não autenticado recebe 401 e não 422,
sem conhecer o formato esperado do recurso protegido.
"""

import pytest

EXPENSES = "/api/v1/auth/financial/expenses"


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer token-invalido"}])
def test_SPEC_001_R08_sem_sessao_valida_recebe_401_mesmo_com_corpo_invalido(client, headers):
    """Cláusulas: SPEC-001-R08."""
    response = client.post(EXPENSES, json={"amount": "x"}, headers=headers)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert "amount" not in response.text
