# SPEC-045: Dividir despesas e registrar acertos

**Estado:** implementada tecnicamente em 2026-10-31 (backend, interface web e testes automatizados). Política de recorte proposta pelo agente e aprovada pelo responsável em 2026-10-31; revisão formal do grupo pendente. Evidências no [registro de implementação](../09-qualidade/implementacao-SPEC-045.md).

## 1. Identificação

- **ID:** SPEC-045
- **Nome:** Dividir despesas e registrar acertos
- **Objetivo:** Validar vínculo aceito; marcar despesa e divisão; atualizar saldo; recalcular ao editar/excluir; registrar acerto; mostrar composição aos dois.
- **Valor entregue:** saldo quem deve quem e detalhamento para dois membros.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-61.
- **RB:** RB-24, RB-29.
- **RNF:** RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20.
- **Fluxo:** UC-16; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** ContaCompartilhada, Despesa, DespesaCompartilhada e AcertoConta; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** dividir despesas e registrar acertos; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Arredondamento, edição por ambos e tratamento de rompimento/exclusão são OPEN-03/31.

## 4. Dependências

[SPEC-044](SPEC-044.md), [SPEC-059](SPEC-059.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-05, OPEN-15, OPEN-31. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar vínculo aceito.
2. marcar despesa e divisão.
3. atualizar saldo.
4. recalcular ao editar/excluir.
5. registrar acerto.
6. mostrar composição aos dois.

**Alternativa observável:** A paga 100 dividido 50/50: B deve 50; acerto registrado de 20 reduz dívida para 30.

**Exceções:** Não membro ou percentuais que não fecham não altera saldo; concorrência não duplica acerto.

**Pós-condições:** saldo quem deve quem e detalhamento para dois membros; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-045-R01 | WHEN ocorrer o fluxo válido de dividir despesas e registrar acertos THE SYSTEM SHALL entregar saldo quem deve quem e detalhamento para dois membros. | CA-001 |
| SPEC-045-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-045-R03 | WHEN o fluxo de dividir despesas e registrar acertos alcançar o comportamento de RF-61/C01 THE SYSTEM SHALL atender ao comportamento: permitir marcar uma despesa (RF-09) como compartilhada, escolhendo divisão igual (50/50) ou percentual customizado. | CA-003 |
| SPEC-045-R04 | WHEN o fluxo de dividir despesas e registrar acertos alcançar o comportamento de RF-61/C02 THE SYSTEM SHALL atender ao comportamento: manter um saldo consolidado "quem deve quem" entre os dois usuários vinculados, atualizado a cada despesa compartilhada incluída, editada ou excluída. | CA-004 |
| SPEC-045-R05 | WHEN o fluxo de dividir despesas e registrar acertos alcançar o comportamento de RF-61/C03 THE SYSTEM SHALL atender ao comportamento: permitir registrar um "acerto de contas" (pagamento entre os usuários) que zera ou reduz o saldo pendente. | CA-005 |
| SPEC-045-R06 | WHEN o fluxo de dividir despesas e registrar acertos alcançar o comportamento de RF-61/C04 THE SYSTEM SHALL atender ao comportamento: o saldo compartilhado deve ser visível para ambos os usuários vinculados, com o detalhamento das despesas que o compõem. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Só despesa explicitamente compartilhada fica visível; acerto reduz saldo sem inventar transferência bancária.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-24: O saldo "quem deve quem" de uma conta compartilhada é recalculado a cada despesa compartilhada incluída, editada, excluída ou acerto de contas registrado; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

DespesaCompartilhada referencia uma Despesa e um vínculo aceito; AcertoConta pertence ao mesmo vínculo. Divisões e acertos compõem saldo visível aos dois membros, sem dados individuais extras.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Dividir despesas e registrar acertos. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | despesa compartilhada, 50/50 ou percentual customizado e acerto |
| Saída | saldo quem deve quem e detalhamento para dois membros |
| Erro | Não membro ou percentuais que não fecham não altera saldo; concorrência não duplica acerto. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-02 (Privacidade / LGPD) | Testar titular A/B, exportação/exclusão aplicável e política aprovada de retenção. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-14 (Backup e recuperação) | Restaurar backup isolado, medir RPO <=24h/RTO <=4h e aplicar exclusões; depende de OPEN-05/32. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-18 (Auditoria) | Inspecionar autoria/ação/instante e recusa de edição operacional; retenção pessoal depende de OPEN-05/19. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: A paga 100 dividido 50/50: B deve 50; acerto registrado de 20 reduz dívida para 30.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Não membro ou percentuais que não fecham não altera saldo; concorrência não duplica acerto.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-61/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir marcar uma despesa (RF-09) como compartilhada, escolhendo divisão igual (50/50) ou percentual customizado.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-61/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve manter um saldo consolidado "quem deve quem" entre os dois usuários vinculados, atualizado a cada despesa compartilhada incluída, editada ou excluída.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-61/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir registrar um "acerto de contas" (pagamento entre os usuários) que zera ou reduz o saldo pendente.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-61/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O saldo compartilhado deve ser visível para ambos os usuários vinculados, com o detalhamento das despesas que o compõem.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-045-R01; CA-001; INV-001, INV-002 | Fixture específica: A paga 100 dividido 50/50: B deve 50; acerto registrado de 20 reduz dívida para 30. |
| T-002 | SPEC-045-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Não membro ou percentuais que não fecham não altera saldo; concorrência não duplica acerto. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-045-R03; CA-003 | RF-61/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir marcar uma despesa (RF-09) como compartilhada, escolhendo divisão igual (50/50) ou percentual customizado. |
| T-004 | SPEC-045-R04; CA-004 | RF-61/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve manter um saldo consolidado "quem deve quem" entre os dois usuários vinculados, atualizado a cada despesa compartilhada incluída, editada ou excluída. |
| T-005 | SPEC-045-R05; CA-005 | RF-61/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir registrar um "acerto de contas" (pagamento entre os usuários) que zera ou reduz o saldo pendente. |
| T-006 | SPEC-045-R06; CA-006 | RF-61/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O saldo compartilhado deve ser visível para ambos os usuários vinculados, com o detalhamento das despesas que o compõem. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes implementados em `backend/tests/test_spec044_045_sharing.py`, nomeados `test_SPEC_045_Rxx` por cláusula, e executados na CI com PostgreSQL. T-006 (RNFs) é coberto parcialmente pela suíte, pelo lint e pela varredura de acessibilidade; evidência operacional (backup, disponibilidade) permanece fora do recorte.

## 13. Questões em Aberto

- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-05 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-31 — decisão necessária: Compartilhamento/mobile: convites e visibilidade após rompimento, conflitos de edição/arredondamento/acertos; política de sincronização offline e isolamento local / SPEC-044, SPEC-045, SPEC-006, SPEC-056 a SPEC-059; RNF-22/24.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

### Decisão adotada para o recorte implementado (2026-10-31)

Divisão 50/50 ou percentual com duas casas que some 100% (`split_must_total_100` → 422). A parte do outro membro é truncada ao centavo e o centavo restante fica com quem pagou. Somente o pagador compartilha, edita a divisão ou remove o compartilhamento, e apenas enquanto o vínculo está ativo. Editar ou excluir a despesa original recalcula o saldo automaticamente, pois o saldo é derivado dos lançamentos persistidos. O acerto exige `Idempotency-Key`, só pode ser registrado por quem deve e não pode superar o saldo pendente (422); não representa transferência bancária. Após o fim do vínculo, o saldo continua consultável e quitável. Despesa recorrente compartilhada é dividida uma única vez, pelo valor do registro.

**Contrato:** `POST /api/v1/auth/sharing/expenses` {expense_id, split, payer_percent?, partner_percent?}, `PATCH|DELETE /sharing/expenses/{id}`, `GET /sharing/balance?link_id` (itens, partes, acertos, `direction` e `amount`) e `POST /sharing/settlements` {amount, link_id?}. Tabelas `shared_expenses` e `shared_settlements` (migração 032).

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
