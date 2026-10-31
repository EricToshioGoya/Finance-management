# SPEC-040 — Enviar resumo mensal automático optativo

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-05/21/26): opt-in; job agendável; mês anterior no fuso de São Paulo; renda, gastos, patrimônio e score; envio por e-mail via SPEC-061; um envio por titular e mês; falha registrada como falha.

## Contrato implementado

`GET|PUT /api/v1/auth/profile/reports`, `GET /api/v1/auth/financial/monthly-summaries`, `GET /api/v1/auth/financial/monthly-summaries/{AAAA-MM}/pdf` (422 para mês não fechado).

## Testes

- `test_SPEC_040_R01_R03_R04_sends_previous_month_pdf_by_email`
- `test_SPEC_040_R02_failure_is_not_recorded_as_sent`
- `test_SPEC_040_R05_opt_out_and_previous_month_only`

## Limites

Envio real depende de despachante de e-mail configurado (OPEN-17). Revisão formal do grupo pendente.
