# SPEC-049 — Exportar resumo anual auxiliar de rendimentos

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-05/21/29): consolidação por ano-calendário com origem explícita; CSV e PDF pela exportação existente; aviso de não oficialidade no corpo; download direto; ano sem dados retorna 404.

## Contrato implementado

`GET /api/v1/auth/financial/annual-summary?year=AAAA`, `/annual-summary/csv`, `/annual-summary/pdf`.

## Testes

- `test_SPEC_049_R01_R03_consolidates_registered_and_simulated`
- `test_SPEC_049_R04_document_is_not_official`
- `test_SPEC_049_R02_year_without_data_and_other_owner`

## Limites

Documento auxiliar; não substitui informes de instituições financeiras. Revisão formal do grupo pendente.
