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

## Tamanho

- [ ] Até 400 linhas alteradas (sem lockfiles); tarefa maior foi dividida em vários PRs

## Auto-revisão (`docs/combinados.md`, seção 2)

<!-- Leia o diff inteiro com a spec aberta. Teste verde não prova correção. -->

- [ ] O código implementa a spec? Cada cláusula `SHALL` alterada tem teste?
- [ ] A spec e a documentação em `/docs` foram atualizadas no mesmo PR?
- [ ] As suítes de risco afetadas foram atualizadas (`docs/10-qualidade/estrategia-de-testes.md`, seção 4)?
- [ ] Sem `float` em cálculo financeiro, sem relógio do sistema no domínio e sem serviço externo real nos testes?
- [ ] Nenhum segredo, senha ou token em código, log ou fixture (C-06, C-10)?

## Riscos de código de agente

- [ ] Nenhuma dependência nova ou, se houver, existe no registro oficial e está no lockfile
- [ ] Nenhuma asserção de teste existente foi alterada para passar (ou a mudança está justificada aqui)
- [ ] Os testes verificam o requisito (valor de referência independente), não repetem a implementação
- [ ] Nenhum arquivo fora do escopo da tarefa
- [ ] Nenhuma lógica nova duplica uma abstração existente
- [ ] Refatoração: sem mudança de comportamento e testes existentes inalterados

## Revisor IA (se houver)

| Comentário | Decisão | Motivo |
|---|---|---|
| <!-- resumo --> | <!-- aceito / rejeitado --> | <!-- por quê --> |

## Uso de agente de IA (C-13)

- **Agente utilizado:** <!-- ex.: Claude Code, Cursor; "nenhum" se não houver -->
- **O que foi gerado:** <!-- arquivos ou trechos -->
- **O que foi revisado e como:** <!-- leitura, testes executados, conferência com a spec -->
