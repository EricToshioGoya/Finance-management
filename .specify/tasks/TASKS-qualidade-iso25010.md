# Tarefas — Revisão de qualidade ISO/IEC 9126/25010

1. [x] Escrever o teste de envio simultâneo para despesa e rendas; reproduzir a falha (despesa: 503 + 201).
2. [x] Tratar `IntegrityError` na criação de despesa e devolver o registro gravado; registrar na SPEC-059.
3. [x] Escrever testes unitários de `cartao`, `market_metrics`, `foreign_currency`, `education`, `identity` e `expansion`.
4. [x] Adicionar o gate de cobertura unitária do domínio na CI.
5. [x] Implementar request id, log JSON e registro de erro não tratado; testes `test_SPEC_060_R07` a `R09`.
6. [x] Acrescentar SPEC-060-R07 a R09, CA-007 a CA-009 e T-008 a T-010.
7. [x] Criar templates de PR e de defeito.
8. [x] Criar scripts de backup e de verificação de restauração; executar caso positivo e negativo; registrar evidência e OPEN-32.
9. [x] Avaliar a limpeza local no logout (mantido o comportamento atual; justificativa no plano).
10. [x] Isolar o transporte HTTP do mobile e testá-lo com fetch falso; conferir o bundle Android.
11. [x] Atualizar o modelo de qualidade e a estratégia de testes.
12. [x] Rodar ruff, a suíte completa com cobertura, os verificadores documentais e os testes do mobile.
