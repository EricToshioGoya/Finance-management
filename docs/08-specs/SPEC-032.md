# SPEC-032: Simular stress financeiro isolado

**Estado:** implementada tecnicamente; código incorporado à `main` em 2026-10-31 (PR #43) e coberto pela CI. Registro anterior: implementação técnica da SPEC-032 no PR #69 (`feature/32-financial-stress`), com API, motor puro, interface PT/EN e testes executados. Política formal de OPEN-03/OPEN-21, revisão do grupo e merge ainda pendentes. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-032
- **Nome:** Simular stress financeiro isolado
- **Objetivo:** Ler posição real sem alterá-la; aplicar choque hipotético; calcular sustentação pelos gastos médios; comparar cenários; sinalizar reserva insuficiente pelo limite configurável de 3 a 6 meses.
- **Valor entregue:** meses de sustentação, alerta e comparação de dois cenários.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-39.
- **RB:** RB-17, RB-29.
- **RNF:** RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-14; fluxo de stress RF-39; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Simulacao, Ativo, Passivo e orçamento; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** simular stress financeiro isolado; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

**Recorte técnico provisório (OPEN-21):** janela de três meses civis completos, reserva conservadora apenas em contas correntes, poupança e dinheiro, horizonte máximo de 120 meses e corte hipotético de despesas uniforme. Detalhes na [implementação](../09-qualidade/implementacao-SPEC-032.md). Revisão formal da política permanece aberta.

## 4. Dependências

[SPEC-006](SPEC-006.md), [SPEC-028](SPEC-028.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** fórmulas e parâmetros de cálculo aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Ler posição real sem alterá-la.
2. aplicar choque hipotético.
3. calcular sustentação pelos gastos médios.
4. comparar cenários.
5. sinalizar reserva insuficiente pelo limite configurável de 3 a 6 meses.

**Alternativa observável:** Com reserva de teste 600 e gasto mensal 100, perda total sem outras entradas sustenta 6 meses na hipótese simplificada aprovada.

**Exceções:** Gasto médio zero/negativo ou patrimônio ilíquido não é interpretado como divisão normal sem política.

**Pós-condições:** meses de sustentação, alerta e comparação de dois cenários; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-032-R01 | WHEN ocorrer o fluxo válido de simular stress financeiro isolado THE SYSTEM SHALL entregar meses de sustentação, alerta e comparação de dois cenários. | CA-001 |
| SPEC-032-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-032-R03 | WHEN o fluxo de simular stress financeiro isolado alcançar o comportamento de RF-39/C01 THE SYSTEM SHALL atender ao comportamento: permitir simular ao menos três tipos de cenário hipotético: perda total da renda, redução parcial da renda (%) e gasto emergencial pontual — cada um por um período/valor informado pelo usuário. | CA-003 |
| SPEC-032-R04 | WHEN o fluxo de simular stress financeiro isolado alcançar o comportamento de RF-39/C02 THE SYSTEM SHALL atender ao comportamento: calcular, com base no patrimônio líquido atual (RF-35) e nos gastos médios mensais (módulo Administração Financeira), por quantos meses o usuário consegue se manter no cenário simulado. | CA-004 |
| SPEC-032-R05 | WHEN o fluxo de simular stress financeiro isolado alcançar o comportamento de RF-39/C03 THE SYSTEM SHALL atender ao comportamento: exibir um alerta se a reserva for insuficiente para cobrir de 3 a 6 meses de gastos (limite configurável). | CA-005 |
| SPEC-032-R06 | WHEN o fluxo de simular stress financeiro isolado alcançar o comportamento de RF-39/C04 THE SYSTEM SHALL atender ao comportamento: permitir comparar dois cenários lado a lado (ex.: "sem ação" vs. "cortando gasto de lazer em 30%"). | CA-006 |
| SPEC-032-R07 | WHEN o fluxo de simular stress financeiro isolado alcançar o comportamento de RF-39/C05 THE SYSTEM SHALL atender ao comportamento: não deve alterar dados reais do usuário — é uma simulação isolada, no mesmo padrão do módulo Simulador (RB-17). | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Stress nunca modifica rendas, despesas, ativos ou passivos reais.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-17: O stress test de renda é uma simulação isolada — nunca altera dados reais do usuário; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Simulacao, Ativo, Passivo e orçamento. A Simulacao guarda parâmetros, hipóteses, prazo e resultado; o motor retorna valores derivados sem alterar saldo ou patrimônio. Entradas específicas estão na seção 9, fórmulas e calendários ausentes nas OPEN locais. Regras configuráveis devem ter versão identificável no resultado.

A implementação reutiliza as tabelas financeiras reais sem criar migrations e realiza o cálculo exclusivamente no motor puro de simulação, sem gravar resultados.

## 8. Impacto arquitetural

Capacidade: Simular stress financeiro isolado. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | perda total, redução percentual ou gasto emergencial; duração e parâmetros |
| Saída | meses de sustentação, alerta e comparação de dois cenários |
| Erro | Gasto médio zero/negativo ou patrimônio ilíquido não é interpretado como divisão normal sem política. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Com reserva de teste 600 e gasto mensal 100, perda total sem outras entradas sustenta 6 meses na hipótese simplificada aprovada.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Gasto médio zero/negativo ou patrimônio ilíquido não é interpretado como divisão normal sem política.

- **CA-003** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-39/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir simular ao menos três tipos de cenário hipotético: perda total da renda, redução parcial da renda (%) e gasto emergencial pontual — cada um por um período/valor informado pelo usuário.

- **CA-004** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-39/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular, com base no patrimônio líquido atual (RF-35) e nos gastos médios mensais (módulo Administração Financeira), por quantos meses o usuário consegue se manter no cenário simulado.

- **CA-005** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-39/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir um alerta se a reserva for insuficiente para cobrir de 3 a 6 meses de gastos (limite configurável).

- **CA-006** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-39/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir comparar dois cenários lado a lado (ex.: "sem ação" vs. "cortando gasto de lazer em 30%").

- **CA-007** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-39/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Não deve alterar dados reais do usuário — é uma simulação isolada, no mesmo padrão do módulo Simulador (RB-17).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-032-R01; CA-001; INV-001, INV-002 | Fixture específica: Com reserva de teste 600 e gasto mensal 100, perda total sem outras entradas sustenta 6 meses na hipótese simplificada aprovada. |
| T-002 | SPEC-032-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Gasto médio zero/negativo ou patrimônio ilíquido não é interpretado como divisão normal sem política. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-032-R03; CA-003 | RF-39/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir simular ao menos três tipos de cenário hipotético: perda total da renda, redução parcial da renda (%) e gasto emergencial pontual — cada um por um período/valor informado pelo usuário. |
| T-004 | SPEC-032-R04; CA-004 | RF-39/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular, com base no patrimônio líquido atual (RF-35) e nos gastos médios mensais (módulo Administração Financeira), por quantos meses o usuário consegue se manter no cenário simulado. |
| T-005 | SPEC-032-R05; CA-005 | RF-39/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir um alerta se a reserva for insuficiente para cobrir de 3 a 6 meses de gastos (limite configurável). |
| T-006 | SPEC-032-R06; CA-006 | RF-39/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir comparar dois cenários lado a lado (ex.: "sem ação" vs. "cortando gasto de lazer em 30%"). |
| T-007 | SPEC-032-R07; CA-007 | RF-39/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Não deve alterar dados reais do usuário — é uma simulação isolada, no mesmo padrão do módulo Simulador (RB-17). |
| T-008 | INV-001, INV-002, INV-003; RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes executáveis estão em `backend/tests/unit/test_spec032_stress_engine.py` e `backend/tests/test_spec032_financial_stress.py`. A evidência de CI está associada ao PR #69. As fórmulas e políticas provisórias não constituem aprovação formal das questões em OPEN.

## 13. Questões em Aberto

- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-21 — decisão necessária: Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais / SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [ ] Todas as cláusulas/CA implementadas e todos os INV preservados.
- [ ] Testes da seção 12 aprovados, com evidência ligada ao commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
