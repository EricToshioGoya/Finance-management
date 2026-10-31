# SPEC-061 — Entregar notificação em canal opcional

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-17/26): opt-in por canal; e-mail pelo despachante da SPEC-015 e push por despachante HTTPS configurável; sem configuração = `provider_unavailable`; registro de canal, status e instante; sem retentativa.

## Contrato implementado

`POST|DELETE /api/v1/notifications/push-devices`, `GET /api/v1/notifications/deliveries`; preferências em `PATCH /api/v1/auth/profile/preferences`.

## Testes

- `test_SPEC_061_R01_R03_in_app_is_base_and_channels_are_opt_in`
- `test_SPEC_061_R04_push_uses_configured_adapter_and_registered_device`
- `test_SPEC_061_R02_missing_provider_or_failure_never_records_success`
- `test_SPEC_061_R03_disabling_channel_stops_delivery`

## Limites

Nenhum provedor real configurado; operação depende de OPEN-17. Revisão formal do grupo pendente.
