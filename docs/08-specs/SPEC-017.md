# SPEC-017: Consultar, renovar e encerrar sessões

**Estado:** implementação técnica concluída na branch feature/17-sessoes, aguardando CI e revisão humana. A autorização do usuário cobre este recorte; não comprova aprovação formal histórica do grupo.

## 1. Identificação

- **ID:** SPEC-017
- **Nome:** Consultar, renovar e encerrar sessões
- **Objetivo:** Validar identidade; listar início/expiração/atual; renovar com rotação; revogar sessão selecionada/todas; remover cookie no logout atual.
- **Valor entregue:** lista sem tokens, novo acesso renovado ou confirmação de revogação.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-73, RF-74.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25.
- **Fluxo:** UC-28, UC-29; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e sessões técnicas, família de refresh; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consultar, renovar e encerrar sessões; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Renovação/logout existentes no ADR-007 são preservados. Esta entrega adiciona consulta e revogação de dispositivos no contrato /api/v1/auth, sem criar um segundo mecanismo de sessão.

## 4. Dependências

[SPEC-001](SPEC-001.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

O pedido de implementação autorizou o contrato técnico abaixo para esta unidade. OPEN-15 permanece parcial para consumidores fora de autenticação e OPEN-18 já possui solução técnica no ADR-007; revisão formal do grupo continua pendente.

## 5. Comportamento esperado

**Pré-condições:** credencial válida da própria sessão para cada contrato; logout idempotente conforme ADR-007; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar identidade.
2. listar início/expiração/atual.
3. renovar com rotação.
4. revogar sessão selecionada ou todas as sessões do próprio titular.
5. remover cookie quando a sessão atual é encerrada ou quando todas são revogadas.

**Alternativa observável:** Logout invalida access e refresh da sessão atual; outra sessão permanece até revogação explícita global.

**Exceções:** Identificador de sessão alheia é recusado sem lista ou revogação; JWT expirado não autoriza gestão.

**Pós-condições:** lista sem tokens, novo acesso renovado ou confirmação de revogação; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-017-R01 | WHEN ocorrer o fluxo válido de consultar, renovar e encerrar sessões THE SYSTEM SHALL entregar lista sem tokens, novo acesso renovado ou confirmação de revogação. | CA-001 |
| SPEC-017-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-017-R03 | WHEN o fluxo de consultar, renovar e encerrar sessões alcançar o comportamento de RF-73/C01 THE SYSTEM SHALL exibir início, expiração e sessão atual sem tokens; proibir acesso a sessões alheias; e revogar uma ou todas as sessões próprias de modo idempotente. | CA-003 |
| SPEC-017-R04 | WHEN o fluxo de consultar, renovar e encerrar sessões alcançar o comportamento de RF-74/C01 THE SYSTEM SHALL atender ao comportamento: preservar contratos da SPEC-001/ADR-005; recusar replay, token expirado e sessão revogada; logout atual não encerra outros dispositivos. Implementado na SPEC-001; novas regras de confirmação e manutenção da conta continuam pendentes. | CA-004 |

## 6. Regras e invariantes

- **INV-001:** Logout atual não encerra outros dispositivos; replay de refresh revoga a família; gestão nunca expõe token/digest.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario possui 0..N sessões técnicas com início UTC, expiração/revogação e vínculo de família de renovação. A migration 004_session_management registra created_at; tokens opacos não são expostos na lista e apenas digests são guardados.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. A migration é aditiva e não impõe atributos de dispositivo. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consultar, renovar e encerrar sessões. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | sessão/refresh, seleção de sessão própria ou todas |
| Saída | lista sem tokens, novo acesso renovado ou confirmação de revogação |
| Erro | Identificador de sessão alheia é recusado sem lista ou revogação; JWT expirado não autoriza gestão. |

Identificadores, filtros e autorizações são verificados no servidor. Esta implementação publica GET /api/v1/auth/sessions com id, started_at, expires_at e current; POST /api/v1/auth/sessions/{id}/revoke com 204; e POST /api/v1/auth/sessions/revoke-all com revoked_sessions. A lista não expõe tokens/digests; 404 session_not_found cobre tanto ID inexistente quanto alheio. Os POSTs são limitados como endpoints sensíveis e a sessão atual remove o cookie ao ser revogada.

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
| RNF-18 (Auditoria) | Inspecionar autoria/ação/instante e recusa de edição operacional; retenção pessoal depende de OPEN-05/19. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Logout invalida access e refresh da sessão atual; outra sessão permanece até revogação explícita global.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Identificador de sessão alheia é recusado sem lista ou revogação; JWT expirado não autoriza gestão.

- **CA-003** — **Dado** credencial válida da própria sessão para cada contrato; logout idempotente conforme ADR-007, entradas válidas e política aprovada de RF-73/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Exibir início, expiração e sessão atual; proibir acesso a sessões alheias; revogação idempotente; listar e revogar outros dispositivos ainda não implementados.

- **CA-004** — **Dado** credencial válida da própria sessão para cada contrato; logout idempotente conforme ADR-007, entradas válidas e política aprovada de RF-74/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Preservar contratos da SPEC-001/ADR-005; recusar replay, token expirado e sessão revogada; logout atual não encerra outros dispositivos. Implementado na SPEC-001; novas regras de confirmação e manutenção da conta continuam pendentes.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-017-R01; CA-001; INV-001, INV-002 | Teste de integração cria duas sessões, lista início/expiração/atual e confirma ausência de token/digest. |
| T-002 | SPEC-017-R02; CA-002; INV-001, INV-002, INV-003 | Teste de ID alheio e malformado usa o mesmo 404 e preserva a sessão alvo. |
| T-003 | SPEC-017-R03; CA-003 | Teste de revogação repetida confirma idempotência, access/refresh revogados e outra sessão preservada. |
| T-004 | SPEC-017-R04; CA-004 | Teste de revogação global limpa cookie e invalida todos os dispositivos; regressões da SPEC-001 cobrem rotação/replay/logout. |
| T-005 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | PostgreSQL real, migration, lint/build e testes de navegador na CI; disponibilidade, backup, monitoramento e auditoria operacional continuam pendentes em OPEN-32. |

Testes de API foram implementados em backend/tests/test_spec017_session_management.py; a execução usa PostgreSQL real e migration. A evidência e limites operacionais estão em ../09-qualidade/implementacao-SPEC-017.md.

## 13. Questões em Aberto

- OPEN-15 — parcial: contratos de autenticação, confirmação e sessões estão explicitados em ADR-007/ADR-008 e nesta Spec; consumidores financeiros seguem pendentes.
- OPEN-18 — solução técnica já registrada para bloqueio de login na SPEC-001; revisão formal histórica permanece pendente.
- OPEN-32 — disponibilidade, backup/restore, monitoramento, proteção remota de branch e auditoria operacional não são demonstrados por esta implementação.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados no recorte técnico.
- [x] Testes da seção 12 implementados; executar e registrar CI no commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
