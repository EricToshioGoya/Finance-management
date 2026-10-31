# SPEC-021: Definir metas de orçamento e acompanhar progresso

**Estado:** rascunho para revisão humana, criado em 2026-10-22. Produção documental autorizada no lote atual; sem implementação/testes novos ou aprovação formal presumida.

## 1. Identificação

- **ID:** SPEC-021
- **Nome:** Definir metas de orçamento e acompanhar progresso
- **Objetivo:** Salvar metas próprias; aplicar edição no mês corrente; apurar valores; calcular razões; mostrar progresso; sinalizar limites.
- **Valor entregue:** metas vigentes, barras de progresso e sinais de ultrapassagem.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-14, RF-15, RF-19.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25.
- **Fluxo:** Fluxos de metas RF-14/15/19; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** MetaGeral, MetaCategoria, Categoria, Renda e Despesa; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-06, DA-07, DA-08, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** definir metas de orçamento e acompanhar progresso; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

A notificação por canal é integração posterior da SPEC-039; esta capacidade entrega sinalização e progresso local.

## 4. Dependências

[SPEC-006](SPEC-006.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-11, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Salvar metas próprias.
2. aplicar edição no mês corrente.
3. apurar valores.
4. calcular razões.
5. mostrar progresso.
6. sinalizar limites.

**Alternativa observável:** Meta de gasto 100 e gasto 120 mostram 120% e estouro; categoria sem meta fica sem alerta.

**Exceções:** Meta zero/negativa e faixas de cor sem decisão não autorizam divisão por zero; regra deve ser fechada em OPEN-21.

**Pós-condições:** metas vigentes, barras de progresso e sinais de ultrapassagem; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-021-R01 | WHEN ocorrer o fluxo válido de definir metas de orçamento e acompanhar progresso THE SYSTEM SHALL entregar metas vigentes, barras de progresso e sinais de ultrapassagem. | CA-001 |
| SPEC-021-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-021-R03 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-14/C01 THE SYSTEM SHALL atender ao comportamento: definir uma meta de gasto total mensal (teto). | CA-003 |
| SPEC-021-R04 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-14/C02 THE SYSTEM SHALL atender ao comportamento: definir uma meta de renda total mensal (piso desejado). | CA-004 |
| SPEC-021-R05 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-14/C03 THE SYSTEM SHALL atender ao comportamento: as metas podem ser editadas a qualquer momento, valendo a partir do mês corrente. | CA-005 |
| SPEC-021-R06 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-14/C04 THE SYSTEM SHALL atender ao comportamento: indicar visualmente quando a meta de gasto for ultrapassada ou a meta de renda não for atingida. | CA-006 |
| SPEC-021-R07 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-15/C01 THE SYSTEM SHALL atender ao comportamento: definir um valor máximo mensal para cada categoria de gasto (ex.: até R$500 em Lazer). | CA-007 |
| SPEC-021-R08 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-15/C02 THE SYSTEM SHALL atender ao comportamento: alertar quando o gasto acumulado da categoria no mês atingir um percentual configurável da meta (ex.: 90%) e quando ultrapassar 100%. | CA-008 |
| SPEC-021-R09 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-15/C03 THE SYSTEM SHALL atender ao comportamento: categorias sem meta definida não geram alerta. | CA-009 |
| SPEC-021-R10 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-19/C01 THE SYSTEM SHALL atender ao comportamento: exibir barra de progresso para a meta geral de gasto (gasto atual / meta) e para a meta geral de renda (renda atual / meta). | CA-010 |
| SPEC-021-R11 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-19/C02 THE SYSTEM SHALL atender ao comportamento: exibir uma barra de progresso por categoria que tenha meta definida (RF-15). | CA-011 |
| SPEC-021-R12 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-19/C03 THE SYSTEM SHALL atender ao comportamento: a cor da barra deve mudar conforme a proximidade do limite (ex.: verde até 70%, amarelo até 90%, vermelho acima de 100%). | CA-012 |
| SPEC-021-R13 | WHEN o fluxo de definir metas de orçamento e acompanhar progresso alcançar o comportamento de RF-19/C04 THE SYSTEM SHALL atender ao comportamento: ser recalculado automaticamente a cada novo lançamento no mês corrente. | CA-013 |

## 6. Regras e invariantes

- **INV-001:** Categoria sem meta não gera alerta de meta; alterar meta não altera lançamentos.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

MetaGeral pertence ao titular e tem tipo renda/gasto, valor e vigência; MetaCategoria liga uma categoria própria/padrão ao limite e período. Progresso é derivado dos lançamentos.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Definir metas de orçamento e acompanhar progresso. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | teto de gasto, piso de renda, limite por categoria e percentuais configuráveis |
| Saída | metas vigentes, barras de progresso e sinais de ultrapassagem |
| Erro | Meta zero/negativa e faixas de cor sem decisão não autorizam divisão por zero; regra deve ser fechada em OPEN-21. |

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
| RNF-14 (Backup e recuperação) | Restaurar backup isolado, medir RPO <=24h/RTO <=4h e aplicar exclusões; depende de OPEN-05/32. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-18 (Auditoria) | Inspecionar autoria/ação/instante e recusa de edição operacional; retenção pessoal depende de OPEN-05/19. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Meta de gasto 100 e gasto 120 mostram 120% e estouro; categoria sem meta fica sem alerta.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Meta zero/negativa e faixas de cor sem decisão não autorizam divisão por zero; regra deve ser fechada em OPEN-21.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-14/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder definir uma meta de gasto total mensal (teto).

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-14/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder definir uma meta de renda total mensal (piso desejado).

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-14/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: As metas podem ser editadas a qualquer momento, valendo a partir do mês corrente.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-14/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve indicar visualmente quando a meta de gasto for ultrapassada ou a meta de renda não for atingida.

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-15/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder definir um valor máximo mensal para cada categoria de gasto (ex.: até R$500 em Lazer).

- **CA-008** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-15/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve alertar quando o gasto acumulado da categoria no mês atingir um percentual configurável da meta (ex.: 90%) e quando ultrapassar 100%.

- **CA-009** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-15/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Categorias sem meta definida não geram alerta.

- **CA-010** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-19/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir barra de progresso para a meta geral de gasto (gasto atual / meta) e para a meta geral de renda (renda atual / meta).

- **CA-011** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-19/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir uma barra de progresso por categoria que tenha meta definida (RF-15).

- **CA-012** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-19/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A cor da barra deve mudar conforme a proximidade do limite (ex.: verde até 70%, amarelo até 90%, vermelho acima de 100%).

- **CA-013** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-19/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve ser recalculado automaticamente a cada novo lançamento no mês corrente.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-021-R01; CA-001; INV-001, INV-002 | Fixture específica: Meta de gasto 100 e gasto 120 mostram 120% e estouro; categoria sem meta fica sem alerta. |
| T-002 | SPEC-021-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Meta zero/negativa e faixas de cor sem decisão não autorizam divisão por zero; regra deve ser fechada em OPEN-21. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-021-R03; CA-003 | RF-14/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder definir uma meta de gasto total mensal (teto). |
| T-004 | SPEC-021-R04; CA-004 | RF-14/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder definir uma meta de renda total mensal (piso desejado). |
| T-005 | SPEC-021-R05; CA-005 | RF-14/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: As metas podem ser editadas a qualquer momento, valendo a partir do mês corrente. |
| T-006 | SPEC-021-R06; CA-006 | RF-14/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve indicar visualmente quando a meta de gasto for ultrapassada ou a meta de renda não for atingida. |
| T-007 | SPEC-021-R07; CA-007 | RF-15/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder definir um valor máximo mensal para cada categoria de gasto (ex.: até R$500 em Lazer). |
| T-008 | SPEC-021-R08; CA-008 | RF-15/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve alertar quando o gasto acumulado da categoria no mês atingir um percentual configurável da meta (ex.: 90%) e quando ultrapassar 100%. |
| T-009 | SPEC-021-R09; CA-009 | RF-15/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Categorias sem meta definida não geram alerta. |
| T-010 | SPEC-021-R10; CA-010 | RF-19/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir barra de progresso para a meta geral de gasto (gasto atual / meta) e para a meta geral de renda (renda atual / meta). |
| T-011 | SPEC-021-R11; CA-011 | RF-19/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir uma barra de progresso por categoria que tenha meta definida (RF-15). |
| T-012 | SPEC-021-R12; CA-012 | RF-19/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A cor da barra deve mudar conforme a proximidade do limite (ex.: verde até 70%, amarelo até 90%, vermelho acima de 100%). |
| T-013 | SPEC-021-R13; CA-013 | RF-19/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve ser recalculado automaticamente a cada novo lançamento no mês corrente. |
| T-014 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

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
