# SPEC-042: Entregar eventos por webhook assinado

**Estado:** implementada em 2026-10-31; validação automatizada registrada no PR da implementação.

## 1. Identificação

- **ID:** SPEC-042
- **Nome:** Entregar eventos por webhook assinado
- **Objetivo:** Validar assinatura/configuração do titular; receber evento; montar conteúdo mínimo; assinar com segredo por integração; enviar; registrar tentativa; permitir reenvio manual de falha.
- **Valor entregue:** payload HMAC, histórico de tentativas e reenvio manual.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-53.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-23.
- **Fluxo:** Fluxo webhook RF-53; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** WebhookSubscription, Usuario e registro de tentativa; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** entregar eventos por webhook assinado; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Algoritmo/canonicalização, entrega duplicada, retries e proteção SSRF em OPEN-25; não fixar protocolo extra nesta Spec.

## 4. Dependências

[SPEC-039](SPEC-039.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-25, OPEN-26. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** rotina/fonte autorizada e contratos externos aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar assinatura/configuração do titular.
2. receber evento.
3. montar conteúdo mínimo.
4. assinar com segredo por integração.
5. enviar.
6. registrar tentativa.
7. permitir reenvio manual de falha.

**Alternativa observável:** Receptor falso valida HMAC do payload original e recusa payload adulterado; falha fica visível para reenvio manual.

**Exceções:** URL inválida, acesso cruzado ou endpoint de rede não autorizado não deve expor segredos.

**Pós-condições:** payload HMAC, histórico de tentativas e reenvio manual; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-042-R01 | WHEN ocorrer o fluxo válido de entregar eventos por webhook assinado THE SYSTEM SHALL entregar payload HMAC, histórico de tentativas e reenvio manual. | CA-001 |
| SPEC-042-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-042-R03 | WHEN o fluxo de entregar eventos por webhook assinado alcançar o comportamento de RF-53/C01 THE SYSTEM SHALL atender ao comportamento: permitir que o usuário (ou uma integração autorizada) cadastre uma URL para receber notificações de eventos (ex.: meta atingida, fatura próxima do vencimento). | CA-003 |
| SPEC-042-R04 | WHEN o fluxo de entregar eventos por webhook assinado alcançar o comportamento de RF-53/C02 THE SYSTEM SHALL atender ao comportamento: o payload do webhook deve ser assinado (HMAC) para permitir verificação de autenticidade pelo receptor. | CA-004 |
| SPEC-042-R05 | WHEN o fluxo de entregar eventos por webhook assinado alcançar o comportamento de RF-53/C03 THE SYSTEM SHALL atender ao comportamento: reaproveitar os mesmos gatilhos de RF-48. | CA-005 |
| SPEC-042-R06 | WHEN o fluxo de entregar eventos por webhook assinado alcançar o comportamento de RF-53/C04 THE SYSTEM SHALL atender ao comportamento: registrar tentativas de entrega e permitir reenvio manual em caso de falha. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Segredos e payload financeiro não aparecem em logs; assinatura de uma integração não autentica outra.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

WebhookSubscription liga titular a URL/eventos e segredo exclusivo em infraestrutura; registro de tentativa preserva resultado sem expor segredo/payload pessoal em logs.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Entregar eventos por webhook assinado. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Integração externa é isolada por adaptador; contratos, fonte/provedor e periodicidade devem ser definidos nas OPEN locais. Testes usam dublês, sem serviços externos reais.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | URL autorizada, eventos e segredo exclusivo |
| Saída | payload HMAC, histórico de tentativas e reenvio manual |
| Erro | URL inválida, acesso cruzado ou endpoint de rede não autorizado não deve expor segredos. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-18 (Auditoria) | Inspecionar autoria/ação/instante e recusa de edição operacional; retenção pessoal depende de OPEN-05/19. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-23 (Segurança de integrações) | Validar HMAC com segredo exclusivo, adulteração e segredo de outra integração; OPEN-25. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Receptor falso valida HMAC do payload original e recusa payload adulterado; falha fica visível para reenvio manual.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: URL inválida, acesso cruzado ou endpoint de rede não autorizado não deve expor segredos.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-53/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir que o usuário (ou uma integração autorizada) cadastre uma URL para receber notificações de eventos (ex.: meta atingida, fatura próxima do vencimento).

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-53/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O payload do webhook deve ser assinado (HMAC) para permitir verificação de autenticidade pelo receptor.

- **CA-005** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-53/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve reaproveitar os mesmos gatilhos de RF-48.

- **CA-006** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-53/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve registrar tentativas de entrega e permitir reenvio manual em caso de falha.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-042-R01; CA-001; INV-001, INV-002 | Fixture específica: Receptor falso valida HMAC do payload original e recusa payload adulterado; falha fica visível para reenvio manual. |
| T-002 | SPEC-042-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: URL inválida, acesso cruzado ou endpoint de rede não autorizado não deve expor segredos. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-042-R03; CA-003 | RF-53/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir que o usuário (ou uma integração autorizada) cadastre uma URL para receber notificações de eventos (ex.: meta atingida, fatura próxima do vencimento). |
| T-004 | SPEC-042-R04; CA-004 | RF-53/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O payload do webhook deve ser assinado (HMAC) para permitir verificação de autenticidade pelo receptor. |
| T-005 | SPEC-042-R05; CA-005 | RF-53/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve reaproveitar os mesmos gatilhos de RF-48. |
| T-006 | SPEC-042-R06; CA-006 | RF-53/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve registrar tentativas de entrega e permitir reenvio manual em caso de falha. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-23 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-25 — decisão necessária: Webhooks: HMAC/canonicalização, segredo/rotação, URL permitida/SSRF, reenvios, duplicidade e registro de tentativas / SPEC-042.
- OPEN-26 — decisão necessária: Eventos e notificações: gatilhos/antecedência, identidade/deduplicação/retry, falhas de coleta, política in-app/opt-out, canais externos, retenção e disparo mensal / SPEC-027, SPEC-039, SPEC-040, SPEC-042, SPEC-051, SPEC-060, SPEC-061.

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
