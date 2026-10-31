# SPEC-025: Exibir volatilidade e Sharpe histórico

**Estado:** implementação técnica autorizada em 2026-10-29; aguardando CI e revisão humana. A política de cálculo foi confirmada pelo responsável nesta sessão.

## 1. Identificação

- **ID:** SPEC-025
- **Nome:** Exibir volatilidade e Sharpe histórico
- **Objetivo:** Obter série e Selic compatíveis; calcular retornos/desvio; calcular Sharpe simplificado; exibir em simulação/comparador; permitir habilitação pelo iniciante.
- **Valor entregue:** volatilidade/Sharpe com período e ressalva.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-27.
- **RB:** RB-08, RB-10, RB-29.
- **RNF:** RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-10, UC-11; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Simulacao e histórico de Cotação; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-03, DA-07, DA-09; ADR-001, ADR-002, ADR-003; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** exibir volatilidade e sharpe histórico; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Política confirmada: retornos diários simples, no mínimo três preços locais sem intervalo superior a três dias, desvio amostral e anualização por √252. Selic anual vira taxa diária por equivalência composta. Volatilidade zero devolve Sharpe nulo, sem infinito/NaN. Perfil arrojado recebe acesso padrão; os demais habilitam manualmente.

## 4. Dependências

[SPEC-003](SPEC-003.md), [SPEC-007](SPEC-007.md), [SPEC-009](SPEC-009.md), [SPEC-010](SPEC-010.md), [SPEC-023](SPEC-023.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-10, OPEN-15, OPEN-20. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** fórmulas e parâmetros de cálculo aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Obter série e Selic compatíveis.
2. calcular retornos/desvio.
3. calcular Sharpe simplificado.
4. exibir em simulação/comparador.
5. permitir habilitação pelo iniciante.

**Alternativa observável:** Série de retorno constante é caso de volatilidade zero e deve apresentar estado previsto em OPEN-20, sem infinito/NaN.

**Exceções:** Série insuficiente, buracos ou periodicidades incompatíveis não produzem métrica sem aviso.

**Pós-condições:** volatilidade/Sharpe com período e ressalva; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-025-R01 | WHEN ocorrer o fluxo válido de exibir volatilidade e sharpe histórico THE SYSTEM SHALL entregar volatilidade/Sharpe com período e ressalva. | CA-001 |
| SPEC-025-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-025-R03 | WHEN o fluxo de exibir volatilidade e sharpe histórico alcançar o comportamento de RF-27/C01 THE SYSTEM SHALL atender ao comportamento: calcular a volatilidade (desvio padrão dos retornos históricos) de ativos simulados via RF-21/RF-24. | CA-003 |
| SPEC-025-R04 | WHEN o fluxo de exibir volatilidade e sharpe histórico alcançar o comportamento de RF-27/C02 THE SYSTEM SHALL atender ao comportamento: calcular o Índice de Sharpe simplificado: `(retorno médio do ativo − taxa livre de risco) / volatilidade`, usando a Selic (RF-23) como taxa livre de risco. | CA-004 |
| SPEC-025-R05 | WHEN o fluxo de exibir volatilidade e sharpe histórico alcançar o comportamento de RF-27/C03 THE SYSTEM SHALL atender ao comportamento: exibir essas métricas junto ao resultado de cada simulação de renda variável e no comparador (RF-25). | CA-005 |
| SPEC-025-R06 | WHEN o fluxo de exibir volatilidade e sharpe histórico alcançar o comportamento de RF-27/C04 THE SYSTEM SHALL atender ao comportamento: deixar claro que as métricas usam dados históricos e não garantem comportamento futuro (mesma ressalva de RB-08). | CA-006 |
| SPEC-025-R07 | WHEN o fluxo de exibir volatilidade e sharpe histórico alcançar o comportamento de RF-27/C05 THE SYSTEM SHALL atender ao comportamento: disponível por padrão para o perfil avançado (RF-03); o perfil iniciante pode habilitar manualmente. | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Métrica histórica não garante futuro; volatilidade zero não permite divisão direta.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-08: Toda projeção de renda variável deve ser exibida como estimativa, sem garantia de retorno; RB-10: M = P × (1 + i)ⁿ + Σ aportes capitalizados; taxa convertida entre mês/ano por equivalência composta, nunca proporcional simples; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Simulacao e histórico de Cotação. A Simulacao guarda parâmetros, hipóteses, prazo e resultado; o motor retorna valores derivados sem alterar saldo ou patrimônio. Entradas específicas estão na seção 9, fórmulas e calendários ausentes nas OPEN locais. Regras configuráveis devem ter versão identificável no resultado.

Não inventar tabelas, classes de estratégia ou colunas nesta etapa; aplicação e domínio mantêm a separação do modelo conceitual.

## 8. Impacto arquitetural

Capacidade: Exibir volatilidade e Sharpe histórico. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-003. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | ticker de referência local, série diária e Selic local válida |
| Saída | `GET /api/v1/market/quotes/{ticker}/metrics`, com período, regra e ressalva |
| Erro | Série insuficiente, buracos ou periodicidades incompatíveis não produzem métrica sem aviso. |

Identificadores, filtros e autorizações são verificados no servidor. A métrica é exposta em `/api/v1`, exige sessão e permissão de métricas avançadas; a simulação variável recebe `ticker` opcional e só incorpora a métrica quando habilitada. A fonte continua local e nunca é apresentada como cotação em tempo real.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-09 (Atualidade de dados de mercado) | Relógio/fonte simulados: referência, coleta, dados ausentes e limites 24h/15min; fechar OPEN-19. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Série de retorno constante é caso de volatilidade zero e deve apresentar estado previsto em OPEN-20, sem infinito/NaN.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Série insuficiente, buracos ou periodicidades incompatíveis não produzem métrica sem aviso.

- **CA-003** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-27/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular a volatilidade (desvio padrão dos retornos históricos) de ativos simulados via RF-21/RF-24.

- **CA-004** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-27/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular o Índice de Sharpe simplificado: `(retorno médio do ativo − taxa livre de risco) / volatilidade`, usando a Selic (RF-23) como taxa livre de risco.

- **CA-005** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-27/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir essas métricas junto ao resultado de cada simulação de renda variável e no comparador (RF-25).

- **CA-006** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-27/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve deixar claro que as métricas usam dados históricos e não garantem comportamento futuro (mesma ressalva de RB-08).

- **CA-007** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-27/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Disponível por padrão para o perfil avançado (RF-03); o perfil iniciante pode habilitar manualmente.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-025-R01; CA-001; INV-001, INV-002 | Fixture específica: Série de retorno constante é caso de volatilidade zero e deve apresentar estado previsto em OPEN-20, sem infinito/NaN. |
| T-002 | SPEC-025-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Série insuficiente, buracos ou periodicidades incompatíveis não produzem métrica sem aviso. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-025-R03; CA-003 | RF-27/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular a volatilidade (desvio padrão dos retornos históricos) de ativos simulados via RF-21/RF-24. |
| T-004 | SPEC-025-R04; CA-004 | RF-27/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular o Índice de Sharpe simplificado: `(retorno médio do ativo − taxa livre de risco) / volatilidade`, usando a Selic (RF-23) como taxa livre de risco. |
| T-005 | SPEC-025-R05; CA-005 | RF-27/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir essas métricas junto ao resultado de cada simulação de renda variável e no comparador (RF-25). |
| T-006 | SPEC-025-R06; CA-006 | RF-27/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve deixar claro que as métricas usam dados históricos e não garantem comportamento futuro (mesma ressalva de RB-08). |
| T-007 | SPEC-025-R07; CA-007 | RF-27/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Disponível por padrão para o perfil avançado (RF-03); o perfil iniciante pode habilitar manualmente. |
| T-008 | INV-001, INV-002, INV-003; RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-03/10/15/20 estão resolvidas somente neste recorte: dados locais de SPEC-023, retornos simples diários, amostra, √252, Selic composta diária, três preços e Sharpe nulo para volatilidade zero. Atualização de mercado, janela diferente e demais comparações continuam abertas.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Cálculo, acesso por perfil/preferência, integração com simulação variável e ressalva foram implementados sem alterar patrimônio.
- [ ] Testes da seção 12 aprovados, com evidência ligada ao commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
