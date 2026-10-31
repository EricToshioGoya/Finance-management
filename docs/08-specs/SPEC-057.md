# SPEC-057: Registrar receita pontual por competência

**Estado:** implementada tecnicamente no código do grupo, incorporado à `main` em 2026-10-31 (PR #43); testes automatizados em `backend/tests/test_spec057_058_variable_income.py` e interface web na navegação por abas (PR #45). A cobertura por cláusula (C-02) usa testes agrupados e deve ser detalhada na revisão; aprovação formal do grupo pendente.

## 1. Identificação

- **ID:** SPEC-057
- **Nome:** Registrar receita pontual por competência
- **Objetivo:** Validar campos; associar titular/origem; gravar uma entrada; agregar somente na competência da data.
- **Valor entregue:** entrada atribuída ao mês correspondente.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-07.
- **RB:** RB-01, RB-05, RB-29.
- **RNF:** RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25.
- **Fluxo:** UC-05; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario, Conta e ReceitaPontual; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09, DA-10, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** registrar receita pontual por competência; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Chave idempotente e fuso seguem RNF-24/25; vínculo a cartão continua OPEN-12.

## 4. Dependências

[SPEC-005](SPEC-005.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-12, OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Validar campos.
2. associar titular/origem.
3. gravar uma entrada.
4. agregar somente na competência da data.

**Alternativa observável:** Receita de 100 datada em janeiro aumenta só janeiro; fevereiro fica sem repetição automática.

**Exceções:** Valor zero/negativo ou origem alheia não cria lançamento.

**Pós-condições:** entrada atribuída ao mês correspondente; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-057-R01 | WHEN ocorrer o fluxo válido de registrar receita pontual por competência THE SYSTEM SHALL entregar entrada atribuída ao mês correspondente. | CA-001 |
| SPEC-057-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-057-R03 | WHEN o fluxo de registrar receita pontual por competência alcançar o comportamento de RF-07/C01 THE SYSTEM SHALL atender ao comportamento: permitir cadastrar lançamentos de renda variável com valor, descrição e data. | CA-003 |
| SPEC-057-R04 | WHEN o fluxo de registrar receita pontual por competência alcançar o comportamento de RF-07/C02 THE SYSTEM SHALL atender ao comportamento: cada lançamento é pontual (referente a um mês específico), diferente da renda fixa recorrente. | CA-004 |
| SPEC-057-R05 | WHEN o fluxo de registrar receita pontual por competência alcançar o comportamento de RF-07/C03 THE SYSTEM SHALL atender ao comportamento: ser somada à renda fixa para compor a renda total do mês. | CA-005 |
| SPEC-057-R06 | WHEN o fluxo de registrar receita pontual por competência alcançar o comportamento de RF-07/C04 THE SYSTEM SHALL atender ao comportamento: validar que o valor é maior que zero. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Receita pontual não se repete automaticamente nem representa retorno projetado de ativo.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-01: Todo valor de renda ou despesa lançado deve ser maior que zero (bônus/PLR pode ser zero); RB-05: Renda total do mês = renda fixa + renda variável do mês + bônus/PLR recebido no mês; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

ReceitaPontual especializa Renda, com valor, descrição e data; cada registro pertence ao titular e contribui somente na competência informada.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Registrar receita pontual por competência. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | descrição, data e valor positivo |
| Saída | entrada atribuída ao mês correspondente |
| Erro | Valor zero/negativo ou origem alheia não cria lançamento. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-03 (Usabilidade) | Contar passos para criar lançamento em desktop e mobile; máximo de três. |
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
| RNF-22 (Modo offline (mobile)) | Simular sem rede e reconectar mobile; sincronizar em até 60s sem perda/duplicidade; conflitos dependem OPEN-31. |
| RNF-24 (Confiabilidade (idempotência)) | Reenviar criação com a mesma Idempotency-Key por titular; confirmar um registro e mesma resposta; retenção em OPEN-15/21. |
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Receita de 100 datada em janeiro aumenta só janeiro; fevereiro fica sem repetição automática.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Valor zero/negativo ou origem alheia não cria lançamento.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-07/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir cadastrar lançamentos de renda variável com valor, descrição e data.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-07/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Cada lançamento é pontual (referente a um mês específico), diferente da renda fixa recorrente.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-07/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve ser somada à renda fixa para compor a renda total do mês.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-07/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve validar que o valor é maior que zero.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-057-R01; CA-001; INV-001, INV-002 | Fixture específica: Receita de 100 datada em janeiro aumenta só janeiro; fevereiro fica sem repetição automática. |
| T-002 | SPEC-057-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Valor zero/negativo ou origem alheia não cria lançamento. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-057-R03; CA-003 | RF-07/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir cadastrar lançamentos de renda variável com valor, descrição e data. |
| T-004 | SPEC-057-R04; CA-004 | RF-07/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Cada lançamento é pontual (referente a um mês específico), diferente da renda fixa recorrente. |
| T-005 | SPEC-057-R05; CA-005 | RF-07/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve ser somada à renda fixa para compor a renda total do mês. |
| T-006 | SPEC-057-R06; CA-006 | RF-07/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve validar que o valor é maior que zero. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes automatizados em `backend/tests/test_spec057_058_variable_income.py`, executados na CI com PostgreSQL. A correspondência um-para-um entre cláusulas e testes (C-02) ainda precisa ser detalhada.

## 13. Questões em Aberto

- OPEN-12 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
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
