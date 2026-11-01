# SPEC-027: Manter watchlist e avisar novo documento

**Estado:** implementada tecnicamente em 2026-10-30, conforme política confirmada pelo responsável. Em 2026-10-31, a sincronização semanal com os Dados Abertos CVM (OPEN-27, ADR-009) passou a alimentar o aviso de documento novo (R05); testes em `backend/tests/test_c02_spec027_cvm_sync.py`. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI). Corrigida a rota `GET /api/v1/companies/watchlist`, que era capturada por `/companies/{company_id}` e respondia 422; testes em `backend/tests/test_c02_spec027_watchlist.py`.

## 1. Identificação

- **ID:** SPEC-027
- **Nome:** Manter watchlist e avisar novo documento
- **Objetivo:** Validar titular/empresa; incluir/remover favorita; limitar ao máximo configurado (padrão 50); listar; ao detectar documento novo gerar alerta respeitando preferências.
- **Valor entregue:** lista pessoal e notificação do evento.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-34.
- **RB:** RB-12, RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-10, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-13; fluxo watchlist; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario, Watchlist, EmpresaAberta e DocumentoCVM; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-04, DA-06, DA-07, DA-09; ADR-001, ADR-004, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** manter watchlist e avisar novo documento; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Definição de documento novo/reapresentado e deduplicação de alerta em OPEN-26/27.

## 4. Dependências

[SPEC-012](SPEC-012.md), [SPEC-039](SPEC-039.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-26, OPEN-27. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar titular/empresa.
2. incluir/remover favorita.
3. limitar ao máximo configurado (padrão 50).
4. listar.
5. ao detectar documento novo gerar alerta respeitando preferências.

**Alternativa observável:** Incluir empresa uma vez mostra um vínculo; com limite padrão 50, a 51ª favorita é recusada.

**Exceções:** Usuário B não altera watchlist de A; documento já conhecido não é tratado como novo sem política de identidade aprovada.

**Pós-condições:** lista pessoal e notificação do evento; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-027-R01 | WHEN ocorrer o fluxo válido de manter watchlist e avisar novo documento THE SYSTEM SHALL entregar lista pessoal e notificação do evento. | CA-001 |
| SPEC-027-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-027-R03 | WHEN o fluxo de manter watchlist e avisar novo documento alcançar o comportamento de RF-34/C01 THE SYSTEM SHALL atender ao comportamento: permitir favoritar/desfavoritar uma empresa a partir da busca (RF-29) ou da ficha da empresa. | CA-003 |
| SPEC-027-R04 | WHEN o fluxo de manter watchlist e avisar novo documento alcançar o comportamento de RF-34/C02 THE SYSTEM SHALL atender ao comportamento: exibir uma lista consolidada das empresas favoritadas pelo usuário. | CA-004 |
| SPEC-027-R05 | WHEN o fluxo de manter watchlist e avisar novo documento alcançar o comportamento de RF-34/C03 THE SYSTEM SHALL atender ao comportamento: notificar o usuário (RF-48) quando um novo documento (DFP, ITR, FRE, IPE) for identificado para uma empresa da watchlist. | CA-005 |
| SPEC-027-R06 | WHEN o fluxo de manter watchlist e avisar novo documento alcançar o comportamento de RF-34/C04 THE SYSTEM SHALL atender ao comportamento: a watchlist é pessoal (por usuário), sem limite mínimo, com limite máximo configurável de 50 empresas (padrão de mercado). | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Favoritar não armazena PDF; remover favorita não remove empresa global.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-12: Documentos completos (PDF) nunca são armazenados — apenas linkados; metadados e indicadores extraídos são mantidos em cache por no máximo 12 meses e depois expurgados; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Watchlist liga exatamente um Usuario e uma EmpresaAberta; cada lado pode ter 0..N vínculos. Documento novo é evento da empresa observada.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Manter watchlist e avisar novo documento. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-004, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | empresa favoritada/desfavoritada e documento novo identificado |
| Saída | lista pessoal e notificação do evento |
| Erro | Usuário B não altera watchlist de A; documento já conhecido não é tratado como novo sem política de identidade aprovada. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-10 (Ciclo de vida de dados externos) | Relógio injetado: expurgo ao atingir 12 meses e consulta após ressincronização. |
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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Incluir empresa uma vez mostra um vínculo; com limite padrão 50, a 51ª favorita é recusada.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Usuário B não altera watchlist de A; documento já conhecido não é tratado como novo sem política de identidade aprovada.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-34/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir favoritar/desfavoritar uma empresa a partir da busca (RF-29) ou da ficha da empresa.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-34/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir uma lista consolidada das empresas favoritadas pelo usuário.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-34/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve notificar o usuário (RF-48) quando um novo documento (DFP, ITR, FRE, IPE) for identificado para uma empresa da watchlist.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-34/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A watchlist é pessoal (por usuário), sem limite mínimo, com limite máximo configurável de 50 empresas (padrão de mercado).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-027-R01; CA-001; INV-001, INV-002 | Fixture específica: Incluir empresa uma vez mostra um vínculo; com limite padrão 50, a 51ª favorita é recusada. |
| T-002 | SPEC-027-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Usuário B não altera watchlist de A; documento já conhecido não é tratado como novo sem política de identidade aprovada. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-027-R03; CA-003 | RF-34/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir favoritar/desfavoritar uma empresa a partir da busca (RF-29) ou da ficha da empresa. |
| T-004 | SPEC-027-R04; CA-004 | RF-34/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir uma lista consolidada das empresas favoritadas pelo usuário. |
| T-005 | SPEC-027-R05; CA-005 | RF-34/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve notificar o usuário (RF-48) quando um novo documento (DFP, ITR, FRE, IPE) for identificado para uma empresa da watchlist. |
| T-006 | SPEC-027-R06; CA-006 | RF-34/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A watchlist é pessoal (por usuário), sem limite mínimo, com limite máximo configurável de 50 empresas (padrão de mercado). |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-10, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-26 — decisão necessária: Eventos e notificações: gatilhos/antecedência, identidade/deduplicação/retry, falhas de coleta, política in-app/opt-out, canais externos, retenção e disparo mensal / SPEC-027, SPEC-039, SPEC-040, SPEC-042, SPEC-051, SPEC-060, SPEC-061.
- OPEN-27 — decisão necessária: CVM: contratos de cadastro/DFP/ITR/FRE/IPE, contas/unidades, reapresentações, identidade de documento, periodicidade de verificação de links e doze meses de calendário / SPEC-012, SPEC-027, SPEC-053, SPEC-054.

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
