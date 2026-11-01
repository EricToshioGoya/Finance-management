# SPEC-035: Buscar conteúdo educativo e ajuda contextual

**Estado:** implementada tecnicamente; código incorporado à `main` em 2026-10-31 (PR #43) e coberto pela CI. Registro anterior: implementação técnica em validação na branch `feature/35-education-help` (PR a abrir). Conteúdo editorial definitivo e revisão humana ainda sujeitos a OPEN-30; não há aprovação formal presumida. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-035
- **Nome:** Buscar conteúdo educativo e ajuda contextual
- **Objetivo:** Manter fonte única de conteúdo; buscar termo; priorizar conceitos conforme perfil; abrir explicação do campo por mouse/teclado/toque sem sair; reutilizar o mesmo texto.
- **Valor entregue:** verbete curto, sugestões e tooltip na tela atual.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-43, RF-44.
- **RB:** RB-09.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-15; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** ConteudoEducacional e perfil de Usuario; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** buscar conteúdo educativo e ajuda contextual; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Foi criado um catálogo educativo bilíngue inicial com fonte única para busca e ajuda contextual, documentado em [implementacao-SPEC-035](../09-qualidade/implementacao-SPEC-035.md). Conteúdo final, autoria/revisão e expansão/termos sem tradução seguem em OPEN-30; a explicação de taxa na SPEC-013 permanece independente.

## 4. Dependências

[SPEC-003](SPEC-003.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-11, OPEN-15, OPEN-30. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Manter fonte única de conteúdo.
2. buscar termo.
3. priorizar conceitos conforme perfil.
4. abrir explicação do campo por mouse/teclado/toque sem sair.
5. reutilizar o mesmo texto.

**Alternativa observável:** Buscar CDI e abrir ajuda do campo correspondente mostram conteúdo da mesma fonte, com fallback de idioma identificado.

**Exceções:** Termo sem verbete não exibe texto de outro conceito nem bloqueia a operação financeira.

**Pós-condições:** verbete curto, sugestões e tooltip na tela atual; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-035-R01 | WHEN ocorrer o fluxo válido de buscar conteúdo educativo e ajuda contextual THE SYSTEM SHALL entregar verbete curto, sugestões e tooltip na tela atual. | CA-001 |
| SPEC-035-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-035-R03 | WHEN o fluxo de buscar conteúdo educativo e ajuda contextual alcançar o comportamento de RF-43/C01 THE SYSTEM SHALL atender ao comportamento: disponibilizar artigos/verbetes curtos explicando termos usados no sistema (ex.: o que é CDI, o que é Sharpe, o que é diversificação). | CA-003 |
| SPEC-035-R04 | WHEN o fluxo de buscar conteúdo educativo e ajuda contextual alcançar o comportamento de RF-43/C02 THE SYSTEM SHALL atender ao comportamento: o conteúdo sugerido na tela inicial deve variar conforme o perfil do usuário (RF-03): iniciante vê conceitos básicos primeiro; avançado vê conceitos técnicos. | CA-004 |
| SPEC-035-R05 | WHEN o fluxo de buscar conteúdo educativo e ajuda contextual alcançar o comportamento de RF-43/C03 THE SYSTEM SHALL atender ao comportamento: ser possível buscar por termo. | CA-005 |
| SPEC-035-R06 | WHEN o fluxo de buscar conteúdo educativo e ajuda contextual alcançar o comportamento de RF-44/C01 THE SYSTEM SHALL atender ao comportamento: campos técnicos do sistema (ex.: "Taxa de juros" em RF-22, "Sharpe" em RF-27) devem ter um ícone de ajuda que abre a explicação correspondente sem sair da tela atual. | CA-006 |
| SPEC-035-R07 | WHEN o fluxo de buscar conteúdo educativo e ajuda contextual alcançar o comportamento de RF-44/C02 THE SYSTEM SHALL atender ao comportamento: o conteúdo do tooltip deve ser reaproveitado do conteúdo da central educacional (RF-43), nunca duplicado. | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Tooltip não duplica uma versão divergente do verbete central.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-09: O resultado do quiz de perfil define a experiência exibida no simulador. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

ConteudoEducacional identifica termo, verbete e variantes de idioma; perfil do Usuario define ordenação de sugestões. Tooltip referencia conteúdo, não cópia independente.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Buscar conteúdo educativo e ajuda contextual. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | termo buscado, perfil e referência do campo técnico |
| Saída | verbete curto, sugestões e tooltip na tela atual |
| Erro | Termo sem verbete não exibe texto de outro conceito nem bloqueia a operação financeira. |

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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Buscar CDI e abrir ajuda do campo correspondente mostram conteúdo da mesma fonte, com fallback de idioma identificado.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Termo sem verbete não exibe texto de outro conceito nem bloqueia a operação financeira.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-43/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve disponibilizar artigos/verbetes curtos explicando termos usados no sistema (ex.: o que é CDI, o que é Sharpe, o que é diversificação).

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-43/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O conteúdo sugerido na tela inicial deve variar conforme o perfil do usuário (RF-03): iniciante vê conceitos básicos primeiro; avançado vê conceitos técnicos.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-43/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve ser possível buscar por termo.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-44/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Campos técnicos do sistema (ex.: "Taxa de juros" em RF-22, "Sharpe" em RF-27) devem ter um ícone de ajuda que abre a explicação correspondente sem sair da tela atual.

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-44/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O conteúdo do tooltip deve ser reaproveitado do conteúdo da central educacional (RF-43), nunca duplicado.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-035-R01; CA-001; INV-001, INV-002 | Fixture específica: Buscar CDI e abrir ajuda do campo correspondente mostram conteúdo da mesma fonte, com fallback de idioma identificado. |
| T-002 | SPEC-035-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Termo sem verbete não exibe texto de outro conceito nem bloqueia a operação financeira. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-035-R03; CA-003 | RF-43/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve disponibilizar artigos/verbetes curtos explicando termos usados no sistema (ex.: o que é CDI, o que é Sharpe, o que é diversificação). |
| T-004 | SPEC-035-R04; CA-004 | RF-43/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O conteúdo sugerido na tela inicial deve variar conforme o perfil do usuário (RF-03): iniciante vê conceitos básicos primeiro; avançado vê conceitos técnicos. |
| T-005 | SPEC-035-R05; CA-005 | RF-43/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve ser possível buscar por termo. |
| T-006 | SPEC-035-R06; CA-006 | RF-44/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Campos técnicos do sistema (ex.: "Taxa de juros" em RF-22, "Sharpe" em RF-27) devem ter um ícone de ajuda que abre a explicação correspondente sem sair da tela atual. |
| T-007 | SPEC-035-R07; CA-007 | RF-44/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O conteúdo do tooltip deve ser reaproveitado do conteúdo da central educacional (RF-43), nunca duplicado. |
| T-008 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Os testes de contrato foram implementados em `backend/tests/test_spec035_education.py`, para consulta autenticada, busca, idiomas e fonte única do conteúdo. A conclusão técnica depende dos checks do PR. Testes de mobile e revisão editorial permanecem pendentes.

## 13. Questões em Aberto

- OPEN-11 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
