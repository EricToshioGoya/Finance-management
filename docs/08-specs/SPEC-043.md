# SPEC-043: Consultar uso por módulo e engajamento

**Estado:** implementada em 2026-10-31; validação automatizada registrada no PR da implementação. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-043
- **Nome:** Consultar uso por módulo e engajamento
- **Objetivo:** Validar administrador; agregar eventos por período/módulo; contar usuários distintos; identificar extremos; calcular métricas; mostrar tendências/inatividade sem dados financeiros individuais.
- **Valor entregue:** acessos/usuários únicos por módulo, DAU/WAU/MAU e evolução.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-57, RF-58.
- **RB:** RB-22, RB-23.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-21, RNF-25.
- **Fluxo:** UC-19; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** EventoUso e Usuario; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consultar uso por módulo e engajamento; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Definição de ativo, janelas e inatividade nominal versus anonimato de RB-22 em OPEN-19/21.

## 4. Dependências

[SPEC-011](SPEC-011.md), [SPEC-060](SPEC-060.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-05, OPEN-11, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** sessão com papel administrativo validada no servidor; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar administrador.
2. agregar eventos por período/módulo.
3. contar usuários distintos.
4. identificar extremos.
5. calcular métricas.
6. mostrar tendências/inatividade sem dados financeiros individuais.

**Alternativa observável:** Dois acessos de A e um de B no módulo produzem três acessos e dois usuários únicos no período.

**Exceções:** Período vazio não inventa engajamento; usuário comum não recebe métricas.

**Pós-condições:** acessos/usuários únicos por módulo, DAU/WAU/MAU e evolução; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-043-R01 | WHEN ocorrer o fluxo válido de consultar uso por módulo e engajamento THE SYSTEM SHALL entregar acessos/usuários únicos por módulo, DAU/WAU/MAU e evolução. | CA-001 |
| SPEC-043-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-043-R03 | WHEN o fluxo de consultar uso por módulo e engajamento alcançar o comportamento de RF-57/C01 THE SYSTEM SHALL atender ao comportamento: exibir gráfico dinâmico com número de acessos e de usuários únicos por módulo (Administração Financeira, Simulador, Relatórios de Empresas, Patrimônio, Score, etc.) num período selecionável. | CA-003 |
| SPEC-043-R04 | WHEN o fluxo de consultar uso por módulo e engajamento alcançar o comportamento de RF-57/C02 THE SYSTEM SHALL atender ao comportamento: destacar o módulo mais e o menos utilizado no período selecionado. | CA-004 |
| SPEC-043-R05 | WHEN o fluxo de consultar uso por módulo e engajamento alcançar o comportamento de RF-57/C03 THE SYSTEM SHALL atender ao comportamento: os dados devem vir do registro de eventos de uso (RF-59), sempre agregados — nunca expondo, nesse gráfico, o comportamento individual nominal de um usuário. | CA-005 |
| SPEC-043-R06 | WHEN o fluxo de consultar uso por módulo e engajamento alcançar o comportamento de RF-58/C01 THE SYSTEM SHALL atender ao comportamento: exibir métricas de engajamento: usuários ativos por dia/semana/mês (DAU/WAU/MAU), frequência média de uso, e usuários inativos há mais de N dias (limite configurável). | CA-006 |
| SPEC-043-R07 | WHEN o fluxo de consultar uso por módulo e engajamento alcançar o comportamento de RF-58/C02 THE SYSTEM SHALL atender ao comportamento: exibir, de forma agregada, quais módulos os usuários mais recorrentes mais utilizam. | CA-007 |
| SPEC-043-R08 | WHEN o fluxo de consultar uso por módulo e engajamento alcançar o comportamento de RF-58/C03 THE SYSTEM SHALL atender ao comportamento: exibir gráfico de evolução do engajamento ao longo do tempo. | CA-008 |

## 6. Regras e invariantes

- **INV-001:** Gráficos de uso são agregados, sem comportamento nominal individual.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-22: O painel administrativo nunca exibe dados financeiros individuais de um usuário específico — apenas metadados de conta e métricas agregadas de uso; RB-23: Eventos de uso não armazenam conteúdo financeiro — apenas usuário, módulo, ação e timestamp. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

EventoUso contém usuário, módulo, ação e timestamp; administração consome agregações. Relação com Usuario não autoriza acessar histórico financeiro individual.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consultar uso por módulo e engajamento. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | período de uso e limite configurado de inatividade |
| Saída | acessos/usuários únicos por módulo, DAU/WAU/MAU e evolução |
| Erro | Período vazio não inventa engajamento; usuário comum não recebe métricas. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-21 (Isolamento administrativo) | Requisitar cada operação administrativa com comum/admin; comum autenticado recebe 403. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Dois acessos de A e um de B no módulo produzem três acessos e dois usuários únicos no período.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Período vazio não inventa engajamento; usuário comum não recebe métricas.

- **CA-003** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-57/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico dinâmico com número de acessos e de usuários únicos por módulo (Administração Financeira, Simulador, Relatórios de Empresas, Patrimônio, Score, etc.) num período selecionável.

- **CA-004** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-57/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve destacar o módulo mais e o menos utilizado no período selecionado.

- **CA-005** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-57/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Os dados devem vir do registro de eventos de uso (RF-59), sempre agregados — nunca expondo, nesse gráfico, o comportamento individual nominal de um usuário.

- **CA-006** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-58/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir métricas de engajamento: usuários ativos por dia/semana/mês (DAU/WAU/MAU), frequência média de uso, e usuários inativos há mais de N dias (limite configurável).

- **CA-007** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-58/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir, de forma agregada, quais módulos os usuários mais recorrentes mais utilizam.

- **CA-008** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-58/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico de evolução do engajamento ao longo do tempo.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-043-R01; CA-001; INV-001, INV-002 | Fixture específica: Dois acessos de A e um de B no módulo produzem três acessos e dois usuários únicos no período. |
| T-002 | SPEC-043-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Período vazio não inventa engajamento; usuário comum não recebe métricas. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-043-R03; CA-003 | RF-57/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico dinâmico com número de acessos e de usuários únicos por módulo (Administração Financeira, Simulador, Relatórios de Empresas, Patrimônio, Score, etc.) num período selecionável. |
| T-004 | SPEC-043-R04; CA-004 | RF-57/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve destacar o módulo mais e o menos utilizado no período selecionado. |
| T-005 | SPEC-043-R05; CA-005 | RF-57/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Os dados devem vir do registro de eventos de uso (RF-59), sempre agregados — nunca expondo, nesse gráfico, o comportamento individual nominal de um usuário. |
| T-006 | SPEC-043-R06; CA-006 | RF-58/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir métricas de engajamento: usuários ativos por dia/semana/mês (DAU/WAU/MAU), frequência média de uso, e usuários inativos há mais de N dias (limite configurável). |
| T-007 | SPEC-043-R07; CA-007 | RF-58/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir, de forma agregada, quais módulos os usuários mais recorrentes mais utilizam. |
| T-008 | SPEC-043-R08; CA-008 | RF-58/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico de evolução do engajamento ao longo do tempo. |
| T-009 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-21, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-05 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-11 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
