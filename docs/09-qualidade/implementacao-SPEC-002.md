# Registro de implementação — SPEC-002

Data: 2026-10-23. Pedido explícito do usuário para seguir o mapa após SPEC-001. Issue [#13](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/issues/13). Branch `feature/13-motor-spec002`, baseada em `aabd4ec0092c373a395a1420a1825872b08b76a2` de `feature/spec001-completa`. Não declara merge de PR #12 ou desta entrega, deploy ou aprovação formal do grupo.

## Entrega

Motor bruto no domínio puro, Decimal com contexto isolado de 50 dígitos, equivalência mensal/anual nos dois sentidos, anos/meses inteiros, aportes ao fim do mês e série/resumo imutáveis. Erro por campo/código, validação estrita de Decimal/unidades/prazo, rejeição controlada de limites técnicos. Política de OPEN-03/15 e recorte de OPEN-06 no ADR-002; plano/tarefas em `.specify`.

## Evidências locais executadas

| Verificação | Resultado |
|---|---|
| pytest tests/unit com cobertura específica do motor | 76 testes aprovados; 100% de cobertura de linhas (87 statements, 0 missing), mínimo requerido 80% |
| Ruff check/format do backend e benchmark | Aprovados |
| Execução sem terceiros | Teste subprocess Python -I -S importa e executa domínio; sem FastAPI/ORM/HTTP |
| Contexto Decimal externo | Precisão baixa, rounding diferente, trap Inexact e flags do chamador preservados; concorrência com contextos diferentes mantém resultado |
| Benchmark sequencial local | 5 aquecimentos + 100 amostras por perfil, conforme tabela |

Dependências locais reaproveitadas do ambiente de teste anterior com as versões do projeto; `uv sync --offline --frozen` não pôde reconstruir todo o ambiente por cache incompleto. Não alterados lockfiles/dependências para contornar isso. CI usa instalação congelada limpa e terá evidência separada. Um aviso de depreciação HTTPX/Starlette é emitido pelo conftest de autenticação, que não solicita fixture/banco nos testes unitários.

## Rastreabilidade executável

| Cláusula / critério | Evidência em backend/tests/unit/test_spec002.py |
|---|---|
| SPEC-002-R01 / CA-001 | Referência 1000, 12% anual, 12 meses: montante exibível 1120; taxa mensal equivalente, sem divisão proporcional |
| SPEC-002-R02 / CA-002 | Inicial zero, aporte 100, 1% mensal, 2 meses: saldos 100 e 201 |
| SPEC-002-R03 / CA-003 | Taxa zero, inicial/aporte zero, zero assinado; arredondamento HALF_UP no consumo |
| SPEC-002-R04 / CA-004 | Negativos, NaN/sNaN/infinidades, float/string/bool/None, prazos inválidos, unidades inclusive não hashable, limites técnicos e erros sem valores |
| SPEC-002-R05 / CA-005 | 1 ano=12 meses e 5 anos=60 meses, resultado completo idêntico |
| SPEC-002-R06 / CA-006 | Taxa 1% mensal resulta aproximadamente 12,6825030132% anual; cinco taxas em ida/volta e identidade |
| SPEC-002-R07 / CA-007 | Cinco perfis contra fórmula fechada de anuidade a 80 dígitos, cada mês, juros/investido/montante; evita arredondamento mensal precoce |
| SPEC-002-R08 / CA-008 | Repetição, imutabilidade, contexto/traps/flags, threads, isolamento -I -S e inspeção AST de importações/ausência de constantes float |

## Perfil local de desempenho (não é P95 da aplicação)

Python 3.12.14; Linux-6.18.55-x86_64-with-glibc2.39; 9 CPUs lógicas reportadas. Execução sequencial; inicial 1000, aporte 100, taxa anual 12%. Quantil por posto mais próximo, sem interpolação. Tempos em nanossegundos; carga/ambiente de produção não foram simulados.

| Meses | Amostras | P50 ns | P95 ns |
|---|---|---|---|
| 12 | 100 | 108978 | 289442 |
| 120 | 100 | 224270 | 721610 |
| 360 | 100 | 554639 | 942992 |
| 600 | 100 | 788652 | 1320618 |

Todos os perfis ficaram abaixo do orçamento de 3.000.000.000 ns do motor. Script reproduzível: `python scripts/benchmark-motor.py --saida .local/benchmark-spec002.json`. Relógio/ambiente/arquivo pertencem ao script de medição, fora do domínio. O workflow dedicado publica JSON como artefato.

## CI e limitações

Código validado no commit `305ff211a8c751e8d4401dc061bbb5d81c398866`, PR [#14](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/pull/14). Os três workflows passaram:

- [SPEC-002 motor puro](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/actions/runs/39894164761): instalação limpa congelada, 76 testes e 100% de cobertura de linhas do motor, Ruff e benchmark; sem banco/configuração de segredos.
- [Regressão backend/HTTPS/navegador](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/actions/runs/39894164650): 114 testes de backend (incluem os 76 do motor), cobertura total 96,62%, smoke HTTPS com certificado/hostname e 8 testes Playwright aprovados.
- [Integridade documental](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/actions/runs/39894164626): 98 documentos verificados.

O benchmark da CI também passou: Python 3.12.15, Linux-6.17.0-1022-azure-x86_64-with-glibc2.39, 2 CPUs lógicas. Mesmo perfil sequencial de 5 aquecimentos e 100 amostras por prazo:

| Meses | Amostras | P50 ns | P95 ns |
|---|---|---|---|
| 12 | 100 | 91068 | 102545 |
| 120 | 100 | 207603 | 221264 |
| 360 | 100 | 470460 | 480876 |
| 600 | 100 | 735611 | 1423169 |

JSON completo preservado em [evidência de benchmark](evidencias/spec002-benchmark-ci.json) e artefato `benchmark-spec002` da execução. O maior P95 medido foi 1.423.169 ns (aproximadamente 1,42 ms), apenas nesse perfil do motor. Isso não declara P95 da API/aplicação nem disponibilidade.

A implementação e os testes foram elaborados e revisados tecnicamente com assistência de Codex; a revisão automatizada e os testes não são atribuídos a um colega humano. O PR permanece separado de merge/deploy.

RF-22 é parcialmente atendido: endpoint, interface/seletores/gráfico/ajuda e origem oficial da taxa são SPEC-013/SPEC-007. Tributação é SPEC-004; persistência de Simulacao é SPEC-008/009. Não existe lançamento ou patrimônio criado por cálculo. O domínio não impõe novo teto funcional de prazo; série tem custo O(n), e limites de consumidor público permanecem em OPEN-30. P95 ponta a ponta, disponibilidade e proteção obrigatória de branch precisam de evidências próprias. Aprovação formal do grupo permanece sem preenchimento automático.
