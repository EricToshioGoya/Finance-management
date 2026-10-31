# Plano — SPEC-059

- registrar despesa pontual ou recorrente com valor positivo, categoria e uma única origem própria (conta ou cartão);
- preservar idempotência por titular e cifrar a descrição em repouso;
- listar imediatamente o lançamento e incluí-lo no resumo mensal de saldo.

Contratos: `GET` e `POST /api/v1/auth/financial/expenses`. A criação exige `Idempotency-Key`.
