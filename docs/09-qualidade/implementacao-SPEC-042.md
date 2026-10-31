# SPEC-042 — Entregar eventos por webhook assinado

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec; este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementada em 2026-10-31; validação automatizada registrada no PR da implementação.

## Testes automatizados

- `backend/tests/test_spec042_webhooks.py`

- `test_spec042_hmac_history_and_manual_retry`
- `test_spec042_owner_isolation`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
