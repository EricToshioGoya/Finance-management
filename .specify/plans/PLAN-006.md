# Plano — SPEC-006

- editar e excluir lançamentos próprios de receitas recorrentes, pontuais, bônus/PLR e despesas;
- recusar acesso a lançamento de outro titular sem revelar seu conteúdo;
- recalcular o resumo mensal a partir dos dados persistidos após cada alteração.

Contrato de agregação: `GET /api/v1/auth/financial/balance-summary?competence=YYYY-MM` retorna receitas, despesas e variação líquida da competência.
