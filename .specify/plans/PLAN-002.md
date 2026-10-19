# PLAN-002 — Motor de juros compostos

- **Spec:** [SPEC-002](../../docs/08-specs/SPEC-002-motor-de-juros-compostos.md) (Aprovada; revisão de 2026-10-19)
- **Issue:** [#38](https://github.com/EricToshioGoya/Finance-management/issues/38)
- **Cláusulas:** SPEC-002-R01 a R08; INV-01 e INV-02; critério de qualidade Q1 (RNF-07)

---

## 1. Camadas afetadas

Apenas a camada de **domínio** (ADR-001, ADR-002). O motor é Python puro: não importa FastAPI nem SQLAlchemy e não faz I/O (`CLAUDE.md` C-05). API, persistência e leitura de indicadores ficam para a SPEC-010.

## 2. Estrutura de arquivos

Confirma a estrutura proposta em `docs/07-arquitetura/arquitetura.md`, seção 6, com subdivisão pelo módulo **simulador**:

```
pyproject.toml                                   # projeto, dependências de desenvolvimento, pytest, cobertura e ruff
src/finnova/__init__.py
src/finnova/domain/__init__.py
src/finnova/domain/simulador/__init__.py         # exporta a interface pública do motor
src/finnova/domain/simulador/juros_compostos.py  # motor (SPEC-002)
tests/unit/domain/simulador/test_juros_compostos.py
```

## 3. Interface pública

| Elemento | Tipo | Conteúdo |
|---|---|---|
| `TipoTaxa` | `Enum` | `MENSAL`, `ANUAL` |
| `TipoPeriodo` | `Enum` | `MESES`, `ANOS` |
| `EvolucaoMensal` | `dataclass` imutável | `mes`, `saldo_inicial`, `aporte`, `juros`, `saldo_final` (R04) |
| `ResultadoEvolucao` | `dataclass` imutável | `taxa_mensal`, `meses`, `evolucao` (tupla de `EvolucaoMensal`), `valor_total_investido`, `total_juros`, `montante_final_bruto` (R05) |
| `converter_taxa_anual_para_mensal(taxa_anual)` | função | Equivalência composta (R02, INV-01) |
| `calcular_evolucao(valor_inicial, aporte_mensal, taxa_juros, tipo_taxa, periodo, tipo_periodo)` | função | Implementação da operação `Simulacao.calcularEvolucao()` do modelo de domínio (R01 a R08) |

Os nomes seguem o glossário (`requisitos.md`, seção 8.1) em `snake_case` (PEP 8). A entidade `Simulacao` passará a delegar a este motor na SPEC-010.

## 4. Decisões de implementação

Decisões técnicas que não criam regra de negócio:

1. **Forma da taxa:** taxa em forma unitária (12% = `Decimal("0.12")`), como exige a fórmula da seção 4 da spec.
2. **Precisão:** cálculo em contexto decimal local com 34 dígitos significativos (equivalente ao `decimal128`), sem alterar o contexto global da aplicação.
3. **Tipos de entrada:** valores monetários e taxa aceitam `Decimal` ou `int`. `float` e `bool` são rejeitados com `TypeError`, para que nenhum valor binário entre no cálculo (R07, INV-02). `periodo` aceita apenas `int`.
4. **Arredondamento (R08):** cada valor monetário da série e do resumo é arredondado para 2 casas com `ROUND_HALF_UP` na montagem do resultado. A `taxa_mensal` não é valor monetário e é devolvida sem arredondamento.
5. **Total de juros:** calculado como montante final bruto menos valor total investido, ambos sem arredondamento, e arredondado depois (R05, R08).

## 5. Dependências

| Dependência | Uso | ADR? |
|---|---|---|
| Biblioteca padrão (`decimal`, `dataclasses`, `enum`) | Motor | Não |
| `pytest`, `pytest-cov` | Testes e cobertura (desenvolvimento) | Não: ferramentas de teste já previstas em `docs/10-qualidade/estrategia-de-testes.md` |
| `ruff` | Lint (desenvolvimento) | Não: proposta já registrada na estratégia de testes |

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Potência com expoente fracionário em `Decimal` é corretamente arredondada "quase sempre" (documentação do Python) | Precisão de 34 dígitos e conferência contra referência independente: `1000 × 1,12 = 1120,00` (Cenário 1) |
| Teste que apenas repete a implementação | Valores esperados calculados à mão e registrados na spec (Cenários 1, 2, 4 e 5) |
| Diferença de centavos entre a soma dos valores exibidos na série e o total | Consequência aceita na decisão de OPEN-01; coberta pelo Cenário 5 |

## 7. Verificação

Comandos registrados em `CLAUDE.md`, seção 5:

- `ruff check .` sem erros.
- `pytest` com todos os testes passando e cobertura de linhas e ramos do pacote `finnova.domain.simulador` maior ou igual a 80% (`--cov-fail-under=80`).
- Tabela cláusula → teste → resultado registrada em `TASKS-002.md` e na descrição do PR.
