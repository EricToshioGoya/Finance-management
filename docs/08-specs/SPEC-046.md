# SPEC-046: Projetar aposentadoria e renda estimada

**Estado:** rascunho para revisão humana, criado em 2026-10-22. Produção documental autorizada no lote atual; sem implementação/testes novos ou aprovação formal presumida.

## 1. Identificação

- **ID:** SPEC-046
- **Nome:** Projetar aposentadoria e renda estimada
- **Objetivo:** Validar idades/prazo; normalizar taxa; projetar aportes pelo motor; aplicar parâmetro aprovado de retirada; mostrar hipóteses educativas.
- **Valor entregue:** patrimônio na data-alvo e renda mensal estimada.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-62.
- **RB:** RB-10, RB-28, RB-29.
- **RNF:** RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** Fluxo aposentadoria RF-62; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Simulacao e ResultadoCalculo; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** projetar aposentadoria e renda estimada; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Regra de 4% é exemplo, não decisão; retirada, inflação e idades fracionárias em OPEN-22.

## 4. Dependências

[SPEC-002](SPEC-002.md), [SPEC-007](SPEC-007.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-07, OPEN-15, OPEN-22. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** fórmulas e parâmetros de cálculo aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar idades/prazo.
2. normalizar taxa.
3. projetar aportes pelo motor.
4. aplicar parâmetro aprovado de retirada.
5. mostrar hipóteses educativas.

**Alternativa observável:** Aporte 100 por 12 meses e taxa zero produz acumulado 1200; retirada depende do parâmetro aprovado.

**Exceções:** Idade-alvo não futura ou parâmetro de retirada indefinido não gera renda garantida.

**Pós-condições:** patrimônio na data-alvo e renda mensal estimada; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-046-R01 | WHEN ocorrer o fluxo válido de projetar aposentadoria e renda estimada THE SYSTEM SHALL entregar patrimônio na data-alvo e renda mensal estimada. | CA-001 |
| SPEC-046-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-046-R03 | WHEN o fluxo de projetar aposentadoria e renda estimada alcançar o comportamento de RF-62/C01 THE SYSTEM SHALL atender ao comportamento: permitir informar idade atual, idade-alvo de aposentadoria, aporte mensal e taxa de rentabilidade esperada (ou sugerida a partir de RF-23). | CA-003 |
| SPEC-046-R04 | WHEN o fluxo de projetar aposentadoria e renda estimada alcançar o comportamento de RF-62/C02 THE SYSTEM SHALL atender ao comportamento: reaproveitar o motor de juros compostos (RF-22/RB-10) para projetar o patrimônio acumulado até a data-alvo. | CA-004 |
| SPEC-046-R05 | WHEN o fluxo de projetar aposentadoria e renda estimada alcançar o comportamento de RF-62/C03 THE SYSTEM SHALL atender ao comportamento: estimar a renda mensal que o patrimônio projetado sustentaria (ex.: regra dos 4% ou parâmetro configurável). | CA-005 |
| SPEC-046-R06 | WHEN o fluxo de projetar aposentadoria e renda estimada alcançar o comportamento de RF-62/C04 THE SYSTEM SHALL atender ao comportamento: exibir aviso de que a projeção é educativa, sujeita a variação de rentabilidade real, inflação e mudanças na legislação previdenciária. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Renda estimada não é benefício previdenciário garantido; projeção não altera patrimônio real.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-10: M = P × (1 + i)ⁿ + Σ aportes capitalizados; taxa convertida entre mês/ano por equivalência composta, nunca proporcional simples; RB-28: O motor genérico aceita valor inicial e aporte não negativos, taxa não negativa e prazo inteiro positivo; esses parâmetros não são lançamentos de renda/despesa e não estão sujeitos ao mínimo estrito de RB-01; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Simulacao e ResultadoCalculo. A Simulacao guarda parâmetros, hipóteses, prazo e resultado; o motor retorna valores derivados sem alterar saldo ou patrimônio. Entradas específicas estão na seção 9, fórmulas e calendários ausentes nas OPEN locais. Regras configuráveis devem ter versão identificável no resultado.

Não inventar tabelas, classes de estratégia ou colunas nesta etapa; aplicação e domínio mantêm a separação do modelo conceitual.

## 8. Impacto arquitetural

Capacidade: Projetar aposentadoria e renda estimada. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | idades atual/alvo, aporte e rentabilidade esperada |
| Saída | patrimônio na data-alvo e renda mensal estimada |
| Erro | Idade-alvo não futura ou parâmetro de retirada indefinido não gera renda garantida. |

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

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Aporte 100 por 12 meses e taxa zero produz acumulado 1200; retirada depende do parâmetro aprovado.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Idade-alvo não futura ou parâmetro de retirada indefinido não gera renda garantida.

- **CA-003** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-62/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir informar idade atual, idade-alvo de aposentadoria, aporte mensal e taxa de rentabilidade esperada (ou sugerida a partir de RF-23).

- **CA-004** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-62/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve reaproveitar o motor de juros compostos (RF-22/RB-10) para projetar o patrimônio acumulado até a data-alvo.

- **CA-005** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-62/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve estimar a renda mensal que o patrimônio projetado sustentaria (ex.: regra dos 4% ou parâmetro configurável).

- **CA-006** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-62/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir aviso de que a projeção é educativa, sujeita a variação de rentabilidade real, inflação e mudanças na legislação previdenciária.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-046-R01; CA-001; INV-001, INV-002 | Fixture específica: Aporte 100 por 12 meses e taxa zero produz acumulado 1200; retirada depende do parâmetro aprovado. |
| T-002 | SPEC-046-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Idade-alvo não futura ou parâmetro de retirada indefinido não gera renda garantida. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-046-R03; CA-003 | RF-62/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir informar idade atual, idade-alvo de aposentadoria, aporte mensal e taxa de rentabilidade esperada (ou sugerida a partir de RF-23). |
| T-004 | SPEC-046-R04; CA-004 | RF-62/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve reaproveitar o motor de juros compostos (RF-22/RB-10) para projetar o patrimônio acumulado até a data-alvo. |
| T-005 | SPEC-046-R05; CA-005 | RF-62/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve estimar a renda mensal que o patrimônio projetado sustentaria (ex.: regra dos 4% ou parâmetro configurável). |
| T-006 | SPEC-046-R06; CA-006 | RF-62/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir aviso de que a projeção é educativa, sujeita a variação de rentabilidade real, inflação e mudanças na legislação previdenciária. |
| T-007 | INV-001, INV-002, INV-003; RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-07 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-22 — decisão necessária: Cálculos de expansão: sistema de amortização, encargos, confirmação/atualização de dívida; retirada na aposentadoria; regimes previdenciários e calendário tributário / SPEC-036 a SPEC-038, SPEC-046 a SPEC-048; sem fixar legislação/alíquotas nesta etapa.

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
