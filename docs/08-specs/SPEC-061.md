# SPEC-061: Entregar notificação em canal opcional

**Estado:** rascunho para revisão humana, criado em 2026-10-22. Produção documental autorizada no lote atual; sem implementação/testes novos ou aprovação formal presumida.

## 1. Identificação

- **ID:** SPEC-061
- **Nome:** Entregar notificação em canal opcional
- **Objetivo:** Checar canal habilitado; obter destino do titular; usar adaptador configurado; registrar resultado mínimo; manter in-app como base; respeitar desativação.
- **Valor entregue:** tentativa e resultado de entrega externa.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-49.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-15; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Notificacao, Usuario e PreferenciasUsuario; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-07, DA-09; ADR-001; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** entregar notificação em canal opcional; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Serviço push citado na arquitetura e provedor de e-mail em OPEN-17/26; não inventar retries, tokens de dispositivo ou consentimento padrão.

## 4. Dependências

[SPEC-039](SPEC-039.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-17, OPEN-26. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** rotina/fonte autorizada e contratos externos aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Checar canal habilitado.
2. obter destino do titular.
3. usar adaptador configurado.
4. registrar resultado mínimo.
5. manter in-app como base.
6. respeitar desativação.

**Alternativa observável:** Canal e-mail desabilitado não envia; habilitado usa somente endereço do titular e preserva aviso in-app.

**Exceções:** Credencial/provedor ausente ou destino inválido não registra entrega bem-sucedida.

**Pós-condições:** tentativa e resultado de entrega externa; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-061-R01 | WHEN ocorrer o fluxo válido de entregar notificação em canal opcional THE SYSTEM SHALL entregar tentativa e resultado de entrega externa. | CA-001 |
| SPEC-061-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-061-R03 | WHEN o fluxo de entregar notificação em canal opcional alcançar o comportamento de RF-49/C01 THE SYSTEM SHALL atender ao comportamento: notificações in-app são obrigatórias (MVP); push (mobile) e e-mail são canais opcionais, configuráveis pelo usuário. | CA-003 |
| SPEC-061-R04 | WHEN o fluxo de entregar notificação em canal opcional alcançar o comportamento de RF-49/C02 THE SYSTEM SHALL atender ao comportamento: o envio por push deve usar um serviço de terceiros (ex.: Firebase Cloud Messaging — ver seção 5). | CA-004 |

## 6. Regras e invariantes

- **INV-001:** Habilitar push/e-mail não remove histórico in-app nem expõe notificação a outro destino.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Notificacao referencia titular e PreferenciasUsuario; destino push/e-mail e segredo ficam em infraestrutura. Resultado de envio não altera notificação original nem dados financeiros.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Entregar notificação em canal opcional. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Integração externa é isolada por adaptador; contratos, fonte/provedor e periodicidade devem ser definidos nas OPEN locais. Testes usam dublês, sem serviços externos reais.

ADRs relacionados: ADR-001. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | notificação, consentimento e destino push/e-mail |
| Saída | tentativa e resultado de entrega externa |
| Erro | Credencial/provedor ausente ou destino inválido não registra entrega bem-sucedida. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-08 (Disponibilidade) | Medir disponibilidade mensal >=99,5% no ambiente operacional aprovado; não inferir de teste unitário. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Canal e-mail desabilitado não envia; habilitado usa somente endereço do titular e preserva aviso in-app.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Credencial/provedor ausente ou destino inválido não registra entrega bem-sucedida.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-49/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Notificações in-app são obrigatórias (MVP); push (mobile) e e-mail são canais opcionais, configuráveis pelo usuário.

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-49/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O envio por push deve usar um serviço de terceiros (ex.: Firebase Cloud Messaging — ver seção 5).

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-061-R01; CA-001; INV-001, INV-002 | Fixture específica: Canal e-mail desabilitado não envia; habilitado usa somente endereço do titular e preserva aviso in-app. |
| T-002 | SPEC-061-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Credencial/provedor ausente ou destino inválido não registra entrega bem-sucedida. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-061-R03; CA-003 | RF-49/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Notificações in-app são obrigatórias (MVP); push (mobile) e e-mail são canais opcionais, configuráveis pelo usuário. |
| T-004 | SPEC-061-R04; CA-004 | RF-49/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O envio por push deve usar um serviço de terceiros (ex.: Firebase Cloud Messaging — ver seção 5). |
| T-005 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-17 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
