"""Rotas inexistentes sob /api respondem 404 JSON, sem cair nos arquivos estáticos do web."""


def test_unknown_api_route_returns_json_404(client):
    for method in ("get", "post", "patch", "delete"):
        response = getattr(client, method)("/api/v1/auth/audit-logs/anything")
        assert response.status_code == 404
        assert response.json() == {"detail": "not_found"}
    assert client.get("/api/v1/health").status_code == 200
