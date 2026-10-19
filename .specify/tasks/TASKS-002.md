# TASKS-002 — Motor de juros compostos

- **Plano:** [PLAN-002](../plans/PLAN-002.md)
- **Spec:** [SPEC-002](../../docs/08-specs/SPEC-002-motor-de-juros-compostos.md)
- **Issue:** [#38](https://github.com/EricToshioGoya/Finance-management/issues/38)

| Ordem | Tarefa | Cláusulas | Verificação | Situação |
|---|---|---|---|---|
| T01 | Criar `pyproject.toml` (Python 3.12+, layout `src/`, extras `dev`, configuração de pytest, cobertura e ruff) | Q1 | `pytest --collect-only` executa sem erro | ☑ |
| T02 | Criar os pacotes `finnova`, `finnova.domain` e `finnova.domain.simulador` | — | Importação do pacote nos testes | ☑ |
| T03 | Escrever os testes unitários, um ou mais por cláusula, com o ID no nome e na docstring | R01 a R08, INV-01, INV-02 | Testes falham antes da implementação | ☑ |
| T04 | Implementar `TipoTaxa`, `TipoPeriodo`, `EvolucaoMensal` e `ResultadoEvolucao` imutáveis | R04, R05, R07 | Testes de estrutura e tipos | ☑ |
| T05 | Implementar a validação de entrada | R06, R07 | Cenário 3 e testes de tipo | ☑ |
| T06 | Implementar a conversão de taxa e de período | R02, R03, INV-01 | Cenário 1 e teste de anos → meses | ☑ |
| T07 | Implementar a iteração mensal, os totais e o arredondamento na saída | R01, R04, R05, R08 | Cenários 1, 2, 4 e 5 | ☑ |
| T08 | Executar `ruff check .` e `pytest` com cobertura de, no mínimo, 80% | Q1 | Saída registrada na seção "Resultado" | ☑ |
| T09 | Atualizar `CLAUDE.md` (seção 5) e `README.md` (Como executar) com os comandos | — | Revisão | ☑ |

## Resultado

Execução em 2026-10-19, Python 3.12.3. A implementação (T01 a T08) foi feita por um subagente do Claude Code em contexto novo, a partir apenas do `CLAUDE.md`, da spec, deste plano e destas tarefas; a revisão e a T09 foram feitas na sessão principal.

| Verificação | Comando | Resultado |
|---|---|---|
| Lint | `ruff check .` | Sem erros |
| Formatação | `ruff format --check src tests` | 5 arquivos já formatados |
| Testes | `pytest` | 51 testes passando |
| Cobertura (Q1, RNF-07) | `pytest` (`--cov-branch --cov-fail-under=80`) | 100% de linhas e de ramos em `finnova.domain.simulador` |
| Teste de mutação (manual) | 7 mutações em cópia do código | 7 detectadas: taxa dividida por 12, `ROUND_HALF_EVEN`, arredondamento intermediário, aporte no início do mês, total investido sem o valor inicial, anos sem conversão e período zero aceito |

### Cláusula → teste

Arquivo: `tests/unit/domain/simulador/test_juros_compostos.py`. Todos os nomes começam com `test_spec002_`.

| Cláusula | Testes | Resultado |
|---|---|---|
| R01 | `r01_saldo_mensal_com_aporte_no_fim_do_periodo` (Cenário 2); `r01_juros_incidem_sobre_o_saldo_do_mes_anterior` (Cenário 4) | Passa |
| R02 | `r02_converte_taxa_anual_por_equivalencia_composta` (Cenário 1); `r02_calculo_com_taxa_anual_usa_taxa_mensal_equivalente`; `r02_taxa_mensal_informada_nao_e_convertida` | Passa |
| R03 | `r03_converte_um_ano_em_doze_meses`; `r03_converte_dois_anos_em_vinte_e_quatro_meses`; `r03_horizonte_de_trinta_anos` | Passa |
| R04 | `r04_serie_mensal_com_saldo_inicial_aporte_juros_e_saldo_final`; `r04_saldo_inicial_do_mes_e_o_saldo_final_do_mes_anterior`; `r04_r05_resultado_e_imutavel` | Passa |
| R05 | `r05_totais_sem_aporte_mensal` (Cenário 1); `r05_totais_com_aportes_mensais` (Cenário 2); `r05_valor_total_investido_inclui_valor_inicial` (Cenário 4) | Passa |
| R06 | Um teste por entrada inválida (valor inicial, aporte e taxa negativos; período zero e negativo; taxa anual negativa na conversão; valores não finitos), `r06_valida_entradas_antes_de_calcular`, `r06_aceita_zero_nos_valores_e_na_taxa` e `r06_zero_negativo_nao_e_negativo` (Cenário 3) | Passa |
| R07 | `r07_resultado_usa_somente_decimal`; `r07_float_na_entrada_gera_type_error`; `r07_bool_na_entrada_gera_type_error`; `r07_periodo_aceita_apenas_int`; `r07_conversao_de_taxa_recusa_float`; `r07_tipo_de_taxa_e_de_periodo_exigem_enum`; `r07_aceita_int_nos_valores_monetarios`; `r07_nao_altera_o_contexto_decimal_global` | Passa |
| R08 | `r08_arredonda_apenas_na_saida` (Cenário 5); `r08_usa_round_half_up`; `r08_soma_exibida_pode_diferir_do_total`; `r08_valores_monetarios_com_duas_casas_decimais`; `r08_taxa_mensal_nao_e_arredondada` | Passa |
| INV-01 | `inv01_taxa_anual_nao_e_convertida_por_divisao_simples`; `inv01_taxa_mensal_recompoe_a_taxa_anual` | Passa |
| INV-02 | `inv02_calculo_em_decimal_exato_sem_float`; `inv02_valores_do_resultado_nao_sao_float` | Passa |
| Q1 | Limite `--cov-fail-under=80` no `pyproject.toml` | 100% |
