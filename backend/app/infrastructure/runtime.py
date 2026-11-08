"""Proteções de execução da API: identidade do cliente, admissão de carga e logs estruturados."""

import asyncio
import ipaddress
import json
import logging
import sys
import time
import traceback
import uuid
import weakref
from datetime import UTC, datetime

LOGGER_NAME = "finnova"


class JsonFormatter(logging.Formatter):
    """Uma linha JSON por evento (RNF-12); campos extras vêm de `extra={"fields": {...}}`."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        payload.update(getattr(record, "fields", {}))
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> logging.Logger:
    """Configura o logger `finnova` uma única vez, em stderr, sem duplicar handlers."""
    logger = logging.getLogger(LOGGER_NAME)
    if not any(getattr(h, "_finnova", False) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        handler._finnova = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def error_location(error: BaseException) -> list[str]:
    """Pilha resumida (arquivo:linha:função), sem mensagens que possam conter dados pessoais."""
    return [
        f"{frame.filename.rsplit('/', 1)[-1]}:{frame.lineno}:{frame.name}"
        for frame in traceback.extract_tb(error.__traceback__)[-5:]
    ]


def parse_trusted_proxies(raw: str) -> tuple:
    """Lista separada por vírgula de IPs/redes (CIDR) dos proxies reversos confiáveis."""
    return tuple(
        ipaddress.ip_network(item.strip(), strict=False) for item in raw.split(",") if item.strip()
    )


def client_address(peer: str | None, forwarded_for: str | None, trusted) -> str:
    """IP do cliente para o rate limit (RNF-13).

    `X-Forwarded-For` só é considerado quando a conexão vem de um proxy confiável configurado;
    o cliente é o endereço mais à direita que não pertence a um proxy confiável.
    """
    if not peer:
        return "unknown"

    def is_trusted(value: str) -> bool:
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False
        return any(address in network for network in trusted)

    if not trusted or not forwarded_for or not is_trusted(peer):
        return peer
    for hop in reversed([part.strip() for part in forwarded_for.split(",") if part.strip()]):
        if not is_trusted(hop):
            try:
                return str(ipaddress.ip_address(hop))
            except ValueError:
                return peer
    return peer


class AdmissionControl:
    """Middleware ASGI: limita requisições HTTP simultâneas e registra cada uma em JSON.

    Requisições acima do limite aguardam (sem ocupar thread nem conexão) até `queue_timeout`;
    depois recebem 503 `server_busy` com Retry-After. Com o limite abaixo do pool de conexões e
    do threadpool, a API degrada com fila em vez de travar por esgotamento (RNF-04).
    """

    def __init__(self, app, max_concurrent: int, queue_timeout: float, logger: logging.Logger):
        self.app = app
        self.max_concurrent = max_concurrent
        self.queue_timeout = queue_timeout
        self.logger = logger
        # Um semáforo por event loop: o TestClient pode usar loops diferentes.
        self._semaphores: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

    def _semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        semaphore = self._semaphores.get(loop)
        if semaphore is None:
            semaphore = asyncio.Semaphore(self.max_concurrent)
            self._semaphores[loop] = semaphore
        return semaphore

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.perf_counter()
        status = {"code": 500}

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        semaphore = self._semaphore()
        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=self.queue_timeout)
        except TimeoutError:
            await self._busy(send_with_id)
            self._log(scope, request_id, 503, started, rejected=True)
            return
        try:
            await self.app(scope, receive, send_with_id)
        finally:
            semaphore.release()
            self._log(scope, request_id, status["code"], started)

    async def _busy(self, send) -> None:
        body = json.dumps({"detail": "server_busy"}).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 503,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                    (b"retry-after", b"5"),
                    (b"cache-control", b"no-store"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

    def _log(self, scope, request_id: str, status: int, started: float, rejected=False) -> None:
        # Caminho sem query string: filtros de busca podem conter dados pessoais.
        self.logger.info(
            "http_request",
            extra={
                "fields": {
                    "request_id": request_id,
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status": status,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                    "rejected_by_admission": rejected,
                }
            },
        )
