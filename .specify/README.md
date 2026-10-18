# .specify — Planos e tarefas derivados das specs

Pasta de trabalho do fluxo Spec-Driven Development definido em `CLAUDE.md` (seção 2).

| Pasta | Conteúdo | Convenção de nome |
|---|---|---|
| `docs/08-specs/` | Specs (fonte única de verdade, revisadas junto com o código) | `SPEC-NNN-descricao.md` |
| `.specify/plans/` | Plano técnico de implementação de cada spec | `PLAN-NNN.md` |
| `.specify/tasks/` | Tarefas ordenadas e verificáveis derivadas do plano | `TASKS-NNN.md` |

As specs ficam em `docs/08-specs/` porque fazem parte da documentação avaliada do projeto. O número `NNN` do plano e das tarefas é o mesmo da spec de origem.
