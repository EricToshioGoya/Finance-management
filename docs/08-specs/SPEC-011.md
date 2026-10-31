# SPEC-011: Proteger painel e consultar metadados de usuários

**Estado:** implementação técnica autorizada nesta sessão em 2026-10-28; revisão formal do grupo pendente. O contrato adotado está registrado na seção 13 e no [registro de implementação](../09-qualidade/implementacao-SPEC-011.md).

## 1. Identificação

- **ID:** SPEC-011
- **Nome:** Proteger painel e consultar metadados de usuários
- **Objetivo:** Validar sessão e papel no servidor; registrar acesso; aplicar filtros; retornar nome/e-mail/cadastro/perfil/status; paginar.
- **Valor entregue:** lista paginada de metadados e auditoria do acesso.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-54, RF-55.
- **RB:** RB-22, RB-27.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-21.
- **Fluxo:** UC-17, UC-18; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario, papel e AuditLog; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** proteger painel e consultar metadados de usuários; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Promoção permanece fora do escopo. O primeiro administrador é configurado localmente por e-mail e só recebe o papel após confirmar a posse do endereço.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-060](SPEC-060.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-05, OPEN-13, OPEN-15. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** sessão com papel administrativo validada no servidor; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar sessão e papel no servidor.
2. registrar acesso.
3. aplicar filtros.
4. retornar nome/e-mail/cadastro/perfil/status.
5. paginar.

**Alternativa observável:** Usuário comum autenticado recebe 403 em operação administrativa; administrador filtra por status sem receber campos financeiros.

**Exceções:** Sessão ausente/inválida é recusada; parâmetro manipulado não eleva papel.

**Pós-condições:** lista paginada de metadados e auditoria do acesso; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-011-R01 | WHEN ocorrer o fluxo válido de proteger painel e consultar metadados de usuários THE SYSTEM SHALL entregar lista paginada de metadados e auditoria do acesso. | CA-001 |
| SPEC-011-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-011-R03 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-54/C01 THE SYSTEM SHALL atender ao comportamento: existir um papel de usuário **administrador**, distinto do usuário comum. | CA-003 |
| SPEC-011-R04 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-54/C02 THE SYSTEM SHALL atender ao comportamento: o acesso a qualquer rota/endpoint administrativo deve ser validado no backend por papel (RBAC) — nunca apenas ocultado na interface. | CA-004 |
| SPEC-011-R05 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-54/C03 THE SYSTEM SHALL atender ao comportamento: usuários sem papel de administrador que tentarem acessar um endpoint administrativo devem receber erro de acesso negado (HTTP 403). | CA-005 |
| SPEC-011-R06 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-54/C04 THE SYSTEM SHALL atender ao comportamento: a promoção de um usuário a administrador deve ser feita apenas por outro administrador (ou via configuração inicial do sistema), nunca pelo cadastro público (RF-01). | CA-006 |
| SPEC-011-R07 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-54/C05 THE SYSTEM SHALL atender ao comportamento: todo acesso ao painel administrativo deve ser registrado no log de auditoria (RNF-18). | CA-007 |
| SPEC-011-R08 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-55/C01 THE SYSTEM SHALL atender ao comportamento: listar os usuários cadastrados com informações não sensíveis: nome, e-mail, data de cadastro, perfil de investidor (RF-03) e status da conta. | CA-008 |
| SPEC-011-R09 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-55/C02 THE SYSTEM SHALL atender ao comportamento: permitir buscar/filtrar por nome, e-mail, perfil de investidor ou status. | CA-009 |
| SPEC-011-R10 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-55/C03 THE SYSTEM SHALL atender ao comportamento: **Não** deve exibir dados financeiros individuais dos usuários (renda, gastos, patrimônio) — apenas metadados de conta e métricas agregadas de uso (RB-22). | CA-010 |
| SPEC-011-R11 | WHEN o fluxo de proteger painel e consultar metadados de usuários alcançar o comportamento de RF-55/C04 THE SYSTEM SHALL atender ao comportamento: a listagem deve ser paginada. | CA-011 |

## 6. Regras e invariantes

- **INV-001:** Cadastro público nunca cria administrador; painel não exibe renda, gastos ou patrimônio individuais.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-22: O painel administrativo nunca exibe dados financeiros individuais de um usuário específico — apenas metadados de conta e métricas agregadas de uso; RB-27: Cadastro exige nome, e-mail válido e único e senha de pelo menos 8 caracteres. A implementação solicitada adota esse mínimo e equivalência de e-mail sem distinção de caixa conforme ADR-005; OPEN-16 preserva a pendência de revisão formal e origem da aprovação histórica, sem usar a própria Spec como evidência de aprovação. Nunca devolver senha/hash em respostas ou logs; cadastro público cria papel usuário. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario tem papel usuario/administrador e metadados de nome/e-mail/data/perfil/status. AuditLog registra ator/ação/instante; não se exige armazenar renda ou gastos no painel.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Proteger painel e consultar metadados de usuários. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | sessão administrativa e filtros de nome/e-mail/perfil/status |
| Saída | lista paginada de metadados e auditoria do acesso |
| Erro | Sessão ausente/inválida é recusada; parâmetro manipulado não eleva papel. |

Identificadores, filtros e autorizações são verificados no servidor. O contrato autorizado é `GET /api/v1/admin/users?page=1&page_size=20&query=&status=active&profile=unassigned`, com página entre 1 e N e `page_size` entre 1 e 100. Perfil é `null` até a SPEC-003 e só aceita o filtro `unassigned`; dados financeiros não fazem parte da resposta. Sessão ausente recebe 401 e papel comum recebe 403 `admin_access_denied`.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-21 (Isolamento administrativo) | Requisitar cada operação administrativa com comum/admin; comum autenticado recebe 403. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Usuário comum autenticado recebe 403 em operação administrativa; administrador filtra por status sem receber campos financeiros.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Sessão ausente/inválida é recusada; parâmetro manipulado não eleva papel.

- **CA-003** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-54/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve existir um papel de usuário **administrador**, distinto do usuário comum.

- **CA-004** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-54/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O acesso a qualquer rota/endpoint administrativo deve ser validado no backend por papel (RBAC) — nunca apenas ocultado na interface.

- **CA-005** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-54/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Usuários sem papel de administrador que tentarem acessar um endpoint administrativo devem receber erro de acesso negado (HTTP 403).

- **CA-006** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-54/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A promoção de um usuário a administrador deve ser feita apenas por outro administrador (ou via configuração inicial do sistema), nunca pelo cadastro público (RF-01).

- **CA-007** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-54/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Todo acesso ao painel administrativo deve ser registrado no log de auditoria (RNF-18).

- **CA-008** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-55/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve listar os usuários cadastrados com informações não sensíveis: nome, e-mail, data de cadastro, perfil de investidor (RF-03) e status da conta.

- **CA-009** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-55/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir buscar/filtrar por nome, e-mail, perfil de investidor ou status.

- **CA-010** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-55/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: **Não** deve exibir dados financeiros individuais dos usuários (renda, gastos, patrimônio) — apenas metadados de conta e métricas agregadas de uso (RB-22).

- **CA-011** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-55/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A listagem deve ser paginada.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-011-R01; CA-001; INV-001, INV-002 | Fixture específica: Usuário comum autenticado recebe 403 em operação administrativa; administrador filtra por status sem receber campos financeiros. |
| T-002 | SPEC-011-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Sessão ausente/inválida é recusada; parâmetro manipulado não eleva papel. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-011-R03; CA-003 | RF-54/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve existir um papel de usuário **administrador**, distinto do usuário comum. |
| T-004 | SPEC-011-R04; CA-004 | RF-54/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O acesso a qualquer rota/endpoint administrativo deve ser validado no backend por papel (RBAC) — nunca apenas ocultado na interface. |
| T-005 | SPEC-011-R05; CA-005 | RF-54/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Usuários sem papel de administrador que tentarem acessar um endpoint administrativo devem receber erro de acesso negado (HTTP 403). |
| T-006 | SPEC-011-R06; CA-006 | RF-54/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A promoção de um usuário a administrador deve ser feita apenas por outro administrador (ou via configuração inicial do sistema), nunca pelo cadastro público (RF-01). |
| T-007 | SPEC-011-R07; CA-007 | RF-54/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Todo acesso ao painel administrativo deve ser registrado no log de auditoria (RNF-18). |
| T-008 | SPEC-011-R08; CA-008 | RF-55/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve listar os usuários cadastrados com informações não sensíveis: nome, e-mail, data de cadastro, perfil de investidor (RF-03) e status da conta. |
| T-009 | SPEC-011-R09; CA-009 | RF-55/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir buscar/filtrar por nome, e-mail, perfil de investidor ou status. |
| T-010 | SPEC-011-R10; CA-010 | RF-55/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: **Não** deve exibir dados financeiros individuais dos usuários (renda, gastos, patrimônio) — apenas metadados de conta e métricas agregadas de uso (RB-22). |
| T-011 | SPEC-011-R11; CA-011 | RF-55/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A listagem deve ser paginada. |
| T-012 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-21 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- **Decisão técnica autorizada em 2026-10-28:** `FINNOVA_INITIAL_ADMIN_EMAIL` identifica o primeiro administrador local. Cadastro público continua criando `usuario`; após confirmação de e-mail, somente o endereço configurado e somente quando ainda não há administrador recebe o papel. Não há rota de promoção nesta Spec. A listagem administrativa usa o contrato da seção 9, registra `admin_users_listed` e expõe apenas metadados. Isso resolve OPEN-05/13/15 apenas para esse recorte técnico; gestão contínua de administradores e retenção operacional continuam abertas.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA do recorte técnico implementadas e invariantes preservados.
- [x] Testes de integração do recorte adicionados; a evidência de execução fica no registro de implementação e no CI do PR.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.

