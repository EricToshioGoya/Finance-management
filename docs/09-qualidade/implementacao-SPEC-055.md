# SPEC-055 — Gerir categorias padrão e pessoais

## Origem

Registro criado em 2026-10-31 a partir do código e dos testes do grupo incorporados à `main` (PR #43), para completar a rastreabilidade. As decisões de política estão na própria Spec e em [`.specify/plans/PLAN-055.md`](../../.specify/plans/PLAN-055.md); este registro não declara aprovação formal do grupo.

## Estado declarado na Spec

implementação técnica concluída em 2026-10-25; aprovação formal humana continua pendente.

## Testes automatizados

- `backend/tests/test_spec055_categories.py`

- `test_SPEC_055_R01_defaults_and_personal_category_with_stable_color`
- `test_SPEC_055_R02_hiding_default_is_per_owner_and_preserves_category`
- `test_SPEC_055_R03_custom_categories_are_private_and_names_are_unique`

## Evidência

Executados na CI (`.github/workflows/ci.yml`) com PostgreSQL; última execução local completa em 2026-10-31: 339 testes aprovados, cobertura de 92%.
