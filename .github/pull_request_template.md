## Resumo

<!-- O que muda e por quê, em poucas linhas. -->

Closes #

## Spec e cláusulas

<!-- Specs alteradas e cláusulas SPEC-NNN-Rxx implementadas ou corrigidas (C-01). -->

## Verificação

- [ ] `uv run --frozen ruff check .` e `uv run --frozen ruff format --check .`
- [ ] `uv run --frozen pytest -q --cov=app --cov-fail-under=90`
- [ ] `npm run lint` e `npm run build` (frontend), quando aplicável
- [ ] `npm run typecheck` e `npm test` (mobile), quando aplicável
- [ ] `python scripts/verificar-documentacao.py` e `python scripts/verificar-c02.py --estrito`

## Auto-revisão (`docs/combinados.md`, seção 2)

- [ ] O código implementa a spec? Cada cláusula `SHALL` alterada tem teste?
- [ ] A spec e a documentação em `/docs` foram atualizadas no mesmo PR?
- [ ] As suítes de risco afetadas foram atualizadas (`docs/10-qualidade/estrategia-de-testes.md`, seção 4)?
- [ ] Sem `float` em cálculo financeiro, sem relógio do sistema no domínio e sem serviço externo real nos testes?
- [ ] Nenhum segredo, senha ou token em código, log ou fixture (C-06, C-10)?

## Uso de agente de IA (C-13)

- **Agente utilizado:** <!-- ex.: Claude Code, Cursor; "nenhum" se não houver -->
- **O que foi gerado:** <!-- arquivos ou trechos -->
- **O que foi revisado e como:** <!-- leitura, testes executados, conferência com a spec -->
