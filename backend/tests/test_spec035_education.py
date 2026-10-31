"""SPEC-035: shared content, profile ordering, private session and unknown keys."""

from test_spec028_net_worth import CaptureDelivery, login, verify

PREFIX = "/api/v1/education/articles"


def test_education_requires_session_and_reuses_exact_article_in_context(client):
    assert client.get(PREFIX).status_code == 401
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    headers = login(client, "education-user@example.com")
    verify(client, headers, delivery)
    listing = client.get(PREFIX + "?q=CDI&lang=pt", headers=headers)
    assert listing.status_code == 200
    items = listing.json()
    assert items and items[0]["key"] == "cdi"
    detailed = client.get(PREFIX + "/cdi?lang=pt", headers=headers)
    assert detailed.status_code == 200
    assert detailed.json() == items[0]
    assert detailed.json()["fallback"] is False

    english = client.get(PREFIX + "/cdi?lang=en", headers=headers)
    assert english.status_code == 200
    assert english.json()["language"] == "en"
    assert english.json()["body"] != detailed.json()["body"]
    assert client.get(PREFIX + "/unknown-article", headers=headers).status_code == 404
    assert client.get(PREFIX + "?q=zzzz-unrelated", headers=headers).json() == []
    assert client.get(PREFIX + "?lang=fr", headers=headers).status_code == 422


def test_profile_based_order_and_search_without_exposing_other_user(client):
    delivery = CaptureDelivery()
    client.app.state.email_delivery = delivery
    first = login(client, "education-basic@example.com")
    verify(client, first, delivery)
    titles = client.get(PREFIX, headers=first).json()
    assert titles[0]["key"] in ("cdi", "compound-interest", "diversification", "interest-rate")
    assert len({item["key"] for item in titles}) == len(titles)
    assert {"cdi", "sharpe", "diversification"}.issubset({item["key"] for item in titles})
    assert len(titles) <= 20

    other = login(client, "education-other@example.com")
    verify(client, other, delivery)
    assert client.get(PREFIX + "?q=sharpe", headers=other).json()[0]["key"] == "sharpe"
