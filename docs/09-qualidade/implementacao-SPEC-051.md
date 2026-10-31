# SPEC-051 — Conceder conquistas sem efeito financeiro

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-11/26): três conquistas fixas, avaliação na consulta, concessão única com notificação in-app respeitando preferências, sem efeito financeiro.

## Contrato implementado

`GET /api/v1/auth/financial/achievements` (403 sem e-mail verificado).

## Testes

- `test_SPEC_051_R01_R03_R05_grants_once_and_notifies`
- `test_SPEC_051_R04_shows_progress_of_next_achievements`
- `test_SPEC_051_R03_three_months_within_budget`
- `test_SPEC_051_R02_R06_cosmetic_only_and_respects_preferences`

## Limites

Sem canais externos para a notificação de conquista (SPEC-061 trata canais opcionais). Revisão formal do grupo pendente.
