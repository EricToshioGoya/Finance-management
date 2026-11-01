# SPEC-053: Consultar indicadores contábeis CVM por período

**Estado:** implementada tecnicamente em 2026-10-28; aguarda revisão humana do grupo. A evidência executável está em [implementacao-SPEC-053](../09-qualidade/implementacao-SPEC-053.md). Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-053
- **Nome:** Consultar indicadores contábeis CVM por período
- **Objetivo:** Consumir DFP/ITR aberto; validar estrutura; extrair números aprovados; guardar referência; apresentar tabela/evolução; aplicar retenção compartilhada.
- **Valor entregue:** tabela/gráfico com valores estruturados e fonte.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-32.
- **RB:** RB-12.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-13, UC-20; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** EmpresaAberta e IndicadorFinanceiro; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-04, DA-07, DA-09; ADR-001, ADR-002, ADR-004; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** catálogo local de referência para PETR4 e VALE3, com receita líquida, lucro líquido e patrimônio líquido de Exercício 2025 e 2º trimestre de 2026. Cada linha guarda período, data de referência, fonte, publicação, sincronização, status e unidade única de R$ mil; tabela e gráfico exibem a revisão efetiva. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

O recorte não executa sincronização externa em tempo real: a fonte é representada por fixture local rastreável para o diretório de dados DFP/ITR. O expurgo automático permanece em SPEC-054.

## 4. Dependências

[SPEC-012](SPEC-012.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-10, OPEN-15, OPEN-27. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** sessão autenticada; empresa presente no catálogo local de referência.

**Fluxo principal:**

1. Consultar os indicadores estruturados da empresa pelo contrato autenticado.
2. Filtrar opcionalmente indicador e periodicidade.
3. Retornar as linhas com fonte, unidade, data de referência e status.
4. Identificar a revisão mais recente como efetiva sem apagar a reapresentada.
5. Apresentar tabela acessível e gráfico textual de evolução usando apenas as linhas efetivas.

**Alternativa observável:** Fixture com receita/lucro/patrimônio em dois períodos aparece nos rótulos corretos com fonte e unidade.

**Exceções:** Conta desconhecida, dado reapresentado ou unidade incompatível não é somado silenciosamente.

**Pós-condições:** tabela/gráfico com valores estruturados e fonte; preservação dos invariantes. Erro não produz confirmação de resultado inexistente. A retenção de 12 meses é responsabilidade explícita da SPEC-054.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-053-R01 | WHEN ocorrer o fluxo válido de consultar indicadores contábeis cvm por período THE SYSTEM SHALL entregar tabela/gráfico com valores estruturados e fonte. | CA-001 |
| SPEC-053-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-053-R03 | WHEN o fluxo de consultar indicadores contábeis cvm por período alcançar o comportamento de RF-32/C01 THE SYSTEM SHALL atender ao comportamento: extrair indicadores estruturados (ex.: receita líquida, lucro líquido, patrimônio líquido) a partir dos arquivos de DFP/ITR do Portal de Dados Abertos da CVM (dados numéricos, não o PDF do relatório). | CA-003 |
| SPEC-053-R04 | WHEN o fluxo de consultar indicadores contábeis cvm por período alcançar o comportamento de RF-32/C02 THE SYSTEM SHALL atender ao comportamento: exibir esses indicadores em tabela e em gráfico de evolução por período (trimestre/ano). | CA-004 |
| SPEC-053-R05 | WHEN o fluxo de consultar indicadores contábeis cvm por período alcançar o comportamento de RF-32/C03 THE SYSTEM SHALL atender ao comportamento: indicar a fonte e a data de referência dos dados extraídos. | CA-005 |
| SPEC-053-R06 | WHEN o fluxo de consultar indicadores contábeis cvm por período alcançar o comportamento de RF-32/C04 THE SYSTEM SHALL atender ao comportamento: diferente do documento completo (RF-31), esses dados numéricos podem ser armazenados localmente, pois são dados abertos de reuso livre — respeitando o limite de retenção de RF-33. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Indicador contábil não é taxa Selic/CDI nem binário do PDF.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** A fixture local não afirma sincronização ao vivo, aprovação humana histórica ou disponibilidade de provedor; seu diretório de origem e recorte são exibidos.

Regras herdadas: RB-12: Documentos completos (PDF) nunca são armazenados — apenas linkados; metadados e indicadores extraídos são mantidos em cache por no máximo 12 meses e depois expurgados. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

EmpresaAberta possui 0..N IndicadorFinanceiro por conta/período, valor/unidade, fonte e sincronizado_em; conceito distinto de indicador de mercado.

O modelo físico `financial_indicators` contém `metric`, `period_kind`, `reference_period`, `reference_date`, `value`, `unit`, `source_name`, `source_url`, `status`, `published_at` e `synced_at`; não possui binário ou conteúdo de PDF. `effective` é calculado pela linha mais recentemente publicada para conta/período, não persistido nem somado.

## 8. Impacto arquitetural

Capacidade: Consultar indicadores contábeis CVM por período. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

O endpoint autenticado é `GET /api/v1/companies/{company_id}/financial-indicators`, com filtros opcionais `metric` e `period_kind`. A migration 017 semeia o catálogo local e não realiza chamada externa. A integração operacional e expurgo continuam nas Specs próprias.

ADRs relacionados: ADR-001, ADR-002, ADR-004. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | ID de empresa e, opcionalmente, métrica (`net_revenue`, `net_income`, `equity`) e periodicidade (`annual`, `quarterly`) |
| Saída | linhas com valor em `BRL_THOUSANDS`, fonte, data de referência/status e campo `effective`; tabela/gráfico no cliente |
| Erro | 401 sem sessão; 404 para empresa ausente; 422 para filtro fora do vocabulário. Reapresentação permanece visível e não é somada. |

Identificadores, filtros e autorizações são verificados no servidor. O contrato usa o prefixo `/api/v1` e não altera a sessão do ADR-007. O diretório de fonte é mostrado como Dados Abertos CVM — catálogo local de referência; o recorte não declara atualização automática.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-10 (Ciclo de vida de dados externos) | Relógio injetado: expurgo ao atingir 12 meses e consulta após ressincronização. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-12 (Observabilidade) | Injetar erro e verificar logging estruturado/alerta sem conteúdo pessoal; observabilidade operacional em OPEN-32. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Fixture com receita/lucro/patrimônio em dois períodos aparece nos rótulos corretos com fonte e unidade.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Conta desconhecida, dado reapresentado ou unidade incompatível não é somado silenciosamente.

- **CA-003** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-32/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve extrair indicadores estruturados (ex.: receita líquida, lucro líquido, patrimônio líquido) a partir dos arquivos de DFP/ITR do Portal de Dados Abertos da CVM (dados numéricos, não o PDF do relatório).

- **CA-004** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-32/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir esses indicadores em tabela e em gráfico de evolução por período (trimestre/ano).

- **CA-005** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-32/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve indicar a fonte e a data de referência dos dados extraídos.

- **CA-006** — **Dado** rotina/fonte autorizada e contratos externos aprovados, entradas válidas e política aprovada de RF-32/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Diferente do documento completo (RF-31), esses dados numéricos podem ser armazenados localmente, pois são dados abertos de reuso livre — respeitando o limite de retenção de RF-33.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-053-R01; CA-001; INV-001, INV-002 | Fixture específica: Fixture com receita/lucro/patrimônio em dois períodos aparece nos rótulos corretos com fonte e unidade. |
| T-002 | SPEC-053-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Conta desconhecida, dado reapresentado ou unidade incompatível não é somado silenciosamente. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-053-R03; CA-003 | RF-32/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve extrair indicadores estruturados (ex.: receita líquida, lucro líquido, patrimônio líquido) a partir dos arquivos de DFP/ITR do Portal de Dados Abertos da CVM (dados numéricos, não o PDF do relatório). |
| T-004 | SPEC-053-R04; CA-004 | RF-32/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir esses indicadores em tabela e em gráfico de evolução por período (trimestre/ano). |
| T-005 | SPEC-053-R05; CA-005 | RF-32/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve indicar a fonte e a data de referência dos dados extraídos. |
| T-006 | SPEC-053-R06; CA-006 | RF-32/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Diferente do documento completo (RF-31), esses dados numéricos podem ser armazenados localmente, pois são dados abertos de reuso livre — respeitando o limite de retenção de RF-33. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-10 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-27 — decisão necessária: CVM: contratos de cadastro/DFP/ITR/FRE/IPE, contas/unidades, reapresentações, identidade de documento, periodicidade de verificação de links e doze meses de calendário / SPEC-012, SPEC-027, SPEC-053, SPEC-054.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [x] Recorte técnico registrado com a autorização da sessão e evidência real.
- [x] Política local de fontes/unidades/reapresentações registrada somente para este contrato.
- [ ] Esta versão revisada individualmente pelo grupo, sem aprovação histórica presumida.
- [x] Cláusulas/CA do recorte implementadas e invariantes preservados.
- [x] Testes de API derivam T-001 a T-007; evidência no registro de implementação.
- [ ] RNFs operacionais (carga, monitoramento e expurgo) continuam dependentes de ambiente/SPEC-054.
- [x] Contrato, migration, cliente e documentação foram conciliados no recorte; sincronização externa não é alegada.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
