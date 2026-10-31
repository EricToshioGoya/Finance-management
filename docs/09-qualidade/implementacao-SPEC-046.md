# SPEC-046 — Projetar aposentadoria e renda estimada

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-03/07/22): taxa obrigatória com sugestão do cache; retirada padrão 4% a.a. configurável; valores nominais; sem persistência.

## Contrato implementado

`POST /api/v1/auth/financial/retirement-projections` (200; 422 `idade_alvo_deve_ser_futura` ou `taxa_retirada_invalida`; 403 e-mail não verificado).

## Testes

- `test_SPEC_046_R01_R03_R04_projects_wealth_with_engine`
- `test_SPEC_046_R02_target_age_must_be_future`
- `test_SPEC_046_R05_income_uses_configurable_withdrawal_rate`
- `test_SPEC_046_R03_suggests_cached_indicator_without_inventing`
- `test_SPEC_046_R06_educational_notice_and_no_persistence`

## Limites

Não considera inflação, INSS nem benefícios públicos. Revisão formal do grupo pendente.
