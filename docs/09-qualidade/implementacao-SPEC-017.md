# SPEC-017 — Consultar, renovar e encerrar sessões

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec e em [`.specify/plans/PLAN-017.md`](../../.specify/plans/PLAN-017.md); este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementação técnica concluída na branch feature/17-sessoes, aguardando CI e revisão humana. A autorização do usuário cobre este recorte; não comprova aprovação formal histórica do grupo.

## Testes automatizados

- `backend/tests/test_spec017_session_management.py`

- `test_SPEC_017_R01_lists_only_owned_sessions_without_tokens`
- `test_SPEC_017_R02_rejects_foreign_or_malformed_session_without_revocation`
- `test_SPEC_017_R03_selected_revocation_is_idempotent_and_isolated`
- `test_SPEC_017_R04_revoking_all_invalidates_every_device_and_clears_cookie`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
