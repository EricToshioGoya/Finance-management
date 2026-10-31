# SPEC-045 — Dividir despesas e registrar acertos

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-03/31): divisão 50/50 ou percentual com duas casas somando 100%; centavo restante para quem pagou; somente o pagador edita/remove; acerto com `Idempotency-Key`, limitado ao saldo e permitido após o fim do vínculo.

## Contrato implementado

`POST /api/v1/auth/sharing/expenses` (201), `PATCH /api/v1/auth/sharing/expenses/{id}`, `DELETE /api/v1/auth/sharing/expenses/{id}` (204), `GET /api/v1/auth/sharing/balance?link_id`, `POST /api/v1/auth/sharing/settlements` (201, idempotente). Erros: 404 despesa de outro titular, 409 sem vínculo ativo/despesa já compartilhada/nada a pagar, 422 percentuais ou acerto acima do saldo.

## Testes

- `test_SPEC_045_R01_R03_equal_and_custom_split`
- `test_SPEC_045_R02_invalid_split_or_non_member_does_not_change_balance`
- `test_SPEC_045_R04_balance_updates_on_edit_and_delete`
- `test_SPEC_045_R05_settlement_reduces_balance_idempotently`
- `test_SPEC_045_R06_both_members_see_composition`

## Limites

Despesa recorrente compartilhada entra uma vez no saldo, pelo valor do registro; a repetição mensal compartilhada exigiria decisão adicional em OPEN-21/31. Revisão formal do grupo pendente.
