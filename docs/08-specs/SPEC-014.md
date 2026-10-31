# SPEC-014: Editar perfil e preferências persistidas

**Estado:** implementação técnica concluída na branch feature/19-perfil-preferencias, aguardando CI e revisão humana. A autorização do usuário cobre este recorte; não comprova aprovação formal histórica do grupo.

## 1. Identificação

- **ID:** SPEC-014
- **Nome:** Editar perfil e preferências persistidas
- **Objetivo:** Consultar perfil; validar nome; se trocar e-mail, reautenticar e usar confirmação; salvar preferências; restaurar em outros acessos.
- **Valor entregue:** perfil próprio atualizado ou e-mail pendente e preferências reaplicadas.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-68, RF-72.
- **RB:** RB-27, RB-29.
- **RNF:** RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-19, RNF-20.
- **Fluxo:** UC-23, UC-27; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Usuario e PreferenciasUsuario; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-05, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** editar perfil e preferências persistidas; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), investimentos reais, Open Finance, push real, app Expo e operação de provedor de e-mail.

Padronizar os aliases PreferenciasUsuario/PreferenciaUsuario em OPEN-19; canais configurados não pressupõem provedores já ativos.

## 4. Dependências

[SPEC-001](SPEC-001.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

O pedido de implementação autorizou os contratos desta unidade. OPEN-15 permanece parcial para consumidores financeiros; OPEN-17 continua aberto para provedor, remetente e operação de e-mail.

## 5. Comportamento esperado

**Pré-condições:** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Consultar perfil.
2. validar nome.
3. se trocar e-mail, reautenticar e usar confirmação.
4. salvar preferências.
5. restaurar em outros acessos.

**Alternativa observável:** Salvar idioma inglês/tema escuro e iniciar nova sessão reaplica as escolhas; e-mail novo só substitui o atual depois de confirmado.

**Exceções:** E-mail duplicado, token de troca inválido ou tentativa de alterar perfil alheio não muda dados válidos.

**Pós-condições:** perfil próprio atualizado ou e-mail pendente e preferências reaplicadas; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-014-R01 | WHEN ocorrer o fluxo válido de editar perfil e preferências persistidas THE SYSTEM SHALL entregar perfil próprio atualizado ou e-mail pendente e preferências reaplicadas. | CA-001 |
| SPEC-014-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-014-R03 | WHEN o titular editar o perfil THE SYSTEM SHALL validar nome, manter e-mail ativo até confirmação do pendente, exigir senha atual para troca e nunca permitir a edição de outro titular. | CA-003 |
| SPEC-014-R04 | WHEN o titular salvar preferências THE SYSTEM SHALL persistir idioma, tema e canais por titular e restaurá-los em nova sessão. | CA-004 |

## 6. Regras e invariantes

- **INV-001:** Troca de e-mail mantém endereço antigo até confirmação; editar perfil não altera papel.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-27: Cadastro exige nome, e-mail válido e único e senha de pelo menos 8 caracteres. A implementação solicitada adota esse mínimo e equivalência de e-mail sem distinção de caixa conforme ADR-005; OPEN-16 preserva a pendência de revisão formal e origem da aprovação histórica, sem usar a própria Spec como evidência de aprovação. Nunca devolver senha/hash em respostas ou logs; cadastro público cria papel usuário; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Um Usuario tem nome/e-mail ativo, e-mail pendente e preferências de idioma/tema/canais. A migration 005_profile_preferences materializa e-mail pendente cifrado, lookup HMAC e PreferenciasUsuario. E-mail só é promovido de pendente após confirmação; papel não é campo editável.

O [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md) mantém a origem das entidades. Não impor modelo físico ou migration nesta revisão. Campos/aliases e relações ainda ausentes são decisões de OPEN-15/19 e das OPEN locais.

## 8. Impacto arquitetural

Capacidade: Editar perfil e preferências persistidas. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-005, ADR-007. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | nome, novo e-mail, reautenticação, idioma/tema/canais |
| Saída | perfil próprio atualizado ou e-mail pendente e preferências reaplicadas |
| Erro | E-mail duplicado, token de troca inválido ou tentativa de alterar perfil alheio não muda dados válidos. |

Identificadores, filtros e autorizações são verificados no servidor. GET /api/v1/auth/profile devolve perfil próprio, e-mail pendente e preferências; PATCH /profile altera nome e inicia troca de e-mail; PATCH /profile/preferences salva idioma, tema e canais. PATCH de e-mail exige current_password, entrega token por adaptador e promove o novo endereço somente na confirmação. As rotas usam prefixo /api/v1, HTTPS, origem válida, JWT e limite de endpoint sensível.

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
| RNF-19 (Personalização visual) | Alternar tema claro/escuro, persistir por titular e restaurar em outra sessão. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Salvar idioma inglês/tema escuro e iniciar nova sessão reaplica as escolhas; e-mail novo só substitui o atual depois de confirmado.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: E-mail duplicado, token de troca inválido ou tentativa de alterar perfil alheio não muda dados válidos.

- **CA-003** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-68/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Nome obrigatório; e-mail único inclusive sob concorrência; impedir edição de outro titular; informar erro sem perder dados válidos.

- **CA-004** — **Dado** titular autenticado; para operações financeiras, e-mail verificado conforme RF-69, entradas válidas e política aprovada de RF-72/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Português/inglês; tema claro/escuro; in-app preservado e push/e-mail opcionais; dados isolados por titular; respeitar RNF-19, RNF-20 e RF-49. Seleção local de idioma atual não equivale à persistência por usuário.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-014-R01; CA-001; INV-001, INV-002 | Teste salva nome e preferências e confirma restauração em sessão posterior. |
| T-002 | SPEC-014-R02; CA-002; INV-001, INV-002, INV-003 | Teste cobre senha atual inválida, e-mail duplicado, falha de entrega e entrada inválida sem alterar dados válidos. |
| T-003 | SPEC-014-R03; CA-003 | Teste confirma que e-mail pendente mantém o anterior até o token de troca ser consumido. |
| T-004 | SPEC-014-R04; CA-004 | Teste isola preferências de titulares distintos e persiste idioma/tema/canais. |
| T-005 | INV-001, INV-002, INV-003; RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-19, RNF-20 | PostgreSQL real, migration, lint/build e navegador são executados na CI; operação de produção continua em OPEN-17/32. |

Testes de API foram implementados em backend/tests/test_spec014_profile_preferences.py. A evidência e limites operacionais estão em ../09-qualidade/implementacao-SPEC-014.md.

## 13. Questões em Aberto

- OPEN-15 — parcial: contratos de autenticação e perfil estão explicitados; consumidores financeiros seguem pendentes.
- OPEN-17 — adaptador HTTPS permanece configurável e falha fechado; provedor, remetente, domínio, fila e operação continuam abertos.
- OPEN-32 — disponibilidade, backup/restore, monitoramento e revisão manual WCAG não são demonstrados por esta implementação.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados no recorte técnico.
- [x] Testes da seção 12 implementados; executar e registrar CI no commit.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
