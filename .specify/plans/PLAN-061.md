# Plano — SPEC-061: Entregar notificação em canal opcional

## Escopo executado

- E-mail e push como canais opcionais configuráveis; in-app obrigatório.
- Adaptador HTTPS provider-neutral; registro mínimo de resultado.
- Respeito à desativação do canal.

## Camadas e arquivos

- Infraestrutura: `backend/app/infrastructure/channel_delivery.py` (`HttpsChannelDelivery`, `UnconfiguredChannelDelivery`).
- Configuração: `push_webhook_url` em `backend/app/config.py`.
- Aplicação: `AuthService.dispatch_external`, chamado por `create_notification`.
- Persistência: `PushDeviceRecord`, `NotificationDeliveryRecord`; migração `035_channels_and_monthly_summary.py`.
- API: rotas `/api/v1/notifications/push-devices` e `/deliveries`.
- Web: `ReportsAndChannels` (aba Minha conta).
- Testes: `backend/tests/test_spec040_061_channels_summary.py` (dublês, sem rede — C-17).

## Riscos e limites

- Sem retentativa nem fila (OPEN-26); falha fica registrada como `failed`.
- Push real depende de app móvel e de provedor (OPEN-17).
