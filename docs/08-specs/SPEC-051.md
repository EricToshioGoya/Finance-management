# SPEC-051: Conceder conquistas sem efeito financeiro

**Estado:** implementada tecnicamente em 2026-10-31 (backend, interface web e testes automatizados). Política de recorte proposta pelo agente e aprovada pelo responsável em 2026-10-31; revisão formal do grupo pendente. Evidências no [registro de implementação](../09-qualidade/implementacao-SPEC-051.md).

## 1. Identificação

- **ID:** SPEC-051
- **Nome:** Conceder conquistas sem efeito financeiro
- **Objetivo:** Avaliar evento de meta/marco; conferir condição; conceder badge; exibir obtidas/próximas; notificar respeitando preferências.
- **Valor entregue:** conquista, progresso e notificação.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-67.
- **RB:** RB-15, RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** Fluxo conquistas RF-67; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Badge, Usuario e metas; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** conceder conquistas sem efeito financeiro; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Catálogo, repetição/revogação e sequência mensal ficam em OPEN-11/26.

## 4. Dependências

[SPEC-021](SPEC-021.md), [SPEC-033](SPEC-033.md), [SPEC-039](SPEC-039.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-11, OPEN-15, OPEN-26. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Avaliar evento de meta/marco.
2. conferir condição.
3. conceder badge.
4. exibir obtidas/próximas.
5. notificar respeitando preferências.

**Alternativa observável:** Evento que satisfaz a regra aprovada concede a conquista e aviso; comparação dos dados financeiros antes/depois é idêntica.

**Exceções:** Regra não aprovada ou evento fora da condição não concede recompensa financeira nem papel.

**Pós-condições:** conquista, progresso e notificação; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-051-R01 | WHEN ocorrer o fluxo válido de conceder conquistas sem efeito financeiro THE SYSTEM SHALL entregar conquista, progresso e notificação. | CA-001 |
| SPEC-051-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-051-R03 | WHEN o fluxo de conceder conquistas sem efeito financeiro alcançar o comportamento de RF-67/C01 THE SYSTEM SHALL atender ao comportamento: conceder conquistas ao atingir metas gerais/por categoria (RF-14 e RF-15), metas nomeadas (RF-40) ou marcos de uso (ex.: "3 meses seguidos dentro do orçamento"). | CA-003 |
| SPEC-051-R04 | WHEN o fluxo de conceder conquistas sem efeito financeiro alcançar o comportamento de RF-67/C02 THE SYSTEM SHALL atender ao comportamento: exibir uma tela com as conquistas obtidas e as próximas conquistas disponíveis (progresso). | CA-004 |
| SPEC-051-R05 | WHEN o fluxo de conceder conquistas sem efeito financeiro alcançar o comportamento de RF-67/C03 THE SYSTEM SHALL atender ao comportamento: a concessão de uma conquista deve gerar uma notificação (RF-48). | CA-005 |
| SPEC-051-R06 | WHEN o fluxo de conceder conquistas sem efeito financeiro alcançar o comportamento de RF-67/C04 THE SYSTEM SHALL atender ao comportamento: conquistas são apenas cosméticas/motivacionais — nunca alteram cálculos financeiros, score (RF-41) ou permissões do usuário. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Badge não altera cálculo financeiro, score ou permissões.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-15: O score de saúde financeira é educativo, não constitui recomendação financeira, e sua fórmula de ponderação deve ser documentada e configurável; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario conquista 0..N Badge; cada conquista referencia condição/meta/marco aprovado. Badge não se relaciona a permissão ou multiplicador financeiro.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Conceder conquistas sem efeito financeiro. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | meta atingida ou marco de comportamento aprovado |
| Saída | conquista, progresso e notificação |
| Erro | Regra não aprovada ou evento fora da condição não concede recompensa financeira nem papel. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-14 (Backup e recuperação) | Restaurar backup isolado, medir RPO <=24h/RTO <=4h e aplicar exclusões; depende de OPEN-05/32. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Evento que satisfaz a regra aprovada concede a conquista e aviso; comparação dos dados financeiros antes/depois é idêntica.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Regra não aprovada ou evento fora da condição não concede recompensa financeira nem papel.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-67/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve conceder conquistas ao atingir metas gerais/por categoria (RF-14 e RF-15), metas nomeadas (RF-40) ou marcos de uso (ex.: "3 meses seguidos dentro do orçamento").

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-67/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir uma tela com as conquistas obtidas e as próximas conquistas disponíveis (progresso).

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-67/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A concessão de uma conquista deve gerar uma notificação (RF-48).

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-67/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Conquistas são apenas cosméticas/motivacionais — nunca alteram cálculos financeiros, score (RF-41) ou permissões do usuário.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-051-R01; CA-001; INV-001, INV-002 | Fixture específica: Evento que satisfaz a regra aprovada concede a conquista e aviso; comparação dos dados financeiros antes/depois é idêntica. |
| T-002 | SPEC-051-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Regra não aprovada ou evento fora da condição não concede recompensa financeira nem papel. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-051-R03; CA-003 | RF-67/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve conceder conquistas ao atingir metas gerais/por categoria (RF-14 e RF-15), metas nomeadas (RF-40) ou marcos de uso (ex.: "3 meses seguidos dentro do orçamento"). |
| T-004 | SPEC-051-R04; CA-004 | RF-67/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir uma tela com as conquistas obtidas e as próximas conquistas disponíveis (progresso). |
| T-005 | SPEC-051-R05; CA-005 | RF-67/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A concessão de uma conquista deve gerar uma notificação (RF-48). |
| T-006 | SPEC-051-R06; CA-006 | RF-67/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Conquistas são apenas cosméticas/motivacionais — nunca alteram cálculos financeiros, score (RF-41) ou permissões do usuário. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes implementados em `backend/tests/test_spec050_052_engagement.py`, nomeados `test_SPEC_051_Rxx` por cláusula, e executados na CI com PostgreSQL. T-006 (RNFs) é coberto parcialmente pela suíte, pelo lint e pela varredura de acessibilidade; evidência operacional (backup, disponibilidade) permanece fora do recorte.

## 13. Questões em Aberto

- OPEN-11 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-26 — decisão necessária: Eventos e notificações: gatilhos/antecedência, identidade/deduplicação/retry, falhas de coleta, política in-app/opt-out, canais externos, retenção e disparo mensal / SPEC-027, SPEC-039, SPEC-040, SPEC-042, SPEC-051, SPEC-060, SPEC-061.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

### Decisão adotada para o recorte implementado (2026-10-31)

Catálogo fixo de três conquistas: `named_goal_reached` (meta nomeada com valor-alvo atingido, RF-40), `budget_month_on_track` (mês anterior dentro de todas as metas de gasto) e `three_months_on_budget` (três meses seguidos dentro das metas de gasto). A avaliação ocorre quando o titular consulta as conquistas; cada uma é concedida uma única vez (restrição única por titular e código) e gera notificação in-app `achievement_unlocked` pela SPEC-039, respeitando o opt-out por tipo. Conquistas são apenas cosméticas: não alteram cálculos, score nem papel. O tipo `achievement_unlocked` não pode ser criado por evento manual do cliente.

**Contrato:** `GET /api/v1/auth/financial/achievements` → lista {code, title, description, unlocked, unlocked_at, progress_percent}. Tabela `achievements` e novos tipos de notificação (migração 034).

As OPEN acima continuam registradas para revisão do grupo; a decisão vale para este recorte e pode ser revista sem perda de rastreabilidade.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [x] Decisões OPEN bloqueantes resolvidas para o recorte (seção 13) e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados.
- [x] Testes da seção 12 aprovados, com evidência ligada ao commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
