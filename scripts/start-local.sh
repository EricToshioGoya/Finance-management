#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.local/uv-cache}"
docker compose --env-file backend/.env up -d --wait db
cd backend
uv run --frozen alembic upgrade head
exec uv run --frozen uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8443 \
  --no-proxy-headers --ssl-keyfile ../.local/localhost.key --ssl-certfile ../.local/localhost.crt
