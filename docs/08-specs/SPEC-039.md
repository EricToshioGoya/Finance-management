# SPEC-039: Gerar alertas e histórico in-app

**Estado:** implementada tecnicamente em 2026-10-29, aguardando verificação de CI e revisão humana. A política do recorte foi confirmada pelo responsável nesta sessão; não equivale à aprovação histórica do grupo. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-039
- **Nome:** Gerar alertas e histórico in-app
- **Objetivo:** Receber evento do módulo existente; verificar tipo habilitado; gerar notificação; manter histórico acessível por 30 dias ou mais; exibir ao titular.
- **Valor entregue:** notificação própria com histórico por ao menos 30 dias.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-48.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** UC-15; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Notificacao, Usuario e eventos dos módulos; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** gerar alertas e histórico in-app; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** canais externos (e-mail/push), fila/retry, disparo mensal e implementação dos módulos produtores ainda ausentes. Não executar investimentos reais nem integrar Open Finance neste recorte.

Política confirmada: o canal é somente in-app; os quatro tipos são `invoice_due`, `budget_goal_exceeded`, `watchlist_document` e `recurring_expense_due`; a preferência global in-app e a preferência individual do tipo precisam estar habilitadas. A identidade de deduplicação é titular + tipo + chave opaca de origem. Os produtores enviam o evento sem conteúdo financeiro e a central persiste histórico por mais de 30 dias. Módulos produtores são integrações condicionais, sem ciclo de dependência.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-014](SPEC-014.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-11, OPEN-15, OPEN-26. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Receber evento do módulo existente.
2. verificar tipo habilitado.
3. gerar notificação.
4. manter histórico acessível por 30 dias ou mais.
5. exibir ao titular.

**Alternativa observável:** Evento de meta ultrapassada habilitado cria aviso; mesmo tipo desabilitado não aparece; aviso permanece na janela mínima de 30 dias.

**Exceções:** Falha de canal externo não apaga histórico in-app.

**Pós-condições:** notificação própria com histórico por ao menos 30 dias; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-039-R01 | WHEN ocorrer o fluxo válido de gerar alertas e histórico in-app THE SYSTEM SHALL entregar notificação própria com histórico por ao menos 30 dias. | CA-001 |
| SPEC-039-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-039-R03 | WHEN o fluxo de gerar alertas e histórico in-app alcançar o comportamento de RF-48/C01 THE SYSTEM SHALL atender ao comportamento: notificar o usuário quando: a fatura do cartão estiver próxima do vencimento (RF-13), uma meta geral ou por categoria for ultrapassada (RF-14, RF-15), um novo documento for identificado para uma empresa da watchlist (RF-34), ou uma despesa recorrente (RF-09, campo `recorrente`) estiver próxima da data de vencimento. | CA-003 |
| SPEC-039-R04 | WHEN o fluxo de gerar alertas e histórico in-app alcançar o comportamento de RF-48/C02 THE SYSTEM SHALL atender ao comportamento: habilitar/desabilitar cada tipo de notificação individualmente. | CA-004 |
| SPEC-039-R05 | WHEN o fluxo de gerar alertas e histórico in-app alcançar o comportamento de RF-48/C03 THE SYSTEM SHALL atender ao comportamento: as notificações in-app devem ficar acessíveis num histórico (central de notificações) por, no mínimo, 30 dias. | CA-005 |

## 6. Regras e invariantes

- **INV-001:** Alerta não muda saldo nem torna dado individual visível a outro usuário.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Notificacao tem titular, tipo, conteúdo mínimo e instante; preferências controlam tipos habilitados. Histórico mínimo é de 30 dias; não transformar notificação em lançamento.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Gerar alertas e histórico in-app. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | `POST /api/v1/notifications/events` autenticado: tipo fechado e chave opaca da origem; preferências |
| Saída | central `GET /api/v1/notifications`, preferências por tipo e marcação individual de leitura |
| Erro | Falha de canal externo não apaga histórico in-app. |

Identificadores, filtros e autorizações são verificados no servidor. A listagem é limitada a 100 entradas mais recentes e aceita `unread_only`; a marcação de leitura e a consulta são sempre do próprio titular. Prefixo `/api/v1`; contratos de sessão existentes do ADR-007 não mudam. Canais externos continuam para SPEC-061/OPEN-26.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-08 (Disponibilidade) | Medir disponibilidade mensal >=99,5% no ambiente operacional aprovado; não inferir de teste unitário. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-14 (Backup e recuperação) | Restaurar backup isolado, medir RPO <=24h/RTO <=4h e aplicar exclusões; depende de OPEN-05/32. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Evento de meta ultrapassada habilitado cria aviso; mesmo tipo desabilitado não aparece; aviso permanece na janela mínima de 30 dias.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Falha de canal externo não apaga histórico in-app.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-48/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve notificar o usuário quando: a fatura do cartão estiver próxima do vencimento (RF-13), uma meta geral ou por categoria for ultrapassada (RF-14, RF-15), um novo documento for identificado para uma empresa da watchlist (RF-34), ou uma despesa recorrente (RF-09, campo `recorrente`) estiver próxima da data de vencimento.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-48/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder habilitar/desabilitar cada tipo de notificação individualmente.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-48/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: As notificações in-app devem ficar acessíveis num histórico (central de notificações) por, no mínimo, 30 dias.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-039-R01; CA-001; INV-001, INV-002 | Fixture específica: Evento de meta ultrapassada habilitado cria aviso; mesmo tipo desabilitado não aparece; aviso permanece na janela mínima de 30 dias. |
| T-002 | SPEC-039-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Falha de canal externo não apaga histórico in-app. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-039-R03; CA-003 | RF-48/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve notificar o usuário quando: a fatura do cartão estiver próxima do vencimento (RF-13), uma meta geral ou por categoria for ultrapassada (RF-14, RF-15), um novo documento for identificado para uma empresa da watchlist (RF-34), ou uma despesa recorrente (RF-09, campo `recorrente`) estiver próxima da data de vencimento. |
| T-004 | SPEC-039-R04; CA-004 | RF-48/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder habilitar/desabilitar cada tipo de notificação individualmente. |
| T-005 | SPEC-039-R05; CA-005 | RF-48/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: As notificações in-app devem ficar acessíveis num histórico (central de notificações) por, no mínimo, 30 dias. |
| T-006 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-11/15/26 são resolvidas somente para este recorte técnico pela política confirmada: os produtores enviam eventos dos quatro tipos por chave opaca; não há antecedência automática inventada, canal externo, retry ou disparo mensal. O histórico é mantido por mais de 30 dias e o titular controla o canal in-app e cada tipo. As decisões restantes continuam abertas para as demais Specs.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [x] Recorte técnico e política confirmados pelo responsável nesta sessão; revisão formal do grupo continua pendente.
- [x] OPEN-11/15/26 resolvidas apenas para este contrato técnico e registradas no registro central.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Central, opt-out granular, deduplicação, isolamento e histórico foram implementados sem alterar lançamentos.
- [ ] Testes da seção 12 aguardam execução de integração na CI PostgreSQL.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
