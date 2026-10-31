# SPEC-054: Expurgar cache CVM após 12 meses

**Estado:** implementada tecnicamente em 2026-10-29; aguarda revisão humana do grupo. Evidências em [implementacao-SPEC-054](../09-qualidade/implementacao-SPEC-054.md).

## 1. Identificação

- **ID:** SPEC-054
- **Nome:** Expurgar cache CVM após 12 meses
- **Objetivo:** Identificar idade desde sincronização; expurgar ao atingir 12 meses; registrar execução sem conteúdo sensível; permitir nova sincronização em consulta futura.
- **Valor entregue:** cache sem registros expirados e execução registrada.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-33.
- **RB:** RB-12.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** UC-21; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** DocumentoCVM e IndicadorFinanceiro; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-04, DA-07, DA-09, DA-11; ADR-001, ADR-004, ADR-006; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** rotina diária no backend às 03:00 de America/Sao_Paulo; corte em `sincronizado_em <= agora − 12 meses de calendário`; expurgo somente de metadados públicos e indicadores estruturados; registro agregado de execução e recomposição pelo catálogo local de referência. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Não há chamada externa ou PDF neste recorte. Uma consulta após expurgo recompõe apenas a fixture local versionada de SPEC-012/SPEC-053; sincronização CVM operacional continua fora do escopo.

## 4. Dependências

[SPEC-012](SPEC-012.md), [SPEC-053](SPEC-053.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-04, OPEN-05, OPEN-15, OPEN-27. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** aplicação em execução e tabelas de cache público existentes.

**Fluxo principal:**

1. Às 03:00 de America/Sao_Paulo, calcular o corte de doze meses por calendário em UTC.
2. Remover documentos indexados e indicadores cujo `synced_at` esteja no limite ou antes dele.
3. Gravar uma única evidência com instante, contagens e status `completed`, na mesma transação.
4. Quando o cliente consultar uma empresa sem linhas públicas, recompor a parte ausente a partir da referência local.

**Alternativa observável:** Registro no limite de 12 meses é removido; imediatamente anterior é preservado conforme convenção de calendário aprovada.

**Exceções:** Falha de rotina não registra sucesso falso; nova consulta não retorna registro já expurgado como atual.

**Pós-condições:** cache sem registros expirados e execução registrada; preservação dos invariantes. Erro não produz confirmação de resultado inexistente: sem commit, não existe execução `completed`.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-054-R01 | WHEN ocorrer o fluxo válido de expurgar cache cvm após 12 meses THE SYSTEM SHALL entregar cache sem registros expirados e execução registrada. | CA-001 |
| SPEC-054-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-054-R03 | WHEN o fluxo de expurgar cache cvm após 12 meses alcançar o comportamento de RF-33/C01 THE SYSTEM SHALL atender ao comportamento: metadados de documentos (RF-30) e indicadores extraídos (RF-32) devem ser mantidos em cache local por, no máximo, **12 meses** a partir da data de sincronização com a fonte oficial. | CA-003 |
| SPEC-054-R04 | WHEN o fluxo de expurgar cache cvm após 12 meses alcançar o comportamento de RF-33/C02 THE SYSTEM SHALL atender ao comportamento: ao atingir 12 meses, o registro deve ser expurgado (removido) automaticamente por uma rotina agendada. | CA-004 |
| SPEC-054-R05 | WHEN o fluxo de expurgar cache cvm após 12 meses alcançar o comportamento de RF-33/C03 THE SYSTEM SHALL atender ao comportamento: se o usuário consultar uma empresa cujos dados foram expurgados, o sistema deve buscar novamente na fonte oficial (CVM) e recriar o cache. | CA-005 |
| SPEC-054-R06 | WHEN o fluxo de expurgar cache cvm após 12 meses alcançar o comportamento de RF-33/C04 THE SYSTEM SHALL atender ao comportamento: o link para o documento completo (RF-31) nunca é uma cópia armazenada — por não guardar o binário, ele não está sujeito a essa política de expurgo. | CA-006 |
| SPEC-054-R07 | WHEN o fluxo de expurgar cache cvm após 12 meses alcançar o comportamento de RF-33/C05 THE SYSTEM SHALL atender ao comportamento: a rotina de expurgo deve ser registrada em log para fins de auditoria (RNF-18). | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Não armazenar PDF nem apagar dados pessoais financeiros ao expurgar cache público.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** A política autorizada vale somente para o catálogo local: não afirma agendador distribuído, serviço externo CVM ou retenção de dados pessoais.

Regras herdadas: RB-12: Documentos completos (PDF) nunca são armazenados — apenas linkados; metadados e indicadores extraídos são mantidos em cache por no máximo 12 meses e depois expurgados. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

DocumentoCVM e IndicadorFinanceiro contêm sincronizado_em; relógio fornece idade. Expurgo do cache não exclui Conta, Despesa ou patrimônio pessoal.

Além de `official_documents` e `financial_indicators`, a tabela `cvm_cache_purge_runs` contém somente `occurred_at`, contagens de cada tipo e `status`. Não possui usuário, documento, PDF ou conteúdo financeiro pessoal.

## 8. Impacto arquitetural

Capacidade: Expurgar cache CVM após 12 meses. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

O ciclo assíncrono do lifespan calcula o próximo horário diário em America/Sao_Paulo e executa o serviço transacional. O serviço recebe relógio injetado; testes não aguardam o relógio real. A recomposição usa adaptador local, sem serviço externo.

ADRs relacionados: ADR-001, ADR-004, ADR-006. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | instante UTC injetável e datas `synced_at` persistidas |
| Saída | cache público sem linhas vencidas e evidência agregada `completed` |
| Erro | Falha de transação não registra sucesso; consulta não devolve linha expurgada, mas pode recompor a fixture pública local. |

Não há endpoint administrativo novo: a rotina é interna e automática. As consultas existentes autenticadas de empresa disparam somente a recomposição local quando a respectiva parte do cache estiver vazia. O prefixo/sessão existentes não são alterados.

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
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Registro no limite de 12 meses é removido; imediatamente anterior é preservado conforme convenção de calendário aprovada.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Falha de rotina não registra sucesso falso; nova consulta não retorna registro já expurgado como atual.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-33/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Metadados de documentos (RF-30) e indicadores extraídos (RF-32) devem ser mantidos em cache local por, no máximo, **12 meses** a partir da data de sincronização com a fonte oficial.

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-33/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Ao atingir 12 meses, o registro deve ser expurgado (removido) automaticamente por uma rotina agendada.

- **CA-005** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-33/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Se o usuário consultar uma empresa cujos dados foram expurgados, o sistema deve buscar novamente na fonte oficial (CVM) e recriar o cache.

- **CA-006** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-33/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O link para o documento completo (RF-31) nunca é uma cópia armazenada — por não guardar o binário, ele não está sujeito a essa política de expurgo.

- **CA-007** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-33/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A rotina de expurgo deve ser registrada em log para fins de auditoria (RNF-18).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-054-R01; CA-001; INV-001, INV-002 | Fixture específica: Registro no limite de 12 meses é removido; imediatamente anterior é preservado conforme convenção de calendário aprovada. |
| T-002 | SPEC-054-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Falha de rotina não registra sucesso falso; nova consulta não retorna registro já expurgado como atual. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-054-R03; CA-003 | RF-33/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Metadados de documentos (RF-30) e indicadores extraídos (RF-32) devem ser mantidos em cache local por, no máximo, **12 meses** a partir da data de sincronização com a fonte oficial. |
| T-004 | SPEC-054-R04; CA-004 | RF-33/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Ao atingir 12 meses, o registro deve ser expurgado (removido) automaticamente por uma rotina agendada. |
| T-005 | SPEC-054-R05; CA-005 | RF-33/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Se o usuário consultar uma empresa cujos dados foram expurgados, o sistema deve buscar novamente na fonte oficial (CVM) e recriar o cache. |
| T-006 | SPEC-054-R06; CA-006 | RF-33/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O link para o documento completo (RF-31) nunca é uma cópia armazenada — por não guardar o binário, ele não está sujeito a essa política de expurgo. |
| T-007 | SPEC-054-R07; CA-007 | RF-33/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A rotina de expurgo deve ser registrada em log para fins de auditoria (RNF-18). |
| T-008 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-04 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-05 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-27 — decisão necessária: CVM: contratos de cadastro/DFP/ITR/FRE/IPE, contas/unidades, reapresentações, identidade de documento, periodicidade de verificação de links e doze meses de calendário / SPEC-012, SPEC-027, SPEC-053, SPEC-054.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [x] Recorte técnico e política autorizada registrados com evidência real.
- [x] Corte calendário, rotina local, auditoria agregada e recomposição local conciliados para este contrato.
- [ ] Esta versão revisada individualmente pelo grupo, sem aprovação histórica presumida.
- [x] Cláusulas/CA do recorte implementadas e invariantes preservados.
- [x] Testes de integração cobrem fronteira, preservação, recomposição, auditoria e ano bissexto.
- [ ] Carga, monitoramento e agendamento distribuído continuam operacionais/fora do recorte.
- [x] Código, migration, teste e documentação foram conciliados; não há alegação de sincronização externa.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
