from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FINNOVA_", env_file=".env", extra="ignore")

    database_url: SecretStr
    jwt_secret: SecretStr
    data_key: SecretStr
    public_origin: str = "https://localhost:8443"
    access_seconds: int = 900
    refresh_seconds: int = 604800
    rate_limit: int = 100
    email_webhook_url: SecretStr | None = None
    # SPEC-061: despachante HTTPS do canal push (ex.: gateway para FCM). Opcional.
    push_webhook_url: SecretStr | None = None
    deletion_journal_path: str = "../.local/account-deletions.sqlite3"
    initial_admin_email: str | None = None
    # ADR-009: rotinas agendadas que consultam fontes oficiais; desligadas por padrão (C-17).
    official_sources_sync: bool = False
    # RNF-13: proxies reversos confiáveis (IPs/CIDR separados por vírgula). Só deles se aceita
    # X-Forwarded-For para identificar o cliente; vazio = usa o IP da conexão.
    trusted_proxies: str = ""
    # RNF-04: requisições simultâneas admitidas; excedentes aguardam até queue_timeout_seconds
    # e depois recebem 503 server_busy. O pool de conexões deve superar esse limite.
    max_concurrent_requests: int = 30
    queue_timeout_seconds: float = 10
    db_pool_size: int = 20
    db_max_overflow: int = 20
    db_pool_timeout_seconds: int = 10
    # Inicialização: novas tentativas se o banco ainda não estiver disponível (fail-closed).
    startup_attempts: int = 10
    startup_retry_seconds: float = 3

    @field_validator("jwt_secret")
    @classmethod
    def strong_signing_key(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode()) < 32:
            raise ValueError("JWT signing key must contain at least 32 bytes")
        return value

    @model_validator(mode="after")
    def validate_runtime(self):
        from cryptography.fernet import Fernet

        Fernet(self.data_key.get_secret_value().encode())
        if not self.database_url.get_secret_value().startswith("postgresql+psycopg://"):
            raise ValueError("A PostgreSQL psycopg URL is required")
        origin = urlsplit(self.public_origin)
        if (
            origin.scheme != "https"
            or not origin.hostname
            or origin.path
            or origin.query
            or origin.fragment
            or origin.username
            or origin.password
        ):
            raise ValueError("public_origin must be an HTTPS origin without trailing slash")
        if self.email_webhook_url is not None:
            delivery = urlsplit(self.email_webhook_url.get_secret_value())
            if delivery.scheme != "https" or not delivery.hostname:
                raise ValueError("email_webhook_url must be an HTTPS URL")
        if self.push_webhook_url is not None:
            push = urlsplit(self.push_webhook_url.get_secret_value())
            if push.scheme != "https" or not push.hostname:
                raise ValueError("push_webhook_url must be an HTTPS URL")
        if self.initial_admin_email is not None and "@" not in self.initial_admin_email:
            raise ValueError("initial_admin_email must be a valid email address")
        if min(self.access_seconds, self.refresh_seconds, self.rate_limit) <= 0:
            raise ValueError("Durations and rate limit must be positive")
        if self.rate_limit > 100:
            raise ValueError("RNF-13 allows at most 100 requests per minute")
        if min(self.max_concurrent_requests, self.db_pool_size, self.startup_attempts) <= 0:
            raise ValueError("Concurrency, pool size and startup attempts must be positive")
        if self.max_concurrent_requests >= self.db_pool_size + self.db_max_overflow:
            raise ValueError("max_concurrent_requests must be below the database pool capacity")
        if self.max_concurrent_requests > 35:
            raise ValueError("max_concurrent_requests must leave threadpool headroom (<= 35)")
        from app.infrastructure.runtime import parse_trusted_proxies

        parse_trusted_proxies(self.trusted_proxies)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
