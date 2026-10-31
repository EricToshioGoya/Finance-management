# SPEC-040: Enviar resumo mensal automático optativo

**Estado:** implementada tecnicamente em 2026-10-31 (backend, interface web e testes automatizados). Política de recorte proposta pelo agente e aprovada pelo responsável em 2026-10-31; revisão formal do grupo pendente. Evidências no [registro de implementação](../09-qualidade/implementacao-SPEC-040.md).

## 1. Identificação

- **ID:** SPEC-040
- **Nome:** Enviar resumo mensal automático optativo
- **Objetivo:** Verificar habilitação; fechar período anterior no fuso; compor renda/gasto/patrimônio/score; gerar PDF reutilizando exportação; enviar pelo canal configurado; permitir desativar.
- **Valor entregue:** PDF do mês anterior e estado de envio.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-51.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** UC-15; relatório mensal; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Renda, Despesa, PatrimonioItem, ScoreSaude e Notificacao; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** enviar resumo mensal automático optativo; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Data/hora da rotina, reenvio e alterações retroativas ficam em OPEN-21/26; não pressupõe agendamento criado nesta tarefa.

## 4. Dependências

[SPEC-019](SPEC-019.md), [SPEC-028](SPEC-028.md), [SPEC-034](SPEC-034.md), [SPEC-039](SPEC-039.md), [SPEC-061](SPEC-061.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-05, OPEN-15, OPEN-21, OPEN-26. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Verificar habilitação.
2. fechar período anterior no fuso.
3. compor renda/gasto/patrimônio/score.
4. gerar PDF reutilizando exportação.
5. enviar pelo canal configurado.
6. permitir desativar.

**Alternativa observável:** Virada de fevereiro gera relatório de janeiro com os valores daquele mês; opção desativada impede envio.

**Exceções:** Falha de entrega não é registrada como envio bem-sucedido nem altera os dados financeiros.

**Pós-condições:** PDF do mês anterior e estado de envio; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-040-R01 | WHEN ocorrer o fluxo válido de enviar resumo mensal automático optativo THE SYSTEM SHALL entregar PDF do mês anterior e estado de envio. | CA-001 |
| SPEC-040-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-040-R03 | WHEN o fluxo de enviar resumo mensal automático optativo alcançar o comportamento de RF-51/C01 THE SYSTEM SHALL atender ao comportamento: gerar e enviar automaticamente, no início de cada mês, um resumo em PDF (reaproveitando o motor de RF-50) com renda, gasto, patrimônio líquido e score de saúde financeira do mês anterior. | CA-003 |
| SPEC-040-R04 | WHEN o fluxo de enviar resumo mensal automático optativo alcançar o comportamento de RF-51/C02 THE SYSTEM SHALL atender ao comportamento: ser enviado pelo canal configurado pelo usuário (RF-49 — e-mail). | CA-004 |
| SPEC-040-R05 | WHEN o fluxo de enviar resumo mensal automático optativo alcançar o comportamento de RF-51/C03 THE SYSTEM SHALL atender ao comportamento: desativar esse relatório automático a qualquer momento. | CA-005 |

## 6. Regras e invariantes

- **INV-001:** Relatório mensal não usa dados do mês corrente nem de outro titular.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Relatório é documento derivado dos dados de Renda/Despesa, patrimônio e ScoreSaude do mesmo mês/titular; preferência de envio e estado de entrega não são dado financeiro autoritativo.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Enviar resumo mensal automático optativo. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | virada do mês e opção habilitada de e-mail |
| Saída | PDF do mês anterior e estado de envio |
| Erro | Falha de entrega não é registrada como envio bem-sucedido nem altera os dados financeiros. |

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
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Virada de fevereiro gera relatório de janeiro com os valores daquele mês; opção desativada impede envio.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Falha de entrega não é registrada como envio bem-sucedido nem altera os dados financeiros.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-51/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve gerar e enviar automaticamente, no início de cada mês, um resumo em PDF (reaproveitando o motor de RF-50) com renda, gasto, patrimônio líquido e score de saúde financeira do mês anterior.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-51/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve ser enviado pelo canal configurado pelo usuário (RF-49 — e-mail).

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-51/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder desativar esse relatório automático a qualquer momento.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-040-R01; CA-001; INV-001, INV-002 | Fixture específica: Virada de fevereiro gera relatório de janeiro com os valores daquele mês; opção desativada impede envio. |
| T-002 | SPEC-040-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Falha de entrega não é registrada como envio bem-sucedido nem altera os dados financeiros. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-040-R03; CA-003 | RF-51/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve gerar e enviar automaticamente, no início de cada mês, um resumo em PDF (reaproveitando o motor de RF-50) com renda, gasto, patrimônio líquido e score de saúde financeira do mês anterior. |
| T-004 | SPEC-040-R04; CA-004 | RF-51/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve ser enviado pelo canal configurado pelo usuário (RF-49 — e-mail). |
| T-005 | SPEC-040-R05; CA-005 | RF-51/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder desativar esse relatório automático a qualquer momento. |
| T-006 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes implementados em `backend/tests/test_spec040_061_channels_summary.py`, nomeados `test_SPEC_040_Rxx` por cláusula, e executados na CI com PostgreSQL. T-006 (RNFs) é coberto parcialmente pela suíte, pelo lint e pela varredura de acessibilidade; evidência operacional (backup, disponibilidade) permanece fora do recorte.

## 13. Questões em Aberto

- OPEN-05 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-21 — decisão necessária: Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais / SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059.
- OPEN-26 — decisão necessária: Eventos e notificações: gatilhos/antecedência, identidade/deduplicação/retry, falhas de coleta, política in-app/opt-out, canais externos, retenção e disparo mensal / SPEC-027, SPEC-039, SPEC-040, SPEC-042, SPEC-051, SPEC-060, SPEC-061.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

### Decisão adotada para o recorte implementado (2026-10-31)

Opt-in (desativado por padrão) em `/profile/reports`. O servidor executa um job diário às 06h de São Paulo (e também há o comando `python -m app.jobs.monthly_summary`); o agendamento externo em produção fica fora do recorte. O resumo cobre o mês anterior fechado no fuso de São Paulo: renda, gastos, variação do saldo, patrimônio líquido da posição registrada no mês e score da competência (quando não registrados, o PDF informa isso, sem inventar valores). O PDF reutiliza o gerador da exportação (SPEC-019) e é enviado pelo canal de e-mail da SPEC-061. Um único envio por titular e competência (restrição única reservada antes do envio); a falha fica registrada como `failed` ou `provider_unavailable`, nunca como enviada, e não altera dados financeiros. O titular pode baixar o PDF de qualquer mês fechado; o mês corrente é recusado (422).

**Contrato:** `GET|PUT /api/v1/auth/profile/reports` {monthly_summary_enabled}, `GET /api/v1/auth/financial/monthly-summaries` (competência, status, instante) e `GET /api/v1/auth/financial/monthly-summaries/{AAAA-MM}/pdf`. Tabelas `report_settings` e `monthly_summaries` (migração 035); gerador de PDF extraído para `backend/app/infrastructure/pdf.py`.

As OPEN acima continuam registradas para revisão do grupo; a decisão vale para este recorte e pode ser revista sem perda de rastreabilidade.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [x] Decisões OPEN bloqueantes resolvidas para o recorte (seção 13) e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados.
- [x] Testes da seção 12 aprovados, com evidência ligada ao commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
