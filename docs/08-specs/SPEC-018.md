# SPEC-018: Excluir conta e dados pessoais

**Estado:** implementação isolada autorizada em 2026-10-28. Exclusão imediata, sessões revogadas, auditoria sem identificação e reaplicação após restauração confirmadas pelo responsável. [Contratos, testes e limites](../09-qualidade/implementacao-SPEC-018.md). Planejamento abaixo preservado como baseline; aprovação histórica e operação não presumidas. Cobertura por cláusula (C-02) concluída em 2026-11-01: cada cláusula `SHALL` é citada por ao menos um teste (`python scripts/verificar-c02.py --estrito`, obrigatório na CI).

## 1. Identificação

- **ID:** SPEC-018
- **Nome:** Excluir conta e dados pessoais
- **Objetivo:** Explicar abrangência e retenções; reautenticar; confirmar; revogar sessões; excluir/anonimizar dados relacionados e de uso em até 15 dias; tratar backups conforme política.
- **Valor entregue:** conta sem novos acessos e exclusão/anonimização rastreável.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-05.
- **RB:** RB-29.
- **RNF:** RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25.
- **Fluxo:** UC-04; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e vínculos pessoais de todos os módulos; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** excluir conta e dados pessoais; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Metas de 15 dias são regra de produto; tratamento legal, compartilhados e auditoria permanece OPEN-05/19, sem interpretação jurídica nova.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-017](SPEC-017.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-05, OPEN-15, OPEN-19, OPEN-29. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Explicar abrangência e retenções.
2. reautenticar.
3. confirmar.
4. revogar sessões.
5. excluir/anonimizar dados relacionados e de uso em até 15 dias.
6. tratar backups conforme política.

**Alternativa observável:** Após confirmação, sessões são recusadas; até 15 dias a conta e dados atingem o estado final definido na política aprovada.

**Exceções:** Senha atual incorreta ou cancelamento não exclui dados; falha parcial não é apresentada como conclusão.

**Pós-condições:** conta sem novos acessos e exclusão/anonimização rastreável; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-018-R01 | WHEN ocorrer o fluxo válido de excluir conta e dados pessoais THE SYSTEM SHALL entregar conta sem novos acessos e exclusão/anonimização rastreável. | CA-001 |
| SPEC-018-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-018-R03 | WHEN o fluxo de excluir conta e dados pessoais alcançar o comportamento de RF-05/C01 THE SYSTEM SHALL atender ao comportamento: permitir ao usuário solicitar a exclusão da conta e de todos os dados pessoais associados. | CA-003 |
| SPEC-018-R04 | WHEN o fluxo de excluir conta e dados pessoais alcançar o comportamento de RF-05/C02 THE SYSTEM SHALL atender ao comportamento: exigir confirmação explícita (reautenticação + confirmação por texto) antes de excluir. | CA-004 |
| SPEC-018-R05 | WHEN o fluxo de excluir conta e dados pessoais alcançar o comportamento de RF-05/C03 THE SYSTEM SHALL atender ao comportamento: excluir ou anonimizar os dados pessoais em até 15 dias corridos após a confirmação, como meta de produto; retenções e tratamento de backups dependem de OPEN-05. | CA-005 |
| SPEC-018-R06 | WHEN o fluxo de excluir conta e dados pessoais alcançar o comportamento de RF-05/C04 THE SYSTEM SHALL atender ao comportamento: antes de confirmar, deve informar ao usuário quais dados serão apagados e se algum dado é retido por obrigação legal. | CA-006 |

## 6. Regras e invariantes

- **INV-001:** Restauração não pode reintroduzir dados excluídos; auditoria não justifica retenção identificável eterna.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario liga dados pessoais de todos os módulos, sessões, tokens e eventos; compartilhamento e auditoria têm retenção própria a conciliar. Excluir não gera entidade financeira compensatória.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Excluir conta e dados pessoais. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | solicitação reautenticada e confirmação por texto |
| Saída | conta sem novos acessos e exclusão/anonimização rastreável |
| Erro | Senha atual incorreta ou cancelamento não exclui dados; falha parcial não é apresentada como conclusão. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-02 (Privacidade / LGPD) | Testar titular A/B, exportação/exclusão aplicável e política aprovada de retenção. |
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
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Após confirmação, sessões são recusadas; até 15 dias a conta e dados atingem o estado final definido na política aprovada.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Senha atual incorreta ou cancelamento não exclui dados; falha parcial não é apresentada como conclusão.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-05/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir ao usuário solicitar a exclusão da conta e de todos os dados pessoais associados.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-05/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve exigir confirmação explícita (reautenticação + confirmação por texto) antes de excluir.

- **CA-005** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-05/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve excluir ou anonimizar os dados pessoais em até 15 dias corridos após a confirmação, como meta de produto; retenções e tratamento de backups dependem de OPEN-05.

- **CA-006** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-05/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Antes de confirmar, deve informar ao usuário quais dados serão apagados e se algum dado é retido por obrigação legal.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-018-R01; CA-001; INV-001, INV-002 | Fixture específica: Após confirmação, sessões são recusadas; até 15 dias a conta e dados atingem o estado final definido na política aprovada. |
| T-002 | SPEC-018-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Senha atual incorreta ou cancelamento não exclui dados; falha parcial não é apresentada como conclusão. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-018-R03; CA-003 | RF-05/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir ao usuário solicitar a exclusão da conta e de todos os dados pessoais associados. |
| T-004 | SPEC-018-R04; CA-004 | RF-05/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve exigir confirmação explícita (reautenticação + confirmação por texto) antes de excluir. |
| T-005 | SPEC-018-R05; CA-005 | RF-05/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve excluir ou anonimizar os dados pessoais em até 15 dias corridos após a confirmação, como meta de produto; retenções e tratamento de backups dependem de OPEN-05. |
| T-006 | SPEC-018-R06; CA-006 | RF-05/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Antes de confirmar, deve informar ao usuário quais dados serão apagados e se algum dado é retido por obrigação legal. |
| T-007 | INV-001, INV-002, INV-003; RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-05 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-19 — decisão necessária: Conciliar inconsistências herdadas: RF-23/RNF-09 versus ADR-003 (cache vencido/referência), RF-35 versus RB-13 (simulado/real), RB-18 (valor/progresso), aliases de entidade, antigos UCs, prazo de token normativo versus proposta e retenção versus auditoria imutável / Specs consumidoras e baseline; registrar alteração aprovada, não escolher silenciosamente.
- OPEN-29 — decisão necessária: Portabilidade/exclusão/arquivos: alcance além de lançamentos, links temporários, expiração/retentativas, titularidade compartilhada e dados de auditoria/backups / SPEC-018, SPEC-019, SPEC-049; complementar OPEN-05.

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

