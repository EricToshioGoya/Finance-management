# Plano — SPEC-047: Comparar previdência PGBL/VGBL/carteira

## Escopo executado

- Comparação lado a lado com os mesmos parâmetros.
- Tabelas simplificadas e versionadas (regressiva por aporte; progressiva com alíquota informada).
- Contexto educativo de quando o PGBL costuma ser vantajoso, sem recomendação.

## Camadas e arquivos

- Domínio: `comparar_previdencia` e `aliquota_previdencia_regressiva` em `backend/app/domain/expansion.py`.
- Aplicação: `PlanningTaxService.pension`.
- API: `POST /api/v1/auth/financial/pension-comparisons`.
- Web: `PensionComparison` (aba Investimentos).
- Testes: `backend/tests/test_spec046_049_planning_tax.py`.

## Riscos e limites

- Simplificação: sem taxas de administração/carregamento e sem cálculo da dedução do PGBL.
- Tabelas fixadas como regra interna versionada; mudanças legais exigem nova versão.
