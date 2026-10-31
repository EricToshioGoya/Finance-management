# SPEC-015: Confirmar posse do e-mail

**Estado:** implementada tecnicamente em 2026-10-23; revisão humana e configuração operacional de entrega pendentes.

## 1. Identificação

- **ID:** SPEC-015
- **Nome:** Confirmar posse do e-mail
- **Objetivo:** Gerar token aleatório e guardar digest/finalidade/validade; enviar ao endereço; impor intervalo de reenvio; verificar token; consumir atomicamente; liberar operações financeiras após confirmação.
- **Valor entregue:** estado pendente/verificado ou erro sem consumo indevido.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-69.
- **RB:** RB-27, RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25.
- **Fluxo:** UC-24; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e token temporário de infraestrutura; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** confirmar posse do e-mail; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** alteração de e-mail, recuperação/troca de senha, módulos financeiros, seleção de provedor/remetente/domínio, fila/outbox e retentativas operacionais.

Cadastro e login continuam aceitando contas pendentes. A migration de confirmação e os endpoints desta unidade existem; módulos financeiros futuros devem exigir e-mail verificado. Provedor e operação permanecem em OPEN-17.

## 4. Dependências

[SPEC-001](SPEC-001.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

OPEN-15 foi concretizada para estes dois contratos e OPEN-19 não altera os prazos normativos de RF-69. OPEN-17 permanece aberto para configuração operacional; não bloqueia o adaptador injetável nem os testes de integração.

## 5. Comportamento esperado

**Pré-condições:** solicitação pública de confirmação ou token recebido; cadastro já existente; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Gerar token aleatório e guardar digest/finalidade/validade.
2. enviar ao endereço.
3. impor intervalo de reenvio.
4. verificar token.
5. consumir atomicamente.
6. liberar operações financeiras após confirmação.

**Alternativa observável:** Token usado uma vez confirma endereço; o mesmo token é recusado na segunda tentativa; reenvio antes de 60s é limitado.

**Exceções:** Token expirado/adulterado/de outro titular ou finalidade não confirma endereço.

**Pós-condições:** estado pendente/verificado ou erro sem consumo indevido; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-015-R01 | WHEN ocorrer o fluxo válido de confirmar posse do e-mail THE SYSTEM SHALL entregar estado pendente/verificado ou erro sem consumo indevido. | CA-001 |
| SPEC-015-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-015-R03 | WHEN o fluxo de confirmar posse do e-mail alcançar o comportamento de RF-69/C01 THE SYSTEM SHALL atender ao comportamento: token aleatório de uso único, armazenado somente como digest; validade de 24h; reenvio com intervalo mínimo de 60s e invalidação do token anterior. Conta pendente pode consultar perfil, reenviar confirmação e sair; operações financeiras exigem e-mail verificado. Cadastro e login atuais ainda não aplicam essa restrição. | CA-003 |

## 6. Regras e invariantes

- **INV-001:** Token é de uso único, válido por 24h; reenvio mínimo 60s invalida o anterior; falha de envio não verifica e-mail.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-27: Cadastro exige nome, e-mail válido e único e senha de pelo menos 8 caracteres. A implementação solicitada adota esse mínimo e equivalência de e-mail sem distinção de caixa conforme ADR-005; OPEN-16 preserva a pendência de revisão formal e origem da aprovação histórica, sem usar a própria Spec como evidência de aprovação. Nunca devolver senha/hash em respostas ou logs; cadastro público cria papel usuário; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario tem endereço e estado pendente/verificado. Token temporário de infraestrutura é associado a titular/finalidade, digest, expiração e consumo; um token não confirma endereço diferente.

A migration `003_email_confirmation` materializa somente o estado de verificação e token temporário desta capacidade. Campos de endereço pendente e relações de alteração de e-mail ficam para SPEC-014; aliases herdados continuam em OPEN-19.

## 8. Impacto arquitetural

Capacidade: Confirmar posse do e-mail. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | solicitação de envio/reenvio e token recebido |
| Saída | estado pendente/verificado ou erro sem consumo indevido |
| Erro | Token expirado/adulterado/de outro titular ou finalidade não confirma endereço. |

Identificadores e autorizações são verificados no servidor. Rotas publicadas: `POST /api/v1/auth/email-confirmation` exige Bearer e devolve 204; `POST /api/v1/auth/email-confirmation/confirm` recebe `{token}` e devolve `{email_verified:true}`. Reenvio precoce devolve 429 com `Retry-After`; token inválido devolve 400 e entrega ausente/falha devolve 503. Prefixo `/api/v1` e contratos de sessão do ADR-007 são preservados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-01 (Segurança) | Inspecionar HTTPS, proteção em repouso e respostas/logs sem segredo; testar negativa de acesso. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-08 (Disponibilidade) | Medir disponibilidade mensal >=99,5% no ambiente operacional aprovado; não inferir de teste unitário. |
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

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Token usado uma vez confirma endereço; o mesmo token é recusado na segunda tentativa; reenvio antes de 60s é limitado.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Token expirado/adulterado/de outro titular ou finalidade não confirma endereço.

- **CA-003** — **Dado** solicitação pública de confirmação ou token recebido; cadastro já existente, entradas válidas e política aprovada de RF-69/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Token aleatório de uso único, armazenado somente como digest; validade de 24h; reenvio com intervalo mínimo de 60s e invalidação do token anterior. Conta pendente pode consultar perfil, reenviar confirmação e sair; operações financeiras exigem e-mail verificado. Cadastro e login atuais ainda não aplicam essa restrição.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-015-R01; CA-001; INV-001, INV-002 | Fixture específica: Token usado uma vez confirma endereço; o mesmo token é recusado na segunda tentativa; reenvio antes de 60s é limitado. |
| T-002 | SPEC-015-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Token expirado/adulterado/de outro titular ou finalidade não confirma endereço. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-015-R03; CA-003 | RF-69/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Token aleatório de uso único, armazenado somente como digest; validade de 24h; reenvio com intervalo mínimo de 60s e invalidação do token anterior. Conta pendente pode consultar perfil, reenviar confirmação e sair; operações financeiras exigem e-mail verificado. Cadastro e login atuais ainda não aplicam essa restrição. |
| T-004 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes foram implementados em `backend/tests/test_spec015_email_confirmation.py`; a CI executa PostgreSQL real e migration. A evidência detalhada está em `../09-qualidade/implementacao-SPEC-015.md`. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-15 — concretizada tecnicamente apenas para as rotas desta Spec; contratos de consumidores financeiros continuam pendentes.
- OPEN-17 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-19 — permanece para inconsistências fora do RF-69; esta implementação aplica os prazos explícitos de 24 h e 60 s, sem alterar os demais conflitos de baseline.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados no recorte técnico.
- [x] Testes da seção 12 implementados e executados pela CI no commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
