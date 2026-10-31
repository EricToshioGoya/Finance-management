# SPEC-007: Consultar indicador oficial válido em cache

**Estado:** implementada tecnicamente no código do grupo, incorporado à `main` em 2026-10-31 (PR #43); testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py` e interface web na navegação por abas (PR #45). Cobertura por cláusula (C-02) concluída em 2026-10-31: cada cláusula `SHALL` tem teste `test_SPEC_007_Rxx` em `backend/tests/test_c02_spec007_010_simulacoes.py`; R03, R04 e R06 implementadas em 2026-10-31 conforme OPEN-04/OPEN-10 e ADR-009 (SGS 432/4389/13522, Tesouro Transparente, rotina diária às 07:00 com novas tentativas), com testes em `backend/tests/test_c02_spec007_indicator_sync.py`; aprovação formal do grupo pendente.

## 1. Identificação

- **ID:** SPEC-007
- **Nome:** Consultar indicador oficial válido em cache
- **Objetivo:** Sincronizar SGS/Tesouro em rotina separada; validar fonte/unidade; atualizar cache local; consultar sem HTTP síncrono; informar validade e falha.
- **Valor entregue:** valor, unidade, periodicidade, referência e estado de disponibilidade.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-23.
- **RB:** RB-11.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-08, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** UC-20 e consulta por UC-09; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** IndicadorMercadoCache (aliases históricos em OPEN-19); [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-03, DA-07, DA-09, DA-11; ADR-001, ADR-003, ADR-006; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consultar indicador oficial válido em cache; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Frequência diária consta do RF; datas de divulgação/última publicação e contratos específicos continuam em OPEN-04/10.

## 4. Dependências

[SPEC-001](SPEC-001.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-04, OPEN-10, OPEN-15, OPEN-19. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** rotina/fonte autorizada e contratos externos aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Sincronizar SGS/Tesouro em rotina separada.
2. validar fonte/unidade.
3. atualizar cache local.
4. consultar sem HTTP síncrono.
5. informar validade e falha.

**Alternativa observável:** Com relógio controlado, cache verificado há 23h é disponibilizado com referência; falha de atualização preserva o registro sem renovar artificialmente sua data.

**Exceções:** Cache ausente/vencido não é apresentado como atual; divergência de política deve ser resolvida em OPEN-19 antes do aceite.

**Pós-condições:** valor, unidade, periodicidade, referência e estado de disponibilidade; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-007-R01 | WHEN ocorrer o fluxo válido de consultar indicador oficial válido em cache THE SYSTEM SHALL entregar valor, unidade, periodicidade, referência e estado de disponibilidade. | CA-001 |
| SPEC-007-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-007-R03 | WHEN o fluxo de consultar indicador oficial válido em cache alcançar o comportamento de RF-23/C01 THE SYSTEM SHALL atender ao comportamento: selic, CDI e IPCA devem ser obtidos via API do **Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS)** (`api.bcb.gov.br/dados/serie`). | CA-003 |
| SPEC-007-R04 | WHEN o fluxo de consultar indicador oficial válido em cache alcançar o comportamento de RF-23/C02 THE SYSTEM SHALL atender ao comportamento: taxas de títulos do Tesouro Direto devem ser obtidas via API do **Tesouro Transparente** (`www.tesourotransparente.gov.br`). | CA-004 |
| SPEC-007-R05 | WHEN o fluxo de consultar indicador oficial válido em cache alcançar o comportamento de RF-23/C03 THE SYSTEM SHALL atender ao comportamento: os valores obtidos devem ser armazenados em cache local, com data/hora da última atualização. | CA-005 |
| SPEC-007-R06 | WHEN o fluxo de consultar indicador oficial válido em cache alcançar o comportamento de RF-23/C04 THE SYSTEM SHALL atender ao comportamento: atualizar o cache automaticamente 1 vez por dia, após o horário de divulgação de cada indicador (padrão de mercado; atende à defasagem máxima de 24h do RNF-09). | CA-006 |
| SPEC-007-R07 | WHEN o fluxo de consultar indicador oficial válido em cache alcançar o comportamento de RF-23/C05 THE SYSTEM SHALL atender ao comportamento: em caso de falha ou indisponibilidade da API oficial, o sistema deve usar o último valor em cache e exibir um aviso visual informando que o dado pode estar desatualizado. | CA-007 |
| SPEC-007-R08 | WHEN o fluxo de consultar indicador oficial válido em cache alcançar o comportamento de RF-23/C06 THE SYSTEM SHALL atender ao comportamento: a data de referência do indicador deve ser exibida sempre que ele for usado em uma simulação (RF-20, RF-22). | CA-008 |

## 6. Regras e invariantes

- **INV-001:** Ausência ou falha não cria taxa zero; coleta e referência econômica são distintas.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-11: ~~Quando a API oficial de indicadores falhar, usa-se o último valor em cache com aviso visual de defasagem — nunca um valor zerado ou inventado~~ **Reclassificada → RF-23** (tratamento de falha do sistema, cláusula IF/THEN). Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

IndicadorMercadoCache contém código/fonte, valor/unidade/periodicidade, referência econômica e última verificação. Nome histórico IndicadorFinanceiroCache não é indicador contábil CVM (OPEN-19).

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consultar indicador oficial válido em cache. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Integração externa é isolada por adaptador; contratos, fonte/provedor e periodicidade devem ser definidos nas OPEN locais. Testes usam dublês, sem serviços externos reais.

ADRs relacionados: ADR-001, ADR-003, ADR-006. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | indicador requerido e referência de verificação da fonte |
| Saída | valor, unidade, periodicidade, referência e estado de disponibilidade |
| Erro | Cache ausente/vencido não é apresentado como atual; divergência de política deve ser resolvida em OPEN-19 antes do aceite. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-08 (Disponibilidade) | Medir disponibilidade mensal >=99,5% no ambiente operacional aprovado; não inferir de teste unitário. |
| RNF-09 (Atualidade de dados de mercado) | Relógio/fonte simulados: referência, coleta, dados ausentes e limites 24h/15min; fechar OPEN-19. |
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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Com relógio controlado, cache verificado há 23h é disponibilizado com referência; falha de atualização preserva o registro sem renovar artificialmente sua data.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Cache ausente/vencido não é apresentado como atual; divergência de política deve ser resolvida em OPEN-19 antes do aceite.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-23/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Selic, CDI e IPCA devem ser obtidos via API do **Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS)** (`api.bcb.gov.br/dados/serie`).

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-23/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Taxas de títulos do Tesouro Direto devem ser obtidas via API do **Tesouro Transparente** (`www.tesourotransparente.gov.br`).

- **CA-005** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-23/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Os valores obtidos devem ser armazenados em cache local, com data/hora da última atualização.

- **CA-006** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-23/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve atualizar o cache automaticamente 1 vez por dia, após o horário de divulgação de cada indicador (padrão de mercado; atende à defasagem máxima de 24h do RNF-09).

- **CA-007** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-23/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Em caso de falha ou indisponibilidade da API oficial, o sistema deve usar o último valor em cache e exibir um aviso visual informando que o dado pode estar desatualizado.

- **CA-008** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-23/C06, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A data de referência do indicador deve ser exibida sempre que ele for usado em uma simulação (RF-20, RF-22).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-007-R01; CA-001; INV-001, INV-002 | Fixture específica: Com relógio controlado, cache verificado há 23h é disponibilizado com referência; falha de atualização preserva o registro sem renovar artificialmente sua data. |
| T-002 | SPEC-007-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Cache ausente/vencido não é apresentado como atual; divergência de política deve ser resolvida em OPEN-19 antes do aceite. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-007-R03; CA-003 | RF-23/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Selic, CDI e IPCA devem ser obtidos via API do **Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS)** (`api.bcb.gov.br/dados/serie`). |
| T-004 | SPEC-007-R04; CA-004 | RF-23/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Taxas de títulos do Tesouro Direto devem ser obtidas via API do **Tesouro Transparente** (`www.tesourotransparente.gov.br`). |
| T-005 | SPEC-007-R05; CA-005 | RF-23/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Os valores obtidos devem ser armazenados em cache local, com data/hora da última atualização. |
| T-006 | SPEC-007-R06; CA-006 | RF-23/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve atualizar o cache automaticamente 1 vez por dia, após o horário de divulgação de cada indicador (padrão de mercado; atende à defasagem máxima de 24h do RNF-09). |
| T-007 | SPEC-007-R07; CA-007 | RF-23/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Em caso de falha ou indisponibilidade da API oficial, o sistema deve usar o último valor em cache e exibir um aviso visual informando que o dado pode estar desatualizado. |
| T-008 | SPEC-007-R08; CA-008 | RF-23/C06: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A data de referência do indicador deve ser exibida sempre que ele for usado em uma simulação (RF-20, RF-22). |
| T-009 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-08, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py`, executados na CI com PostgreSQL. A correspondência um-para-um entre cláusulas e testes (C-02) está nos testes `test_SPEC_NNN_Rxx` indicados no Estado desta spec.

## 13. Questões em Aberto

- OPEN-04 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
