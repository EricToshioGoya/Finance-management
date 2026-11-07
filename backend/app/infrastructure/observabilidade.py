"""Logs estruturados e identificador de requisição (RNF-12, SPEC-060-R07 a R09).

Cada linha de log é um objeto JSON. O registro de acesso contém apenas método, rota,
status, duração e identificador; nunca corpo, cabeçalhos, query string, senha ou token (C-06).
"""

import json
import logging
import re
import sys
import uuid
from datetime import UTC, datetime

LOGGER = "finnova"
REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_VALIDO = re.compile(r"^[A-Za-z0-9-]{8,64}$")
# Campos extras aceitos no JSON; o restante do LogRecord é ignorado.
_CAMPOS = ("request_id", "method", "path", "status", "duration_ms", "error_type")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entrada = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entrada.update({c: getattr(record, c) for c in _CAMPOS if hasattr(record, c)})
        if record.exc_info:
            entrada["stack"] = self.formatException(record.exc_info)
        return json.dumps(entrada, ensure_ascii=False)


def configurar_logs() -> logging.Logger:
    """Configura o logger da aplicação uma única vez (idempotente entre create_app)."""
    logger = logging.getLogger(LOGGER)
    if not any(getattr(h, "finnova_json", False) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        handler.finnova_json = True
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def request_id(recebido: str | None) -> str:
    """Reaproveita o identificador do cliente se for seguro; senão gera um novo."""
    if recebido and _REQUEST_ID_VALIDO.fullmatch(recebido):
        return recebido
    return uuid.uuid4().hex
