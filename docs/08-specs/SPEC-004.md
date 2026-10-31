# SPEC-004: Tributação de produto na projeção

**Estado:** implementada tecnicamente no código do grupo, incorporado à `main` em 2026-10-31 (PR #43); testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py` e interface web na navegação por abas (PR #45). A cobertura por cláusula (C-02) usa testes agrupados e deve ser detalhada na revisão; aprovação formal do grupo pendente.

## 1. Identificação

- **ID:** SPEC-004
- **Nome:** Tributação de produto na projeção
- **Objetivo:** Identificar produto e regra aprovada; calcular base e imposto; apurar líquido; devolver regra/hipóteses; distinguir produto isento.
- **Valor entregue:** imposto estimado e resultado líquido identificado.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-20, RF-64.
- **RB:** RB-07, RB-25, RB-28.
- **RNF:** RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-09; fluxo tributário de RF-64; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Simulacao e resultado bruto; tabela tributária conceitual; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** tributação de produto na projeção; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Cobertura parcial: somente tributação usada pela renda fixa. Ações/FIIs/day trade e DARF pertencem à SPEC-048. Não fixar alíquotas ou incidência de aportes sem OPEN-07.

## 4. Dependências

[SPEC-002](SPEC-002.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-07, OPEN-03, OPEN-15. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** fórmulas e parâmetros de cálculo aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Identificar produto e regra aprovada.
2. calcular base e imposto.
3. apurar líquido.
4. devolver regra/hipóteses.
5. distinguir produto isento.

**Alternativa observável:** Aplicar produto de teste com regra explícita e conferir bruto, imposto e líquido com referência independente aprovada.

**Exceções:** Produto sem regra vigente não recebe imposto zero inventado.

**Pós-condições:** imposto estimado e resultado líquido identificado; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-004-R01 | WHEN ocorrer o fluxo válido de tributação de produto na projeção THE SYSTEM SHALL entregar imposto estimado e resultado líquido identificado. | CA-001 |
| SPEC-004-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-004-R03 | WHEN o fluxo de tributação de produto na projeção alcançar o comportamento de RF-20/tributação THE SYSTEM SHALL atender ao comportamento: distinguir bruto, imposto e líquido conforme regra do produto e prazo. | CA-003 |
| SPEC-004-R04 | WHEN o fluxo de tributação de produto na projeção alcançar o comportamento de RF-64/regra THE SYSTEM SHALL atender ao comportamento: usar regra interna versionada sem afirmar cobertura de ações/FIIs/day trade nesta unidade. | CA-004 |

## 6. Regras e invariantes

- **INV-001:** A regra não é obtida em chamada síncrona à Receita; resultado bruto não é apresentado como líquido.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: o motor numérico não faz I/O, não persiste e não altera dados reais; a aplicação desta capacidade coordena os adaptadores previstos no fluxo.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-07: Simulações de renda fixa usam juros compostos indexados a CDI, Selic ou IPCA conforme o produto; RB-25: A estimativa de IR usa tabela de alíquotas interna e configurável, variando por tipo de aplicação e prazo — nunca chamada em tempo real à Receita Federal; RB-28: O motor genérico aceita valor inicial e aporte não negativos, taxa não negativa e prazo inteiro positivo; esses parâmetros não são lançamentos de renda/despesa e não estão sujeitos ao mínimo estrito de RB-01. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Resultado bruto mantém capital/aportes e prazo que determinam a base tributável; resultado líquido é valor derivado. Regra tributária é versionada, não uma tabela física nova definida aqui.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Tributação de produto na projeção. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | resultado bruto, capital/aportes, produto, prazo e versão de regra |
| Saída | imposto estimado e resultado líquido identificado |
| Erro | Produto sem regra vigente não recebe imposto zero inventado. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Aplicar produto de teste com regra explícita e conferir bruto, imposto e líquido com referência independente aprovada.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Produto sem regra vigente não recebe imposto zero inventado.

- **CA-003** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-20/tributação, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Distinguir bruto, imposto e líquido conforme regra do produto e prazo.

- **CA-004** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-64/regra, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Usar regra interna versionada sem afirmar cobertura de ações/FIIs/day trade nesta unidade.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-004-R01; CA-001; INV-001, INV-002 | Fixture específica: Aplicar produto de teste com regra explícita e conferir bruto, imposto e líquido com referência independente aprovada. |
| T-002 | SPEC-004-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Produto sem regra vigente não recebe imposto zero inventado. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-004-R03; CA-003 | RF-20/tributação: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Distinguir bruto, imposto e líquido conforme regra do produto e prazo. |
| T-004 | SPEC-004-R04; CA-004 | RF-64/regra: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Usar regra interna versionada sem afirmar cobertura de ações/FIIs/day trade nesta unidade. |
| T-005 | INV-001, INV-002, INV-003; RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py`, executados na CI com PostgreSQL. A correspondência um-para-um entre cláusulas e testes (C-02) ainda precisa ser detalhada.

## 13. Questões em Aberto

- OPEN-07 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.

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
