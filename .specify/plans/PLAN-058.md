# Plano — SPEC-058

- registrar bônus ou PLR mensal/anual com valor não negativo;
- exigir mês de referência no anual e não diluir o valor entre meses;
- preservar idempotência e isolamento por titular.

Contratos: `GET` e `POST /api/v1/auth/financial/bonuses`; a contribuição aparece no resumo mensal de renda.
