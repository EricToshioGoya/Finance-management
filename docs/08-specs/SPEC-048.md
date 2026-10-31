# SPEC-048: Estimar imposto de operações e lembrete DARF

**Estado:** implementada tecnicamente em 2026-10-31 (backend, interface web e testes automatizados). Política de recorte proposta pelo agente e aprovada pelo responsável em 2026-10-31; revisão formal do grupo pendente. Evidências no [registro de implementação](../09-qualidade/implementacao-SPEC-048.md).

## 1. Identificação

- **ID:** SPEC-048
- **Nome:** Estimar imposto de operações e lembrete DARF
- **Objetivo:** Identificar regime renda fixa/ações/FIIs/day trade; aplicar regra interna versionada; apurar estimativa; calcular lembrete do último dia útil do mês seguinte; avisar caráter educativo.
- **Valor entregue:** IR estimado e prazo de DARF quando aplicável.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-64.
- **RB:** RB-25, RB-29.
- **RNF:** RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** Fluxo tributário RF-64; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Simulacao e operação registrada conceitual; regra tributária; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-006; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** estimar imposto de operações e lembrete darf; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Não pesquisar ou fixar legislação vigente nesta etapa: validação humana de tabelas e calendário está em OPEN-07/22.

## 4. Dependências

[SPEC-004](SPEC-004.md), [SPEC-009](SPEC-009.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-07, OPEN-15, OPEN-22. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** fórmulas e parâmetros de cálculo aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Identificar regime renda fixa/ações/FIIs/day trade.
2. aplicar regra interna versionada.
3. apurar estimativa.
4. calcular lembrete do último dia útil do mês seguinte.
5. avisar caráter educativo.

**Alternativa observável:** Para fixture de alíquota/base aprovadas, imposto é conferido independentemente e documento registra versão e hipótese.

**Exceções:** Calendário de feriados ou compensação de prejuízos indefinidos não recebe regra inventada.

**Pós-condições:** IR estimado e prazo de DARF quando aplicável; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-048-R01 | WHEN ocorrer o fluxo válido de estimar imposto de operações e lembrete darf THE SYSTEM SHALL entregar IR estimado e prazo de DARF quando aplicável. | CA-001 |
| SPEC-048-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-048-R03 | WHEN o fluxo de estimar imposto de operações e lembrete darf alcançar o comportamento de RF-64/C01 THE SYSTEM SHALL atender ao comportamento: calcular a estimativa de IR para renda fixa (tabela regressiva por prazo), ações/FIIs em operação comum (isenção até limite mensal configurável para ações) e day trade (alíquota fixa configurável). | CA-003 |
| SPEC-048-R04 | WHEN o fluxo de estimar imposto de operações e lembrete darf alcançar o comportamento de RF-64/C02 THE SYSTEM SHALL atender ao comportamento: usar uma tabela de alíquotas interna, versionada e configurável — não depende de API externa da Receita Federal. | CA-004 |
| SPEC-048-R05 | WHEN o fluxo de estimar imposto de operações e lembrete darf alcançar o comportamento de RF-64/C03 THE SYSTEM SHALL atender ao comportamento: quando houver IR a recolher via DARF, deve indicar a data-limite de vencimento (último dia útil do mês seguinte) como lembrete, sem gerar ou enviar o DARF. | CA-005 |
| SPEC-048-R06 | WHEN o fluxo de estimar imposto de operações e lembrete darf alcançar o comportamento de RF-64/C04 THE SYSTEM SHALL atender ao comportamento: exibir aviso de que a estimativa é educativa e não substitui a apuração de um contador ou o e-CAC da Receita Federal. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Não gerar/enviar DARF nem chamar Receita em tempo real; regra não definida impede estimativa categórica.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-25: A estimativa de IR usa tabela de alíquotas interna e configurável, variando por tipo de aplicação e prazo — nunca chamada em tempo real à Receita Federal; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Simulacao e operação registrada conceitual; regra tributária. A Simulacao guarda parâmetros, hipóteses, prazo e resultado; o motor retorna valores derivados sem alterar saldo ou patrimônio. Entradas específicas estão na seção 9, fórmulas e calendários ausentes nas OPEN locais. Regras configuráveis devem ter versão identificável no resultado.

Não inventar tabelas, classes de estratégia ou colunas nesta etapa; aplicação e domínio mantêm a separação do modelo conceitual.

## 8. Impacto arquitetural

Capacidade: Estimar imposto de operações e lembrete DARF. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-006. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | tipo de aplicação, resultado, prazo/data e versão tributária |
| Saída | IR estimado e prazo de DARF quando aplicável |
| Erro | Calendário de feriados ou compensação de prejuízos indefinidos não recebe regra inventada. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Para fixture de alíquota/base aprovadas, imposto é conferido independentemente e documento registra versão e hipótese.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Calendário de feriados ou compensação de prejuízos indefinidos não recebe regra inventada.

- **CA-003** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-64/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular a estimativa de IR para renda fixa (tabela regressiva por prazo), ações/FIIs em operação comum (isenção até limite mensal configurável para ações) e day trade (alíquota fixa configurável).

- **CA-004** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-64/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve usar uma tabela de alíquotas interna, versionada e configurável — não depende de API externa da Receita Federal.

- **CA-005** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-64/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Quando houver IR a recolher via DARF, deve indicar a data-limite de vencimento (último dia útil do mês seguinte) como lembrete, sem gerar ou enviar o DARF.

- **CA-006** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-64/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir aviso de que a estimativa é educativa e não substitui a apuração de um contador ou o e-CAC da Receita Federal.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-048-R01; CA-001; INV-001, INV-002 | Fixture específica: Para fixture de alíquota/base aprovadas, imposto é conferido independentemente e documento registra versão e hipótese. |
| T-002 | SPEC-048-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Calendário de feriados ou compensação de prejuízos indefinidos não recebe regra inventada. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-048-R03; CA-003 | RF-64/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular a estimativa de IR para renda fixa (tabela regressiva por prazo), ações/FIIs em operação comum (isenção até limite mensal configurável para ações) e day trade (alíquota fixa configurável). |
| T-004 | SPEC-048-R04; CA-004 | RF-64/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve usar uma tabela de alíquotas interna, versionada e configurável — não depende de API externa da Receita Federal. |
| T-005 | SPEC-048-R05; CA-005 | RF-64/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Quando houver IR a recolher via DARF, deve indicar a data-limite de vencimento (último dia útil do mês seguinte) como lembrete, sem gerar ou enviar o DARF. |
| T-006 | SPEC-048-R06; CA-006 | RF-64/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir aviso de que a estimativa é educativa e não substitui a apuração de um contador ou o e-CAC da Receita Federal. |
| T-007 | INV-001, INV-002, INV-003; RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes implementados em `backend/tests/test_spec046_049_planning_tax.py`, nomeados `test_SPEC_048_Rxx` por cláusula, e executados na CI com PostgreSQL. T-006 (RNFs) é coberto parcialmente pela suíte, pelo lint e pela varredura de acessibilidade; evidência operacional (backup, disponibilidade) permanece fora do recorte.

## 13. Questões em Aberto

- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-07 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-22 — decisão necessária: Cálculos de expansão: sistema de amortização, encargos, confirmação/atualização de dívida; retirada na aposentadoria; regimes previdenciários e calendário tributário / SPEC-036 a SPEC-038, SPEC-046 a SPEC-048; sem fixar legislação/alíquotas nesta etapa.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

### Decisão adotada para o recorte implementado (2026-10-31)

Regimes e alíquotas da tabela interna `2026-10`: ações em operação comum 15%, isentas quando as vendas do mês somam até R$ 20.000,00; FIIs 20% sem isenção; day trade 20% sem isenção; renda fixa pela tabela regressiva (22,5% a 15% por dias de aplicação), retida na fonte e sem DARF. Prejuízo ou resultado nulo não gera imposto; a compensação de prejuízos anteriores não é calculada e o aviso é exibido. Vencimento do DARF: último dia útil do mês seguinte, desconsiderando sábados, domingos, feriados nacionais fixos e a Sexta-feira Santa (calculada pela Páscoa); pontos facultativos não são considerados. As estimativas são persistidas por titular para alimentar a SPEC-049. O FinNova não gera nem envia DARF e não chama serviços da Receita.

**Contrato:** `POST /api/v1/auth/financial/tax-estimates` {regime, competence AAAA-MM, result, sales, holding_days?} → estimativa com `tax_rate`, `tax`, `exempt`, `darf_due_on`, `rule_version`, `notes` e `notice`; `GET` lista e `DELETE /tax-estimates/{id}` remove (404 para estimativa de outro titular). Tabela `tax_estimates` (migração 033).

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
