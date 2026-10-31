# Implementação — SPEC-028: patrimônio real e itens manuais

**Data:** 2026-10-29  
**Política autorizada:** contas e faturas abertas são origens reais; itens manuais pertencem ao titular; projeções nunca integram patrimônio; não há snapshot histórico ou financiamento nesta entrega.

## Entrega

- A consulta autenticada consolida saldo de contas, faturas abertas e itens manuais, retornando ativos, passivos, origem e patrimônio líquido.
- Itens manuais têm nome cifrado, valor positivo, tipo ativo/passivo e taxa anual opcional; criação, edição e exclusão exigem e-mail confirmado.
- Os identificadores de item são sempre filtrados pelo titular. Item de outro usuário permanece inexistente para ele.
- O resultado é recalculado por consulta: `ativos − passivos`. Nenhuma simulação de cálculo ou investimento é lida como origem patrimonial.

## Verificações

`test_spec028_net_worth.py` cobre conta 100 menos dívida manual 30, projeção excluída, fatura como passivo, validação, confirmação de e-mail, edição/exclusão e isolamento entre titulares. A CI executa a suíte PostgreSQL completa e o cliente web; lint, migration e documentação são validados no PR.
