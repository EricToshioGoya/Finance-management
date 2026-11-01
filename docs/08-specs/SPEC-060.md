# SPEC-060: Coletar eventos e auditar ações sensíveis

**Estado:** implementação técnica autorizada nesta sessão em 2026-10-28; revisão formal do grupo pendente. O recorte e as decisões adotadas estão registrados na seção 13 e no [registro de implementação](../09-qualidade/implementacao-SPEC-060.md). Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-060
- **Nome:** Coletar eventos e auditar ações sensíveis
- **Objetivo:** Registrar evento sem bloquear fluxo; incluir apenas usuário/módulo/ação/timestamp; informar política de uso agregado; registrar ações sensíveis; proteger trilha contra edição operacional.
- **Valor entregue:** evento de uso assíncrono mínimo e auditoria protegida.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-59.
- **RB:** RB-23.
- **RNF:** RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25.
- **Fluxo:** UC-22; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** EventoUso e AuditLog; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** coletar eventos e auditar ações sensíveis; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Auditoria é requisito transversal entregue junto a esta capacidade observável, não Spec isolada para um RNF. Neste recorte autorizado, eventos e auditoria são anonimizados na exclusão; retenção legal/operacional continua fora do escopo.

## 4. Dependências

[SPEC-001](SPEC-001.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-05, OPEN-15, OPEN-19, OPEN-26. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Registrar evento sem bloquear fluxo.
2. incluir apenas usuário/módulo/ação/timestamp.
3. informar política de uso agregado.
4. registrar ações sensíveis.
5. proteger trilha contra edição operacional.

**Alternativa observável:** Acesso ao Simulador registra identificador/módulo/ação/instante e nenhum valor de projeção; alterar via API a trilha é recusado.

**Exceções:** Falha de coleta não é confundida com ação financeira concluída ou registrada; neste recorte não há retry automático. A falha é isolada e não muda o resultado da ação do usuário.

**Pós-condições:** evento de uso assíncrono mínimo e auditoria protegida; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-060-R01 | WHEN ocorrer o fluxo válido de coletar eventos e auditar ações sensíveis THE SYSTEM SHALL entregar evento de uso assíncrono mínimo e auditoria protegida. | CA-001 |
| SPEC-060-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-060-R03 | WHEN o fluxo de coletar eventos e auditar ações sensíveis alcançar o comportamento de RF-59/C01 THE SYSTEM SHALL atender ao comportamento: registrar, de forma assíncrona (sem impactar a performance percebida pelo usuário — RNF-04), um evento a cada vez que o usuário acessa um módulo/aba. | CA-003 |
| SPEC-060-R04 | WHEN o fluxo de coletar eventos e auditar ações sensíveis alcançar o comportamento de RF-59/C02 THE SYSTEM SHALL atender ao comportamento: o evento deve conter apenas: usuário (id), módulo, ação e timestamp — nunca conteúdo financeiro sensível (RB-23). | CA-004 |
| SPEC-060-R05 | WHEN o fluxo de coletar eventos e auditar ações sensíveis alcançar o comportamento de RF-59/C03 THE SYSTEM SHALL atender ao comportamento: a política de privacidade do sistema deve informar que dados de uso agregados são coletados para fins de melhoria do produto e vistos, de forma agregada, por administradores (transparência LGPD). | CA-005 |
| SPEC-060-R06 | WHEN o fluxo de coletar eventos e auditar ações sensíveis alcançar o comportamento de RF-59/C04 THE SYSTEM SHALL atender ao comportamento: solicitar a exclusão desses dados de uso junto com a exclusão de conta (RF-05). | CA-006 |

## 6. Regras e invariantes

- **INV-001:** EventoUso nunca contém valor financeiro; auditoria não expõe senha/token; exclusão segue retenção aprovada.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-23: Eventos de uso não armazenam conteúdo financeiro — apenas usuário, módulo, ação e timestamp. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

EventoUso tem só usuário, módulo, ação e timestamp. AuditLog contém ator/ação/instante para ações sensíveis; retenção/anonimização não é substituída por tabelas eternas.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Coletar eventos e auditar ações sensíveis. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | acesso a módulo ou ação sensível, titular, ação e instante |
| Saída | evento de uso assíncrono mínimo e auditoria protegida |
| Erro | Falha de coleta não é confundida com ação financeira concluída ou registrada; política de retry em OPEN-26. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-02 (Privacidade / LGPD) | Testar titular A/B, exportação/exclusão aplicável e política aprovada de retenção. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-14 (Backup e recuperação) | Restaurar backup isolado, medir RPO <=24h/RTO <=4h e aplicar exclusões; depende de OPEN-05/32. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-18 (Auditoria) | Inspecionar autoria/ação/instante e recusa de edição operacional; retenção pessoal depende de OPEN-05/19. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Acesso ao Simulador registra identificador/módulo/ação/instante e nenhum valor de projeção; alterar via API a trilha é recusado.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Falha de coleta não é confundida com ação financeira concluída ou registrada; política de retry em OPEN-26.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-59/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve registrar, de forma assíncrona (sem impactar a performance percebida pelo usuário — RNF-04), um evento a cada vez que o usuário acessa um módulo/aba.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-59/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O evento deve conter apenas: usuário (id), módulo, ação e timestamp — nunca conteúdo financeiro sensível (RB-23).

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-59/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A política de privacidade do sistema deve informar que dados de uso agregados são coletados para fins de melhoria do produto e vistos, de forma agregada, por administradores (transparência LGPD).

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-59/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder solicitar a exclusão desses dados de uso junto com a exclusão de conta (RF-05).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-060-R01; CA-001; INV-001, INV-002 | Fixture específica: Acesso ao Simulador registra identificador/módulo/ação/instante e nenhum valor de projeção; alterar via API a trilha é recusado. |
| T-002 | SPEC-060-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Falha de coleta não é confundida com ação financeira concluída ou registrada; política de retry em OPEN-26. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-060-R03; CA-003 | RF-59/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve registrar, de forma assíncrona (sem impactar a performance percebida pelo usuário — RNF-04), um evento a cada vez que o usuário acessa um módulo/aba. |
| T-004 | SPEC-060-R04; CA-004 | RF-59/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O evento deve conter apenas: usuário (id), módulo, ação e timestamp — nunca conteúdo financeiro sensível (RB-23). |
| T-005 | SPEC-060-R05; CA-005 | RF-59/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A política de privacidade do sistema deve informar que dados de uso agregados são coletados para fins de melhoria do produto e vistos, de forma agregada, por administradores (transparência LGPD). |
| T-006 | SPEC-060-R06; CA-006 | RF-59/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder solicitar a exclusão desses dados de uso junto com a exclusão de conta (RF-05). |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- **Decisão técnica autorizada em 2026-10-28:** eventos aceitam somente usuário, módulo, ação e instante; são gravados em tarefa de fundo. Falha não tem retry automático e não muda o resultado da ação do usuário. Na exclusão de conta, `usuario_id` de eventos/auditoria é tornado nulo; registros não carregam conteúdo financeiro, senha ou token. Rotas de leitura/edição da trilha não são publicadas. Isso resolve OPEN-05/15/19/26 somente para este recorte técnico; retenção legal/operacional, dashboards administrativos, fila/retry e notificações continuam abertos para as Specs correspondentes.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA do recorte técnico implementadas e invariantes de dados mínimos preservados.
- [x] Testes de integração do recorte adicionados; a evidência de execução fica no registro de implementação e no CI do PR.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.

