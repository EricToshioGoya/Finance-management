"""SPEC-060-R07 a R09 (RNF-12): request id, erro não tratado e logs sem segredo."""

import json
import logging

from fastapi.testclient import TestClient

from app.infrastructure.observabilidade import LOGGER, JsonFormatter

AUTH = "/api/v1/auth"
SENHA = "SenhaSecreta123"


class Captura(logging.Handler):
    """Coleta as linhas JSON que o formatter de produção emitiria."""

    def __init__(self):
        super().__init__()
        self.setFormatter(JsonFormatter())
        self.linhas: list[dict] = []

    def emit(self, record):
        self.linhas.append(json.loads(self.format(record)))


def capturar():
    handler = Captura()
    logging.getLogger(LOGGER).addHandler(handler)
    return handler


def soltar(handler):
    logging.getLogger(LOGGER).removeHandler(handler)


def test_SPEC_060_R07_toda_resposta_traz_request_id_e_log_estruturado(client):
    """Cláusulas: SPEC-060-R07."""
    handler = capturar()
    try:
        gerado = client.get("/api/v1/health")
        propagado = client.get("/api/v1/health", headers={"X-Request-ID": "cliente-abc-123"})
        invalido = client.get("/api/v1/health", headers={"X-Request-ID": "x y\nz"})
    finally:
        soltar(handler)
    assert len(gerado.headers["X-Request-ID"]) == 32
    assert propagado.headers["X-Request-ID"] == "cliente-abc-123"
    assert invalido.headers["X-Request-ID"] != "x y\nz"
    acesso = [linha for linha in handler.linhas if linha["message"] == "request"]
    assert {linha["request_id"] for linha in acesso} >= {"cliente-abc-123"}
    registro = next(linha for linha in acesso if linha["request_id"] == "cliente-abc-123")
    assert registro["method"] == "GET"
    assert registro["path"] == "/api/v1/health"
    assert registro["status"] == 200
    assert registro["level"] == "INFO"
    assert isinstance(registro["duration_ms"], float)


def test_SPEC_060_R07_recusa_de_protecao_tambem_e_registrada(app):
    """Cláusulas: SPEC-060-R07 — o pedido HTTP sem TLS recusado ainda recebe identificador."""
    handler = capturar()
    try:
        with TestClient(app, base_url="http://localhost:8443") as inseguro:
            response = inseguro.get("/api/v1/health")
    finally:
        soltar(handler)
    assert response.status_code == 400
    assert response.headers["X-Request-ID"]
    assert any(linha.get("status") == 400 for linha in handler.linhas)


def test_SPEC_060_R08_erro_nao_tratado_vira_500_generico_e_e_registrado(app, monkeypatch):
    """Cláusulas: SPEC-060-R08."""

    def falhar(*_args, **_kwargs):
        raise RuntimeError("falha interna com detalhe que não pode vazar")

    monkeypatch.setattr("app.application.auth.AuthService.register", falhar)
    handler = capturar()
    try:
        with TestClient(
            app, base_url="https://localhost:8443", raise_server_exceptions=False
        ) as instancia:
            response = instancia.post(
                f"{AUTH}/register",
                json={"name": "Ana", "email": "erro@example.com", "password": SENHA},
            )
    finally:
        soltar(handler)
    assert response.status_code == 500
    corpo = response.json()
    assert corpo == {"detail": "internal_error", "request_id": response.headers["X-Request-ID"]}
    assert "detalhe" not in response.text
    erro = next(linha for linha in handler.linhas if linha["message"] == "unhandled_error")
    assert erro["level"] == "ERROR"
    assert erro["error_type"] == "RuntimeError"
    assert erro["request_id"] == corpo["request_id"]
    assert erro["path"] == f"{AUTH}/register"
    assert "RuntimeError" in erro["stack"]


def test_SPEC_060_R09_logs_nao_contem_senha_token_nem_email(client):
    """Cláusulas: SPEC-060-R09 (C-06, RB-23)."""
    handler = capturar()
    try:
        client.post(
            f"{AUTH}/register",
            json={"name": "Ana", "email": "segredo@example.com", "password": SENHA},
        )
        login = client.post(
            f"{AUTH}/login", json={"email": "segredo@example.com", "password": SENHA}
        )
        token = login.json()["access_token"]
        client.get(
            f"{AUTH}/me?email=segredo@example.com", headers={"Authorization": f"Bearer {token}"}
        )
    finally:
        soltar(handler)
    texto = json.dumps(handler.linhas, ensure_ascii=False)
    assert handler.linhas
    assert SENHA not in texto
    assert token not in texto
    assert "segredo@example.com" not in texto
    assert "Authorization" not in texto
