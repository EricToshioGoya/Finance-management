# Plano — SPEC-016

## Escopo executado

- criar token opaco de recuperação, persistido apenas como digest, com uso único e TTL de 30 minutos;
- manter resposta pública idêntica para e-mail existente, inexistente e falha de entrega;
- permitir redefinição por token e alteração autenticada por senha atual;
- revogar todas as sessões do titular na mesma transação que altera o hash;
- expor a experiência web em PT/EN e testes de aceitação.

## Contratos publicados

- `POST /api/v1/auth/password-recovery`
- `POST /api/v1/auth/password-recovery/confirm`
- `PATCH /api/v1/auth/password`
