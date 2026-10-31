"""Adapter boundary for the transactional confirmation e-mail service."""

import json
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen


class EmailDeliveryError(Exception):
    """The external delivery service did not accept the message."""


class EmailConfirmationDelivery(Protocol):
    def deliver_confirmation(self, *, recipient: str, token: str) -> None: ...

    def deliver_password_reset(self, *, recipient: str, token: str) -> None: ...


class UnconfiguredEmailConfirmationDelivery:
    """Safe default: no token is persisted as deliverable without a sender."""

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        raise EmailDeliveryError("confirmation delivery is not configured")

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        raise EmailDeliveryError("password reset delivery is not configured")


class WebhookEmailConfirmationDelivery:
    """Posts a provider-neutral delivery command to a configured HTTPS dispatcher."""

    def __init__(self, endpoint: str, public_origin: str):
        self.endpoint = endpoint
        self.public_origin = public_origin

    def deliver_confirmation(self, *, recipient: str, token: str) -> None:
        body = json.dumps(
            {
                "kind": "email_confirmation",
                "recipient": recipient,
                "confirmation_url": f"{self.public_origin}/#/confirmar-email?token={token}",
            }
        ).encode()
        request = Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:  # noqa: S310  # nosec B310 - HTTPS validado
                if not 200 <= response.status < 300:
                    raise EmailDeliveryError("confirmation delivery was rejected")
        except (OSError, URLError) as exc:
            raise EmailDeliveryError("confirmation delivery unavailable") from exc

    def deliver_password_reset(self, *, recipient: str, token: str) -> None:
        body = json.dumps(
            {
                "kind": "password_reset",
                "recipient": recipient,
                "password_reset_url": f"{self.public_origin}/#/redefinir-senha?token={token}",
            }
        ).encode()
        request = Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:  # noqa: S310  # nosec B310 - HTTPS validado
                if not 200 <= response.status < 300:
                    raise EmailDeliveryError("password reset delivery was rejected")
        except (OSError, URLError) as exc:
            raise EmailDeliveryError("password reset delivery unavailable") from exc
