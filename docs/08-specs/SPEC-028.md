# SPEC-028: Consolidar patrimônio real e itens manuais

**Estado:** implementada tecnicamente em 2026-10-29; aguarda revisão humana do grupo. Evidências em [implementacao-SPEC-028](../09-qualidade/implementacao-SPEC-028.md).

## 1. Identificação

- **ID:** SPEC-028
- **Nome:** Consolidar patrimônio real e itens manuais
- **Objetivo:** Ler origens reais disponíveis; preservar espelhos de origem; registrar itens manuais; somar ativos e subtrair passivos; recalcular na mudança da origem.
- **Valor entregue:** ativos/passivos consolidados e patrimônio líquido.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-35.
- **RB:** RB-13, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20.
- **Fluxo:** UC-14; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Conta, Cartao, Ativo, Passivo e PatrimonioItem; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-06, DA-07, DA-08, DA-09; ADR-001, ADR-002, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consolidar patrimônio real e itens manuais; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Este recorte consolida contas reais e faturas abertas já disponíveis, além de itens manuais. Simulações de investimento são sempre excluídas; financiamentos reais permanecem origem futura da SPEC-038.

## 4. Dependências

[SPEC-005](SPEC-005.md), [SPEC-020](SPEC-020.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-19, OPEN-21, OPEN-28. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; criar, editar e excluir item manual exige e-mail verificado conforme RF-69.

**Fluxo principal:**

1. Ler contas reais e faturas abertas do titular.
2. Calcular o saldo de cada conta a partir do saldo inicial e lançamentos vinculados até a data consultada.
3. Registrar, editar ou excluir ativos/passivos manuais próprios com nome, valor positivo e taxa anual opcional.
4. Somar ativos e subtrair passivos em cada consulta, sem snapshot histórico.

**Alternativa observável:** Conta 100 e dívida manual 30 produzem patrimônio 70; executar projeção de 1000 não aumenta esse patrimônio.

**Exceções:** Origem alheia ou valor sem validação não é consolidado.

**Pós-condições:** ativos/passivos consolidados e patrimônio líquido; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-028-R01 | WHEN ocorrer o fluxo válido de consolidar patrimônio real e itens manuais THE SYSTEM SHALL entregar ativos/passivos consolidados e patrimônio líquido. | CA-001 |
| SPEC-028-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-028-R03 | WHEN o fluxo de consolidar patrimônio real e itens manuais alcançar o comportamento de RF-35/C01 THE SYSTEM SHALL atender ao comportamento: consolidar automaticamente como **ativos**: saldo das contas (RF-12) e valor atual dos investimentos simulados/registrados (módulo Simulador de Investimentos). | CA-003 |
| SPEC-028-R04 | WHEN o fluxo de consolidar patrimônio real e itens manuais alcançar o comportamento de RF-35/C02 THE SYSTEM SHALL atender ao comportamento: consolidar automaticamente como **passivos**: fatura de cartão em aberto (RF-13) e saldo devedor de financiamentos ativos (RF-47). | CA-004 |
| SPEC-028-R05 | WHEN o fluxo de consolidar patrimônio real e itens manuais alcançar o comportamento de RF-35/C03 THE SYSTEM SHALL atender ao comportamento: permitir cadastro manual de outros ativos (ex.: imóvel, veículo, reserva de emergência) e passivos (ex.: empréstimo pessoal) não capturados automaticamente pelos demais módulos. | CA-005 |
| SPEC-028-R06 | WHEN o fluxo de consolidar patrimônio real e itens manuais alcançar o comportamento de RF-35/C04 THE SYSTEM SHALL atender ao comportamento: cada ativo/passivo manual deve ter nome, valor e, opcionalmente, uma rentabilidade (ativo) ou taxa de juros (passivo) informada pelo usuário. | CA-006 |
| SPEC-028-R07 | WHEN o fluxo de consolidar patrimônio real e itens manuais alcançar o comportamento de RF-35/C05 THE SYSTEM SHALL atender ao comportamento: calcular patrimônio líquido = soma dos ativos − soma dos passivos. | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Resultado meramente simulado nunca vira ativo real; espelho não duplica o registro manual da mesma origem.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** O recorte não transforma simulação em ativo nem inventa saldo de financiamento, investimento real ou snapshot histórico.

Regras herdadas: RB-13: Patrimônio líquido = soma dos ativos reais registrados − soma dos passivos reais registrados. Recalcular quando uma origem real mudar; executar simulação não cria ativo nem altera patrimônio real; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

`net_worth_items` armazena itens manuais do titular com nome cifrado, tipo, valor e taxa anual opcional. A consulta devolve linhas automáticas de `accounts` e faturas de `credit_cards`, sem duplicá-las como itens manuais.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consolidar patrimônio real e itens manuais. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

O serviço de aplicação calcula o resultado sob consulta e mantém a autorização de titular no servidor. Nenhuma integração externa é escolhida; e-mail confirmado é exigido apenas para mutações financeiras.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | `GET /api/v1/auth/financial/net-worth`; `POST/PATCH/DELETE /api/v1/auth/financial/net-worth/items`; itens manuais com nome, valor e taxa opcional |
| Saída | ativos/passivos consolidados, origem de cada linha e patrimônio líquido |
| Erro | item alheio/não existente retorna 404; sem confirmação retorna 403; valor inválido retorna 422. |

Identificadores e titularidade são verificados no servidor. A leitura exige sessão; mutações exigem sessão e e-mail confirmado. O prefixo/sessões existentes não são alterados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Conta 100 e dívida manual 30 produzem patrimônio 70; executar projeção de 1000 não aumenta esse patrimônio.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Origem alheia ou valor sem validação não é consolidado.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-35/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve consolidar automaticamente como **ativos**: saldo das contas (RF-12) e valor atual dos investimentos simulados/registrados (módulo Simulador de Investimentos).

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-35/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve consolidar automaticamente como **passivos**: fatura de cartão em aberto (RF-13) e saldo devedor de financiamentos ativos (RF-47).

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-35/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir cadastro manual de outros ativos (ex.: imóvel, veículo, reserva de emergência) e passivos (ex.: empréstimo pessoal) não capturados automaticamente pelos demais módulos.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-35/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Cada ativo/passivo manual deve ter nome, valor e, opcionalmente, uma rentabilidade (ativo) ou taxa de juros (passivo) informada pelo usuário.

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-35/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular patrimônio líquido = soma dos ativos − soma dos passivos.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-028-R01; CA-001; INV-001, INV-002 | Fixture específica: Conta 100 e dívida manual 30 produzem patrimônio 70; executar projeção de 1000 não aumenta esse patrimônio. |
| T-002 | SPEC-028-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Origem alheia ou valor sem validação não é consolidado. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-028-R03; CA-003 | RF-35/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve consolidar automaticamente como **ativos**: saldo das contas (RF-12) e valor atual dos investimentos simulados/registrados (módulo Simulador de Investimentos). |
| T-004 | SPEC-028-R04; CA-004 | RF-35/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve consolidar automaticamente como **passivos**: fatura de cartão em aberto (RF-13) e saldo devedor de financiamentos ativos (RF-47). |
| T-005 | SPEC-028-R05; CA-005 | RF-35/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir cadastro manual de outros ativos (ex.: imóvel, veículo, reserva de emergência) e passivos (ex.: empréstimo pessoal) não capturados automaticamente pelos demais módulos. |
| T-006 | SPEC-028-R06; CA-006 | RF-35/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Cada ativo/passivo manual deve ter nome, valor e, opcionalmente, uma rentabilidade (ativo) ou taxa de juros (passivo) informada pelo usuário. |
| T-007 | SPEC-028-R07; CA-007 | RF-35/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular patrimônio líquido = soma dos ativos − soma dos passivos. |
| T-008 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-19 — decisão necessária: Conciliar inconsistências herdadas: RF-23/RNF-09 versus ADR-003 (cache vencido/referência), RF-35 versus RB-13 (simulado/real), RB-18 (valor/progresso), aliases de entidade, antigos UCs, prazo de token normativo versus proposta e retenção versus auditoria imutável / Specs consumidoras e baseline; registrar alteração aprovada, não escolher silenciosamente.
- OPEN-21 — decisão necessária: Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais / SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059.
- OPEN-28 — decisão necessária: Patrimônio: fechar a contradição entre investimento simulado/registrado em RF-35 e apenas patrimônio real em RB-13; origem de investimento real não modelada integralmente / SPEC-028 e consumidores; proibido considerar projeção um ativo entregue.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [x] Recorte técnico e política autorizados com evidência real.
- [x] OPEN-15/19/21/28 delimitadas somente para contas/faturas reais e itens manuais.
- [ ] Esta versão revisada individualmente pelo grupo, sem aprovação histórica presumida.
- [x] Cláusulas/CA do recorte implementadas e invariantes preservados.
- [x] Testes de integração cobrem contas, fatura, itens manuais, projeção excluída, validação e titularidade.
- [ ] Carga, snapshots históricos, financiamento e investimento registrado continuam fora do recorte.
- [x] Código, migration, testes e documentação foram conciliados sem alegar integração externa.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
