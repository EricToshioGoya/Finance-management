# SPEC-055: Gerir categorias padrão e pessoais

**Estado:** implementação técnica concluída em 2026-10-25; aprovação formal humana continua pendente. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-055
- **Nome:** Gerir categorias padrão e pessoais
- **Objetivo:** Disponibilizar padrão Moradia/Custos básicos/Alimentação/Locomoção/Saúde/Educação/Lazer/Investimentos/Doações; criar personalizada; atribuir cor consistente; ocultar padrão sem apagar histórico.
- **Valor entregue:** categorias padrão/pessoais disponíveis e histórico preservado.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-10.
- **RB:** RB-02, RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20.
- **Fluxo:** UC-07; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Categoria, Usuario e Despesa; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** gerir categorias padrão e pessoais; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Duplicidade de nomes, cores e uso de categoria inativa em lançamentos antigos em OPEN-21.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-21. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Disponibilizar padrão Moradia/Custos básicos/Alimentação/Locomoção/Saúde/Educação/Lazer/Investimentos/Doações.
2. criar personalizada.
3. atribuir cor consistente.
4. ocultar padrão sem apagar histórico.

**Alternativa observável:** Ocultar Lazer para um titular não a oculta para outro e não apaga despesa antiga em Lazer.

**Exceções:** Categoria de outro titular não é oferecida como personalizada própria.

**Pós-condições:** categorias padrão/pessoais disponíveis e histórico preservado; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-055-R01 | WHEN ocorrer o fluxo válido de gerir categorias padrão e pessoais THE SYSTEM SHALL entregar categorias padrão/pessoais disponíveis e histórico preservado. | CA-001 |
| SPEC-055-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-055-R03 | WHEN o fluxo de gerir categorias padrão e pessoais alcançar o comportamento de RF-10/C01 THE SYSTEM SHALL atender ao comportamento: trazer, por padrão, as categorias: **Moradia**, **Custos básicos**, **Alimentação**, **Locomoção**, **Saúde**, **Educação**, **Lazer**, **Investimentos** (aportes tratados como saída do orçamento) e **Doações**. | CA-003 |
| SPEC-055-R04 | WHEN o fluxo de gerir categorias padrão e pessoais alcançar o comportamento de RF-10/C02 THE SYSTEM SHALL atender ao comportamento: criar categorias personalizadas adicionais. | CA-004 |
| SPEC-055-R05 | WHEN o fluxo de gerir categorias padrão e pessoais alcançar o comportamento de RF-10/C03 THE SYSTEM SHALL atender ao comportamento: ocultar/desativar categorias padrão que não usa (sem apagar histórico já lançado nelas). | CA-005 |
| SPEC-055-R06 | WHEN o fluxo de gerir categorias padrão e pessoais alcançar o comportamento de RF-10/C04 THE SYSTEM SHALL atender ao comportamento: cada despesa deve pertencer a exatamente uma categoria. | CA-006 |
| SPEC-055-R07 | WHEN o fluxo de gerir categorias padrão e pessoais alcançar o comportamento de RF-10/C05 THE SYSTEM SHALL atender ao comportamento: cada categoria deve ter uma cor associada, usada de forma consistente em todos os gráficos. | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Cada despesa usa uma categoria; padrão global não é alterado por preferência individual.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-02: Cada despesa pertence a exatamente uma categoria; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Categoria padrão não tem titular individual; personalizada tem um. Cada Despesa usa exatamente uma categoria; ocultação por usuário não elimina histórico.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Gerir categorias padrão e pessoais. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | categoria pessoal, cor e opção de ativação |
| Saída | categorias padrão/pessoais disponíveis e histórico preservado |
| Erro | Categoria de outro titular não é oferecida como personalizada própria. |

Identificadores, filtros e autorizações são verificados no servidor. Contratos publicados: `GET /api/v1/auth/categories` lista o catálogo e as categorias próprias; `POST /api/v1/auth/categories` cria categoria pessoal; `PATCH /api/v1/auth/categories/standard/{category_key}` oculta ou mostra padrão para o titular. Escritas exigem e-mail confirmado. Prefixo HTTP segue /api/v1 e contratos de sessão do ADR-007 não são alterados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Ocultar Lazer para um titular não a oculta para outro e não apaga despesa antiga em Lazer.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Categoria de outro titular não é oferecida como personalizada própria.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-10/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O sistema deve trazer, por padrão, as categorias: **Moradia**, **Custos básicos**, **Alimentação**, **Locomoção**, **Saúde**, **Educação**, **Lazer**, **Investimentos** (aportes tratados como saída do orçamento) e **Doações**.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-10/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder criar categorias personalizadas adicionais.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-10/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O usuário deve poder ocultar/desativar categorias padrão que não usa (sem apagar histórico já lançado nelas).

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-10/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Cada despesa deve pertencer a exatamente uma categoria.

- **CA-007** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-10/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Cada categoria deve ter uma cor associada, usada de forma consistente em todos os gráficos.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-055-R01; CA-001; INV-001, INV-002 | Fixture específica: Ocultar Lazer para um titular não a oculta para outro e não apaga despesa antiga em Lazer. |
| T-002 | SPEC-055-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Categoria de outro titular não é oferecida como personalizada própria. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-055-R03; CA-003 | RF-10/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O sistema deve trazer, por padrão, as categorias: **Moradia**, **Custos básicos**, **Alimentação**, **Locomoção**, **Saúde**, **Educação**, **Lazer**, **Investimentos** (aportes tratados como saída do orçamento) e **Doações**. |
| T-004 | SPEC-055-R04; CA-004 | RF-10/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder criar categorias personalizadas adicionais. |
| T-005 | SPEC-055-R05; CA-005 | RF-10/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O usuário deve poder ocultar/desativar categorias padrão que não usa (sem apagar histórico já lançado nelas). |
| T-006 | SPEC-055-R06; CA-006 | RF-10/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Cada despesa deve pertencer a exatamente uma categoria. |
| T-007 | SPEC-055-R07; CA-007 | RF-10/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Cada categoria deve ter uma cor associada, usada de forma consistente em todos os gráficos. |
| T-008 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes de integração em `backend/tests/test_spec055_categories.py` exercitam catálogo, criação, cor, ocultação, isolamento e duplicidade. A CI é a evidência executada do PostgreSQL e do navegador; OPEN-21 segue para os módulos consumidores de lançamentos.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-21 — decisão necessária: Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais / SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados no recorte técnico.
- [x] Testes da seção 12 implementados, com evidência ligada ao commit/CI.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
