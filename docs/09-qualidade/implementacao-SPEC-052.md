# SPEC-052 — Guiar primeiro acesso com tour opcional

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-08/30): estado persistido por usuário; quatro etapas; pular e reabrir; didático para sem perfil ou conservador, resumido para moderado e arrojado.

## Contrato implementado

`GET|PUT /api/v1/auth/profile/tour` (401 sem sessão; 422 ação inválida).

## Testes

- `test_SPEC_052_R01_R03_first_access_tour_covers_core_steps`
- `test_SPEC_052_R04_skip_at_any_point_without_creating_data`
- `test_SPEC_052_R05_reopen_from_help`
- `test_SPEC_052_R02_R06_adapts_to_profile_without_inventing`

## Limites

Conteúdo editorial definitivo do tour segue OPEN-30. Revisão formal do grupo pendente.
