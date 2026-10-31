# Plano — SPEC-057

- registrar renda pontual com descrição, valor positivo, data de competência e conta própria opcional;
- proteger dados por titular e impedir duplicidade por `Idempotency-Key`;
- consolidar a renda pontual somente no mês da data informada.

Contratos: `GET` e `POST /api/v1/auth/financial/one-time-incomes` e `GET /api/v1/auth/financial/income-summary?competence=YYYY-MM`.
