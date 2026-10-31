# Plano — SPEC-055

## Escopo executado

- disponibilizar as nove categorias padrão com cores determinísticas;
- criar categoria pessoal do titular, com nome cifrado e unicidade por titular;
- ocultar/reativar somente uma categoria padrão do próprio titular;
- exigir confirmação de e-mail para alterar categorias e preservar a listagem isolada;
- entregar contratos HTTP, interface PT/EN, migração e testes de aceitação.

## Contratos publicados

- `GET /api/v1/auth/categories`
- `POST /api/v1/auth/categories`
- `PATCH /api/v1/auth/categories/standard/{category_key}`
