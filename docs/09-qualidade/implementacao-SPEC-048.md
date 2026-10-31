# SPEC-048 — Estimar imposto de operações e lembrete DARF

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-03/07/22): ações 15% com isenção até R$ 20 mil/mês; FIIs e day trade 20%; renda fixa retida na fonte; sem compensação de prejuízos; DARF no último dia útil do mês seguinte considerando feriados nacionais fixos e Sexta-feira Santa; estimativa persistida.

## Contrato implementado

`POST|GET /api/v1/auth/financial/tax-estimates`, `DELETE /api/v1/auth/financial/tax-estimates/{id}`. 422 para regra indisponível (ex.: renda fixa sem prazo).

## Testes

- `test_SPEC_048_R03_regimes_and_stock_exemption`
- `test_SPEC_048_R04_R05_darf_due_last_business_day_of_next_month`
- `test_SPEC_048_R01_R06_api_persists_estimate_with_notice`
- `test_SPEC_048_R02_losses_and_unknown_rules_are_not_invented`

## Limites

Estimativa educativa; não substitui contador nem e-CAC. Revisão formal do grupo pendente.
