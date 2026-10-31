# SPEC-029 — Consultar evolução mensal do patrimônio

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec; este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementada tecnicamente; código incorporado à `main` em 2026-10-31 (PR #43) e coberto pela CI. Registro anterior: implementação em andamento na branch `feature/29-net-worth-history`; política de snapshots mensais do patrimônio real aprovada. Backend, interface e testes adicionados, mas execução do CI e captura automática pendentes; sem aprovação formal de merge presumida.

## Testes automatizados

- `backend/tests/test_spec029_month_boundary.py`
- `backend/tests/test_spec029_net_worth_history.py`
- `backend/tests/test_spec029_snapshot_concurrency.py`

- `test_monthly_capture_uses_sao_paulo_and_verified_email`
- `test_snapshot_is_real_idempotent_and_not_retroactively_recalculated`
- `test_history_is_private_and_does_not_backfill_missing_months`
- `test_two_simultaneous_captures_are_idempotent`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
