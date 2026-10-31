# Implementação — SPEC-039: alertas e histórico in-app

**Data:** 2026-10-29  
**Política autorizada:** central somente in-app, com quatro tipos de evento, opt-out global e individual, retenção mínima de 30 dias e sem canal externo.

## Entrega

- `POST /api/v1/notifications/events` recebe do produtor autenticado o tipo fechado e uma chave opaca de origem; a mensagem é controlada pelo servidor e não aceita conteúdo financeiro do cliente.
- `GET /api/v1/notifications` devolve no máximo 100 notificações próprias, com filtro `unread_only`; `PATCH /api/v1/notifications/{id}/read` marca uma entrada como lida.
- `GET/PUT /api/v1/notifications/preferences` expõe e altera o opt-out de cada tipo. A preferência global in-app já existente também é respeitada.
- A migration `022_notification_center` cria preferências e histórico com deduplicação por titular, tipo e chave de origem. Não há expurgo antes de 30 dias; portanto, a janela mínima é preservada.

## Limites explícitos

Os módulos de watchlist, vencimento automático de fatura e despesa recorrente ainda poderão se tornar produtores quando suas Specs forem implementadas. Este contrato recebe esses eventos sem criar ciclos de dependência. E-mail, push, webhooks, fila/retry e resumo mensal continuam fora do escopo.

## Verificações

`test_spec039_notifications.py` cobre os quatro tipos, retenção após 31 dias, opt-out global e granular, deduplicação, leitura, titularidade, sessão e confirmação de e-mail. Ruff, compilação e a cadeia Alembic passaram localmente. A execução de integração exige PostgreSQL e o executável de testes não está disponível neste ambiente; a CI da branch é a evidência pendente.
