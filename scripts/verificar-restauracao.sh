#!/usr/bin/env bash
# Teste de restauração (RNF-14): restaura um backup em banco isolado, compara a contagem de
# linhas de cada tabela com a origem e mede o tempo de restauração (RTO observado).
# Uso: scripts/verificar-restauracao.sh <arquivo.dump> [--manter]
# Compare com a origem logo após o backup: escritas posteriores aparecem como divergência.
# Exclusões de conta registradas depois do backup são reaplicadas pelo diário de exclusão na
# inicialização da API (DeletionJournal), e não por este script (OPEN-05).
set -euo pipefail
cd "$(dirname "$0")/.."

ARQUIVO="${1:?informe o arquivo .dump gerado por scripts/backup.sh}"
MANTER="${2:-}"
if [[ -z "${FINNOVA_DATABASE_URL:-}" && -f backend/.env ]]; then
  FINNOVA_DATABASE_URL="$(grep -E '^FINNOVA_DATABASE_URL=' backend/.env | cut -d= -f2-)"
fi
: "${FINNOVA_DATABASE_URL:?defina FINNOVA_DATABASE_URL ou backend/.env}"
ORIGEM="${FINNOVA_DATABASE_URL/+psycopg/}"
SERVIDOR="${ORIGEM%/*}"
ISOLADO="finnova_restauracao_$(date -u +%Y%m%d%H%M%S)"
DESTINO="$SERVIDOR/$ISOLADO"

limpar() {
  if [[ "$MANTER" != "--manter" ]]; then
    psql -q -d "$SERVIDOR/postgres" -c "DROP DATABASE IF EXISTS \"$ISOLADO\" WITH (FORCE)"
  fi
}
trap limpar EXIT

contagens() {
  # Uma linha "tabela|linhas" por tabela do schema public, em ordem alfabética.
  psql -At -d "$1" -c "
    SELECT table_name || '|' || (xpath('/row/c/text()', query_to_xml(
      format('SELECT count(*) AS c FROM public.%I', table_name), false, true, '')))[1]::text
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name"
}

inicio=$(date +%s)
psql -q -d "$SERVIDOR/postgres" -c "CREATE DATABASE \"$ISOLADO\""
pg_restore --no-owner --exit-on-error --dbname="$DESTINO" "$ARQUIVO"
fim=$(date +%s)

if diff <(contagens "$ORIGEM") <(contagens "$DESTINO") > /dev/null; then
  tabelas=$(contagens "$DESTINO" | wc -l)
  linhas=$(contagens "$DESTINO" | awk -F'|' '{s += $2} END {print s}')
  versao=$(psql -At -d "$DESTINO" -c "SELECT version_num FROM alembic_version")
  echo "OK: $tabelas tabelas e $linhas linhas iguais à origem; migration $versao."
  echo "Tempo de restauração: $((fim - inicio)) s (meta RTO: 4 h)."
else
  echo "ERRO: contagem de linhas diverge entre origem e restauração:" >&2
  diff <(contagens "$ORIGEM") <(contagens "$DESTINO") >&2 || true
  exit 1
fi
