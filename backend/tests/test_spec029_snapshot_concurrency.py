"""Concurrent snapshot requests retain exactly one monthly position."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from test_spec028_net_worth import CaptureDelivery, login, verify

from app.application.auth import AuthService

PREFIX = "/api/v1/auth/financial"


def test_two_simultaneous_captures_are_idempotent(client, monkeypatch):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "concurrent-history@example.com")
    verify(client, headers, delivery)

    original = AuthService.net_worth
    barrier = Barrier(2)

    def synchronize(self, user_id, as_of=None):
        result = original(self, user_id, as_of)
        barrier.wait(timeout=10)
        return result

    monkeypatch.setattr(AuthService, "net_worth", synchronize)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda _: client.post(f"{PREFIX}/net-worth/history/snapshots", headers=headers),
                range(2),
            )
        )
    assert [response.status_code for response in responses] == [201, 201]
    assert responses[0].json() == responses[1].json()
    history = client.get(f"{PREFIX}/net-worth/history", headers=headers).json()
    assert history == [responses[0].json()]
