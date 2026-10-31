# Plano — SPEC-049: Exportar resumo anual auxiliar de rendimentos

## Escopo executado

- Consolidação anual de rendimentos registrados, IR estimado e simulações (distinguindo simulado de registrado).
- Exportação CSV e PDF com aviso de não oficialidade.
- Isolamento por titular e recusa de ano sem dados.

## Camadas e arquivos

- Aplicação: `PlanningTaxService.annual_summary` em `backend/app/application/planning_tax.py`.
- API: `/api/v1/auth/financial/annual-summary` (+ `/csv` e `/pdf`) em `backend/app/main.py`, reaproveitando `pdf_document` e `csv_cell`.
- Web: seção Resumo anual na aba Impostos.
- Testes: `backend/tests/test_spec046_049_planning_tax.py`.

## Riscos e limites

- Simulações entram pelo valor final salvo; o rendimento simulado detalhado depende do tipo de simulação.
- Sem link temporário nem retentativa (OPEN-29 permanece para esses casos).
