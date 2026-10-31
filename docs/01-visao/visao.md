# Visão do Projeto — FinNova

Plataforma **web e mobile** que unifica **controle financeiro pessoal** e **simulação de investimentos** em um só lugar. Diferente de apps que tratam essas duas frentes separadamente, o sistema conecta o controle de gastos à decisão de investir: mostra quanto sobra no orçamento e simula o que esse valor pode render, adaptando a experiência ao nível de conhecimento do usuário (iniciante ou avançado) por meio de um quiz de perfil de investidor.

- **Status:** rascunho
- **Versão do documento:** 0.6
- **Última atualização:** 2026-10-18

Detalhamento completo dos requisitos em `/docs/03-requisitos/requisitos.md`, das personas em `/docs/02-personas/personas.md` e do benchmark em `/docs/01-visao/benchmark.md`.

---

## 1. Problema e contexto

**Problema.** Pessoas físicas no Brasil costumam controlar gastos e investimentos em ferramentas separadas: aplicativos de orçamento, corretoras e planilhas. Como consequência:

- O usuário iniciante sabe, no máximo, quanto gastou, mas não sabe quanto sobra nem o que fazer com a sobra; por insegurança e falta de familiaridade com os termos, permanece na poupança.
- O usuário avançado mantém dados dispersos entre corretoras e planilhas, perde tempo para consolidá-los e não consegue comparar cenários de investimento em um só lugar.

**Contexto.** As soluções existentes atendem metade do problema: aplicativos de controle financeiro (ex.: Mobills, Organizze) tratam o orçamento, enquanto consolidadores (ex.: Kinvo, Gorila) atendem quem já investe. Nenhuma das soluções analisadas conecta a sobra do orçamento à simulação do investimento com taxas oficiais (Selic, CDI, IPCA). A análise completa está em `/docs/01-visao/benchmark.md`.

**Público-alvo.** Investidores iniciantes e avançados, pessoas físicas, descritos em `/docs/02-personas/personas.md`.

**Categoria do tema.** O FinNova se enquadra principalmente como **sistema de apoio à decisão** (simula cenários para o usuário decidir, sem aconselhar) e, de forma secundária, como **sistema de acompanhamento de progresso** (metas, patrimônio e score de saúde financeira).

## 2. Escopo

> **Recorte de entrega da disciplina:** para a apresentação do projeto (26/11/2026), o compromisso de entrega é o conjunto **Must have** do backlog priorizado (seção 4): RF-01, RF-02, RF-06 a RF-12, RF-20 a RF-23 e RF-25. Os demais módulos permanecem no backlog e só entram após a conclusão desse recorte.

**Catálogo do produto e backlog candidato ao MVP**

O núcleo Must have está na tabela priorizada; os itens Should/Could abaixo representam evolução e não promessa de implementar todas as abas no semestre. OPEN-08 registra a aprovação do recorte final. As prioridades existentes foram preservadas.

- Módulo de **Conta e Acesso** (cadastro, login, quiz de perfil de investidor).
- Módulo de **Administração Financeira** (renda, gastos, categorias, contas/cartões, metas, dashboards).
- Módulo de **Simulador de Investimentos** (renda fixa, renda variável, comparador, metas).
- Módulo de **Relatórios de Empresas** (busca de empresas listadas, watchlist, indicadores extraídos de dados abertos da CVM, e link direto para os documentos oficiais).
- Módulo de **Patrimônio** (consolidação de ativos e passivos, evolução do patrimônio líquido, mapa de calor visual e alocação da carteira).
- Módulo de **Score de Saúde Financeira** (nota única que resume a saúde financeira do usuário).
- Módulo de **Conteúdo Educacional** (explicações e ajuda contextual sobre termos financeiros).
- Módulo de **Simulador de Compras Financiadas** (financiar vs. investir e comprar depois).
- Recursos transversais de **Notificações/Alertas** e **Exportação de Dados**, usados pelos demais módulos.
- Módulo de **Painel Administrativo** (visível apenas a usuários com papel de administrador): informações dos usuários, distribuição por perfil de investidor e uso por módulo/aba.
- Extensão de **Contas Compartilhadas** (casal/família) dentro de Administração Financeira: vínculo entre dois usuários e divisão de despesas.
- Módulo de **Simulador de Aposentadoria e Previdência**: projeção de aposentadoria e comparador PGBL x VGBL x carteira própria.
- Módulo de **Calculadora de Imposto de Renda sobre Investimentos**: estimativa de IR e exportação de informe de rendimentos.
- Extensão de **Benchmark anônimo** dentro de Score de Saúde Financeira.
- Módulo de **Gamificação e Conquistas** (badges por metas atingidas).
- Clientes **web** e **mobile** consumindo o mesmo backend.
- Arquitetura modular preparada para receber novos módulos (novas abas a serem detalhadas).
- Cada módulo listado acima (Conta e Acesso, Administração Financeira, Simulador de Investimentos, Relatórios de Empresas, Patrimônio, Score de Saúde Financeira, Conteúdo Educacional, Compras Financiadas) é uma aba/tela independente na navegação principal — nenhuma é sub-item da outra. A conexão entre módulos é de dados (ex.: saldo disponível usado em RF-26, ativos/passivos consolidados em RF-35), não de hierarquia de UI.

**Fora do escopo (MVP)**

- Integração com Open Finance / sincronização automática com bancos e corretoras.
- Execução de ordens ou qualquer operação real de investimento.
- Recomendação personalizada de investimentos (o sistema simula, não aconselha).

## 3. Stack e Restrições Técnicas

A stack e as restrições técnicas ficam no documento de arquitetura (`/docs/07-arquitetura/arquitetura.md`, seção 5), fonte única das escolhas de tecnologia. Restrição principal: backend único atendendo web e mobile pela mesma API REST.

## 4. Roadmap / Entregas

Ordem sugerida: núcleo funcional primeiro (conta + lançamentos + simulações básicas), depois personalização, metas e análise visual.

- [ ] **Etapa 1 — Conta e Acesso:** RF-01, RF-02
- [ ] **Etapa 2 — Administração Financeira essencial:** RF-06, RF-07, RF-08, RF-09, RF-10, RF-11, RF-12
- [ ] **Etapa 3 — Simulador essencial:** RF-22, RF-23, RF-20, RF-21, RF-25, RF-24
- [ ] **Etapa 4 — Perfil de investidor:** RF-03
- [ ] **Etapa 5 — Administração Financeira análise:** RF-13, RF-16, RF-17, RF-18
- [ ] **Etapa 6 — Metas:** RF-14, RF-15, RF-19, RF-26
- [ ] **Etapa 7 — Relatórios de Empresas:** RF-29, RF-30, RF-31, RF-33, RF-32
- [ ] **Etapa 8 — Patrimônio:** RF-35, RF-37, RF-36, RF-38
- [ ] **Etapa 9 — Score de Saúde Financeira:** RF-41, RF-42
- [ ] **Etapa 10 — Compras Financiadas:** RF-45, RF-46, RF-47
- [ ] **Etapa 11 — Recursos transversais:** RF-48, RF-50, RF-49
- [ ] **Etapa 12 — Conteúdo Educacional e watchlist:** RF-43, RF-44, RF-34, RF-27
- [ ] **Etapa 13 — Onboarding e exclusão de conta:** RF-04, RF-05
- [ ] **Etapa 14 — Moeda estrangeira e stress test:** RF-28, RF-39
- [ ] **Etapa 15 — Metas nomeadas e relatório automático:** RF-40, RF-51
- [ ] **Etapa 16 — API pública e webhooks:** RF-52, RF-53
- [ ] **Etapa 17 — Painel Administrativo:** RF-54, RF-59, RF-55, RF-56, RF-57, RF-58
- [ ] **Etapa 18 — Contas Compartilhadas:** RF-60, RF-61
- [ ] **Etapa 19 — Aposentadoria, Previdência e Impostos:** RF-62, RF-63, RF-64, RF-65
- [ ] **Etapa 20 — Benchmark e Gamificação:** RF-66, RF-67
- [ ] **Etapa 21+ — Novas abas** (a detalhar em próximas atualizações deste documento)

> Dark mode (RNF-19) e internacionalização (RNF-20) são requisitos transversais de front-end — não entram como etapa isolada; devem ser considerados desde a estrutura inicial do cliente web/mobile para evitar retrabalho.

### Backlog priorizado (MoSCoW)

| Prioridade | Épico | RFs |
|---|---|---|
| Must have | Conta e Acesso | RF-01, RF-02 |
| Must have | Administração Financeira — essencial | RF-06, RF-07, RF-08, RF-09, RF-10, RF-11, RF-12 |
| Must have | Simulador — essencial | RF-20, RF-21, RF-25, RF-22, RF-23 |
| Should have | Perfil de investidor | RF-03 |
| Should have | Administração Financeira — metas e análise | RF-13, RF-14, RF-15, RF-16, RF-17, RF-18, RF-19 |
| Should have | Simulador — planejamento e cotações | RF-26, RF-24 |
| Should have | Relatórios de Empresas — busca e acesso | RF-29, RF-30, RF-31, RF-33 |
| Should have | Patrimônio — consolidação e mapa de calor | RF-35, RF-37 |
| Should have | Score de Saúde Financeira | RF-41, RF-42 |
| Should have | Recursos transversais — essencial | RF-48, RF-50 |
| Could have | Relatórios de Empresas — indicadores e watchlist | RF-32, RF-34 |
| Could have | Patrimônio — evolução e alocação | RF-36, RF-38 |
| Could have | Simulador — métricas de risco | RF-27 |
| Could have | Compras Financiadas | RF-45, RF-46, RF-47 |
| Could have | Conteúdo Educacional e canal de notificação estendido | RF-43, RF-44, RF-49 |
| Should have | Conta e Acesso — onboarding e exclusão | RF-04, RF-05 |
| Could have | Simulador — moeda estrangeira | RF-28 |
| Could have | Patrimônio — stress test e metas nomeadas | RF-39, RF-40 |
| Could have | Recursos transversais — relatório automático | RF-51 |
| Could have | Recursos transversais — API pública e webhooks | RF-52, RF-53 |
| Should have | Painel Administrativo — acesso, listagem e coleta | RF-54, RF-55, RF-59 |
| Could have | Painel Administrativo — dashboards | RF-56, RF-57, RF-58 |
| Could have | Contas Compartilhadas | RF-60, RF-61 |
| Could have | Aposentadoria e Previdência | RF-62, RF-63 |
| Could have | Impostos | RF-64, RF-65 |
| Could have | Score de Saúde Financeira — benchmark anônimo | RF-66 |
| Could have | Gamificação | RF-67 |


## 4. Situação das decisões

ADRs existentes registram monólito em camadas, motor isolado, cache de indicadores e indexação CVM. [Arquitetura](../07-arquitetura/arquitetura.md) organiza drivers e responsabilidades. Parâmetros ainda não decididos permanecem em [OPEN](../08-specs/questoes-abertas.md).

Framework e bibliotecas listados são escolhas documentadas, não dependências instaladas. Serviço de deploy, notificações e provedor de cotações mantêm alternativas explícitas. Sem aplicação implementada, não há resultado validado de desempenho, segurança ou disponibilidade.

Benchmark de produtos existentes está pendente (OPEN-14). Não foi substituído por RF-66, que compara usuários da própria plataforma.


## Ciclo de vida da conta e recorte atualizado

O produto deve permitir manter identidade e preferências, confirmar a posse do e-mail, recuperar/alterar senha e encerrar sessões (RF-68 a RF-74). Esses recursos completam Conta e Acesso e antecedem a liberação de dados financeiros para contas não verificadas. O usuário pode acessar a manutenção da conta pendente para concluir a confirmação.

A main consolidada possui somente a implementação inicial de autenticação; funcionalidades financeiras, perfil/quiz e administração seguem planejadas. Exclusão/exportação (RF-05/RF-50), backups/restauração (RNF-14), observabilidade e permissões continuam critérios de entrega próprios, sem alegação de produção pronta.

## Ciclo de vida da conta

O produto inclui cadastro, confirmação e troca de e-mail, login, logout/expiração, recuperação e alteração de senha, edição de nome e preferências de idioma/tema/notificações (RF-68 a RF-73), além de exclusão e exportação (RF-05 e RF-50). As funções financeiras permanecem o núcleo de negócio e dependem de persistência e isolamento por titular. Implementação disponível e pendências estão na [matriz de cobertura](../09-qualidade/cobertura-funcional.md); esta ampliação documental não implementa essas capacidades.
