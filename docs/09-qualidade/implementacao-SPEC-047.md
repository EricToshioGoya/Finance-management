# SPEC-047 — Comparar previdência PGBL/VGBL/carteira

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-07/22): tabela regressiva de previdência por aporte; progressiva com alíquota informada pelo usuário; PGBL sobre o total e VGBL sobre o rendimento; carteira própria pela tabela de renda fixa; dedução apenas explicada; versão `2026-10`.

## Contrato implementado

`POST /api/v1/auth/financial/pension-comparisons` (200; 422 `aliquota_progressiva_obrigatoria`, `regime_nao_configurado` ou entrada inválida).

## Testes

- `test_SPEC_047_R01_R03_same_parameters_for_three_modalities`
- `test_SPEC_047_R04_simplified_configurable_tables`
- `test_SPEC_047_R02_regime_not_configured_is_not_replaced`
- `test_SPEC_047_R05_explains_pgbl_context_without_recommendation`

## Limites

Não substitui análise de profissional habilitado. Revisão formal do grupo pendente.
