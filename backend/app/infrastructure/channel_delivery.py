"""SPEC-061: adaptador provider-neutral para canais externos opcionais (e-mail e push).

Nenhum provedor real é fixado (OPEN-17): o envio é um POST HTTPS para um despachante
configurado. Sem configuração, a tentativa é registrada como `provider_unavailable`.
"""

import base64
import json
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen


class ChannelUnavailable(Exception):
    """Canal sem despachante configurado."""


class ChannelDeliveryError(Exception):
    """O despachante recusou ou não respondeu."""


class ChannelDelivery(Protocol):
    def send(
        self,
        *,
        channel: str,
        destination: str,
        title: str,
        message: str,
        attachment: tuple[str, bytes] | None = None,
    ) -> None: ...


class UnconfiguredChannelDelivery:
    def send(self, **_: object) -> None:
        raise ChannelUnavailable("channel delivery is not configured")


class HttpsChannelDelivery:
    """Envia um comando JSON ao despachante HTTPS (ex.: gateway FCM ou serviço de e-mail)."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def send(
        self,
        *,
        channel: str,
        destination: str,
        title: str,
        message: str,
        attachment: tuple[str, bytes] | None = None,
    ) -> None:
        payload: dict[str, object] = {
            "kind": "notification",
            "channel": channel,
            "destination": destination,
            "title": title,
            "message": message,
        }
        if attachment is not None:
            name, content = attachment
            payload["attachment"] = {
                "filename": name,
                "content_base64": base64.b64encode(content).decode(),
            }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:  # noqa: S310  # nosec B310 - HTTPS validado
                if not 200 <= response.status < 300:
                    raise ChannelDeliveryError("delivery rejected")
        except (OSError, URLError) as exc:
            raise ChannelDeliveryError("delivery unavailable") from exc
