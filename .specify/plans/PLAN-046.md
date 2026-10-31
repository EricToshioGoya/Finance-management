# Plano — SPEC-046: Projetar aposentadoria e renda estimada

## Escopo executado

- Projeção do patrimônio até a idade-alvo pelo motor de juros compostos.
- Renda mensal estimada por taxa de retirada configurável (padrão 4% a.a.).
- Sugestão de taxa a partir do cache SELIC, sem substituição silenciosa; aviso educativo.

## Camadas e arquivos

- Domínio: `projetar_aposentadoria` em `backend/app/domain/expansion.py`.
- Aplicação: `PlanningTaxService.retirement` em `backend/app/application/planning_tax.py`.
- API: `POST /api/v1/auth/financial/retirement-projections`.
- Web: `RetirementPlanner` (aba Planejamento).
- Testes: `backend/tests/test_spec046_049_planning_tax.py`.

## Riscos e limites

- Valores nominais (sem inflação) — explicitado nas hipóteses.
- A taxa de retirada é uma regra de bolso educativa, não benefício garantido.
