# Plano — SPEC-005

## Escopo executado

- cadastrar múltiplas contas próprias, com nome, tipo e saldo inicial;
- cadastrar cartões de crédito próprios, com limite, dia de fechamento e vencimento;
- listar as fontes financeiras sem expor dados de outro titular;
- exigir e-mail confirmado para escrita e manter valores/nomes pessoais cifrados em repouso.

## Contratos publicados

- `GET /api/v1/auth/financial/sources`
- `POST /api/v1/auth/financial/accounts`
- `POST /api/v1/auth/financial/credit-cards`

O vínculo de lançamentos a uma fonte será consumido pelas Specs de receitas e despesas. Ciclo, fatura e parcelamento permanecem no recorte da SPEC-020/OPEN-12.
