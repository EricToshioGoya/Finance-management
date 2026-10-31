"""Exercise actual HTTPS, persistence and revocation with the local trusted certificate."""

import json
import ssl
import urllib.error
import urllib.request
import uuid
from http.cookiejar import CookieJar
from pathlib import Path

root = Path(__file__).resolve().parents[1]
context = ssl.create_default_context(cafile=str(root / ".local/localhost.crt"))
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=context), urllib.request.HTTPCookieProcessor(CookieJar())
)
origin = "https://localhost:8443"


def request(path, data=None, token=None):
    headers = {"Content-Type": "application/json", "Origin": origin}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        origin + "/api/v1" + path,
        data=json.dumps(data).encode() if data is not None else None, headers=headers,
    )
    try:
        with opener.open(req, timeout=10) as result:
            body = result.read()
            return result.status, json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


identity = {"name": "Smoke Test", "email": f"smoke-{uuid.uuid4()}@example.com",
            "password": uuid.uuid4().hex}
assert request("/health")[0] == 200
assert request("/auth/register", identity)[0] == 201
assert request("/auth/register", identity)[0] == 409
status, login = request("/auth/login", {k: identity[k] for k in ("email", "password")})
assert status == 200
assert request("/auth/me", token=login["access_token"])[0] == 200
status, refreshed = request("/auth/refresh", {})
assert status == 200
assert request("/auth/logout", {}, refreshed["access_token"])[0] == 204
assert request("/auth/me", token=refreshed["access_token"])[0] == 401
assert request("/auth/refresh", {})[0] == 401
print("HTTPS certificate/hostname verified; register, duplicate, login, identity, refresh and logout passed.")
