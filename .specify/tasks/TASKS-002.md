# TASKS-002 — Motor de juros compostos

- **Plano:** [PLAN-002](../plans/PLAN-002.md)
- **Spec:** [SPEC-002](../../docs/08-specs/SPEC-002-motor-de-juros-compostos.md)
- **Issue:** [#38](https://github.com/EricToshioGoya/Finance-management/issues/38)

| Ordem | Tarefa | Cláusulas | Verificação | Situação |
|---|---|---|---|---|
| T01 | Criar `pyproject.toml` (Python 3.12+, layout `src/`, extras `dev`, configuração de pytest, cobertura e ruff) | Q1 | `pytest --collect-only` executa sem erro | ☐ |
| T02 | Criar os pacotes `finnova`, `finnova.domain` e `finnova.domain.simulador` | — | Importação do pacote nos testes | ☐ |
| T03 | Escrever os testes unitários, um ou mais por cláusula, com o ID no nome e na docstring | R01 a R08, INV-01, INV-02 | Testes falham antes da implementação | ☐ |
| T04 | Implementar `TipoTaxa`, `TipoPeriodo`, `EvolucaoMensal` e `ResultadoEvolucao` imutáveis | R04, R05, R07 | Testes de estrutura e tipos | ☐ |
| T05 | Implementar a validação de entrada | R06, R07 | Cenário 3 e testes de tipo | ☐ |
| T06 | Implementar a conversão de taxa e de período | R02, R03, INV-01 | Cenário 1 e teste de anos → meses | ☐ |
| T07 | Implementar a iteração mensal, os totais e o arredondamento na saída | R01, R04, R05, R08 | Cenários 1, 2, 4 e 5 | ☐ |
| T08 | Executar `ruff check .` e `pytest` com cobertura de, no mínimo, 80% | Q1 | Saída registrada na seção "Resultado" | ☐ |
| T09 | Atualizar `CLAUDE.md` (seção 5) e `README.md` (Como executar) com os comandos | — | Revisão | ☐ |

## Resultado

A preencher após a execução da T08.
