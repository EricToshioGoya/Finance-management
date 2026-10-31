# SPEC-008: Executar simulação rastreável de renda fixa

**Estado:** implementada tecnicamente no código do grupo, incorporado à `main` em 2026-10-31 (PR #43); testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py` e interface web na navegação por abas (PR #45). Cobertura por cláusula (C-02) concluída em 2026-10-31: cada cláusula `SHALL` tem teste `test_SPEC_008_Rxx` em `backend/tests/test_c02_spec007_010_simulacoes.py`; aprovação formal do grupo pendente.

## 1. Identificação

- **ID:** SPEC-008
- **Nome:** Executar simulação rastreável de renda fixa
- **Objetivo:** Validar titular e entradas; selecionar taxa de cache válido ou hipótese manual explícita; chamar motor e regra tributária; registrar parâmetros/referência; apresentar resultado.
- **Valor entregue:** projeção bruta/líquida com hipóteses e indicador referenciado.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-20.
- **RB:** RB-07, RB-10, RB-28, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-09; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario, Simulacao e IndicadorMercadoCache; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-03, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-003, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** executar simulação rastreável de renda fixa; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

SPEC-004 resolve tributação, SPEC-002 calcula bruto; registrar a origem da taxa e avisar quando manual.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-002](SPEC-002.md), [SPEC-004](SPEC-004.md), [SPEC-007](SPEC-007.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-07, OPEN-10, OPEN-15, OPEN-19. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar titular e entradas.
2. selecionar taxa de cache válido ou hipótese manual explícita.
3. chamar motor e regra tributária.
4. registrar parâmetros/referência.
5. apresentar resultado.

**Alternativa observável:** Cenário com inicial 1000, sem aporte e taxa hipotética anual 12% por 12 meses apresenta bruto 1120; líquido depende da regra de teste aprovada.

**Exceções:** Falha do cache não vira taxa zero nem aplicação automática de taxa manual.

**Pós-condições:** projeção bruta/líquida com hipóteses e indicador referenciado; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-008-R01 | WHEN ocorrer o fluxo válido de executar simulação rastreável de renda fixa THE SYSTEM SHALL entregar projeção bruta/líquida com hipóteses e indicador referenciado. | CA-001 |
| SPEC-008-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-008-R03 | WHEN o fluxo de executar simulação rastreável de renda fixa alcançar o comportamento de RF-20/C01 THE SYSTEM SHALL atender ao comportamento: permitir simular CDB, Tesouro e poupança informando valor inicial, aporte mensal e prazo. | CA-003 |
| SPEC-008-R04 | WHEN o fluxo de executar simulação rastreável de renda fixa alcançar o comportamento de RF-20/C02 THE SYSTEM SHALL atender ao comportamento: usar o motor de cálculo de juros compostos (RF-22), alimentado pela taxa vinda dos indicadores oficiais (RF-23) — sem o usuário precisar digitar a taxa manualmente. | CA-004 |
| SPEC-008-R05 | WHEN o fluxo de executar simulação rastreável de renda fixa alcançar o comportamento de RF-20/C03 THE SYSTEM SHALL atender ao comportamento: permitir ao usuário sobrepor a taxa sugerida por um valor manual, caso queira simular um cenário hipotético. | CA-005 |
| SPEC-008-R06 | WHEN o fluxo de executar simulação rastreável de renda fixa alcançar o comportamento de RF-20/C04 THE SYSTEM SHALL atender ao comportamento: exibir o valor bruto e, quando aplicável, o valor líquido de IR (tabela regressiva conforme prazo, exceto poupança e produtos isentos). | CA-006 |
| SPEC-008-R07 | WHEN o fluxo de executar simulação rastreável de renda fixa alcançar o comportamento de RF-20/C05 THE SYSTEM SHALL atender ao comportamento: exibir a data de referência do indicador usado na simulação. | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Simular não movimenta saldo nem cria ativo real; líquido depende de regra tributária definida.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-07: Simulações de renda fixa usam juros compostos indexados a CDI, Selic ou IPCA conforme o produto; RB-10: M = P × (1 + i)ⁿ + Σ aportes capitalizados; taxa convertida entre mês/ano por equivalência composta, nunca proporcional simples; RB-28: O motor genérico aceita valor inicial e aporte não negativos, taxa não negativa e prazo inteiro positivo; esses parâmetros não são lançamentos de renda/despesa e não estão sujeitos ao mínimo estrito de RB-01; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario possui 0..N Simulacao; registro mantém tipo, parâmetros, resultado e origem/data de referência do indicador; ResultadoCalculo não representa patrimônio.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Executar simulação rastreável de renda fixa. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-003, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | CDB/Tesouro/poupança, inicial, aporte, prazo e opção oficial/manual |
| Saída | projeção bruta/líquida com hipóteses e indicador referenciado |
| Erro | Falha do cache não vira taxa zero nem aplicação automática de taxa manual. |

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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Cenário com inicial 1000, sem aporte e taxa hipotética anual 12% por 12 meses apresenta bruto 1120; líquido depende da regra de teste aprovada.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Falha do cache não vira taxa zero nem aplicação automática de taxa manual.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-20/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir simular CDB, Tesouro e poupança informando valor inicial, aporte mensal e prazo.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-20/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve usar o motor de cálculo de juros compostos (RF-22), alimentado pela taxa vinda dos indicadores oficiais (RF-23) — sem o usuário precisar digitar a taxa manualmente.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-20/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir ao usuário sobrepor a taxa sugerida por um valor manual, caso queira simular um cenário hipotético.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-20/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir o valor bruto e, quando aplicável, o valor líquido de IR (tabela regressiva conforme prazo, exceto poupança e produtos isentos).

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-20/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir a data de referência do indicador usado na simulação.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-008-R01; CA-001; INV-001, INV-002 | Fixture específica: Cenário com inicial 1000, sem aporte e taxa hipotética anual 12% por 12 meses apresenta bruto 1120; líquido depende da regra de teste aprovada. |
| T-002 | SPEC-008-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Falha do cache não vira taxa zero nem aplicação automática de taxa manual. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-008-R03; CA-003 | RF-20/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir simular CDB, Tesouro e poupança informando valor inicial, aporte mensal e prazo. |
| T-004 | SPEC-008-R04; CA-004 | RF-20/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve usar o motor de cálculo de juros compostos (RF-22), alimentado pela taxa vinda dos indicadores oficiais (RF-23) — sem o usuário precisar digitar a taxa manualmente. |
| T-005 | SPEC-008-R05; CA-005 | RF-20/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir ao usuário sobrepor a taxa sugerida por um valor manual, caso queira simular um cenário hipotético. |
| T-006 | SPEC-008-R06; CA-006 | RF-20/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir o valor bruto e, quando aplicável, o valor líquido de IR (tabela regressiva conforme prazo, exceto poupança e produtos isentos). |
| T-007 | SPEC-008-R07; CA-007 | RF-20/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir a data de referência do indicador usado na simulação. |
| T-008 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py`, executados na CI com PostgreSQL. A correspondência um-para-um entre cláusulas e testes (C-02) está nos testes `test_SPEC_NNN_Rxx` indicados no Estado desta spec.

## 13. Questões em Aberto

- OPEN-07 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
