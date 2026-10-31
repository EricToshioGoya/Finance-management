# SPEC-013: Operar calculadora de juros com explicação

**Estado:** implementada tecnicamente no código do grupo, incorporado à `main` em 2026-10-31 (PR #43); testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py` e interface web na navegação por abas (PR #45). Cobertura por cláusula (C-02) concluída em 2026-10-31: cada cláusula `SHALL` tem teste `test_SPEC_013_Rxx` em `backend/tests/test_c02_spec004_013_024_calculos.py`; seletores de período da taxa, unidade de prazo e origem da taxa (manual ou indicador do cache local) disponíveis na API e na interface web; aprovação formal do grupo pendente.

## 1. Identificação

- **ID:** SPEC-013
- **Nome:** Operar calculadora de juros com explicação
- **Objetivo:** Apresentar campos/seletores; obter taxa oficial ou aceitar manual explícita; validar; executar motor; renderizar tabela/gráfico/resumo; abrir explicação sem sair.
- **Valor entregue:** tabela mensal, gráfico, resumo e ajuda da taxa.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-22, RF-44.
- **RB:** RB-10, RB-28, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-08; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** ResultadoCalculo e IndicadorMercadoCache; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-03, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-003, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** operar calculadora de juros com explicação; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Cobertura parcial de RF-44: ajuda da taxa deve consumir a mesma fonte de conteúdo da SPEC-035, dependência condicional desse componente. Regra geral de tooltips pertence à SPEC-035.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-002](SPEC-002.md), [SPEC-007](SPEC-007.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-10, OPEN-15, OPEN-19. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Apresentar campos/seletores.
2. obter taxa oficial ou aceitar manual explícita.
3. validar.
4. executar motor.
5. renderizar tabela/gráfico/resumo.
6. abrir explicação sem sair.

**Alternativa observável:** Taxa mensal 1%, aporte 100, inicial zero e 2 meses mostra 100/201 na tabela e montante 201 no resumo.

**Exceções:** Taxa negativa, prazo zero ou valor inicial negativo impedem cálculo e indicam campo.

**Pós-condições:** tabela mensal, gráfico, resumo e ajuda da taxa; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-013-R01 | WHEN ocorrer o fluxo válido de operar calculadora de juros com explicação THE SYSTEM SHALL entregar tabela mensal, gráfico, resumo e ajuda da taxa. | CA-001 |
| SPEC-013-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-013-R03 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C02 THE SYSTEM SHALL atender ao comportamento: o campo **Taxa de juros** deve ter um seletor para o usuário escolher se o percentual informado é **mensal** ou **anual**. | CA-003 |
| SPEC-013-R04 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C03 THE SYSTEM SHALL atender ao comportamento: o campo **Período** deve ter um seletor para o usuário escolher se o número informado é em **meses** ou em **anos**. | CA-004 |
| SPEC-013-R05 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C06 THE SYSTEM SHALL atender ao comportamento: o clique no ícone de ajuda (`?`) ao lado de "Taxa de juros" deve exibir uma explicação em linguagem simples do que é a taxa e de como ela é usada no cálculo. | CA-005 |
| SPEC-013-R06 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C08 THE SYSTEM SHALL atender ao comportamento: aceitar a taxa em duas origens: (a) indicador oficial buscado via RF-23 (pré-preenchendo o campo), ou (b) valor informado manualmente pelo usuário (sobrescrevendo o valor sugerido). | CA-006 |
| SPEC-013-R07 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C10 THE SYSTEM SHALL atender ao comportamento: gerar uma tabela mês a mês com saldo acumulado, juros do período e aporte do período. | CA-007 |
| SPEC-013-R08 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C11 THE SYSTEM SHALL atender ao comportamento: gerar os dados para um gráfico de evolução do saldo acumulado ao longo do prazo. | CA-008 |
| SPEC-013-R09 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-22/C12 THE SYSTEM SHALL atender ao comportamento: exibir o resultado final consolidado: valor total investido (aportes), total de juros ganhos e montante final. | CA-009 |
| SPEC-013-R10 | WHEN o fluxo de operar calculadora de juros com explicação alcançar o comportamento de RF-44/ajuda-taxa THE SYSTEM SHALL atender ao comportamento: abrir explicação da taxa em linguagem simples sem sair da calculadora; reutilizar conteúdo educativo. | CA-010 |

## 6. Regras e invariantes

- **INV-001:** UI não duplica motor; aporte ocorre no fim do mês e equivalência nunca usa divisão simples.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-10: M = P × (1 + i)ⁿ + Σ aportes capitalizados; taxa convertida entre mês/ano por equivalência composta, nunca proporcional simples; RB-28: O motor genérico aceita valor inicial e aporte não negativos, taxa não negativa e prazo inteiro positivo; esses parâmetros não são lançamentos de renda/despesa e não estão sujeitos ao mínimo estrito de RB-01; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

ResultadoCalculo contém resumo e série mensal; Simulacao registra execução se houver persistência prevista pela aplicação. Entrada guarda unidade da taxa/prazo e origem oficial/manual para exibição.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Operar calculadora de juros com explicação. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-003, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | inicial/aporte, taxa com seletor mensal/anual e prazo meses/anos |
| Saída | tabela mensal, gráfico, resumo e ajuda da taxa |
| Erro | Taxa negativa, prazo zero ou valor inicial negativo impedem cálculo e indicam campo. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-09 (Atualidade de dados de mercado) | Relógio/fonte simulados: referência, coleta, dados ausentes e limites 24h/15min; fechar OPEN-19. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Taxa mensal 1%, aporte 100, inicial zero e 2 meses mostra 100/201 na tabela e montante 201 no resumo.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Taxa negativa, prazo zero ou valor inicial negativo impedem cálculo e indicam campo.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O campo **Taxa de juros** deve ter um seletor para o usuário escolher se o percentual informado é **mensal** ou **anual**.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O campo **Período** deve ter um seletor para o usuário escolher se o número informado é em **meses** ou em **anos**.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C06, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O clique no ícone de ajuda (`?`) ao lado de "Taxa de juros" deve exibir uma explicação em linguagem simples do que é a taxa e de como ela é usada no cálculo.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C08, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve aceitar a taxa em duas origens: (a) indicador oficial buscado via RF-23 (pré-preenchendo o campo), ou (b) valor informado manualmente pelo usuário (sobrescrevendo o valor sugerido).

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C10, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve gerar uma tabela mês a mês com saldo acumulado, juros do período e aporte do período.

- **CA-008** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C11, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve gerar os dados para um gráfico de evolução do saldo acumulado ao longo do prazo.

- **CA-009** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-22/C12, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir o resultado final consolidado: valor total investido (aportes), total de juros ganhos e montante final.

- **CA-010** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-44/ajuda-taxa, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Abrir explicação da taxa em linguagem simples sem sair da calculadora; reutilizar conteúdo educativo.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-013-R01; CA-001; INV-001, INV-002 | Fixture específica: Taxa mensal 1%, aporte 100, inicial zero e 2 meses mostra 100/201 na tabela e montante 201 no resumo. |
| T-002 | SPEC-013-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Taxa negativa, prazo zero ou valor inicial negativo impedem cálculo e indicam campo. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-013-R03; CA-003 | RF-22/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O campo **Taxa de juros** deve ter um seletor para o usuário escolher se o percentual informado é **mensal** ou **anual**. |
| T-004 | SPEC-013-R04; CA-004 | RF-22/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O campo **Período** deve ter um seletor para o usuário escolher se o número informado é em **meses** ou em **anos**. |
| T-005 | SPEC-013-R05; CA-005 | RF-22/C06: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O clique no ícone de ajuda (`?`) ao lado de "Taxa de juros" deve exibir uma explicação em linguagem simples do que é a taxa e de como ela é usada no cálculo. |
| T-006 | SPEC-013-R06; CA-006 | RF-22/C08: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve aceitar a taxa em duas origens: (a) indicador oficial buscado via RF-23 (pré-preenchendo o campo), ou (b) valor informado manualmente pelo usuário (sobrescrevendo o valor sugerido). |
| T-007 | SPEC-013-R07; CA-007 | RF-22/C10: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve gerar uma tabela mês a mês com saldo acumulado, juros do período e aporte do período. |
| T-008 | SPEC-013-R08; CA-008 | RF-22/C11: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve gerar os dados para um gráfico de evolução do saldo acumulado ao longo do prazo. |
| T-009 | SPEC-013-R09; CA-009 | RF-22/C12: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir o resultado final consolidado: valor total investido (aportes), total de juros ganhos e montante final. |
| T-010 | SPEC-013-R10; CA-010 | RF-44/ajuda-taxa: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Abrir explicação da taxa em linguagem simples sem sair da calculadora; reutilizar conteúdo educativo. |
| T-011 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py`, executados na CI com PostgreSQL. A correspondência um-para-um entre cláusulas e testes (C-02) está nos testes `test_SPEC_NNN_Rxx` indicados no Estado desta spec.

## 13. Questões em Aberto

- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-10 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-19 — decisão necessária: Conciliar inconsistências herdadas: RF-23/RNF-09 versus ADR-003 (cache vencido/referência), RF-35 versus RB-13 (simulado/real), RB-18 (valor/progresso), aliases de entidade, antigos UCs, prazo de token normativo versus proposta e retenção versus auditoria imutável / Specs consumidoras e baseline; registrar alteração aprovada, não escolher silenciosamente.

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
