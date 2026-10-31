# Implementação — SPEC-020: ciclo da fatura, parcelas e alerta (OPEN-12)

Decisão aprovada pelo responsável em 2026-10-31, registrada em `docs/08-specs/questoes-abertas.md`.

## Regras implementadas

- **Ciclo:** `app/domain/cartao.py` (`competencia_da_fatura`) — compra com data até o dia de fechamento entra na fatura que fecha naquele mês; depois do fechamento, na fatura seguinte. Fechamento em dia inexistente (29 a 31) usa o último dia do mês. Despesa recorrente no cartão entra em toda fatura a partir do ciclo da primeira ocorrência.
- **Parcelas:** `POST /api/v1/auth/financial/expenses` aceita `installments` (1 a 48), somente para compra pontual no cartão. São criadas N despesas mensais (mesmo dia; dia inexistente vira o último dia do mês), com o resíduo de centavos na 1ª parcela (`dividir_parcelas`, `Decimal`). As parcelas compartilham `installment_group` e trazem `installment_number`/`installment_count`. A chave de idempotência do cliente fica na 1ª parcela e as demais derivam dela; o reenvio não duplica (C-16).
- **Limite disponível:** limite total − fatura da competência − parcelas futuras (`future_installments`). Faturas anteriores são tratadas como pagas, porque o pagamento de fatura segue fora da OPEN-12.
- **Alerta (R05):** `alert_threshold` por cartão (70% a 100%, padrão 80%), definido no cadastro ou em `PATCH /api/v1/auth/financial/credit-cards/{id}`. `near_limit` é verdadeiro quando (fatura + parcelas futuras) ≥ limite × percentual.
- **Patrimônio (SPEC-028):** o passivo do cartão passou a ser a fatura aberta no ciclo que contém a data de referência (antes: mês civil).

## Persistência

Migration 038: `credit_cards.alert_threshold` e `expenses.installment_group/installment_number/installment_count`, com restrição de consistência (parcelas só no cartão, sem recorrência, 2 a 48).

## Interface web

Cadastro do cartão com o percentual de alerta; campo de parcelas na despesa; fatura com parcelas futuras, dias de fechamento/vencimento e explicação do ciclo.

## Evidências

`backend/tests/test_c02_spec020_card_cycle.py` (domínio e API). Testes anteriores que assumiam o mês civil foram ajustados para datas até o fechamento.

## Fora do escopo

Pagamento de fatura, juros rotativos e registro de financiamento (RF-45 a RF-47).
