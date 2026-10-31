# SPEC-015 — Confirmar posse do e-mail

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec e em [`.specify/plans/PLAN-015.md`](../../.specify/plans/PLAN-015.md); este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementada tecnicamente em 2026-10-23; revisão humana e configuração operacional de entrega pendentes.

## Testes automatizados

- `backend/tests/test_spec015_email_confirmation.py`

- `test_SPEC_015_R01_one_time_confirmation_and_pending_profile`
- `test_SPEC_015_R02_expired_tampered_and_cross_account_tokens_do_not_confirm`
- `test_SPEC_015_R03_digest_ttl_resend_limit_and_previous_invalidation`
- `test_email_delivery_failure_keeps_prior_token_usable`
- `test_token_is_bound_to_its_owner_and_confirmation_is_atomic`
- `test_unconfigured_delivery_does_not_persist_token_or_expose_it`
- `test_confirmation_rejects_malformed_input_without_echoing_token`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
