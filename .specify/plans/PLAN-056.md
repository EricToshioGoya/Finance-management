# Plano — SPEC-056

## Escopo executado

- cadastrar mais de uma fonte de receita recorrente com valor mensal positivo;
- iniciar a vigência no dia de criação ou na data informada;
- permitir vínculo opcional somente a uma conta do próprio titular;
- impedir duplicidade de reenvio com `Idempotency-Key` isolada por titular;
- listar receitas recorrentes exclusivamente do titular autenticado.

## Contratos publicados

- `GET /api/v1/auth/financial/recurring-incomes`
- `POST /api/v1/auth/financial/recurring-incomes` com cabeçalho obrigatório `Idempotency-Key`.

O cálculo consolidado de saldo/orçamento será ligado pelas Specs consumidoras; esta capacidade registra corretamente a fonte e a competência inicial, sem criar lançamento pago ou movimentar saldo.
