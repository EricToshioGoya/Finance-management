#!/usr/bin/env bash
# Backup do PostgreSQL do FinNova (RNF-14). Formato custom do pg_dump, restaurável com pg_restore.
# Uso: scripts/backup.sh [diretório-de-destino]   (padrão: .local/backups, fora do Git — C-10)
# A URL vem de FINNOVA_DATABASE_URL ou de backend/.env.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${FINNOVA_DATABASE_URL:-}" && -f backend/.env ]]; then
  FINNOVA_DATABASE_URL="$(grep -E '^FINNOVA_DATABASE_URL=' backend/.env | cut -d= -f2-)"
fi
: "${FINNOVA_DATABASE_URL:?defina FINNOVA_DATABASE_URL ou backend/.env}"
# O driver do SQLAlchemy (+psycopg) não é entendido pelas ferramentas do PostgreSQL.
URL="${FINNOVA_DATABASE_URL/+psycopg/}"

DESTINO="${1:-.local/backups}"
mkdir -p "$DESTINO"
chmod 700 "$DESTINO"
ARQUIVO="$DESTINO/finnova-$(date -u +%Y%m%dT%H%M%SZ).dump"

umask 077
pg_dump --format=custom --no-owner --dbname="$URL" --file="$ARQUIVO"
echo "Backup gravado em $ARQUIVO ($(du -h "$ARQUIVO" | cut -f1))"
