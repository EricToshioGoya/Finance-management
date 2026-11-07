"""RNF-24 sob concorrência: dois envios simultâneos com a mesma Idempotency-Key.

Caso de referência do material de qualidade (checkout duplicado por clique múltiplo):
um reenvio paralelo não pode duplicar o lançamento nem receber erro no lugar da resposta.
A barreira força as duas requisições a passarem pela verificação de existência antes
de qualquer gravação, reproduzindo a corrida de forma determinística.
"""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from clause_support import FIN, account, verified_user

from app.infrastructure.security import Security

CASOS = {
    "despesa": (
        "expenses",
        {
            "description": "Mercado",
            "amount": "30.00",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-03-10",
        },
    ),
    "renda_recorrente": ("recurring-incomes", {"description": "Salário", "amount": "100.00"}),
    "renda_pontual": (
        "one-time-incomes",
        {"description": "Freela", "amount": "100.00", "occurred_on": "2026-01-15"},
    ),
    "bonus": (
        "bonuses",
        {
            "description": "PLR",
            "amount": "120.00",
            "periodicity": "annual",
            "reference_month": 6,
            "starts_on": "2026-01-01",
        },
    ),
}


def envio_simultaneo(client, monkeypatch, headers, recurso, corpo):
    """Envia duas criações em paralelo com a mesma chave; ambas cifram a descrição juntas."""
    original = Security.encrypt
    barreira = Barrier(2)

    def sincronizar(self, value):
        barreira.wait(timeout=10)
        return original(self, value)

    monkeypatch.setattr(Security, "encrypt", sincronizar)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(
                pool.map(
                    lambda _: client.post(
                        f"{FIN}/{recurso}",
                        headers={**headers, "Idempotency-Key": "clique-duplo"},
                        json=corpo,
                    ),
                    range(2),
                )
            )
    finally:
        monkeypatch.setattr(Security, "encrypt", original)


@pytest.mark.parametrize("caso", list(CASOS))
def test_SPEC_059_R01_SPEC_056_R02_SPEC_057_R01_SPEC_058_R01_envio_paralelo_cria_um_registro(
    client, app, monkeypatch, caso
):
    """Cláusulas: SPEC-059-R01, SPEC-056-R02, SPEC-057-R01, SPEC-058-R01 (RNF-24, C-16)."""
    headers = verified_user(client, app, f"concorrencia-{caso}@example.com")
    recurso, corpo = CASOS[caso]
    if recurso == "expenses":
        corpo = {**corpo, "account_id": account(client, headers)}

    respostas = envio_simultaneo(client, monkeypatch, headers, recurso, corpo)

    assert [r.status_code for r in respostas] == [201, 201]
    assert respostas[0].json() == respostas[1].json()
    registros = client.get(f"{FIN}/{recurso}", headers=headers).json()
    assert [item["id"] for item in registros] == [respostas[0].json()["id"]]
