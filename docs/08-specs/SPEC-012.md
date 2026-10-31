# SPEC-012: Pesquisar empresas e abrir documentos oficiais

**Estado:** implementada em branch de trabalho, aguardando CI e revisão humana. Recorte local confirmado pelo responsável em 2026-10-28.

## 1. Identificação

- **ID:** SPEC-012
- **Nome:** Pesquisar empresas e abrir documentos oficiais
- **Objetivo:** Consultar cadastro CVM; mostrar autocomplete; selecionar empresa; listar DFP/ITR/FRE/IPE com filtros; abrir link oficial em nova aba; sinalizar links quebrados.
- **Valor entregue:** sugestões, ficha, metadados e links oficiais.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-29, RF-30, RF-31.
- **RB:** RB-12.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-08, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-13 e UC-20; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** EmpresaAberta e DocumentoCVM; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-04, DA-07, DA-09; ADR-001, ADR-004; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** pesquisar empresas e abrir documentos oficiais; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** sincronização automática da CVM, extração de indicadores (SPEC-053), expurgo automático (SPEC-054), watchlist e armazenamento de PDFs. O catálogo inicial é local e contém somente metadados e links oficiais.

SPEC-053 cobre números CVM e SPEC-054 o expurgo. A implementação desta capacidade deve integrar política de retenção antes de uso operacional.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões resolvidas neste recorte: OPEN-10, OPEN-15 e OPEN-27. A verificação de link é manual sob demanda e não baixa conteúdo externo.

## 5. Comportamento esperado

**Pré-condições:** rotina/fonte autorizada e contratos externos aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Consultar cadastro CVM.
2. mostrar autocomplete.
3. selecionar empresa.
4. listar DFP/ITR/FRE/IPE com filtros.
5. abrir link oficial em nova aba.
6. sinalizar links quebrados.

**Alternativa observável:** Filtrar empresa por CNPJ e documentos por tipo/período retorna só os itens correspondentes, com status e aviso de responsabilidade externa.

**Exceções:** Sem empresa/documentos mostrar vazio; falha de fonte/link não produz documento fictício.

**Pós-condições:** sugestões, ficha, metadados e links oficiais; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-012-R01 | WHEN ocorrer o fluxo válido de pesquisar empresas e abrir documentos oficiais THE SYSTEM SHALL entregar sugestões, ficha, metadados e links oficiais. | CA-001 |
| SPEC-012-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-012-R03 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-29/C01 THE SYSTEM SHALL atender ao comportamento: permitir buscar uma empresa de capital aberto por ticker (ex.: PETR4), CNPJ ou razão social. | CA-003 |
| SPEC-012-R04 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-29/C02 THE SYSTEM SHALL atender ao comportamento: exibir sugestões (autocomplete) conforme o usuário digita. | CA-004 |
| SPEC-012-R05 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-29/C03 THE SYSTEM SHALL atender ao comportamento: retornar dados cadastrais básicos da empresa (razão social, CNPJ, setor) a partir do dataset de Informação Cadastral da CVM. | CA-005 |
| SPEC-012-R06 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-30/C01 THE SYSTEM SHALL atender ao comportamento: para a empresa selecionada, deve listar os documentos disponíveis: DFP (Demonstrações Financeiras Padronizadas), ITR (Informações Trimestrais), FRE (Formulário de Referência) e demais documentos do IPE (Informações Periódicas e Eventuais). | CA-006 |
| SPEC-012-R07 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-30/C02 THE SYSTEM SHALL atender ao comportamento: cada item da lista deve exibir: tipo de documento, categoria/assunto, período de referência (ex.: 2º trimestre de 2026), data de entrega e status (ativo ou reapresentado/substituído). | CA-007 |
| SPEC-012-R08 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-30/C03 THE SYSTEM SHALL atender ao comportamento: armazenar apenas os metadados listados acima — nunca o conteúdo binário do documento (PDF). | CA-008 |
| SPEC-012-R09 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-30/C04 THE SYSTEM SHALL atender ao comportamento: a listagem deve poder ser filtrada por tipo de documento e por intervalo de datas. | CA-009 |
| SPEC-012-R10 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-31/C01 THE SYSTEM SHALL atender ao comportamento: cada item da listagem (RF-30) deve conter um link direto para o documento original no sistema RAD/ENET da CVM. | CA-010 |
| SPEC-012-R11 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-31/C02 THE SYSTEM SHALL atender ao comportamento: o link deve abrir em nova aba/janela, redirecionando o usuário ao site oficial da CVM. | CA-011 |
| SPEC-012-R12 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-31/C03 THE SYSTEM SHALL atender ao comportamento: a tela deve exibir um aviso indicando que o conteúdo do documento é de responsabilidade da empresa emissora e da CVM, e que o FinNova apenas indexa e referencia o material. | CA-012 |
| SPEC-012-R13 | WHEN o fluxo de pesquisar empresas e abrir documentos oficiais alcançar o comportamento de RF-31/C04 THE SYSTEM SHALL atender ao comportamento: se o link oficial mudar de endereço (ex.: migração de sistema pela CVM), o sistema deve ter um mecanismo de verificação periódica para identificar e sinalizar links quebrados. | CA-013 |

## 6. Regras e invariantes

- **INV-001:** Nenhum binário PDF da empresa é hospedado pelo FinNova.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-12: Documentos completos (PDF) nunca são armazenados — apenas linkados; metadados e indicadores extraídos são mantidos em cache por no máximo 12 meses e depois expurgados. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

EmpresaAberta possui 0..N DocumentoCVM, com tipo, assunto, período, entrega, status, URL oficial e sincronizado_em. Empresa tem ticker, CNPJ, razão social e setor.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Pesquisar empresas e abrir documentos oficiais. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Integração externa é isolada por adaptador; contratos, fonte/provedor e periodicidade devem ser definidos nas OPEN locais. Testes usam dublês, sem serviços externos reais.

ADRs relacionados: ADR-001, ADR-004. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | ticker/CNPJ/razão social; empresa; tipo e intervalo de documentos |
| Saída | sugestões, ficha, metadados e links oficiais |
| Erro | Sem empresa/documentos mostrar vazio; falha de fonte/link não produz documento fictício. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-08 (Disponibilidade) | Medir disponibilidade mensal >=99,5% no ambiente operacional aprovado; não inferir de teste unitário. |
| RNF-10 (Ciclo de vida de dados externos) | Relógio injetado: expurgo ao atingir 12 meses e consulta após ressincronização. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Filtrar empresa por CNPJ e documentos por tipo/período retorna só os itens correspondentes, com status e aviso de responsabilidade externa.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Sem empresa/documentos mostrar vazio; falha de fonte/link não produz documento fictício.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-29/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir buscar uma empresa de capital aberto por ticker (ex.: PETR4), CNPJ ou razão social.

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-29/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir sugestões (autocomplete) conforme o usuário digita.

- **CA-005** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-29/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve retornar dados cadastrais básicos da empresa (razão social, CNPJ, setor) a partir do dataset de Informação Cadastral da CVM.

- **CA-006** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-30/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Para a empresa selecionada, deve listar os documentos disponíveis: DFP (Demonstrações Financeiras Padronizadas), ITR (Informações Trimestrais), FRE (Formulário de Referência) e demais documentos do IPE (Informações Periódicas e Eventuais).

- **CA-007** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-30/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Cada item da lista deve exibir: tipo de documento, categoria/assunto, período de referência (ex.: 2º trimestre de 2026), data de entrega e status (ativo ou reapresentado/substituído).

- **CA-008** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-30/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve armazenar apenas os metadados listados acima — nunca o conteúdo binário do documento (PDF).

- **CA-009** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-30/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A listagem deve poder ser filtrada por tipo de documento e por intervalo de datas.

- **CA-010** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-31/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Cada item da listagem (RF-30) deve conter um link direto para o documento original no sistema RAD/ENET da CVM.

- **CA-011** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-31/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O link deve abrir em nova aba/janela, redirecionando o usuário ao site oficial da CVM.

- **CA-012** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-31/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A tela deve exibir um aviso indicando que o conteúdo do documento é de responsabilidade da empresa emissora e da CVM, e que o FinNova apenas indexa e referencia o material.

- **CA-013** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-31/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Se o link oficial mudar de endereço (ex.: migração de sistema pela CVM), o sistema deve ter um mecanismo de verificação periódica para identificar e sinalizar links quebrados.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-012-R01; CA-001; INV-001, INV-002 | Fixture específica: Filtrar empresa por CNPJ e documentos por tipo/período retorna só os itens correspondentes, com status e aviso de responsabilidade externa. |
| T-002 | SPEC-012-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Sem empresa/documentos mostrar vazio; falha de fonte/link não produz documento fictício. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-012-R03; CA-003 | RF-29/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir buscar uma empresa de capital aberto por ticker (ex.: PETR4), CNPJ ou razão social. |
| T-004 | SPEC-012-R04; CA-004 | RF-29/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir sugestões (autocomplete) conforme o usuário digita. |
| T-005 | SPEC-012-R05; CA-005 | RF-29/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve retornar dados cadastrais básicos da empresa (razão social, CNPJ, setor) a partir do dataset de Informação Cadastral da CVM. |
| T-006 | SPEC-012-R06; CA-006 | RF-30/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Para a empresa selecionada, deve listar os documentos disponíveis: DFP (Demonstrações Financeiras Padronizadas), ITR (Informações Trimestrais), FRE (Formulário de Referência) e demais documentos do IPE (Informações Periódicas e Eventuais). |
| T-007 | SPEC-012-R07; CA-007 | RF-30/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Cada item da lista deve exibir: tipo de documento, categoria/assunto, período de referência (ex.: 2º trimestre de 2026), data de entrega e status (ativo ou reapresentado/substituído). |
| T-008 | SPEC-012-R08; CA-008 | RF-30/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve armazenar apenas os metadados listados acima — nunca o conteúdo binário do documento (PDF). |
| T-009 | SPEC-012-R09; CA-009 | RF-30/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A listagem deve poder ser filtrada por tipo de documento e por intervalo de datas. |
| T-010 | SPEC-012-R10; CA-010 | RF-31/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Cada item da listagem (RF-30) deve conter um link direto para o documento original no sistema RAD/ENET da CVM. |
| T-011 | SPEC-012-R11; CA-011 | RF-31/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O link deve abrir em nova aba/janela, redirecionando o usuário ao site oficial da CVM. |
| T-012 | SPEC-012-R12; CA-012 | RF-31/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A tela deve exibir um aviso indicando que o conteúdo do documento é de responsabilidade da empresa emissora e da CVM, e que o FinNova apenas indexa e referencia o material. |
| T-013 | SPEC-012-R13; CA-013 | RF-31/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Se o link oficial mudar de endereço (ex.: migração de sistema pela CVM), o sistema deve ter um mecanismo de verificação periódica para identificar e sinalizar links quebrados. |
| T-014 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-08, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-10 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
