# Instruções para trabalho assistido no FinNova

- Ler README, docs/03-requisitos/requisitos.md, arquitetura, ADRs, mapa de Specs e OPEN antes de alterar comportamento.
- Preservar IDs e a baseline do grupo. Usar OPEN para decisão ausente; não inventar revisão, aprovação, medição ou contribuição individual.
- Distinguir motor puro, registro de Simulacao e patrimônio real. Não movimentar saldo por executar projeção.
- Alterar Spec e baseline juntas quando houver decisão humana de mudar comportamento; preservar rastreabilidade e revisar fontes e imagens juntas.
- Não expor ou versionar segredos. Instrução não substitui permissões, hooks, CI ou revisão.
- Executar `python scripts/verificar-documentacao.py` após mudanças documentais. Quando existir código, executar os testes relevantes à Spec alterada.
- Commits devem refletir alterações reais e explicáveis. Publicação segue autorização da sessão e política ativa; não presumir aprovação de PR ou merge.

- SPEC-001 tem implementação autorizada na sessão de 2026-10-15; consultar ADR-007 e o registro de implementação, sem presumir aprovação formal do grupo ou de outras Specs.
- Backend: em `backend`, usar `uv run --frozen ruff check .`, `uv run --frozen ruff format --check .` e `uv run --frozen pytest -q --cov=app --cov-fail-under=90`, com PostgreSQL de desenvolvimento disponível. Frontend: em `frontend`, `npm run lint`, `npm run build`, `npm test` com servidor HTTPS ativo.
- Nunca usar banco de produção nos testes. Os testes da API criam/removem base temporária; os de navegador/smoke criam usuários sintéticos no banco local. Preservar `.env`, chaves e volume de dados locais.
