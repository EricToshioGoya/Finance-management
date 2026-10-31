"""Generate local-only secrets and a localhost development TLS certificate."""

import os
import secrets
import subprocess
from pathlib import Path

from cryptography.fernet import Fernet

root = Path(__file__).resolve().parents[1]
local = root / ".local"
local.mkdir(exist_ok=True, mode=0o700)
config = root / "backend/.env"
if not config.exists():
    password = secrets.token_urlsafe(32)
    contents = (
        f"POSTGRES_PASSWORD={password}\n"
        f"FINNOVA_DATABASE_URL=postgresql+psycopg://finnova:{password}@127.0.0.1:5432/finnova\n"
        f"FINNOVA_JWT_SECRET={secrets.token_urlsafe(48)}\n"
        f"FINNOVA_DATA_KEY={Fernet.generate_key().decode()}\n"
        "FINNOVA_PUBLIC_ORIGIN=https://localhost:8443\n"
    )
    fd = os.open(config, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(contents)
cert, key = local / "localhost.crt", local / "localhost.key"
if not cert.exists() and not key.exists():
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
        "-keyout", str(key), "-out", str(cert), "-days", "30",
        "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
    ], check=True, capture_output=True)
    key.chmod(0o600)
elif not cert.exists() or not key.exists():
    raise SystemExit("Incomplete TLS pair: restore both files or remove the local pair to regenerate.")
print("Local configuration ready; existing secrets were preserved. No credentials were printed.")
