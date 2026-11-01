# SPEC-034: Calcular e explicar score de saúde financeira

**Estado:** implementada tecnicamente em 2026-10-29; aguarda revisão humana do grupo. Evidências em [implementacao-SPEC-034](../09-qualidade/implementacao-SPEC-034.md). Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-034
- **Nome:** Calcular e explicar score de saúde financeira
- **Objetivo:** Obter fatores do mesmo titular; aplicar pesos configuráveis aprovados; salvar resultado com regra; mostrar nota/faixa e 1-2 fatores negativos; exibir evolução mensal.
- **Valor entregue:** nota 0..100, fatores, classificação e histórico mensal.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-41, RF-42.
- **RB:** RB-15, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25.
- **Fluxo:** UC-14; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** ScoreSaude, Usuario e fatores de orçamento/patrimônio; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** calcular e explicar score de saúde financeira; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Fórmula, classes, desempates e fechamento do histórico permanecem OPEN-11/21; sem eles esta Spec não está pronta para implementar.

## 4. Dependências

[SPEC-020](SPEC-020.md), [SPEC-021](SPEC-021.md), [SPEC-028](SPEC-028.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-11, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Obter fatores do mesmo titular.
2. aplicar pesos configuráveis aprovados.
3. salvar resultado com regra.
4. mostrar nota/faixa e 1-2 fatores negativos.
5. exibir evolução mensal.

**Alternativa observável:** Com fixture de fatores e pesos aprovada, conferir nota independente em 0..100; sem mudar dados, repetir preserva resultado.

**Exceções:** Renda zero, fator ausente ou regra não configurada não produz nota arbitrária.

**Pós-condições:** nota 0..100, fatores, classificação e histórico mensal; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-034-R01 | WHEN ocorrer o fluxo válido de calcular e explicar score de saúde financeira THE SYSTEM SHALL entregar nota 0..100, fatores, classificação e histórico mensal. | CA-001 |
| SPEC-034-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-034-R03 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-41/C01 THE SYSTEM SHALL atender ao comportamento: calcular uma nota (0 a 100) combinando pelo menos: relação gasto/renda do mês (Administração Financeira), existência e tamanho da reserva de emergência (RF-35), comprometimento de renda com dívidas/fatura (RF-13, Compras Financiadas) e aderência às metas definidas (RF-14, RF-15). | CA-003 |
| SPEC-034-R04 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-41/C02 THE SYSTEM SHALL atender ao comportamento: a fórmula de ponderação de cada fator deve ser documentada e configurável (não fixa no código), para permitir ajuste sem nova implantação. | CA-004 |
| SPEC-034-R05 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-41/C03 THE SYSTEM SHALL atender ao comportamento: recalcular o score automaticamente a cada mudança relevante nos módulos de origem. | CA-005 |
| SPEC-034-R06 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-41/C04 THE SYSTEM SHALL atender ao comportamento: deixar explícito que o score é educativo e não constitui recomendação financeira. | CA-006 |
| SPEC-034-R07 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-42/C01 THE SYSTEM SHALL atender ao comportamento: exibir o score atual em destaque (ex.: velocímetro/gauge) com faixa de classificação (ex.: crítico, atenção, saudável, excelente). | CA-007 |
| SPEC-034-R08 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-42/C02 THE SYSTEM SHALL atender ao comportamento: exibir a evolução do score mês a mês (gráfico de linha). | CA-008 |
| SPEC-034-R09 | WHEN o fluxo de calcular e explicar score de saúde financeira alcançar o comportamento de RF-42/C03 THE SYSTEM SHALL atender ao comportamento: exibir, junto ao score, os 1-2 fatores que mais impactaram negativamente o resultado, com uma sugestão genérica de melhoria (ex.: "sua fatura consome X% da sua renda"). | CA-009 |

## 6. Regras e invariantes

- **INV-001:** Score é educativo e não recomendação; gamificação não altera nota.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-15: O score de saúde financeira é educativo, não constitui recomendação financeira, e sua fórmula de ponderação deve ser documentada e configurável; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

ScoreSaude liga Usuario, nota, fatores e data de cálculo; regras de ponderação configuradas determinam faixa e histórico. Não definir pesos ou armazenamento histórico físico sem OPEN-11/21.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Calcular e explicar score de saúde financeira. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | renda/gasto, reserva, dívidas/faturas e metas; fórmula configurada |
| Saída | nota 0..100, fatores, classificação e histórico mensal |
| Erro | Renda zero, fator ausente ou regra não configurada não produz nota arbitrária. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

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
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Com fixture de fatores e pesos aprovada, conferir nota independente em 0..100; sem mudar dados, repetir preserva resultado.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Renda zero, fator ausente ou regra não configurada não produz nota arbitrária.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-41/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve calcular uma nota (0 a 100) combinando pelo menos: relação gasto/renda do mês (Administração Financeira), existência e tamanho da reserva de emergência (RF-35), comprometimento de renda com dívidas/fatura (RF-13, Compras Financiadas) e aderência às metas definidas (RF-14, RF-15).

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-41/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A fórmula de ponderação de cada fator deve ser documentada e configurável (não fixa no código), para permitir ajuste sem nova implantação.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-41/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve recalcular o score automaticamente a cada mudança relevante nos módulos de origem.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-41/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve deixar explícito que o score é educativo e não constitui recomendação financeira.

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-42/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir o score atual em destaque (ex.: velocímetro/gauge) com faixa de classificação (ex.: crítico, atenção, saudável, excelente).

- **CA-008** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-42/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir a evolução do score mês a mês (gráfico de linha).

- **CA-009** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-42/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir, junto ao score, os 1-2 fatores que mais impactaram negativamente o resultado, com uma sugestão genérica de melhoria (ex.: "sua fatura consome X% da sua renda").

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-034-R01; CA-001; INV-001, INV-002 | Fixture específica: Com fixture de fatores e pesos aprovada, conferir nota independente em 0..100; sem mudar dados, repetir preserva resultado. |
| T-002 | SPEC-034-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Renda zero, fator ausente ou regra não configurada não produz nota arbitrária. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-034-R03; CA-003 | RF-41/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve calcular uma nota (0 a 100) combinando pelo menos: relação gasto/renda do mês (Administração Financeira), existência e tamanho da reserva de emergência (RF-35), comprometimento de renda com dívidas/fatura (RF-13, Compras Financiadas) e aderência às metas definidas (RF-14, RF-15). |
| T-004 | SPEC-034-R04; CA-004 | RF-41/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A fórmula de ponderação de cada fator deve ser documentada e configurável (não fixa no código), para permitir ajuste sem nova implantação. |
| T-005 | SPEC-034-R05; CA-005 | RF-41/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve recalcular o score automaticamente a cada mudança relevante nos módulos de origem. |
| T-006 | SPEC-034-R06; CA-006 | RF-41/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve deixar explícito que o score é educativo e não constitui recomendação financeira. |
| T-007 | SPEC-034-R07; CA-007 | RF-42/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir o score atual em destaque (ex.: velocímetro/gauge) com faixa de classificação (ex.: crítico, atenção, saudável, excelente). |
| T-008 | SPEC-034-R08; CA-008 | RF-42/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir a evolução do score mês a mês (gráfico de linha). |
| T-009 | SPEC-034-R09; CA-009 | RF-42/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir, junto ao score, os 1-2 fatores que mais impactaram negativamente o resultado, com uma sugestão genérica de melhoria (ex.: "sua fatura consome X% da sua renda"). |
| T-010 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-11 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-21 — decisão necessária: Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais / SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059.

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
