# SPEC-031: Comparar alocação atual e alvo

**Estado:** implementação técnica da SPEC-031 em validação no PR #68, branch `feature/31-portfolio-allocation`. Backend, interface, migração e testes adicionados; revisão/aceite formal do grupo e merge ainda não presumidos.

## 1. Identificação

- **ID:** SPEC-031
- **Nome:** Comparar alocação atual e alvo
- **Objetivo:** Agrupar investimentos por classe; calcular fração sobre total; permitir alvos; apresentar atual/alvo/desvio.
- **Valor entregue:** distribuição percentual e desvios.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-38.
- **RB:** RB-13, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-14; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Ativo e classes patrimoniais; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** comparar alocação atual e alvo; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

**Recorte técnico provisório de OPEN-21:** cinco classes fixas, soma exata dos alvos em 100%, duas casas decimais, classificação explícita de ativos manuais; contas poupança e investimento recebem classe pela modalidade da conta, e demais contas não integram o total investido. Não se inventam taxas nem se incluem projeções. [Decisões e contrato](../09-qualidade/implementacao-SPEC-031.md).

## 4. Dependências

[SPEC-028](SPEC-028.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Agrupar investimentos por classe.
2. calcular fração sobre total.
3. permitir alvos.
4. apresentar atual/alvo/desvio.

**Alternativa observável:** Ativos 25 e 75 em duas classes mostram 25%/75%; alvo 50% em cada mostra desvios -25/+25 pontos.

**Exceções:** Total zero ou alvos inconsistentes não produz NaN nem normalização silenciosa.

**Pós-condições:** distribuição percentual e desvios; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-031-R01 | WHEN ocorrer o fluxo válido de comparar alocação atual e alvo THE SYSTEM SHALL entregar distribuição percentual e desvios. | CA-001 |
| SPEC-031-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-031-R03 | WHEN o fluxo de comparar alocação atual e alvo alcançar o comportamento de RF-38/C01 THE SYSTEM SHALL atender ao comportamento: exibir gráfico de pizza/barras com a distribuição dos ativos de investimento por classe (renda fixa, ações, FIIs, poupança, outros). | CA-003 |
| SPEC-031-R04 | WHEN o fluxo de comparar alocação atual e alvo alcançar o comportamento de RF-38/C02 THE SYSTEM SHALL atender ao comportamento: calcular o percentual de cada classe sobre o total investido. | CA-004 |
| SPEC-031-R05 | WHEN o fluxo de comparar alocação atual e alvo alcançar o comportamento de RF-38/C03 THE SYSTEM SHALL atender ao comportamento: permitir ao usuário definir uma alocação-alvo (%) por classe e comparar com a alocação atual, indicando o desvio. | CA-005 |

## 6. Regras e invariantes

- **INV-001:** Percentual usa a mesma base total em todas as classes; não recomendar compra automaticamente.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-13: Patrimônio líquido = soma dos ativos reais registrados − soma dos passivos reais registrados. Recalcular quando uma origem real mudar; executar simulação não cria ativo nem altera patrimônio real; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Ativos de investimento são agrupados por classe; alocação-alvo percentual pertence ao titular. Classificação e soma dos alvos dependem OPEN-21.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Comparar alocação atual e alvo. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | ativos reais por classe e alvos percentuais |
| Saída | distribuição percentual e desvios |
| Erro | Total zero ou alvos inconsistentes não produz NaN nem normalização silenciosa. |

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

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Ativos 25 e 75 em duas classes mostram 25%/75%; alvo 50% em cada mostra desvios -25/+25 pontos.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Total zero ou alvos inconsistentes não produz NaN nem normalização silenciosa.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-38/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico de pizza/barras com a distribuição dos ativos de investimento por classe (renda fixa, ações, FIIs, poupança, outros).

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-38/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular o percentual de cada classe sobre o total investido.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-38/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir ao usuário definir uma alocação-alvo (%) por classe e comparar com a alocação atual, indicando o desvio.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-031-R01; CA-001; INV-001, INV-002 | Fixture específica: Ativos 25 e 75 em duas classes mostram 25%/75%; alvo 50% em cada mostra desvios -25/+25 pontos. |
| T-002 | SPEC-031-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Total zero ou alvos inconsistentes não produz NaN nem normalização silenciosa. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-031-R03; CA-003 | RF-38/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico de pizza/barras com a distribuição dos ativos de investimento por classe (renda fixa, ações, FIIs, poupança, outros). |
| T-004 | SPEC-031-R04; CA-004 | RF-38/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular o percentual de cada classe sobre o total investido. |
| T-005 | SPEC-031-R05; CA-005 | RF-38/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir ao usuário definir uma alocação-alvo (%) por classe e comparar com a alocação atual, indicando o desvio. |
| T-006 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Os testes de integração foram implementados em `backend/tests/test_spec031_investment_allocation.py` e executados no CI do PR #68. A decisão formal do grupo sobre OPEN-21 e validação operacional/mobile permanecem pendentes. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

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
