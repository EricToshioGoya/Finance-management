# SPEC-050 — Comparar score por grupo anônimo

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-05/11): grupo do mesmo perfil, mínimo de 30, média e mediana do score e da taxa de poupança; comparação ativada por padrão; opt-out também retira o titular do agregado.

## Contrato implementado

`GET /api/v1/auth/financial/health-score/benchmark`, `GET|PUT /api/v1/auth/profile/privacy`. 403 sem e-mail verificado.

## Testes

- `test_SPEC_050_R01_R03_aggregated_comparison_for_same_profile`
- `test_SPEC_050_R02_R04_group_below_minimum_shows_nothing`
- `test_SPEC_050_R05_opt_out_keeps_score_and_leaves_group`

## Limites

O grupo depende de scores já calculados na competência. Revisão formal do grupo pendente.
