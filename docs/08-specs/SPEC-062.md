# SPEC-062: Consultar distribuição de perfis no painel

**Estado:** implementada tecnicamente em 2026-10-31 (backend, interface web e testes automatizados). Política de recorte proposta pelo agente e aprovada pelo responsável em 2026-10-31; revisão formal do grupo pendente. Evidências no [registro de implementação](../09-qualidade/implementacao-SPEC-062.md).

## 1. Identificação

- **ID:** SPEC-062
- **Nome:** Consultar distribuição de perfis no painel
- **Objetivo:** Validar administrador; selecionar período de cadastro; agrupar por perfil aprovado; mostrar pizza/barras; atualizar quando quiz é concluído.
- **Valor entregue:** distribuição agregada por resultado do quiz.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-56.
- **RB:** RB-09, RB-22.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** UC-19; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e perfil de investidor; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** consultar distribuição de perfis no painel; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Classe sem resposta, filtros de data e classificação dependem de OPEN-11/21.

## 4. Dependências

[SPEC-003](SPEC-003.md), [SPEC-011](SPEC-011.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-11, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** sessão com papel administrativo validada no servidor; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar administrador.
2. selecionar período de cadastro.
3. agrupar por perfil aprovado.
4. mostrar pizza/barras.
5. atualizar quando quiz é concluído.

**Alternativa observável:** Duas contas de perfil A e uma de B no período exibem contagens 2/1, sem incluir cadastro fora do período.

**Exceções:** Usuário comum não recebe gráfico; conta sem quiz não recebe perfil inventado.

**Pós-condições:** distribuição agregada por resultado do quiz; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-062-R01 | WHEN ocorrer o fluxo válido de consultar distribuição de perfis no painel THE SYSTEM SHALL entregar distribuição agregada por resultado do quiz. | CA-001 |
| SPEC-062-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-062-R03 | WHEN o fluxo de consultar distribuição de perfis no painel alcançar o comportamento de RF-56/C01 THE SYSTEM SHALL atender ao comportamento: exibir gráfico dinâmico (pizza ou barras) com a distribuição dos usuários por resultado do quiz de perfil de investidor (RF-03) — ex.: iniciante/avançado ou conservador/moderado/arrojado. | CA-003 |
| SPEC-062-R04 | WHEN o fluxo de consultar distribuição de perfis no painel alcançar o comportamento de RF-56/C02 THE SYSTEM SHALL atender ao comportamento: permitir filtrar por período de cadastro. | CA-004 |
| SPEC-062-R05 | WHEN o fluxo de consultar distribuição de perfis no painel alcançar o comportamento de RF-56/C03 THE SYSTEM SHALL atender ao comportamento: atualizar automaticamente conforme novos usuários completam o quiz. | CA-005 |

## 6. Regras e invariantes

- **INV-001:** Gráfico não expõe respostas individuais nem dados financeiros.
- **INV-002:** Acesso pessoal e efeitos externos seguem o limite desta capacidade: autorização é verificada no servidor; erro não confirma alteração/entrega inexistente.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-09: O resultado do quiz de perfil define a experiência exibida no simulador; RB-22: O painel administrativo nunca exibe dados financeiros individuais de um usuário específico — apenas metadados de conta e métricas agregadas de uso. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario mantém data de cadastro e perfil classificado; painel agrega contagens por perfil/período. Perfil não respondido depende de apresentação aprovada, não classificar por suposição.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Consultar distribuição de perfis no painel. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | período de cadastro dos usuários |
| Saída | distribuição agregada por resultado do quiz |
| Erro | Usuário comum não recebe gráfico; conta sem quiz não recebe perfil inventado. |

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

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Duas contas de perfil A e uma de B no período exibem contagens 2/1, sem incluir cadastro fora do período.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Usuário comum não recebe gráfico; conta sem quiz não recebe perfil inventado.

- **CA-003** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-56/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exibir gráfico dinâmico (pizza ou barras) com a distribuição dos usuários por resultado do quiz de perfil de investidor (RF-03) — ex.: iniciante/avançado ou conservador/moderado/arrojado.

- **CA-004** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-56/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir filtrar por período de cadastro.

- **CA-005** — **Dado** sessão com papel administrativo validada no servidor, entradas válidas e política aprovada de RF-56/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve atualizar automaticamente conforme novos usuários completam o quiz.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-062-R01; CA-001; INV-001, INV-002 | Fixture específica: Duas contas de perfil A e uma de B no período exibem contagens 2/1, sem incluir cadastro fora do período. |
| T-002 | SPEC-062-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Usuário comum não recebe gráfico; conta sem quiz não recebe perfil inventado. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-062-R03; CA-003 | RF-56/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exibir gráfico dinâmico (pizza ou barras) com a distribuição dos usuários por resultado do quiz de perfil de investidor (RF-03) — ex.: iniciante/avançado ou conservador/moderado/arrojado. |
| T-004 | SPEC-062-R04; CA-004 | RF-56/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir filtrar por período de cadastro. |
| T-005 | SPEC-062-R05; CA-005 | RF-56/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve atualizar automaticamente conforme novos usuários completam o quiz. |
| T-006 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes implementados em `backend/tests/test_spec062_profile_distribution.py`, nomeados `test_SPEC_062_Rxx` por cláusula, e executados na CI com PostgreSQL. T-006 (RNFs) é coberto parcialmente pela suíte, pelo lint e pela varredura de acessibilidade; evidência operacional (backup, disponibilidade) permanece fora do recorte.

## 13. Questões em Aberto

- OPEN-11 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-21 — decisão necessária: Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais / SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

### Decisão adotada para o recorte implementado (2026-10-31)

Perfis considerados: `conservador`, `moderado` e `arrojado` (SPEC-003). Contas sem quiz aparecem em `without_profile`, sem perfil inventado. O filtro usa a data de cadastro, com limites inclusivos no fuso America/Sao_Paulo (ADR-006); início maior que o fim retorna 422. Percentuais são calculados sobre usuários com perfil, arredondados a duas casas (HALF_EVEN). A consulta é feita em tempo real; a tela administrativa recarrega a cada 60 segundos (R05).

**Contrato:** `GET /api/v1/admin/investor-profiles?start=AAAA-MM-DD&end=AAAA-MM-DD` → `total_users`, `profiled_users`, `without_profile`, `items[{profile, count, percentage}]`, `generated_at`. 401 sem sessão; 403 `admin_access_denied` para usuário comum (RNF-21).

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
