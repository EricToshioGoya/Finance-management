# Plano — SPEC-048: Estimar imposto de operações e lembrete DARF

## Escopo executado

- Estimativa de IR por regime com tabela interna versionada.
- Isenção de ações até R$ 20 mil de vendas no mês; renda fixa sem DARF.
- Data-limite do DARF (último dia útil do mês seguinte) e aviso educativo; estimativas persistidas por titular.

## Camadas e arquivos

- Domínio: `estimar_ir`, `vencimento_darf`, `feriados_nacionais` e `pascoa` em `backend/app/domain/expansion.py`.
- Persistência: `TaxEstimateRecord`; migração `033_tax_estimates.py`.
- Aplicação: `PlanningTaxService` (criar, listar e excluir).
- API: `/api/v1/auth/financial/tax-estimates`.
- Web: aba Impostos (`Taxes`).
- Testes: `backend/tests/test_spec046_049_planning_tax.py`.

## Riscos e limites

- Sem compensação de prejuízos e sem regra de DARF mínimo; ambos sinalizados como fora do recorte.
- Feriados: apenas nacionais fixos e Sexta-feira Santa.
