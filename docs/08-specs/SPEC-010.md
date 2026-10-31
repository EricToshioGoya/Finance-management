# SPEC-010: Comparar simulações existentes

**Estado:** implementada tecnicamente no código do grupo, incorporado à `main` em 2026-10-31 (PR #43); testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py` e interface web na navegação por abas (PR #45). Cobertura por cláusula (C-02) concluída em 2026-10-31: cada cláusula `SHALL` tem teste `test_SPEC_010_Rxx` em `backend/tests/test_c02_spec007_010_simulacoes.py`; aprovação formal do grupo pendente.

## 1. Identificação

- **ID:** SPEC-010
- **Nome:** Comparar simulações existentes
- **Objetivo:** Selecionar registros; verificar titular e compatibilidade; apresentar hipóteses, resultados e diferenças; indicar maior montante comparável.
- **Valor entregue:** resultados lado a lado, diferenças percentuais e maior resultado.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-25.
- **RB:** RB-08, RB-29.
- **RNF:** RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-11; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e Simulacao; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** comparar simulações existentes; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

A entrega é vertical: interface/contrato, aplicação, regras e persistência necessárias ao comportamento; não é um projeto inteiro de backend ou banco.

## 4. Dependências

[SPEC-008](SPEC-008.md), [SPEC-009](SPEC-009.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-20. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Selecionar registros.
2. verificar titular e compatibilidade.
3. apresentar hipóteses, resultados e diferenças.
4. indicar maior montante comparável.

**Alternativa observável:** Resultados comparáveis 100 e 110 mostram ambos e vencedor 110; referência do percentual depende de OPEN-20.

**Exceções:** Menos de duas simulações, base zero ou moedas/prazos incompatíveis seguem erro/normalização a definir em OPEN-20, sem divisão por zero.

**Pós-condições:** resultados lado a lado, diferenças percentuais e maior resultado; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-010-R01 | WHEN ocorrer o fluxo válido de comparar simulações existentes THE SYSTEM SHALL entregar resultados lado a lado, diferenças percentuais e maior resultado. | CA-001 |
| SPEC-010-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-010-R03 | WHEN o fluxo de comparar simulações existentes alcançar o comportamento de RF-25/C01 THE SYSTEM SHALL atender ao comportamento: permitir selecionar 2 ou mais simulações já feitas (ex.: poupança vs. CDB vs. Tesouro) para comparação lado a lado. | CA-003 |
| SPEC-010-R04 | WHEN o fluxo de comparar simulações existentes alcançar o comportamento de RF-25/C02 THE SYSTEM SHALL atender ao comportamento: exibir os resultados finais e a diferença percentual entre os cenários. | CA-004 |
| SPEC-010-R05 | WHEN o fluxo de comparar simulações existentes alcançar o comportamento de RF-25/C03 THE SYSTEM SHALL atender ao comportamento: indicar qual cenário rende mais ao final do prazo. | CA-005 |

## 6. Regras e invariantes

- **INV-001:** Não misturar resultado bruto e líquido sem identificação nem acessar simulação alheia.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-08: Toda projeção de renda variável deve ser exibida como estimativa, sem garantia de retorno; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Duas ou mais Simulacao selecionadas pertencem ao mesmo titular; comparar é operação de leitura e não cria novos saldos.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Comparar simulações existentes. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | duas ou mais simulações próprias selecionadas |
| Saída | resultados lado a lado, diferenças percentuais e maior resultado |
| Erro | Menos de duas simulações, base zero ou moedas/prazos incompatíveis seguem erro/normalização a definir em OPEN-20, sem divisão por zero. |

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
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Resultados comparáveis 100 e 110 mostram ambos e vencedor 110; referência do percentual depende de OPEN-20.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Menos de duas simulações, base zero ou moedas/prazos incompatíveis seguem erro/normalização a definir em OPEN-20, sem divisão por zero.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-25/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir selecionar 2 ou mais simulações já feitas (ex.: poupança vs. CDB vs. Tesouro) para comparação lado a lado.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-25/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir os resultados finais e a diferença percentual entre os cenários.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-25/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve indicar qual cenário rende mais ao final do prazo.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-010-R01; CA-001; INV-001, INV-002 | Fixture específica: Resultados comparáveis 100 e 110 mostram ambos e vencedor 110; referência do percentual depende de OPEN-20. |
| T-002 | SPEC-010-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Menos de duas simulações, base zero ou moedas/prazos incompatíveis seguem erro/normalização a definir em OPEN-20, sem divisão por zero. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-010-R03; CA-003 | RF-25/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir selecionar 2 ou mais simulações já feitas (ex.: poupança vs. CDB vs. Tesouro) para comparação lado a lado. |
| T-004 | SPEC-010-R04; CA-004 | RF-25/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir os resultados finais e a diferença percentual entre os cenários. |
| T-005 | SPEC-010-R05; CA-005 | RF-25/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve indicar qual cenário rende mais ao final do prazo. |
| T-006 | INV-001, INV-002, INV-003; RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes automatizados em `backend/tests/test_spec004_007_008_010_013_020_024.py`, executados na CI com PostgreSQL. A correspondência um-para-um entre cláusulas e testes (C-02) está nos testes `test_SPEC_NNN_Rxx` indicados no Estado desta spec.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-20 — decisão necessária: Comparações/métricas: base percentual, zero, moeda/prazo/tributação compatíveis; janela de retornos, desvio e anualização; critério de vantagem financeira / SPEC-010, SPEC-025, SPEC-037.

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
