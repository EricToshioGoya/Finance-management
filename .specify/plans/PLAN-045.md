# Plano — SPEC-045: Dividir despesas e registrar acertos

## Escopo executado

- Marcar despesa própria como compartilhada com divisão 50/50 ou percentual.
- Saldo consolidado quem deve quem, recalculado a partir dos lançamentos persistidos.
- Acerto de contas idempotente e limitado ao saldo pendente; composição visível aos dois membros.

## Camadas e arquivos

- Persistência: `SharedExpenseRecord` e `SettlementRecord`; migração `032_shared_accounts.py`.
- Aplicação: `backend/app/application/sharing.py` (`split_amount`, `share_expense`, `balance`, `settle`).
- Apresentação: rotas `/api/v1/auth/sharing/expenses`, `/balance` e `/settlements`.
- Web: aba Compartilhado (`frontend/src/Sharing.tsx`).
- Testes: `backend/tests/test_spec044_045_sharing.py`.

## Riscos e limites

- Arredondamento: parte do outro membro truncada ao centavo; centavo restante com o pagador (OPEN-03/31).
- Acerto concorrente: o vínculo é bloqueado (`FOR UPDATE`) e a chave de idempotência é única por vínculo e pagador.
