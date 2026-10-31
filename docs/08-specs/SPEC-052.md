# SPEC-052: Guiar primeiro acesso com tour opcional

**Estado:** rascunho para revisão humana, criado em 2026-10-22. Produção documental autorizada no lote atual; sem implementação/testes novos ou aprovação formal presumida.

## 1. Identificação

- **ID:** SPEC-052
- **Nome:** Guiar primeiro acesso com tour opcional
- **Objetivo:** Detectar primeiro acesso segundo política aprovada; apresentar primeira receita/despesa/quiz/simulador; permitir pular em qualquer ponto; reabrir na ajuda; adaptar didática ao perfil.
- **Valor entregue:** tour adaptado com acesso às funções principais.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-04.
- **RB:** RB-09.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** Fluxo onboarding RF-04; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e perfil de experiência; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** guiar primeiro acesso com tour opcional; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Persistência do estado concluído e ordem de quem ainda não fez quiz estão em OPEN-30.

## 4. Dependências

[SPEC-003](SPEC-003.md), [SPEC-006](SPEC-006.md), [SPEC-008](SPEC-008.md), [SPEC-013](SPEC-013.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-08, OPEN-15, OPEN-30. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Detectar primeiro acesso segundo política aprovada.
2. apresentar primeira receita/despesa/quiz/simulador.
3. permitir pular em qualquer ponto.
4. reabrir na ajuda.
5. adaptar didática ao perfil.

**Alternativa observável:** Usuário pula na primeira etapa e acessa as funções; depois reabre o mesmo conteúdo de ajuda.

**Exceções:** Perfil ainda não respondido não recebe classificação inventada para guiar o tour.

**Pós-condições:** tour adaptado com acesso às funções principais; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-052-R01 | WHEN ocorrer o fluxo válido de guiar primeiro acesso com tour opcional THE SYSTEM SHALL entregar tour adaptado com acesso às funções principais. | CA-001 |
| SPEC-052-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-052-R03 | WHEN o fluxo de guiar primeiro acesso com tour opcional alcançar o comportamento de RF-04/C01 THE SYSTEM SHALL atender ao comportamento: no primeiro login, deve apresentar um tour guiado cobrindo, no mínimo: cadastro da primeira renda, cadastro da primeira despesa, e como acessar o quiz de perfil (RF-03) e o simulador. | CA-003 |
| SPEC-052-R04 | WHEN o fluxo de guiar primeiro acesso com tour opcional alcançar o comportamento de RF-04/C02 THE SYSTEM SHALL atender ao comportamento: permitir pular o tour a qualquer momento. | CA-004 |
| SPEC-052-R05 | WHEN o fluxo de guiar primeiro acesso com tour opcional alcançar o comportamento de RF-04/C03 THE SYSTEM SHALL atender ao comportamento: poder ser reaberto manualmente pelo usuário depois (ex.: menu de ajuda). | CA-005 |
| SPEC-052-R06 | WHEN o fluxo de guiar primeiro acesso com tour opcional alcançar o comportamento de RF-04/C04 THE SYSTEM SHALL atender ao comportamento: o conteúdo sugerido deve se adaptar ao perfil: iniciante recebe um tour mais didático; avançado pode pular direto para funcionalidades avançadas. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Pular tour não impede acesso às funções nem cria dados financeiros fictícios.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-09: O resultado do quiz de perfil define a experiência exibida no simulador. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario possui estado de introdução a definir e perfil para adaptar conteúdo; tour referencia capacidades existentes, sem criar receita/despesa fictícia.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Guiar primeiro acesso com tour opcional. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | primeiro login, perfil e ação pular/reabrir |
| Saída | tour adaptado com acesso às funções principais |
| Erro | Perfil ainda não respondido não recebe classificação inventada para guiar o tour. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Usuário pula na primeira etapa e acessa as funções; depois reabre o mesmo conteúdo de ajuda.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Perfil ainda não respondido não recebe classificação inventada para guiar o tour.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-04/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: No primeiro login, deve apresentar um tour guiado cobrindo, no mínimo: cadastro da primeira renda, cadastro da primeira despesa, e como acessar o quiz de perfil (RF-03) e o simulador.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-04/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir pular o tour a qualquer momento.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-04/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve poder ser reaberto manualmente pelo usuário depois (ex.: menu de ajuda).

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-04/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O conteúdo sugerido deve se adaptar ao perfil: iniciante recebe um tour mais didático; avançado pode pular direto para funcionalidades avançadas.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-052-R01; CA-001; INV-001, INV-002 | Fixture específica: Usuário pula na primeira etapa e acessa as funções; depois reabre o mesmo conteúdo de ajuda. |
| T-002 | SPEC-052-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Perfil ainda não respondido não recebe classificação inventada para guiar o tour. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-052-R03; CA-003 | RF-04/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: No primeiro login, deve apresentar um tour guiado cobrindo, no mínimo: cadastro da primeira renda, cadastro da primeira despesa, e como acessar o quiz de perfil (RF-03) e o simulador. |
| T-004 | SPEC-052-R04; CA-004 | RF-04/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir pular o tour a qualquer momento. |
| T-005 | SPEC-052-R05; CA-005 | RF-04/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve poder ser reaberto manualmente pelo usuário depois (ex.: menu de ajuda). |
| T-006 | SPEC-052-R06; CA-006 | RF-04/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O conteúdo sugerido deve se adaptar ao perfil: iniciante recebe um tour mais didático; avançado pode pular direto para funcionalidades avançadas. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-08 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-30 — decisão necessária: Conteúdo/UI: acervo e revisão de PT/EN, termos sem verbete, fluxo inicial sem quiz, estado de tour e limites/formatos de entrada ainda sem contrato / SPEC-013, SPEC-035, SPEC-052; complementar OPEN-15.

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
