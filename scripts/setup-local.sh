#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .local
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.local/uv-cache}"
export npm_config_cache="${npm_config_cache:-$PWD/.local/npm-cache}"
uv sync --project backend --frozen
backend/.venv/bin/python scripts/prepare-local.py
npm ci --prefix frontend
npm run build --prefix frontend
docker compose --env-file backend/.env up -d --wait db
cd backend
uv run --frozen alembic upgrade head
