# SPEC-016: Recuperar e alterar senha com revogação

**Estado:** implementação técnica concluída em 2026-10-25; aprovação formal humana continua pendente.

## 1. Identificação

- **ID:** SPEC-016
- **Nome:** Recuperar e alterar senha com revogação
- **Objetivo:** Responder genericamente à solicitação; enviar link apenas ao endereço cadastrado; validar token de 30min ou senha atual; validar nova senha; alterar hash e revogar todas as sessões.
- **Valor entregue:** senha protegida atualizada e sessões revogadas.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-70, RF-71.
- **RB:** RB-27, RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25.
- **Fluxo:** UC-25, UC-26; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e tokens/sessões de infraestrutura; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** recuperar e alterar senha com revogação; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Algoritmo e política de senha seguem ADR-007/RB-27; serviço transacional e migração de contas seguem OPEN-17.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-015](SPEC-015.md), [SPEC-017](SPEC-017.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-15, OPEN-17, OPEN-19. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** recuperação é pública por token; troca autenticada exige sessão e senha atual; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Responder genericamente à solicitação.
2. enviar link apenas ao endereço cadastrado.
3. validar token de 30min ou senha atual.
4. validar nova senha.
5. alterar hash e revogar todas as sessões.

**Alternativa observável:** Após recuperação válida, login com nova senha funciona e sessões antigas são recusadas; endereço inexistente recebe a mesma resposta pública.

**Exceções:** Token reutilizado/expirado ou senha atual incorreta não altera hash nem encerra sessões de terceiros.

**Pós-condições:** senha protegida atualizada e sessões revogadas; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-016-R01 | WHEN ocorrer o fluxo válido de recuperar e alterar senha com revogação THE SYSTEM SHALL entregar senha protegida atualizada e sessões revogadas. | CA-001 |
| SPEC-016-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-016-R03 | WHEN o fluxo de recuperar e alterar senha com revogação alcançar o comportamento de RF-70/C01 THE SYSTEM SHALL atender ao comportamento: token de uso único com validade de 30 minutos; digest no banco; nunca enviar senha; limitar pedidos e tentativas; token expirado/reutilizado não altera senha. | CA-003 |
| SPEC-016-R04 | WHEN o fluxo de recuperar e alterar senha com revogação alcançar o comportamento de RF-71/C01 THE SYSTEM SHALL atender ao comportamento: reautenticação obrigatória; nova senha segue RB-27; senha incorreta não altera credenciais; nunca retornar ou registrar senha ou token. | CA-004 |

## 6. Regras e invariantes

- **INV-001:** Nenhuma senha ou token bruto aparece em logs/respostas; consumo, hash e revogação não podem concluir parcialmente.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-27: Cadastro exige nome, e-mail válido e único e senha de pelo menos 8 caracteres. A implementação solicitada adota esse mínimo e equivalência de e-mail sem distinção de caixa conforme ADR-005; OPEN-16 preserva a pendência de revisão formal e origem da aprovação histórica, sem usar a própria Spec como evidência de aprovação. Nunca devolver senha/hash em respostas ou logs; cadastro público cria papel usuário; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Usuario mantém hash de senha; token de recuperação tem titular/finalidade/digest/expiração/consumo em infraestrutura. Sessões do titular são revogadas ao trocar credencial.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Recuperar e alterar senha com revogação. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-006, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | e-mail para recuperação; token e nova senha; ou sessão, senha atual e nova |
| Saída | senha protegida atualizada e sessões revogadas |
| Erro | Token reutilizado/expirado ou senha atual incorreta não altera hash nem encerra sessões de terceiros. |

Identificadores, filtros e autorizações são verificados no servidor. Contratos publicados: `POST /api/v1/auth/password-recovery` recebe e-mail e sempre retorna 204; `POST /api/v1/auth/password-recovery/confirm` recebe token e `new_password`; `PATCH /api/v1/auth/password` exige Bearer, `current_password` e `new_password`. Token inválido, expirado ou reutilizado retorna `invalid_password_reset_token` sem alteração parcial. Contratos de sessão existentes do ADR-007 não são alterados por esta Spec.

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
| RNF-25 (Consistência temporal) | Testar instantes UTC e competência America/Sao_Paulo nas fronteiras de mês; datas sem hora seguem ADR-006. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Após recuperação válida, login com nova senha funciona e sessões antigas são recusadas; endereço inexistente recebe a mesma resposta pública.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Token reutilizado/expirado ou senha atual incorreta não altera hash nem encerra sessões de terceiros.

- **CA-003** — **Dado** recuperação é pública por token; troca autenticada exige sessão e senha atual, entradas válidas e política aprovada de RF-70/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Token de uso único com validade de 30 minutos; digest no banco; nunca enviar senha; limitar pedidos e tentativas; token expirado/reutilizado não altera senha.

- **CA-004** — **Dado** recuperação é pública por token; troca autenticada exige sessão e senha atual, entradas válidas e política aprovada de RF-71/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Reautenticação obrigatória; nova senha segue RB-27; senha incorreta não altera credenciais; nunca retornar ou registrar senha ou token.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-016-R01; CA-001; INV-001, INV-002 | Fixture específica: Após recuperação válida, login com nova senha funciona e sessões antigas são recusadas; endereço inexistente recebe a mesma resposta pública. |
| T-002 | SPEC-016-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Token reutilizado/expirado ou senha atual incorreta não altera hash nem encerra sessões de terceiros. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-016-R03; CA-003 | RF-70/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Token de uso único com validade de 30 minutos; digest no banco; nunca enviar senha; limitar pedidos e tentativas; token expirado/reutilizado não altera senha. |
| T-004 | SPEC-016-R04; CA-004 | RF-71/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Reautenticação obrigatória; nova senha segue RB-27; senha incorreta não altera credenciais; nunca retornar ou registrar senha ou token. |
| T-005 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes de integração em `backend/tests/test_spec016_password_recovery.py` exercitam recuperação, token expirado e troca autenticada. A CI é a evidência executada do PostgreSQL e do navegador; os exemplos não fecham decisões OPEN ainda pendentes.

## 13. Questões em Aberto

- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-17 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-19 — decisão necessária: Conciliar inconsistências herdadas: RF-23/RNF-09 versus ADR-003 (cache vencido/referência), RF-35 versus RB-13 (simulado/real), RB-18 (valor/progresso), aliases de entidade, antigos UCs, prazo de token normativo versus proposta e retenção versus auditoria imutável / Specs consumidoras e baseline; registrar alteração aprovada, não escolher silenciosamente.

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
