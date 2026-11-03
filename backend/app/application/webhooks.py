from __future__ import annotations

import hashlib
import hmac
import http.client
import ipaddress
import json
import secrets
import socket
import ssl
from typing import Protocol
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.auth import AuthError, AuthService
from app.infrastructure.models import WebhookAttemptRecord, WebhookSubscriptionRecord
from app.infrastructure.security import Security

EVENT_TYPE = "notification.created"
SIGNATURE_HEADER = "X-FinNova-Signature"


class WebhookDelivery(Protocol):
    def deliver(self, url: str, payload: bytes, headers: dict[str, str]) -> int: ...


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Conecta ao IP já validado, mantendo SNI e verificação de certificado pelo hostname.

    Evita DNS rebinding entre a validação e a conexão (SSRF).
    """

    def __init__(self, host: str, port: int, address: str, **kwargs):
        super().__init__(host, port, **kwargs)
        self._pinned_address = address

    def connect(self) -> None:
        sock = socket.create_connection((self._pinned_address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


class HttpWebhookDelivery:
    """Entrega POST HTTPS sem seguir redirecionamentos (3xx é registrado como falha)."""

    def __init__(self, context: ssl.SSLContext | None = None, resolver=None):
        self.context = context or ssl.create_default_context()
        self.resolver = resolver or socket.getaddrinfo

    def deliver(self, url: str, payload: bytes, headers: dict[str, str]) -> int:
        address = _validate_public_https_destination(url, resolve=True, resolver=self.resolver)
        parsed = urlparse(url)
        target = (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")
        connection = _PinnedHTTPSConnection(
            parsed.hostname, parsed.port or 443, address, timeout=5, context=self.context
        )
        try:
            connection.request("POST", target, body=payload, headers=headers)
            return int(connection.getresponse().status)
        except (OSError, ValueError, http.client.HTTPException):
            return 0
        finally:
            connection.close()


def _validate_public_https_destination(url: str, *, resolve: bool, resolver=None) -> str | None:
    """Valida destino HTTPS público; com `resolve`, devolve o IP global a ser usado."""
    try:
        p = urlparse(url)
        h = p.hostname
        if (
            p.scheme != "https"
            or not h
            or p.username is not None
            or p.password is not None
            or h.lower() == "localhost"
            or h.lower().endswith(".localhost")
        ):
            raise ValueError
        port = p.port
    except ValueError as exc:
        raise AuthError("invalid_webhook_url", 422) from exc
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        ip = None
    if ip is not None and not ip.is_global:
        raise AuthError("invalid_webhook_url", 422)
    if not resolve:
        return None
    try:
        lookup = resolver or socket.getaddrinfo
        ips = sorted({x[4][0] for x in lookup(h, port or 443, type=socket.SOCK_STREAM)})
        if not ips or any(not ipaddress.ip_address(x).is_global for x in ips):
            raise ValueError
    except (OSError, ValueError) as exc:
        raise AuthError("invalid_webhook_destination", 422) from exc
    return ips[0]


class WebhookService:
    def __init__(
        self, db: Session, security: Security, auth: AuthService, delivery: WebhookDelivery
    ):
        self.db, self.security, self.auth, self.delivery = db, security, auth, delivery

    def _sub(self, x):
        return {
            "id": x.id,
            "url": self.security.decrypt(x.url_encrypted),
            "enabled": x.enabled,
            "created_at": x.created_at,
            "disabled_at": x.disabled_at,
        }

    @staticmethod
    def _attempt(x):
        return {
            "id": x.id,
            "subscription_id": x.subscription_id,
            "event_type": x.event_type,
            "outcome": x.outcome,
            "status_code": x.status_code,
            "failure_code": x.failure_code,
            "attempted_at": x.attempted_at,
            "retry_of_id": x.retry_of_id,
        }

    def list_subscriptions(self, owner_id):
        self.auth.require_category_owner(owner_id)
        return [
            self._sub(x)
            for x in self.db.scalars(
                select(WebhookSubscriptionRecord)
                .where(WebhookSubscriptionRecord.user_id == owner_id)
                .order_by(WebhookSubscriptionRecord.created_at.desc())
            ).all()
        ]

    def create_subscription(self, owner_id, url):
        self.auth.require_category_owner(owner_id)
        _validate_public_https_destination(url, resolve=False)
        secret = secrets.token_urlsafe(32)
        x = WebhookSubscriptionRecord(
            user_id=owner_id,
            url_encrypted=self.security.encrypt(url),
            secret_encrypted=self.security.encrypt(secret),
            enabled=True,
            created_at=self.auth.clock(),
        )
        self.db.add(x)
        self.db.commit()
        self.db.refresh(x)
        return {**self._sub(x), "signing_secret": secret}

    def disable_subscription(self, owner_id, subscription_id):
        self.auth.require_category_owner(owner_id)
        x = self.db.scalar(
            select(WebhookSubscriptionRecord)
            .where(
                WebhookSubscriptionRecord.id == subscription_id,
                WebhookSubscriptionRecord.user_id == owner_id,
            )
            .with_for_update()
        )
        if x is None:
            raise AuthError("webhook_subscription_not_found", 404)
        if x.enabled:
            x.enabled = False
            x.disabled_at = self.auth.clock()
            self.db.commit()

    def _deliver(self, sub, payload, retry_of_id=None):
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        sig = hmac.new(
            self.security.decrypt(sub.secret_encrypted).encode(), data, hashlib.sha256
        ).hexdigest()
        status = 0
        failure = None
        try:
            status = self.delivery.deliver(
                self.security.decrypt(sub.url_encrypted),
                data,
                {
                    "Content-Type": "application/json",
                    "X-FinNova-Event": EVENT_TYPE,
                    SIGNATURE_HEADER: f"sha256={sig}",
                },
            )
            if not 200 <= status < 300:
                failure = "http_status"
        except AuthError:
            failure = "destination_rejected"
        except (OSError, ValueError):
            failure = "delivery_failed"
        x = WebhookAttemptRecord(
            subscription_id=sub.id,
            user_id=sub.user_id,
            event_type=EVENT_TYPE,
            payload_encrypted=self.security.encrypt(data.decode()),
            outcome="succeeded" if failure is None else "failed",
            status_code=status or None,
            failure_code=failure,
            attempted_at=self.auth.clock(),
            retry_of_id=retry_of_id,
        )
        self.db.add(x)
        self.db.commit()
        self.db.refresh(x)
        return x

    def dispatch_notification(self, owner_id, notification):
        if notification is None:
            return
        payload = {
            "event": EVENT_TYPE,
            "notification": {
                "id": str(notification["id"]),
                "kind": notification["kind"],
                "created_at": notification["created_at"].isoformat(),
            },
        }
        for x in self.db.scalars(
            select(WebhookSubscriptionRecord).where(
                WebhookSubscriptionRecord.user_id == owner_id,
                WebhookSubscriptionRecord.enabled.is_(True),
            )
        ).all():
            self._deliver(x, payload)

    def list_attempts(self, owner_id, subscription_id):
        self.auth.require_category_owner(owner_id)
        return [
            self._attempt(x)
            for x in self.db.scalars(
                select(WebhookAttemptRecord)
                .where(
                    WebhookAttemptRecord.user_id == owner_id,
                    WebhookAttemptRecord.subscription_id == subscription_id,
                )
                .order_by(WebhookAttemptRecord.attempted_at.desc())
            ).all()
        ]

    def retry_attempt(self, owner_id, subscription_id, attempt_id):
        self.auth.require_category_owner(owner_id)
        a = self.db.scalar(
            select(WebhookAttemptRecord).where(
                WebhookAttemptRecord.id == attempt_id,
                WebhookAttemptRecord.subscription_id == subscription_id,
                WebhookAttemptRecord.user_id == owner_id,
            )
        )
        if a is None:
            raise AuthError("webhook_attempt_not_found", 404)
        if a.outcome != "failed":
            raise AuthError("webhook_attempt_not_retryable", 409)
        s = self.db.scalar(
            select(WebhookSubscriptionRecord).where(
                WebhookSubscriptionRecord.id == subscription_id,
                WebhookSubscriptionRecord.user_id == owner_id,
                WebhookSubscriptionRecord.enabled.is_(True),
            )
        )
        if s is None:
            raise AuthError("webhook_subscription_not_found", 404)
        return self._attempt(
            self._deliver(s, json.loads(self.security.decrypt(a.payload_encrypted)), a.id)
        )
