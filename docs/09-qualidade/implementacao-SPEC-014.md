# SPEC-014 — Editar perfil e preferências persistidas

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec e em [`.specify/plans/PLAN-014.md`](../../.specify/plans/PLAN-014.md); este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementação técnica concluída na branch feature/19-perfil-preferencias, aguardando CI e revisão humana. A autorização do usuário cobre este recorte; não comprova aprovação formal histórica do grupo.

## Testes automatizados

- `backend/tests/test_spec014_profile_preferences.py`

- `test_SPEC_014_R01_profile_and_preferences_persist_across_sessions`
- `test_SPEC_014_R02_email_change_requires_reauthentication_and_promotes_only_on_confirmation`
- `test_SPEC_014_R03_duplicate_or_failed_delivery_keeps_valid_profile_data`
- `test_SPEC_014_R04_profiles_are_isolated_and_invalid_input_is_generic`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
