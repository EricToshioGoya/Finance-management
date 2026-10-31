# SPEC-016 — Recuperar e alterar senha com revogação

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec e em [`.specify/plans/PLAN-016.md`](../../.specify/plans/PLAN-016.md); este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementação técnica concluída em 2026-10-25; aprovação formal humana continua pendente.

## Testes automatizados

- `backend/tests/test_spec016_password_recovery.py`

- `test_SPEC_016_R01_recovery_changes_password_and_revokes_sessions`
- `test_SPEC_016_R02_invalid_or_expired_token_preserves_credentials`
- `test_SPEC_016_R03_authenticated_change_requires_current_password_and_revokes`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
