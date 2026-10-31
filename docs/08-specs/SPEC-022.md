# SPEC-022: Consultar dashboards financeiros por período

**Estado:** rascunho para revisão humana, criado em 2026-10-22. Produção documental autorizada no lote atual; sem implementação/testes novos ou aprovação formal presumida.

## 1. Identificação

- **ID:** SPEC-022
- **Nome:** Consultar dashboards financeiros por período
- **Objetivo:** Filtrar período; agregar lançamentos; omitir categoria sem gasto; renderizar valores/percentuais; atualizar após alterações; destacar gasto acima da renda e meses com PLR.
- **Valor entregue:** gráficos por categoria, saldo e renda versus gasto.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-16, RF-17, RF-18.
- **RB:** RB-05, RB-06, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** Fluxos de dashboards RF-16 a RF-18; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Renda, Despesa, Conta e Categoria; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-06, DA-07, DA-08, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consultar dashboards financeiros por período; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Definição de saldo acumulado versus resultado mensal e limites de período em OPEN-21, sem escolher representação conflitante.

## 4. Dependências

[SPEC-006](SPEC-006.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-06, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Filtrar período.
2. agregar lançamentos.
3. omitir categoria sem gasto.
4. renderizar valores/percentuais.
5. atualizar após alterações.
6. destacar gasto acima da renda e meses com PLR.

**Alternativa observável:** Receita 100, PLR anual 50 e despesa 40 no mês mostram renda 150 e variação 110; PLR não aparece como 50/12.

**Exceções:** Período vazio não produz percentual NaN; dados alheios não aparecem.

**Pós-condições:** gráficos por categoria, saldo e renda versus gasto; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-022-R01 | WHEN ocorrer o fluxo válido de consultar dashboards financeiros por período THE SYSTEM SHALL entregar gráficos por categoria, saldo e renda versus gasto. | CA-001 |
| SPEC-022-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-022-R03 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-16/C01 THE SYSTEM SHALL atender ao comportamento: exibir gráfico de pizza (ou barras) com o total gasto por categoria no período selecionado. | CA-003 |
| SPEC-022-R04 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-16/C02 THE SYSTEM SHALL atender ao comportamento: filtrar por mês. | CA-004 |
| SPEC-022-R05 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-16/C03 THE SYSTEM SHALL atender ao comportamento: categorias sem gasto no período não devem aparecer no gráfico. | CA-005 |
| SPEC-022-R06 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-16/C04 THE SYSTEM SHALL atender ao comportamento: ao passar o mouse/tocar em uma fatia, deve exibir valor e percentual do total. | CA-006 |
| SPEC-022-R07 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-17/C01 THE SYSTEM SHALL atender ao comportamento: exibir gráfico de linha com saldo consolidado mês a mês (renda total − gasto total). | CA-007 |
| SPEC-022-R08 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-17/C02 THE SYSTEM SHALL atender ao comportamento: permitir selecionar um intervalo de meses. | CA-008 |
| SPEC-022-R09 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-17/C03 THE SYSTEM SHALL atender ao comportamento: atualizar automaticamente ao registrar novos lançamentos. | CA-009 |
| SPEC-022-R10 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-18/C01 THE SYSTEM SHALL atender ao comportamento: exibir gráfico de barras agrupadas com renda total e gasto total lado a lado, por mês. | CA-010 |
| SPEC-022-R11 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-18/C02 THE SYSTEM SHALL atender ao comportamento: compor a renda total a partir de renda fixa + renda variável + bônus/PLR do mês. | CA-011 |
| SPEC-022-R12 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-18/C03 THE SYSTEM SHALL atender ao comportamento: permitir selecionar um intervalo de meses (ex.: últimos 6 ou 12 meses). | CA-012 |
| SPEC-022-R13 | WHEN o fluxo de consultar dashboards financeiros por período alcançar o comportamento de RF-18/C04 THE SYSTEM SHALL atender ao comportamento: destacar visualmente os meses em que o gasto superou a renda. | CA-013 |

## 6. Regras e invariantes

- **INV-001:** Todos os gráficos usam o mesmo conjunto filtrado; bônus anual é integral no mês de referência.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-05: Renda total do mês = renda fixa + renda variável do mês + bônus/PLR recebido no mês; RB-06: Bônus/PLR anual é integralmente atribuído ao mês de referência informado, sem diluição automática; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Renda/Despesa são agregadas por titular, categoria e mês de competência; séries derivadas não criam lançamentos ou substituem registros de origem.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consultar dashboards financeiros por período. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | mês ou intervalo de meses do próprio titular |
| Saída | gráficos por categoria, saldo e renda versus gasto |
| Erro | Período vazio não produz percentual NaN; dados alheios não aparecem. |

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
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Receita 100, PLR anual 50 e despesa 40 no mês mostram renda 150 e variação 110; PLR não aparece como 50/12.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Período vazio não produz percentual NaN; dados alheios não aparecem.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-16/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico de pizza (ou barras) com o total gasto por categoria no período selecionado.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-16/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder filtrar por mês.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-16/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Categorias sem gasto no período não devem aparecer no gráfico.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-16/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Ao passar o mouse/tocar em uma fatia, deve exibir valor e percentual do total.

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-17/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico de linha com saldo consolidado mês a mês (renda total − gasto total).

- **CA-008** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-17/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir selecionar um intervalo de meses.

- **CA-009** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-17/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve atualizar automaticamente ao registrar novos lançamentos.

- **CA-010** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-18/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico de barras agrupadas com renda total e gasto total lado a lado, por mês.

- **CA-011** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-18/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve compor a renda total a partir de renda fixa + renda variável + bônus/PLR do mês.

- **CA-012** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-18/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir selecionar um intervalo de meses (ex.: últimos 6 ou 12 meses).

- **CA-013** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-18/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve destacar visualmente os meses em que o gasto superou a renda.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-022-R01; CA-001; INV-001, INV-002 | Fixture específica: Receita 100, PLR anual 50 e despesa 40 no mês mostram renda 150 e variação 110; PLR não aparece como 50/12. |
| T-002 | SPEC-022-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Período vazio não produz percentual NaN; dados alheios não aparecem. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-022-R03; CA-003 | RF-16/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico de pizza (ou barras) com o total gasto por categoria no período selecionado. |
| T-004 | SPEC-022-R04; CA-004 | RF-16/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder filtrar por mês. |
| T-005 | SPEC-022-R05; CA-005 | RF-16/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Categorias sem gasto no período não devem aparecer no gráfico. |
| T-006 | SPEC-022-R06; CA-006 | RF-16/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Ao passar o mouse/tocar em uma fatia, deve exibir valor e percentual do total. |
| T-007 | SPEC-022-R07; CA-007 | RF-17/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico de linha com saldo consolidado mês a mês (renda total − gasto total). |
| T-008 | SPEC-022-R08; CA-008 | RF-17/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir selecionar um intervalo de meses. |
| T-009 | SPEC-022-R09; CA-009 | RF-17/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve atualizar automaticamente ao registrar novos lançamentos. |
| T-010 | SPEC-022-R10; CA-010 | RF-18/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico de barras agrupadas com renda total e gasto total lado a lado, por mês. |
| T-011 | SPEC-022-R11; CA-011 | RF-18/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve compor a renda total a partir de renda fixa + renda variável + bônus/PLR do mês. |
| T-012 | SPEC-022-R12; CA-012 | RF-18/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir selecionar um intervalo de meses (ex.: últimos 6 ou 12 meses). |
| T-013 | SPEC-022-R13; CA-013 | RF-18/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve destacar visualmente os meses em que o gasto superou a renda. |
| T-014 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-06 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
