"""Regressão das correções da varredura de QA de 2026-11-03 (registro em docs/09-qualidade).

Cada teste cita a cláusula da Spec afetada (C-02); itens transversais citam o RNF.
Nenhum teste chama serviço externo real (C-17): servidores HTTP são locais e efêmeros.
"""

import asyncio
import datetime as dt
import http.server
import json
import logging
import ssl
import threading
import uuid
from decimal import Decimal

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.application.auth import AuthService
from app.application.webhooks import HttpWebhookDelivery
from app.infrastructure.models import ExpenseRecord
from app.infrastructure.runtime import (
    AdmissionControl,
    JsonFormatter,
    client_address,
    parse_trusted_proxies,
)
from tests.clause_support import FIN, account, card, set_indicator, verified_user

AUTH = "/api/v1/auth"


def key(headers):
    return {**headers, "Idempotency-Key": str(uuid.uuid4())}


def recurring_income(client, headers, account_id, amount, starts_on):
    response = client.post(
        f"{FIN}/recurring-incomes",
        headers=key(headers),
        json={
            "description": "Salário",
            "amount": amount,
            "account_id": account_id,
            "starts_on": starts_on,
        },
    )
    assert response.status_code == 201, response.text


# --------------------------------------------------------------------------- patrimônio
def test_SPEC_028_R03_SPEC_006_R05_SPEC_059_R06_recurring_expense_reduces_every_month(client, app):
    """Despesa recorrente é descontada em cada competência, como no resumo mensal."""
    headers = verified_user(client, app)
    account_id = account(client, headers, balance="10000.00")
    recurring_income(client, headers, account_id, "5000.00", "2026-01-05")
    response = client.post(
        f"{FIN}/expenses",
        headers=key(headers),
        json={
            "description": "Aluguel",
            "amount": "2000.00",
            "category_key": "standard:moradia",
            "occurred_on": "2026-01-05",
            "account_id": account_id,
            "recurring": True,
        },
    )
    assert response.status_code == 201
    one_off = client.post(
        f"{FIN}/expenses",
        headers=key(headers),
        json={
            "description": "Mercado",
            "amount": "300.00",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-03-10",
            "account_id": account_id,
        },
    )
    assert one_off.status_code == 201

    variations = sum(
        Decimal(
            client.get(
                f"{FIN}/balance-summary", headers=headers, params={"competence": f"2026-{m:02d}"}
            ).json()["balance_variation"]
        )
        for m in range(1, 12)
    )
    net_worth = client.get(
        f"{FIN}/net-worth", headers=headers, params={"as_of": "2026-11-15"}
    ).json()
    # 10000 + 11×5000 − 11×2000 − 300 = 42700, igual ao saldo inicial + soma das variações.
    assert Decimal(net_worth["net_worth"]) == Decimal("42700.00")
    assert Decimal(net_worth["net_worth"]) == Decimal("10000.00") + variations
    before_start = client.get(f"{FIN}/net-worth", headers=headers, params={"as_of": "2025-12-31"})
    assert Decimal(before_start.json()["net_worth"]) == Decimal("10000.00")


# --------------------------------------------------------------------------- períodos e datas
def test_SPEC_022_R02_R08_R12_dashboard_period_is_bounded(client, app):
    headers = verified_user(client, app)
    ok = client.get(
        f"{FIN}/dashboard", headers=headers, params={"start": "2017-01", "end": "2026-12"}
    )
    assert ok.status_code == 200 and len(ok.json()) == 120
    too_long = client.get(
        f"{FIN}/dashboard", headers=headers, params={"start": "2016-12", "end": "2026-12"}
    )
    assert too_long.status_code == 400 and too_long.json()["detail"] == "period_too_long"
    for start, end in (("1800-01", "1800-02"), ("9999-11", "9999-12"), ("2026-13", "2026-12")):
        response = client.get(
            f"{FIN}/dashboard", headers=headers, params={"start": start, "end": end}
        )
        assert response.status_code == 400, (start, end)
    spending = client.get(
        f"{FIN}/spending-by-category",
        headers=headers,
        params={"start": "2000-01", "end": "2026-12"},
    )
    assert spending.status_code == 400 and spending.json()["detail"] == "period_too_long"
    summary = client.get(
        f"{FIN}/balance-summary", headers=headers, params={"competence": "9999-12"}
    )
    assert summary.status_code == 400


def test_SPEC_019_R02_R04_export_rejects_out_of_range_periods(client, app):
    headers = verified_user(client, app)
    for fmt in ("csv", "pdf"):
        for params in ({"year": 0}, {"year": -5}, {"year": 10000}, {"month": "0000-01"}):
            response = client.get(f"{FIN}/exports/{fmt}", headers=headers, params=params)
            assert response.status_code == 400, (fmt, params)
        long_range = client.get(
            f"{FIN}/exports/{fmt}",
            headers=headers,
            params={"start": "2000-01-01", "end": "2026-12-31"},
        )
        assert long_range.json()["detail"] == "period_too_long"
        assert (
            client.get(f"{FIN}/exports/{fmt}", headers=headers, params={"year": 2026}).status_code
            == 200
        )


def test_SPEC_059_R02_R03_expense_dates_and_description_are_validated(client, app):
    headers = verified_user(client, app)
    card_id = card(client, headers)
    account_id = account(client, headers)
    base = {
        "description": "Compra",
        "amount": "10.00",
        "category_key": "standard:alimentacao",
        "occurred_on": "2026-03-10",
    }
    # Antes: 500 por estouro do calendário ao gerar parcelas após 9999-12.
    for occurred_on in ("9999-12-15", "0001-01-01", "1899-12-31", "2101-01-01"):
        response = client.post(
            f"{FIN}/expenses",
            headers=key(headers),
            json={**base, "occurred_on": occurred_on, "credit_card_id": card_id, "installments": 3},
        )
        assert response.status_code == 422, occurred_on
    edge = client.post(
        f"{FIN}/expenses",
        headers=key(headers),
        json={**base, "occurred_on": "2100-12-15", "credit_card_id": card_id, "installments": 3},
    )
    assert edge.status_code == 201
    blank = client.post(
        f"{FIN}/expenses",
        headers=key(headers),
        json={**base, "description": "   ", "account_id": account_id},
    )
    assert blank.status_code == 422
    created = client.post(
        f"{FIN}/expenses",
        headers=key(headers),
        json={**base, "description": "  Feira ", "account_id": account_id},
    ).json()
    assert created["description"] == "Feira"
    edited = client.patch(
        f"{FIN}/expenses/{created['id']}", headers=headers, json={"description": "  "}
    )
    assert edited.status_code == 422
    income = client.post(
        f"{FIN}/one-time-incomes",
        headers=key(headers),
        json={"description": "x", "amount": "1.00", "occurred_on": "0001-01-01"},
    )
    assert income.status_code == 422


def test_SPEC_059_R01_R02_concurrent_resend_returns_existing_expense(client, app, monkeypatch):
    """RNF-24: a corrida entre a checagem e o INSERT devolve o lançamento já gravado (sem 503)."""
    headers = verified_user(client, app)
    account_id = account(client, headers)
    idempotency_key = str(uuid.uuid4())
    original = AuthService.valid_expense_category
    competitor: dict[str, object] = {}

    def racing_category_check(self, user_id, category_key):
        # Outro pedido com a mesma chave grava entre a checagem de existência e o INSERT.
        if not competitor:
            competitor["done"] = True
            with app.state.sessions() as db:
                other = AuthService(db, self.settings, self.security, clock=self.clock)
                competitor["id"] = other.create_expense(
                    user_id,
                    {
                        "description": "Concorrente",
                        "amount": Decimal("12.00"),
                        "category_key": category_key,
                        "occurred_on": dt.date(2026, 3, 10),
                        "recurring": False,
                        "account_id": uuid.UUID(account_id),
                        "credit_card_id": None,
                        "installments": 1,
                    },
                    idempotency_key,
                )["id"]
        return original(self, user_id, category_key)

    monkeypatch.setattr(AuthService, "valid_expense_category", racing_category_check)
    response = client.post(
        f"{FIN}/expenses",
        headers={**headers, "Idempotency-Key": idempotency_key},
        json={
            "description": "Duplo clique",
            "amount": "12.00",
            "category_key": "standard:alimentacao",
            "occurred_on": "2026-03-10",
            "account_id": account_id,
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["id"] == str(competitor["id"])
    with app.state.sessions() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(ExpenseRecord)
                .where(ExpenseRecord.idempotency_key == idempotency_key)
            )
            == 1
        )


def test_SPEC_007_R02_unknown_indicator_is_404_and_missing_cache_is_503(client, app):
    headers = verified_user(client, app)
    assert client.get(f"{FIN}/indicators/selic' OR 1=1--", headers=headers).status_code == 404
    assert (
        client.get(f"{FIN}/indicators/0", headers=headers).json()["detail"] == "indicator_not_found"
    )
    missing = client.get(f"{FIN}/indicators/selic", headers=headers)
    assert missing.status_code == 503 and missing.json()["detail"] == "indicator_unavailable"
    set_indicator(app)
    assert client.get(f"{FIN}/indicators/selic", headers=headers).status_code == 200


# --------------------------------------------------------------------------- rate limit (RNF-13)
def test_SPEC_001_R07_rate_limit_covers_put_and_every_write_route(client, app, monkeypatch):
    monkeypatch.setattr("app.main.time.time", lambda: 5000.0)
    headers = verified_user(client, app)
    answers = {"answers": [1, 1, 1, 1, 1]}
    codes = [
        client.put(f"{AUTH}/investor-profile", headers=headers, json=answers).status_code
        for _ in range(101)
    ]
    assert codes[:100] == [200] * 100 and codes[100] == 429
    for _ in range(100):
        client.post(f"{AUTH}/webhooks", headers=headers, json={"url": "http://x"})
    assert (
        client.post(f"{AUTH}/webhooks", headers=headers, json={"url": "http://x"}).status_code
        == 429
    )


def test_SPEC_001_R07_client_identity_only_trusts_configured_proxies():
    trusted = parse_trusted_proxies("10.0.0.0/8, 192.168.1.10")
    # Sem proxy confiável, X-Forwarded-For é ignorado (não permite trocar de balde).
    assert client_address("203.0.113.5", "198.51.100.1", trusted) == "203.0.113.5"
    assert client_address("203.0.113.5", "198.51.100.1", ()) == "203.0.113.5"
    # Atrás do proxy: o cliente é o endereço mais à direita que não é proxy confiável.
    assert client_address("10.1.2.3", "198.51.100.1", trusted) == "198.51.100.1"
    assert (
        client_address("10.1.2.3", "6.6.6.6, 198.51.100.1, 192.168.1.10", trusted) == "198.51.100.1"
    )
    assert client_address("10.1.2.3", "lixo", trusted) == "10.1.2.3"
    assert client_address(None, None, trusted) == "unknown"


# --------------------------------------------------------------------------- webhooks (SSRF)
@pytest.fixture
def local_tls(tmp_path):
    private = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    now = dt.datetime.now(dt.UTC)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=1))
        .not_valid_after(now + dt.timedelta(hours=1))
        .sign(private, hashes.SHA256())
    )
    cert_path, key_path = tmp_path / "cert.pem", tmp_path / "key.pem"
    cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return cert_path, key_path


def serve(handler, tls=None):
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    if tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(*tls)
        server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def test_SPEC_042_R02_webhook_never_follows_redirects_and_pins_validated_ip(local_tls, monkeypatch):
    internal_hits: list[str] = []

    class Internal(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            internal_hits.append(self.path)
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *args):
            pass

    internal = serve(Internal)

    class Redirecting(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{internal.server_port}/metadata")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *args):
            pass

    hook = serve(Redirecting, local_tls)
    resolved: list[str] = []

    def resolver(host, port, type=None):
        # Simula um host público já validado; a conexão deve usar este IP (sem nova resolução).
        resolved.append(host)
        return [(None, None, None, "", ("127.0.0.1", port))]

    fake_ipaddress = type("FakeIpaddress", (), {"ip_address": staticmethod(_global_loopback)})
    monkeypatch.setattr("app.application.webhooks.ipaddress", fake_ipaddress)
    context = ssl.create_default_context(cafile=str(local_tls[0]))
    context.check_hostname = False
    delivery = HttpWebhookDelivery(context=context, resolver=resolver)
    status = delivery.deliver(
        f"https://hooks.example:{hook.server_port}/events",
        b"{}",
        {"Content-Type": "application/json"},
    )
    assert status == 302  # registrado como falha (não 2xx); o redirecionamento não é seguido
    assert internal_hits == []
    assert resolved == ["hooks.example"]
    hook.shutdown()
    internal.shutdown()


def _global_loopback(value):
    """Trata 127.0.0.1 como global apenas neste teste, para exercitar a conexão local."""
    import ipaddress

    address = ipaddress.ip_address(value)

    class Wrapper:
        is_global = True

        def __eq__(self, other):
            return address == other

    return Wrapper() if str(address) == "127.0.0.1" else address


def test_SPEC_042_R02_webhook_rejects_private_resolution():
    from app.application.auth import AuthError

    def private_resolver(host, port, type=None):
        return [(None, None, None, "", ("169.254.169.254", port))]

    delivery = HttpWebhookDelivery(resolver=private_resolver)
    with pytest.raises(AuthError) as error:
        delivery.deliver("https://rebind.example/events", b"{}", {})
    assert error.value.code == "invalid_webhook_destination"


# --------------------------------------------------------------------------- capacidade (RNF-04)
def test_rnf04_admission_control_queues_then_rejects_with_retry_after():
    async def slow_app(scope, receive, send):
        await asyncio.sleep(0.3)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    logger = logging.getLogger("finnova.test.admission")
    middleware = AdmissionControl(slow_app, max_concurrent=1, queue_timeout=0.05, logger=logger)

    async def call():
        messages = []

        async def receive():
            return {"type": "http.request", "body": b""}

        async def send(message):
            messages.append(message)

        await middleware({"type": "http", "method": "GET", "path": "/api/v1/health"}, receive, send)
        return messages

    async def scenario():
        return await asyncio.gather(call(), call())

    first, second = asyncio.run(scenario())
    statuses = sorted(m["status"] for m in (first[0], second[0]))
    assert statuses == [200, 503]
    busy = first if first[0]["status"] == 503 else second
    headers = dict(busy[0]["headers"])
    assert headers[b"retry-after"] == b"5"
    assert json.loads(busy[1]["body"]) == {"detail": "server_busy"}
    assert all(b"x-request-id" in dict(m[0]["headers"]) for m in (first, second))


def test_rnf04_settings_keep_admission_below_pool_capacity():
    from app.config import Settings

    with pytest.raises(ValueError):
        Settings(max_concurrent_requests=40, db_pool_size=20, db_max_overflow=20)
    with pytest.raises(ValueError):
        Settings(trusted_proxies="não-é-ip")


# ---------------------------------------------------------------- observabilidade (RNF-12)
def test_SPEC_001_R09_unhandled_error_is_logged_without_personal_data(client, app, monkeypatch):
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record):
            records.append(record)

    handler = Capture()
    logging.getLogger("finnova").addHandler(handler)
    headers = verified_user(client, app, email="erro-interno@example.com")

    def broken(self, user_id):
        raise RuntimeError("erro-interno@example.com")

    monkeypatch.setattr(AuthService, "list_expenses", broken)
    try:
        with TestClient(app, base_url="https://localhost:8443", raise_server_exceptions=False) as c:
            response = c.get(f"{FIN}/expenses", headers=headers)
    finally:
        logging.getLogger("finnova").removeHandler(handler)
    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "internal_error" and body["request_id"]
    errors = [r for r in records if r.getMessage() == "unhandled_error"]
    assert errors and errors[0].fields["error_type"] == "RuntimeError"
    rendered = JsonFormatter().format(errors[0])
    assert "erro-interno@example.com" not in rendered and json.loads(rendered)["request_id"]
    requests = [r for r in records if r.getMessage() == "http_request"]
    assert any(r.fields["status"] == 500 and "?" not in r.fields["path"] for r in requests)


def test_rnf08_startup_retries_until_database_is_available(app, monkeypatch):
    from app.infrastructure.account_deletion import DeletionJournal
    from app.main import create_app

    calls = {"n": 0}
    original = DeletionJournal.apply

    def flaky(self, db):
        calls["n"] += 1
        if calls["n"] < 3:
            raise OSError("database starting")
        return original(self, db)

    monkeypatch.setattr(DeletionJournal, "apply", flaky)
    settings = app.state.settings.model_copy(
        update={"startup_attempts": 3, "startup_retry_seconds": 0}
    )
    instance = create_app(settings)
    with TestClient(instance, base_url="https://localhost:8443") as started:
        assert started.get("/api/v1/health").status_code == 200
    instance.state.engine.dispose()
    assert calls["n"] == 3

    calls["n"] = -10  # sempre falha: a API não sobe (fail-closed)
    failing = create_app(settings)
    with pytest.raises(OSError):
        with TestClient(failing, base_url="https://localhost:8443"):
            pass
    failing.state.engine.dispose()
