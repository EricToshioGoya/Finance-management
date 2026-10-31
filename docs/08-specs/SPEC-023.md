# SPEC-023: Consultar cotação e histórico de ações/FIIs

**Estado:** implementada tecnicamente em 2026-10-29; aguarda revisão humana do grupo. Evidências em [implementacao-SPEC-023](../09-qualidade/implementacao-SPEC-023.md).

## 1. Identificação

- **ID:** SPEC-023
- **Nome:** Consultar cotação e histórico de ações/FIIs
- **Objetivo:** Validar ticker; consultar fonte homologada por adaptador; informar preço/variação/histórico e referência; em falha oferecer entrada manual explícita no consumidor.
- **Valor entregue:** preço, variação diária, histórico e referência temporal.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-24.
- **RB:** RB-08.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-10; fluxo de RF-24; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Cotação como dado de integração e Simulacao consumidora; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-03, DA-07, DA-09; ADR-001, ADR-003; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consultar cotação e histórico de ações/fiis; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Neste contrato local não há agregador nem chamada de mercado: o catálogo versionado contém PETR4 e MXRF11, sempre identificado como referência local datada. A referência só pode ser apresentada como atual até 24 horas após `referenced_at`; depois disso, ou se estiver indisponível, a API informa indisponibilidade e autoriza entrada manual ao consumidor.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-10, OPEN-15, OPEN-19. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** sessão autenticada e referência local disponível dentro da janela de 24 horas.

**Fluxo principal:**

1. Validar e normalizar o ticker.
2. Consultar o catálogo local versionado, sem I/O externo na solicitação.
3. Conferir disponibilidade e idade máxima de 24 horas.
4. Informar preço, variação diária, histórico e referência temporal; em erro, responder `manual_entry_permitted=true` para o consumidor prosseguir com valor/rentabilidade manual.

**Alternativa observável:** PETR4 e MXRF11 retornam preço/histórico datados e `catalogue_type=local_reference`; referência indisponível ou vencida retorna 503 sem preço zero e com `manual_entry_permitted=true`.

**Exceções:** Ticker malformado retorna 422; ticker desconhecido retorna 404; dado acima da defasagem máxima não é apresentado como atual.

**Pós-condições:** preço, variação diária, histórico e referência temporal; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-023-R01 | WHEN ocorrer o fluxo válido de consultar cotação e histórico de ações/fiis THE SYSTEM SHALL entregar preço, variação diária, histórico e referência temporal. | CA-001 |
| SPEC-023-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-023-R03 | WHEN o fluxo de consultar cotação e histórico de ações/fiis alcançar o comportamento de RF-24/C01 THE SYSTEM SHALL atender ao comportamento: buscar um ativo pelo ticker (ex.: PETR4, MXRF11). | CA-003 |
| SPEC-023-R04 | WHEN o fluxo de consultar cotação e histórico de ações/fiis alcançar o comportamento de RF-24/C02 THE SYSTEM SHALL atender ao comportamento: retornar preço mais recente disponível, variação do dia e data/hora de referência da cotação. | CA-004 |
| SPEC-023-R05 | WHEN o fluxo de consultar cotação e histórico de ações/fiis alcançar o comportamento de RF-24/C03 THE SYSTEM SHALL atender ao comportamento: retornar histórico de preços do ativo para cálculo de rentabilidade histórica (usada como sugestão em RF-21). | CA-005 |
| SPEC-023-R06 | WHEN o fluxo de consultar cotação e histórico de ações/fiis alcançar o comportamento de RF-24/C04 THE SYSTEM SHALL atender ao comportamento: caso a fonte de dados esteja indisponível, o sistema deve permitir que o usuário prossiga informando valor e rentabilidade manualmente. | CA-006 |
| SPEC-023-R07 | WHEN o fluxo de consultar cotação e histórico de ações/fiis alcançar o comportamento de RF-24/C05 THE SYSTEM SHALL atender ao comportamento: **Nota técnica:** a B3 não oferece API pública gratuita de cotações em tempo real para pessoa física; a fonte de dados (provedor de mercado homologado, ou agregador que consome dados da B3) precisa ser definida antes da implementação — ver risco correspondente na seção 7 (Riscos). | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Fonte indisponível não vira preço zero; histórico não é previsão.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Este recorte local não seleciona provedor de mercado nem declara cotação em tempo real; o contrato é extensível por adaptador futuro.

Regras herdadas: RB-08: Toda projeção de renda variável deve ser exibida como estimativa, sem garantia de retorno. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

`market_quotes` guarda ticker, classe, último/preço anterior, referência temporal, disponibilidade e origem local; `market_quote_history` guarda fechamentos datados. A variação é calculada a partir de último/preço anterior, e o histórico não é previsão.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consultar cotação e histórico de ações/FIIs. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

`MarketQuoteService` mantém validação, janela de 24 horas e contrato de indisponibilidade na aplicação; a persistência é local. Um adaptador de provedor homologado pode substituir a origem no futuro sem alterar a rota. Testes usam catálogo/momento injetáveis, sem serviços externos reais.

ADRs relacionados: ADR-001, ADR-003. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | `GET /api/v1/market/quotes/{ticker}` autenticado; ticker de ação/FII |
| Saída | preço, variação diária, histórico, `referenced_at`, `fresh_until` e `catalogue_type=local_reference` |
| Erro | 422 para ticker inválido, 404 para desconhecido; 503 `market_reference_stale`/`market_reference_unavailable` com `manual_entry_permitted=true` sem preço inventado. |

O endpoint é autenticado e utiliza o prefixo `/api/v1`; não altera os contratos de sessão. A tela web permite consultar o ticker e apresenta a origem/localidade temporal; o simulador, quando vier a consumi-lo, recebe sinal explícito para aceitar valores manuais na indisponibilidade.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Dublê para PETR4 retorna preço/histórico datados; erro de fonte habilita caminho manual sem fingir cotação atual.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Ticker desconhecido retorna ausência identificável; dado acima da defasagem máxima não é apresentado como atual.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-24/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder buscar um ativo pelo ticker (ex.: PETR4, MXRF11).

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-24/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve retornar preço mais recente disponível, variação do dia e data/hora de referência da cotação.

- **CA-005** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-24/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve retornar histórico de preços do ativo para cálculo de rentabilidade histórica (usada como sugestão em RF-21).

- **CA-006** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-24/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Caso a fonte de dados esteja indisponível, o sistema deve permitir que o usuário prossiga informando valor e rentabilidade manualmente.

- **CA-007** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-24/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: **Nota técnica:** a B3 não oferece API pública gratuita de cotações em tempo real para pessoa física; a fonte de dados (provedor de mercado homologado, ou agregador que consome dados da B3) precisa ser definida antes da implementação — ver risco correspondente na seção 7 (Riscos).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-023-R01; CA-001; INV-001, INV-002 | Fixture específica: Dublê para PETR4 retorna preço/histórico datados; erro de fonte habilita caminho manual sem fingir cotação atual. |
| T-002 | SPEC-023-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Ticker desconhecido retorna ausência identificável; dado acima da defasagem máxima não é apresentado como atual. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-023-R03; CA-003 | RF-24/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder buscar um ativo pelo ticker (ex.: PETR4, MXRF11). |
| T-004 | SPEC-023-R04; CA-004 | RF-24/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve retornar preço mais recente disponível, variação do dia e data/hora de referência da cotação. |
| T-005 | SPEC-023-R05; CA-005 | RF-24/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve retornar histórico de preços do ativo para cálculo de rentabilidade histórica (usada como sugestão em RF-21). |
| T-006 | SPEC-023-R06; CA-006 | RF-24/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Caso a fonte de dados esteja indisponível, o sistema deve permitir que o usuário prossiga informando valor e rentabilidade manualmente. |
| T-007 | SPEC-023-R07; CA-007 | RF-24/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: **Nota técnica:** a B3 não oferece API pública gratuita de cotações em tempo real para pessoa física; a fonte de dados (provedor de mercado homologado, ou agregador que consome dados da B3) precisa ser definida antes da implementação — ver risco correspondente na seção 7 (Riscos). |
| T-008 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-10 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-19 — decisão necessária: Conciliar inconsistências herdadas: RF-23/RNF-09 versus ADR-003 (cache vencido/referência), RF-35 versus RB-13 (simulado/real), RB-18 (valor/progresso), aliases de entidade, antigos UCs, prazo de token normativo versus proposta e retenção versus auditoria imutável / Specs consumidoras e baseline; registrar alteração aprovada, não escolher silenciosamente.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [x] Recorte técnico e política local autorizados com evidência real.
- [x] OPEN-10/15/19 delimitadas para este contrato sem selecionar provedor externo.
- [ ] Esta versão revisada individualmente pelo grupo, sem aprovação histórica presumida.
- [x] Cláusulas/CA do recorte implementadas e invariantes preservados.
- [x] Testes de integração cobrem consulta autenticada, ação/FII, ticker inválido/desconhecido, indisponibilidade e defasagem.
- [ ] Carga, provedor homologado e observabilidade operacional continuam fora do recorte.
- [x] Código, migration, interface e documentação foram conciliados; não há alegação de dado em tempo real.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
