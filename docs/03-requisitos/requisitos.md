# Requisitos — FinNova

**Convenção de identificadores:** `RF-01`, `RF-02`... (Requisitos Funcionais — o que o sistema faz), `RNF-01`, `RNF-02`... (Requisitos Não Funcionais — como o sistema se comporta) e `RB-01`, `RB-02`... (Regras de Negócio — políticas e restrições do domínio), numerados sequencialmente na ordem em que aparecem no documento. Cada RF e RNF traz, além dos critérios de aceite detalhados, um **enunciado em sintaxe EARS** (*Easy Approach to Requirements Syntax*) como definição objetiva e testável do comportamento esperado. A tabela da seção 1.1 indica a qual módulo/aba cada RF pertence.

**Padrões EARS adotados:** Ubiquitous (sem gatilho — vale sempre), Event-driven (`WHEN` — evento pontual), State-driven (`WHILE` — estado que persiste durante um intervalo), Unwanted behavior (`IF ... THEN` — condição indesejada, erro ou falha) e Optional feature (`WHERE` — recurso ou configuração presente). Um mesmo requisito pode ter mais de uma cláusula EARS. As Regras de Negócio permanecem em forma declarativa (invariantes do domínio), com indicação do RF que as aplica.

**Convenção de obrigação:** `SHALL` = obrigatório (o não atendimento reprova a aceitação); `SHOULD` = recomendado (desejável, não bloqueia a entrega); `MAY` = opcional (fica a critério da equipe). Nos RF, a obrigação acompanha a prioridade MoSCoW da tabela 1.1: Must have → `SHALL`, Should have → `SHOULD`, Could have → `MAY`. **Exceção:** RF que materializa obrigação legal ou restrição já exigida por um RNF mantém `SHALL` independentemente da prioridade (RF-05 e RF-50 — LGPD/RNF-02; RF-33 — RNF-10; RF-54 — RNF-21). Os RNF usam `SHALL`, por definirem limites de qualidade verificáveis; a coluna Prioridade da seção 2 indica em que entrega cada RNF passa a valer.

---

## 1. Requisitos Funcionais (RF)

*Descrevem o que o sistema faz. IDs sequenciais na ordem em que aparecem no documento; a coluna Módulo indica a aba a que cada RF pertence.*

### 1.1 Visão geral por módulo

| ID | Módulo | Requisito | Prioridade | Status |
|---|---|---|---|---|
| RF-01 | Conta e Acesso | Cadastro de usuário | Must have | ☐ |
| RF-02 | Conta e Acesso | Login e autenticação | Must have | ☐ |
| RF-03 | Conta e Acesso | Quiz de perfil de investidor | Should have | ☐ |
| RF-04 | Conta e Acesso | Onboarding guiado | Should have | ☐ |
| RF-05 | Conta e Acesso | Exclusão de conta e dados | Should have | ☐ |
| RF-06 | Administração Financeira | Cadastro de renda fixa mensal | Must have | ☐ |
| RF-07 | Administração Financeira | Cadastro de renda variável | Must have | ☐ |
| RF-08 | Administração Financeira | Cadastro de bônus e PLR | Must have | ☐ |
| RF-09 | Administração Financeira | Cadastro de despesas por categoria | Must have | ☐ |
| RF-10 | Administração Financeira | Categorias padrão e personalizadas de gastos | Must have | ☐ |
| RF-11 | Administração Financeira | Edição e exclusão de lançamentos | Must have | ☐ |
| RF-12 | Administração Financeira | Cadastro de contas bancárias e cartões de crédito | Must have | ☐ |
| RF-13 | Administração Financeira | Controle de fatura de cartão de crédito | Should have | ☐ |
| RF-14 | Administração Financeira | Meta geral de renda e de gasto | Should have | ☐ |
| RF-15 | Administração Financeira | Meta de gasto por categoria | Should have | ☐ |
| RF-16 | Administração Financeira | Dashboard — gastos por categoria (pizza) | Should have | ☐ |
| RF-17 | Administração Financeira | Dashboard — evolução de saldo (linha) | Should have | ☐ |
| RF-18 | Administração Financeira | Dashboard — comparativo renda vs. gasto mensal (barras) | Should have | ☐ |
| RF-19 | Administração Financeira | Dashboard — progresso de metas | Should have | ☐ |
| RF-20 | Simulador de Investimentos | Simulação de investimento em renda fixa | Must have | ☐ |
| RF-21 | Simulador de Investimentos | Simulação de investimento em renda variável | Must have | ☐ |
| RF-25 | Simulador de Investimentos | Comparador de cenários de investimento | Must have | ☐ |
| RF-26 | Simulador de Investimentos | Projeção de objetivo financeiro | Should have | ☐ |
| RF-22 | Simulador de Investimentos | Calculadora de juros compostos (motor genérico) | Must have | ☐ |
| RF-23 | Simulador de Investimentos | Integração com indicadores oficiais (Selic, CDI, IPCA, Tesouro Direto) | Must have | ☐ |
| RF-24 | Simulador de Investimentos | Cotação de ações e FIIs via fonte de mercado | Should have | ☐ |
| RF-27 | Simulador de Investimentos | Métricas de risco e retorno (volatilidade, Sharpe simplificado) | Could have | ☐ |
| RF-28 | Simulador de Investimentos | Simulação em moeda estrangeira (câmbio) | Could have | ☐ |
| RF-29 | Relatórios de Empresas | Busca de empresa (ticker, CNPJ ou razão social) | Should have | ☐ |
| RF-30 | Relatórios de Empresas | Listagem de documentos oficiais (metadados) | Should have | ☐ |
| RF-31 | Relatórios de Empresas | Acesso ao documento completo via link externo | Should have | ☐ |
| RF-32 | Relatórios de Empresas | Indicadores financeiros extraídos de dados abertos da CVM | Could have | ☐ |
| RF-33 | Relatórios de Empresas | Retenção e expurgo automático dos dados sincronizados (12 meses) | Should have | ☐ |
| RF-34 | Relatórios de Empresas | Watchlist de empresas | Could have | ☐ |
| RF-35 | Patrimônio | Consolidação de patrimônio (ativos e passivos) | Should have | ☐ |
| RF-36 | Patrimônio | Evolução do patrimônio líquido | Could have | ☐ |
| RF-37 | Patrimônio | Mapa de calor patrimonial (ativos em verde, passivos em cores quentes) | Should have | ☐ |
| RF-38 | Patrimônio | Alocação da carteira por classe de ativo | Could have | ☐ |
| RF-39 | Patrimônio | Simulação de stress financeiro (perda de renda) | Could have | ☐ |
| RF-40 | Patrimônio | Metas nomeadas (objetivos financeiros) | Could have | ☐ |
| RF-41 | Score de Saúde Financeira | Cálculo do score de saúde financeira | Should have | ☐ |
| RF-42 | Score de Saúde Financeira | Exibição e histórico do score | Could have | ☐ |
| RF-43 | Conteúdo Educacional | Central de conteúdo educacional | Could have | ☐ |
| RF-44 | Conteúdo Educacional | Ajuda contextual (tooltips educativos) | Could have | ☐ |
| RF-45 | Compras Financiadas | Simulação de compra financiada | Could have | ☐ |
| RF-46 | Compras Financiadas | Comparador: financiar vs. investir e comprar depois | Could have | ☐ |
| RF-47 | Compras Financiadas | Registro do financiamento como passivo | Could have | ☐ |
| RF-48 | Notificações | Notificações e alertas | Should have | ☐ |
| RF-49 | Notificações | Canal de envio (in-app, push, e-mail) | Could have | ☐ |
| RF-50 | Exportação de Dados | Exportação de dados pessoais (CSV/PDF) | Should have | ☐ |
| RF-51 | Notificações | Relatório mensal automático | Could have | ☐ |
| RF-52 | API Pública | API pública documentada | Could have | ☐ |
| RF-53 | API Pública | Webhooks para eventos do usuário | Could have | ☐ |
| RF-54 | Painel Administrativo | Controle de acesso administrativo | Should have | ☐ |
| RF-55 | Painel Administrativo | Listagem e busca de usuários | Should have | ☐ |
| RF-56 | Painel Administrativo | Dashboard: distribuição de perfil de investidor | Could have | ☐ |
| RF-57 | Painel Administrativo | Dashboard: uso por módulo/aba | Could have | ☐ |
| RF-58 | Painel Administrativo | Dashboard: usuários mais recorrentes (engajamento) | Could have | ☐ |
| RF-59 | Painel Administrativo | Registro de eventos de uso | Should have | ☐ |
| RF-60 | Contas Compartilhadas | Vínculo de conta compartilhada entre dois usuários | Could have | ☐ |
| RF-61 | Contas Compartilhadas | Divisão de despesas compartilhadas | Could have | ☐ |
| RF-62 | Aposentadoria e Previdência | Simulação de aposentadoria | Could have | ☐ |
| RF-63 | Aposentadoria e Previdência | Comparador de modalidades de previdência (PGBL x VGBL x carteira própria) | Could have | ☐ |
| RF-64 | Impostos | Estimativa de IR devido sobre operações simuladas | Could have | ☐ |
| RF-65 | Impostos | Exportação de informe de rendimentos consolidado | Could have | ☐ |
| RF-66 | Score de Saúde Financeira | Benchmark anônimo com usuários do mesmo perfil | Could have | ☐ |
| RF-67 | Gamificação | Badges/conquistas por metas atingidas | Could have | ☐ |

---

### 1.2 Módulo — Conta e Acesso

#### RF-01 — Cadastro de usuário

**Enunciado EARS:**

- Event-driven. WHEN o usuário envia o formulário de cadastro com nome, e-mail e senha válidos THE SYSTEM SHALL criar a conta e armazenar a senha com hash.
- Unwanted behavior. IF o e-mail informado tiver formato inválido ou já estiver cadastrado THEN THE SYSTEM SHALL recusar o cadastro e exibir mensagem de erro indicando o campo inválido.

**Critérios de aceite:**

- [ ] Deve exigir nome, e-mail e senha.
- [ ] Deve validar formato de e-mail e impedir e-mail duplicado.
- [ ] Senha deve ser armazenada de forma criptografada (hash).

#### RF-02 — Login e autenticação

**Enunciado EARS:**

- Event-driven. WHEN o usuário submete e-mail e senha corretos THE SYSTEM SHALL iniciar a sessão e retornar um token de sessão.
- State-driven. WHILE a sessão do usuário estiver ativa (token válido e não expirado) THE SYSTEM SHALL permitir o acesso às funcionalidades autenticadas sem nova solicitação de credenciais.
- Unwanted behavior. IF as credenciais forem inválidas THEN THE SYSTEM SHALL recusar o acesso e exibir mensagem de erro genérica, sem indicar qual campo falhou.
- Unwanted behavior. IF ocorrerem 5 tentativas de login inválidas consecutivas para a mesma conta THEN THE SYSTEM SHALL bloquear novas tentativas dessa conta por 15 minutos.

**Critérios de aceite:**

- [ ] Deve autenticar por e-mail e senha.
- [ ] Deve bloquear novas tentativas por 15 minutos após 5 tentativas inválidas consecutivas para a mesma conta (padrão de mercado); o contador é zerado após um login bem-sucedido.
- [ ] Deve manter sessão ativa até logout ou expiração do token.

#### RF-03 — Quiz de perfil de investidor

**Enunciado EARS:** Event-driven. WHEN o usuário conclui o quiz de perfil de investidor THE SYSTEM SHOULD classificar e salvar seu perfil de investidor.

**Critérios de aceite:**

- [ ] O sistema deve apresentar um conjunto de perguntas sobre conhecimento e tolerância a risco.
- [ ] Ao final, deve classificar o usuário (ex.: iniciante/avançado ou conservador/moderado/arrojado).
- [ ] O resultado deve ficar salvo no perfil e influenciar a experiência exibida no simulador.
- [ ] O usuário deve poder refazer o quiz quando quiser.

#### RF-04 — Onboarding guiado

**Enunciado EARS:** Event-driven. WHEN o usuário realiza o primeiro login THE SYSTEM SHOULD exibir o tour guiado de introdução ao sistema.

**Critérios de aceite:**

- [ ] No primeiro login, deve apresentar um tour guiado cobrindo, no mínimo: cadastro da primeira renda, cadastro da primeira despesa, e como acessar o quiz de perfil (RF-03) e o simulador.
- [ ] Deve permitir pular o tour a qualquer momento.
- [ ] Deve poder ser reaberto manualmente pelo usuário depois (ex.: menu de ajuda).
- [ ] O conteúdo sugerido deve se adaptar ao perfil: iniciante recebe um tour mais didático; avançado pode pular direto para funcionalidades avançadas.

#### RF-05 — Exclusão de conta e dados (direito ao esquecimento)

**Enunciado EARS:** Event-driven. WHEN o usuário confirma a exclusão da conta, reautenticado, THE SYSTEM SHALL excluir ou anonimizar seus dados pessoais em até 15 dias corridos.

**Critérios de aceite:**

- [ ] Deve permitir ao usuário solicitar a exclusão da conta e de todos os dados pessoais associados.
- [ ] Deve exigir confirmação explícita (reautenticação + confirmação por texto) antes de excluir.
- [ ] Deve excluir ou anonimizar os dados pessoais em até 15 dias corridos após a confirmação (padrão de mercado, alinhado ao prazo de 15 dias para atendimento ao titular do art. 19, II, da LGPD).
- [ ] Antes de confirmar, deve informar ao usuário quais dados serão apagados e se algum dado é retido por obrigação legal.

---

### 1.3 Módulo — Administração Financeira

> Aba independente na navegação principal (não é sub-aba do Simulador).

Reúne o registro de todas as fontes de renda e de gastos do usuário, organizados por categoria, com definição de metas e visualização em gráficos dinâmicos.

#### RF-06 — Cadastro de renda fixa mensal

**Descrição:** salário ou renda fixa recorrente do usuário.

**Enunciado EARS:**

- Event-driven. WHEN o usuário cadastra uma renda fixa mensal THE SYSTEM SHALL considerá-la automaticamente no cálculo de saldo do mês corrente e dos meses seguintes.
- Unwanted behavior. IF o valor informado for menor ou igual a zero THEN THE SYSTEM SHALL rejeitar o cadastro e exibir mensagem de erro.

**Critérios de aceite:**

- [ ] Deve permitir informar o valor da renda fixa mensal (ex.: salário líquido).
- [ ] Deve permitir mais de uma fonte de renda fixa (ex.: usuário com dois empregos).
- [ ] O valor deve ser considerado automaticamente no cálculo de saldo/orçamento do mês corrente e dos meses seguintes, até ser alterado.
- [ ] Deve validar que o valor é maior que zero.

#### RF-07 — Cadastro de renda variável

**Descrição:** rendas sem valor fixo mensal (freelas, comissões, renda extra).

**Enunciado EARS:**

- Event-driven. WHEN o usuário registra um lançamento de renda variável THE SYSTEM SHALL somá-lo à renda total do mês correspondente.
- Unwanted behavior. IF o valor informado for menor ou igual a zero THEN THE SYSTEM SHALL rejeitar o lançamento e exibir mensagem de erro.

**Critérios de aceite:**

- [ ] Deve permitir cadastrar lançamentos de renda variável com valor, descrição e data.
- [ ] Cada lançamento é pontual (referente a um mês específico), diferente da renda fixa recorrente.
- [ ] Deve ser somada à renda fixa para compor a renda total do mês.
- [ ] Deve validar que o valor é maior que zero.

#### RF-08 — Cadastro de bônus e PLR

**Descrição:** bonificações e Participação nos Lucros e Resultados.

**Enunciado EARS:** Event-driven. WHEN o usuário cadastra um bônus/PLR com periodicidade anual e mês de referência THE SYSTEM SHALL somar integralmente o valor à renda total do mês informado, sem diluí-lo pelos demais meses.

**Critérios de aceite:**

- [ ] Deve permitir cadastrar valor de bônus/PLR.
- [ ] Deve permitir escolher a periodicidade do lançamento: **mensal** ou **anual**.
- [ ] Quando periodicidade **anual**, o usuário deve informar o mês de referência em que o valor é recebido (o sistema não deve diluir automaticamente ao longo dos 12 meses).
- [ ] Deve ser somado à renda total do mês em que é recebido.
- [ ] Deve validar que o valor é maior ou igual a zero.

#### RF-09 — Cadastro de despesas por categoria

**Enunciado EARS:**

- Event-driven. WHEN o usuário registra uma despesa com valor, categoria e data válidos THE SYSTEM SHALL persistir o lançamento e atualizar a listagem e os dashboards imediatamente.
- Unwanted behavior. IF o valor for menor ou igual a zero, ou se a categoria ou a data não forem informadas, THEN THE SYSTEM SHALL rejeitar o lançamento e indicar o campo inválido.

**Critérios de aceite:**

- [ ] Deve exigir valor, categoria e data.
- [ ] Deve validar que o valor é maior que zero.
- [ ] A despesa deve aparecer na listagem e nos dashboards imediatamente após salvar.
- [ ] Deve permitir marcar a despesa como recorrente (repete todo mês com o mesmo valor) ou pontual.

#### RF-10 — Categorias padrão e personalizadas de gastos

**Enunciado EARS:** Event-driven. WHEN o usuário cria uma categoria personalizada THE SYSTEM SHALL disponibilizá-la, junto às categorias padrão, para uso em novos lançamentos.

**Critérios de aceite:**

- [ ] O sistema deve trazer, por padrão, as categorias: **Moradia**, **Custos básicos**, **Alimentação**, **Locomoção**, **Saúde**, **Educação**, **Lazer**, **Investimentos** (aportes tratados como saída do orçamento) e **Doações**.
- [ ] O usuário deve poder criar categorias personalizadas adicionais.
- [ ] O usuário deve poder ocultar/desativar categorias padrão que não usa (sem apagar histórico já lançado nelas).
- [ ] Cada despesa deve pertencer a exatamente uma categoria.
- [ ] Cada categoria deve ter uma cor associada, usada de forma consistente em todos os gráficos.

#### RF-11 — Edição e exclusão de lançamentos

**Enunciado EARS:** Event-driven. WHEN o usuário edita ou exclui um lançamento THE SYSTEM SHALL recalcular automaticamente o saldo, os dashboards e o progresso das metas.

**Critérios de aceite:**

- [ ] O usuário deve poder editar valor, categoria/tipo de renda e data de qualquer lançamento (renda fixa, variável, bônus/PLR ou despesa).
- [ ] O usuário deve poder excluir um lançamento, com confirmação prévia.
- [ ] Saldo, dashboards e progresso de metas devem ser recalculados automaticamente após qualquer alteração.

#### RF-12 — Cadastro de contas bancárias e cartões de crédito

**Enunciado EARS:** Event-driven. WHEN o usuário cadastra uma conta bancária ou cartão de crédito THE SYSTEM SHALL disponibilizá-lo para vínculo com lançamentos.

**Critérios de aceite:**

- [ ] Deve permitir cadastrar múltiplas contas, cada uma com nome, tipo e saldo inicial.
- [ ] Deve permitir cadastrar cartões de crédito com limite e data de fechamento/vencimento.
- [ ] Cada lançamento (renda ou despesa) deve poder ser vinculado a uma conta ou cartão específico.

#### RF-13 — Controle de fatura de cartão de crédito

**Enunciado EARS:** Event-driven. WHEN um lançamento é vinculado a um cartão de crédito THE SYSTEM SHOULD somá-lo à fatura do ciclo atual e recalcular o limite disponível.

**Critérios de aceite:**

- [ ] O sistema deve somar os lançamentos do cartão no ciclo da fatura atual.
- [ ] Deve exibir o limite disponível (limite total − fatura atual).
- [ ] Deve alertar visualmente quando o limite estiver próximo de estourar (percentual a definir, ex.: 80%).

#### RF-14 — Meta geral de renda e de gasto

**Enunciado EARS:** Event-driven. WHEN o gasto total do mês ultrapassa a meta geral definida THE SYSTEM SHOULD sinalizar visualmente o estouro da meta.

**Critérios de aceite:**

- [ ] O usuário deve poder definir uma meta de gasto total mensal (teto).
- [ ] O usuário deve poder definir uma meta de renda total mensal (piso desejado).
- [ ] As metas podem ser editadas a qualquer momento, valendo a partir do mês corrente.
- [ ] O sistema deve indicar visualmente quando a meta de gasto for ultrapassada ou a meta de renda não for atingida.

#### RF-15 — Meta de gasto por categoria

**Enunciado EARS:** Event-driven. WHEN o gasto acumulado de uma categoria atinge o percentual configurado da meta daquela categoria THE SYSTEM SHOULD alertar o usuário.

**Critérios de aceite:**

- [ ] O usuário deve poder definir um valor máximo mensal para cada categoria de gasto (ex.: até R$500 em Lazer).
- [ ] O sistema deve alertar quando o gasto acumulado da categoria no mês atingir um percentual configurável da meta (ex.: 90%) e quando ultrapassar 100%.
- [ ] Categorias sem meta definida não geram alerta.

#### RF-16 — Dashboard: gastos por categoria (pizza)

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona um período no dashboard de categorias THE SYSTEM SHOULD exibir o gráfico com o total gasto por categoria naquele período.

**Critérios de aceite:**

- [ ] Deve exibir gráfico de pizza (ou barras) com o total gasto por categoria no período selecionado.
- [ ] O usuário deve poder filtrar por mês.
- [ ] Categorias sem gasto no período não devem aparecer no gráfico.
- [ ] Ao passar o mouse/tocar em uma fatia, deve exibir valor e percentual do total.

#### RF-17 — Dashboard: evolução de saldo (linha)

**Enunciado EARS:** Event-driven. WHEN um novo lançamento é registrado THE SYSTEM SHOULD atualizar automaticamente o gráfico de evolução de saldo.

**Critérios de aceite:**

- [ ] Deve exibir gráfico de linha com saldo consolidado mês a mês (renda total − gasto total).
- [ ] Deve permitir selecionar um intervalo de meses.
- [ ] Deve atualizar automaticamente ao registrar novos lançamentos.

#### RF-18 — Dashboard: comparativo renda vs. gasto mensal (barras)

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona um intervalo de meses no dashboard comparativo THE SYSTEM SHOULD exibir renda total e gasto total lado a lado para cada mês do intervalo.

**Critérios de aceite:**

- [ ] Deve exibir gráfico de barras agrupadas com renda total e gasto total lado a lado, por mês.
- [ ] Deve compor a renda total a partir de renda fixa + renda variável + bônus/PLR do mês.
- [ ] Deve permitir selecionar um intervalo de meses (ex.: últimos 6 ou 12 meses).
- [ ] Deve destacar visualmente os meses em que o gasto superou a renda.

#### RF-19 — Dashboard: progresso de metas

**Enunciado EARS:** Event-driven. WHEN um lançamento altera o gasto ou a renda do mês corrente THE SYSTEM SHOULD recalcular e exibir o progresso das metas gerais e por categoria.

**Critérios de aceite:**

- [ ] Deve exibir barra de progresso para a meta geral de gasto (gasto atual / meta) e para a meta geral de renda (renda atual / meta).
- [ ] Deve exibir uma barra de progresso por categoria que tenha meta definida (RF-15).
- [ ] A cor da barra deve mudar conforme a proximidade do limite (ex.: verde até 70%, amarelo até 90%, vermelho acima de 100%).
- [ ] Deve ser recalculado automaticamente a cada novo lançamento no mês corrente.

---

### 1.4 Módulo — Simulador de Investimentos

> Aba independente na navegação principal (não é sub-aba da Administração Financeira). Pode ler o saldo calculado por lá (RF-26), mas tem sua própria tela.

#### RF-20 — Simulação de investimento em renda fixa

**Enunciado EARS:** Event-driven. WHEN o usuário solicita uma simulação de renda fixa com valor inicial, aporte mensal e prazo THE SYSTEM SHALL calcular e retornar o valor bruto e o valor líquido de IR ao final do prazo.

**Critérios de aceite:**

- [ ] Deve permitir simular CDB, Tesouro e poupança informando valor inicial, aporte mensal e prazo.
- [ ] Deve usar o motor de cálculo de juros compostos (RF-22), alimentado pela taxa vinda dos indicadores oficiais (RF-23) — sem o usuário precisar digitar a taxa manualmente.
- [ ] Deve permitir ao usuário sobrepor a taxa sugerida por um valor manual, caso queira simular um cenário hipotético.
- [ ] Deve exibir o valor bruto e, quando aplicável, o valor líquido de IR (tabela regressiva conforme prazo, exceto poupança e produtos isentos).
- [ ] Deve exibir a data de referência do indicador usado na simulação.

#### RF-21 — Simulação de investimento em renda variável

**Enunciado EARS:** Event-driven. WHEN o usuário informa um ticker ou valor investido para simulação de renda variável THE SYSTEM SHALL retornar a evolução estimada do investimento, identificada como projeção.

**Critérios de aceite:**

- [ ] Deve permitir simular aporte em ações e/ou FIIs informando o ticker do ativo (busca via RF-24) ou valor investido manual.
- [ ] Quando o ticker é informado, o preço atual e o histórico de cotações devem ser pré-preenchidos automaticamente a partir de RF-24; o usuário pode ajustar a rentabilidade esperada.
- [ ] Deve deixar explícito que se trata de uma projeção, sem garantia de retorno, e que rentabilidade passada não garante rentabilidade futura.
- [ ] Deve exibir a evolução estimada do valor investido ao longo do prazo simulado.

#### RF-22 — Calculadora de juros compostos (motor genérico)

**Descrição:** núcleo de cálculo reutilizado por RF-20, RF-21 e RF-26, para não duplicar a lógica financeira em cada simulação.

**Campos de entrada (UI):**

| Campo | Tipo | Observações |
|---|---|---|
| Valor inicial | Moeda (R$) | Aporte único no início da simulação; aceita 0 |
| Valor mensal | Moeda (R$) | Aporte recorrente por período; aceita 0 |
| Taxa de juros | Percentual (%) + seletor **Mensal / Anual** | Ícone de ajuda (`?`) explicando o que é a taxa e como ela é aplicada |
| Período | Número inteiro + seletor **Meses / Anos** | Prazo total da simulação |

**Enunciado EARS:**

- Event-driven. WHEN o usuário informa valor inicial, valor mensal, taxa de juros e período THE SYSTEM SHALL calcular o montante final usando juros compostos, com taxa equivalente entre as periodicidades informadas.
- Unwanted behavior. IF o valor inicial, o valor mensal ou a taxa de juros forem negativos, ou se o período for menor ou igual a zero, THEN THE SYSTEM SHALL rejeitar a simulação e indicar o campo inválido.

**Critérios de aceite:**

- [ ] Deve calcular `M = P × (1 + i)^n + Σ aportes mensais capitalizados`, onde P = valor inicial, i = taxa periódica, n = número de períodos.
- [ ] O campo **Taxa de juros** deve ter um seletor para o usuário escolher se o percentual informado é **mensal** ou **anual**.
- [ ] O campo **Período** deve ter um seletor para o usuário escolher se o número informado é em **meses** ou em **anos**.
- [ ] Independentemente da combinação escolhida pelo usuário (ex.: taxa anual + período em meses), o sistema deve converter internamente tudo para uma base mensal comum antes de calcular, usando **taxa equivalente composta** — nunca taxa proporcional simples (ex.: taxa mensal ≠ taxa anual ÷ 12).
- [ ] Fórmula de conversão anual → mensal: `i_mensal = (1 + i_anual)^(1/12) − 1`. Conversão mensal → anual: `i_anual = (1 + i_mensal)^12 − 1`.
- [ ] O clique no ícone de ajuda (`?`) ao lado de "Taxa de juros" deve exibir uma explicação em linguagem simples do que é a taxa e de como ela é usada no cálculo.
- [ ] Deve validar que valor inicial e valor mensal não sejam negativos, que a taxa de juros não seja negativa e que o período seja maior que zero.
- [ ] Deve aceitar a taxa em duas origens: (a) indicador oficial buscado via RF-23 (pré-preenchendo o campo), ou (b) valor informado manualmente pelo usuário (sobrescrevendo o valor sugerido).
- [ ] O aporte mensal ("Valor mensal") é aplicado no fim de cada período mensal.
- [ ] Deve gerar uma tabela mês a mês com saldo acumulado, juros do período e aporte do período.
- [ ] Deve gerar os dados para um gráfico de evolução do saldo acumulado ao longo do prazo.
- [ ] Deve exibir o resultado final consolidado: valor total investido (aportes), total de juros ganhos e montante final.
- [ ] Deve ser coberto por testes automatizados que validem o resultado contra cálculo de referência (RNF-07), incluindo casos de conversão de taxa mensal↔anual e período em meses↔anos.

#### RF-23 — Integração com indicadores oficiais (Selic, CDI, IPCA, Tesouro Direto)

**Descrição:** busca de taxas reais em fontes oficiais do governo/mercado brasileiro, evitando que o usuário precise digitar valores desatualizados.

**Enunciado EARS:**

- Event-driven. WHEN uma simulação de renda fixa é solicitada THE SYSTEM SHALL obter a taxa do indicador oficial correspondente (Selic, CDI, IPCA ou Tesouro Direto) a partir do cache local mais recente.
- Unwanted behavior. IF a API oficial estiver indisponível ou retornar erro na atualização THEN THE SYSTEM SHALL usar o último valor em cache e exibir aviso visual de que o dado pode estar desatualizado — nunca um valor zerado ou inventado (incorpora a antiga RB-11).

**Critérios de aceite:**

- [ ] Selic, CDI e IPCA devem ser obtidos via API do **Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS)** (`api.bcb.gov.br/dados/serie`).
- [ ] Taxas de títulos do Tesouro Direto devem ser obtidas via API do **Tesouro Transparente** (`www.tesourotransparente.gov.br`).
- [ ] Os valores obtidos devem ser armazenados em cache local, com data/hora da última atualização.
- [ ] O sistema deve atualizar o cache automaticamente 1 vez por dia, após o horário de divulgação de cada indicador (padrão de mercado; atende à defasagem máxima de 24h do RNF-09).
- [ ] Em caso de falha ou indisponibilidade da API oficial, o sistema deve usar o último valor em cache e exibir um aviso visual informando que o dado pode estar desatualizado.
- [ ] A data de referência do indicador deve ser exibida sempre que ele for usado em uma simulação (RF-20, RF-22).

#### RF-24 — Cotação de ações e FIIs via fonte de mercado

**Descrição:** consulta de preço atual e histórico de ativos de renda variável para uso em RF-21.

**Enunciado EARS:**

- Event-driven. WHEN o usuário busca um ticker de ação ou FII THE SYSTEM SHOULD retornar o preço mais recente disponível e a data/hora de referência da cotação.
- Unwanted behavior. IF a fonte de dados de mercado estiver indisponível THEN THE SYSTEM SHOULD permitir que o usuário prossiga informando valor e rentabilidade manualmente.

**Critérios de aceite:**

- [ ] O usuário deve poder buscar um ativo pelo ticker (ex.: PETR4, MXRF11).
- [ ] O sistema deve retornar preço mais recente disponível, variação do dia e data/hora de referência da cotação.
- [ ] O sistema deve retornar histórico de preços do ativo para cálculo de rentabilidade histórica (usada como sugestão em RF-21).
- [ ] Caso a fonte de dados esteja indisponível, o sistema deve permitir que o usuário prossiga informando valor e rentabilidade manualmente.
- [ ] **Nota técnica:** a B3 não oferece API pública gratuita de cotações em tempo real para pessoa física; a fonte de dados (provedor de mercado homologado, ou agregador que consome dados da B3) precisa ser definida antes da implementação — ver risco correspondente na seção 7 (Riscos).

#### RF-25 — Comparador de cenários de investimento

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona duas ou mais simulações para comparação THE SYSTEM SHALL exibir os resultados finais lado a lado com a diferença percentual entre eles.

**Critérios de aceite:**

- [ ] Deve permitir selecionar 2 ou mais simulações já feitas (ex.: poupança vs. CDB vs. Tesouro) para comparação lado a lado.
- [ ] Deve exibir os resultados finais e a diferença percentual entre os cenários.
- [ ] Deve indicar qual cenário rende mais ao final do prazo.

#### RF-26 — Projeção de objetivo financeiro

**Enunciado EARS:** Event-driven. WHEN o usuário informa um valor-alvo e um prazo THE SYSTEM SHOULD calcular o aporte mensal necessário para atingir a meta, dado o rendimento estimado.

**Critérios de aceite:**

- [ ] O usuário deve poder informar uma meta (valor-alvo e prazo).
- [ ] O sistema deve calcular o aporte mensal necessário para atingir a meta, dado um rendimento estimado.
- [ ] Deve avisar se a meta é inviável com os parâmetros informados (ex.: aporte necessário maior que a renda disponível, usando o saldo calculado na Administração Financeira).

#### RF-27 — Métricas de risco e retorno (volatilidade, Sharpe simplificado)

**Descrição:** métricas adicionais para o usuário avançado comparar cenários de renda variável com mais profundidade técnica.

**Enunciado EARS:** Event-driven. WHEN uma simulação de renda variável é concluída THE SYSTEM MAY calcular e exibir a volatilidade e o Índice de Sharpe simplificado do ativo.

**Critérios de aceite:**

- [ ] Deve calcular a volatilidade (desvio padrão dos retornos históricos) de ativos simulados via RF-21/RF-24.
- [ ] Deve calcular o Índice de Sharpe simplificado: `(retorno médio do ativo − taxa livre de risco) / volatilidade`, usando a Selic (RF-23) como taxa livre de risco.
- [ ] Deve exibir essas métricas junto ao resultado de cada simulação de renda variável e no comparador (RF-25).
- [ ] Deve deixar claro que as métricas usam dados históricos e não garantem comportamento futuro (mesma ressalva de RB-08).
- [ ] Disponível por padrão para o perfil avançado (RF-03); o perfil iniciante pode habilitar manualmente.

#### RF-28 — Simulação em moeda estrangeira (câmbio)

**Descrição:** permite simular investimentos em moeda estrangeira, útil para quem pensa em diversificação internacional.

**Enunciado EARS:** Event-driven. WHEN o usuário informa um valor em moeda estrangeira para simulação THE SYSTEM MAY converter o valor para BRL usando a taxa PTAX oficial e exibir o resultado nas duas moedas.

**Critérios de aceite:**

- [ ] Deve permitir informar um valor em moeda estrangeira (ex.: USD, EUR — lista a definir) e converter para BRL usando a taxa de câmbio oficial.
- [ ] A taxa de câmbio deve ser obtida via API **PTAX do Banco Central do Brasil** (`olinda.bcb.gov.br/olinda/servico/PTAX`).
- [ ] Deve permitir simular a evolução de um investimento em moeda estrangeira considerando tanto a rentabilidade do ativo quanto a variação cambial esperada (informada pelo usuário).
- [ ] Deve deixar explícito que a variação cambial é uma fonte adicional de risco/retorno, distinta da rentabilidade do ativo em si.
- [ ] O resultado deve ser exibido tanto na moeda original quanto convertido para BRL.

---

### 1.5 Módulo — Relatórios de Empresas

> Aba independente na navegação principal. Permite ao usuário pesquisar uma empresa de capital aberto e consultar seus relatórios oficiais (DFP, ITR, Formulário de Referência) para apoiar a decisão de investir.

**Decisão de arquitetura (ver seção 6 — Premissas):** o sistema **não hospeda cópia dos documentos completos em PDF**. Ele indexa metadados desses documentos e indicadores financeiros estruturados (fonte: Portal de Dados Abertos da CVM) e aponta, via link direto, para o documento oficial no sistema RAD/ENET da CVM. Isso evita problemas de direitos autorais sobre o conteúdo redigido pela empresa emissora, custo de armazenamento e risco de desatualização.

#### RF-29 — Busca de empresa

**Enunciado EARS:** Event-driven. WHEN o usuário digita um ticker, CNPJ ou razão social na busca THE SYSTEM SHOULD retornar sugestões de empresas correspondentes.

**Critérios de aceite:**

- [ ] Deve permitir buscar uma empresa de capital aberto por ticker (ex.: PETR4), CNPJ ou razão social.
- [ ] Deve exibir sugestões (autocomplete) conforme o usuário digita.
- [ ] Deve retornar dados cadastrais básicos da empresa (razão social, CNPJ, setor) a partir do dataset de Informação Cadastral da CVM.

#### RF-30 — Listagem de documentos oficiais (metadados)

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona uma empresa THE SYSTEM SHOULD listar os metadados dos documentos oficiais disponíveis (DFP, ITR, FRE, IPE).

**Critérios de aceite:**

- [ ] Para a empresa selecionada, deve listar os documentos disponíveis: DFP (Demonstrações Financeiras Padronizadas), ITR (Informações Trimestrais), FRE (Formulário de Referência) e demais documentos do IPE (Informações Periódicas e Eventuais).
- [ ] Cada item da lista deve exibir: tipo de documento, categoria/assunto, período de referência (ex.: 2º trimestre de 2026), data de entrega e status (ativo ou reapresentado/substituído).
- [ ] O sistema deve armazenar apenas os metadados listados acima — nunca o conteúdo binário do documento (PDF).
- [ ] A listagem deve poder ser filtrada por tipo de documento e por intervalo de datas.

#### RF-31 — Acesso ao documento completo via link externo

**Enunciado EARS:** Event-driven. WHEN o usuário clica em um documento da listagem THE SYSTEM SHOULD redirecioná-lo, em nova aba, ao documento oficial no RAD/ENET da CVM.

**Critérios de aceite:**

- [ ] Cada item da listagem (RF-30) deve conter um link direto para o documento original no sistema RAD/ENET da CVM.
- [ ] O link deve abrir em nova aba/janela, redirecionando o usuário ao site oficial da CVM.
- [ ] A tela deve exibir um aviso indicando que o conteúdo do documento é de responsabilidade da empresa emissora e da CVM, e que o FinNova apenas indexa e referencia o material.
- [ ] Se o link oficial mudar de endereço (ex.: migração de sistema pela CVM), o sistema deve ter um mecanismo de verificação periódica para identificar e sinalizar links quebrados.

#### RF-32 — Indicadores financeiros extraídos de dados abertos da CVM

**Enunciado EARS:** Event-driven. WHEN novos dados de DFP/ITR são sincronizados do Portal de Dados Abertos da CVM THE SYSTEM MAY extrair e disponibilizar os indicadores financeiros estruturados da empresa.

**Critérios de aceite:**

- [ ] Deve extrair indicadores estruturados (ex.: receita líquida, lucro líquido, patrimônio líquido) a partir dos arquivos de DFP/ITR do Portal de Dados Abertos da CVM (dados numéricos, não o PDF do relatório).
- [ ] Deve exibir esses indicadores em tabela e em gráfico de evolução por período (trimestre/ano).
- [ ] Deve indicar a fonte e a data de referência dos dados extraídos.
- [ ] Diferente do documento completo (RF-31), esses dados numéricos podem ser armazenados localmente, pois são dados abertos de reuso livre — respeitando o limite de retenção de RF-33.

#### RF-33 — Retenção e expurgo automático dos dados sincronizados

**Enunciado EARS:** Event-driven. WHEN um registro de metadado ou indicador completar 12 meses desde a sincronização THE SYSTEM SHALL expurgá-lo automaticamente do cache local.

**Critérios de aceite:**

- [ ] Metadados de documentos (RF-30) e indicadores extraídos (RF-32) devem ser mantidos em cache local por, no máximo, **12 meses** a partir da data de sincronização com a fonte oficial.
- [ ] Ao atingir 12 meses, o registro deve ser expurgado (removido) automaticamente por uma rotina agendada.
- [ ] Se o usuário consultar uma empresa cujos dados foram expurgados, o sistema deve buscar novamente na fonte oficial (CVM) e recriar o cache.
- [ ] O link para o documento completo (RF-31) nunca é uma cópia armazenada — por não guardar o binário, ele não está sujeito a essa política de expurgo.
- [ ] A rotina de expurgo deve ser registrada em log para fins de auditoria (RNF-18).

#### RF-34 — Watchlist de empresas

**Descrição:** permite ao usuário acompanhar empresas de interesse sem precisar buscar novamente.

**Enunciado EARS:** Event-driven. WHEN um novo documento é identificado para uma empresa da watchlist do usuário THE SYSTEM MAY notificá-lo.

**Critérios de aceite:**

- [ ] Deve permitir favoritar/desfavoritar uma empresa a partir da busca (RF-29) ou da ficha da empresa.
- [ ] Deve exibir uma lista consolidada das empresas favoritadas pelo usuário.
- [ ] Deve notificar o usuário (RF-48) quando um novo documento (DFP, ITR, FRE, IPE) for identificado para uma empresa da watchlist.
- [ ] A watchlist é pessoal (por usuário), sem limite mínimo, com limite máximo configurável de 50 empresas (padrão de mercado).

---

### 1.6 Módulo — Patrimônio

> Aba independente na navegação principal. Consolida tudo que o usuário possui (ativos) e deve (passivos) num raio-x único do patrimônio líquido, alimentado pelos dados dos módulos Administração Financeira, Simulador e Compras Financiadas.

#### RF-35 — Consolidação de patrimônio (ativos e passivos)

**Enunciado EARS:** Event-driven. WHEN dados de conta, investimento, fatura ou financiamento do usuário mudam THE SYSTEM SHOULD recalcular o patrimônio líquido consolidado (ativos menos passivos).

**Critérios de aceite:**

- [ ] Deve consolidar automaticamente como **ativos**: saldo das contas (RF-12) e valor atual dos investimentos simulados/registrados (módulo Simulador de Investimentos).
- [ ] Deve consolidar automaticamente como **passivos**: fatura de cartão em aberto (RF-13) e saldo devedor de financiamentos ativos (RF-47).
- [ ] Deve permitir cadastro manual de outros ativos (ex.: imóvel, veículo, reserva de emergência) e passivos (ex.: empréstimo pessoal) não capturados automaticamente pelos demais módulos.
- [ ] Cada ativo/passivo manual deve ter nome, valor e, opcionalmente, uma rentabilidade (ativo) ou taxa de juros (passivo) informada pelo usuário.
- [ ] Deve calcular patrimônio líquido = soma dos ativos − soma dos passivos.

#### RF-36 — Evolução do patrimônio líquido

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona um intervalo de meses no dashboard de patrimônio THE SYSTEM MAY exibir a evolução do patrimônio líquido, dos ativos e dos passivos nesse período.

**Critérios de aceite:**

- [ ] Deve exibir gráfico de linha com o patrimônio líquido consolidado mês a mês.
- [ ] Deve permitir visualizar ativos totais e passivos totais separadamente no mesmo gráfico.
- [ ] Deve permitir selecionar um intervalo de meses.

#### RF-37 — Mapa de calor patrimonial (ativos e passivos por cor)

**Descrição:** visualização única do patrimônio, em que o tamanho de cada item representa o valor e a cor comunica a natureza (ativo/passivo) e o desempenho.

**Enunciado EARS:** Event-driven. WHEN o usuário abre o mapa de calor patrimonial THE SYSTEM SHOULD exibir cada ativo em tom de verde proporcional à sua rentabilidade e cada passivo em tom quente proporcional à sua taxa de juros.

**Critérios de aceite:**

- [ ] Deve exibir um gráfico dinâmico (treemap ou gráfico de bolhas) com um item por ativo e um item por passivo do usuário.
- [ ] O tamanho de cada item deve ser proporcional ao valor absoluto do ativo/passivo em relação ao total exibido.
- [ ] **Passivos** devem ser exibidos em tons quentes (do amarelo ao vermelho); a intensidade da cor é proporcional ao custo da dívida (taxa de juros do passivo) — passivos mais caros aparecem em vermelho mais intenso. *(Regra padrão sugerida — pode ser ajustada, por exemplo, para intensidade proporcional ao valor da dívida.)*
- [ ] **Ativos** devem ser exibidos em tons de verde; a cor escurece (fica mais saturada) conforme a rentabilidade do ativo aumenta. Ativos com rentabilidade nula ou negativa aparecem em verde bem claro/acinzentado.
- [ ] Ao passar o mouse/tocar em um item, deve exibir nome, valor, tipo (ativo/passivo) e o indicador usado na cor (rentabilidade ou taxa de juros).
- [ ] Deve permitir filtrar a visualização por "todos", "somente ativos" ou "somente passivos".
- [ ] Deve atualizar automaticamente quando dados de Administração Financeira, Simulador de Investimentos ou Compras Financiadas mudarem, ou quando um ativo/passivo manual for editado.

#### RF-38 — Alocação da carteira por classe de ativo

**Enunciado EARS:** Event-driven. WHEN o usuário abre o dashboard de alocação THE SYSTEM MAY exibir o percentual investido em cada classe de ativo e o desvio em relação à alocação-alvo definida.

**Critérios de aceite:**

- [ ] Deve exibir gráfico de pizza/barras com a distribuição dos ativos de investimento por classe (renda fixa, ações, FIIs, poupança, outros).
- [ ] Deve calcular o percentual de cada classe sobre o total investido.
- [ ] Deve permitir ao usuário definir uma alocação-alvo (%) por classe e comparar com a alocação atual, indicando o desvio.

#### RF-39 — Simulador de cenários "E se..." (stress financeiro)

**Descrição:** stress test do orçamento sob diferentes cenários hipotéticos de choque financeiro, mostrando por quanto tempo o patrimônio sustenta o usuário e o impacto no orçamento.

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona um tipo de cenário (perda de renda, redução de renda ou gasto emergencial) e informa os parâmetros THE SYSTEM MAY calcular e exibir o impacto no orçamento e por quantos meses o patrimônio atual sustenta os gastos médios do usuário.

**Critérios de aceite:**

- [ ] Deve permitir simular ao menos três tipos de cenário hipotético: perda total da renda, redução parcial da renda (%) e gasto emergencial pontual — cada um por um período/valor informado pelo usuário.
- [ ] Deve calcular, com base no patrimônio líquido atual (RF-35) e nos gastos médios mensais (módulo Administração Financeira), por quantos meses o usuário consegue se manter no cenário simulado.
- [ ] Deve exibir um alerta se a reserva for insuficiente para cobrir de 3 a 6 meses de gastos (limite configurável).
- [ ] Deve permitir comparar dois cenários lado a lado (ex.: "sem ação" vs. "cortando gasto de lazer em 30%").
- [ ] Não deve alterar dados reais do usuário — é uma simulação isolada, no mesmo padrão do módulo Simulador (RB-17).

#### RF-40 — Metas nomeadas (objetivos financeiros)

**Enunciado EARS:** Event-driven. WHEN o usuário cria uma meta nomeada vinculada a um ativo THE SYSTEM MAY calcular e exibir o progresso da meta com base no valor atual do ativo vinculado.

**Critérios de aceite:**

- [ ] Deve permitir criar metas nomeadas com nome, valor-alvo, prazo e categoria (ex.: reserva de emergência, viagem, entrada de imóvel).
- [ ] Deve permitir vincular a meta a um ativo específico (RF-35) que acumula o progresso.
- [ ] Deve reaproveitar o motor de projeção RF-26 para calcular o aporte mensal necessário.
- [ ] Deve exibir progresso visual (barra) por meta.

---

### 1.7 Módulo — Score de Saúde Financeira

> Aba independente na navegação principal (com destaque também na tela inicial). Resume, numa única métrica, a saúde financeira do usuário a partir dos demais módulos.

#### RF-41 — Cálculo do score de saúde financeira

**Enunciado EARS:** Event-driven. WHEN dados de renda, gasto, reserva ou dívida do usuário mudam THE SYSTEM SHOULD recalcular o score de saúde financeira.

**Critérios de aceite:**

- [ ] Deve calcular uma nota (0 a 100) combinando pelo menos: relação gasto/renda do mês (Administração Financeira), existência e tamanho da reserva de emergência (RF-35), comprometimento de renda com dívidas/fatura (RF-13, Compras Financiadas) e aderência às metas definidas (RF-14, RF-15).
- [ ] A fórmula de ponderação de cada fator deve ser documentada e configurável (não fixa no código), para permitir ajuste sem nova implantação.
- [ ] Deve recalcular o score automaticamente a cada mudança relevante nos módulos de origem.
- [ ] Deve deixar explícito que o score é educativo e não constitui recomendação financeira.

#### RF-42 — Exibição e histórico do score

**Enunciado EARS:** Event-driven. WHEN o usuário abre a tela de score THE SYSTEM MAY exibir a nota atual, a classificação, o histórico mensal e os fatores que mais impactaram o resultado.

**Critérios de aceite:**

- [ ] Deve exibir o score atual em destaque (ex.: velocímetro/gauge) com faixa de classificação (ex.: crítico, atenção, saudável, excelente).
- [ ] Deve exibir a evolução do score mês a mês (gráfico de linha).
- [ ] Deve exibir, junto ao score, os 1-2 fatores que mais impactaram negativamente o resultado, com uma sugestão genérica de melhoria (ex.: "sua fatura consome X% da sua renda").

---

### 1.8 Módulo — Conteúdo Educacional

> Aba independente na navegação principal, complementada por ajuda contextual dentro dos outros módulos.

#### RF-43 — Central de conteúdo educacional

**Enunciado EARS:** Event-driven. WHEN o usuário busca um termo na central educacional THE SYSTEM MAY retornar o verbete correspondente.

**Critérios de aceite:**

- [ ] Deve disponibilizar artigos/verbetes curtos explicando termos usados no sistema (ex.: o que é CDI, o que é Sharpe, o que é diversificação).
- [ ] O conteúdo sugerido na tela inicial deve variar conforme o perfil do usuário (RF-03): iniciante vê conceitos básicos primeiro; avançado vê conceitos técnicos.
- [ ] Deve ser possível buscar por termo.

#### RF-44 — Ajuda contextual (tooltips educativos)

**Enunciado EARS:** Event-driven. WHEN o usuário clica no ícone de ajuda de um campo técnico THE SYSTEM MAY exibir a explicação correspondente da central educacional sem sair da tela atual.

**Critérios de aceite:**

- [ ] Campos técnicos do sistema (ex.: "Taxa de juros" em RF-22, "Sharpe" em RF-27) devem ter um ícone de ajuda que abre a explicação correspondente sem sair da tela atual.
- [ ] O conteúdo do tooltip deve ser reaproveitado do conteúdo da central educacional (RF-43), nunca duplicado.

---

### 1.9 Módulo — Simulador de Compras Financiadas

> Aba independente na navegação principal. Estava listado como módulo futuro na visão original do FinNova e passou a fazer parte do backlog do MVP.

#### RF-45 — Simulação de compra financiada

**Enunciado EARS:** Event-driven. WHEN o usuário informa valor do bem, entrada, parcelas e taxa de juros THE SYSTEM MAY calcular e exibir a tabela de amortização e o valor total pago.

**Critérios de aceite:**

- [ ] Deve permitir informar valor do bem, valor de entrada, número de parcelas e taxa de juros do financiamento (ou taxa média de mercado sugerida — fonte a definir).
- [ ] Deve calcular o valor total pago ao final do financiamento (juros inclusos), reaproveitando o motor de juros compostos (RF-22) com sistema de amortização a definir (ex.: tabela Price).
- [ ] Deve exibir a tabela de amortização parcela a parcela (valor, juros, amortização, saldo devedor).

#### RF-46 — Comparador: financiar vs. investir e comprar depois

**Enunciado EARS:** Event-driven. WHEN o usuário solicita a comparação entre financiar e investir para comprar depois THE SYSTEM MAY exibir o custo total e o tempo até a posse do bem para os dois cenários.

**Critérios de aceite:**

- [ ] Deve comparar dois cenários: (a) comprar financiado agora, ou (b) investir mensalmente o valor equivalente à parcela (via RF-22) até acumular o valor à vista do bem.
- [ ] Deve exibir, lado a lado, o custo total de cada cenário e o tempo até a posse do bem.
- [ ] Deve indicar qual cenário é financeiramente mais vantajoso ao final do prazo informado.

#### RF-47 — Registro do financiamento como passivo

**Enunciado EARS:** Event-driven. WHEN o usuário confirma uma simulação de compra financiada como financiamento real THE SYSTEM MAY registrar o saldo devedor como passivo no módulo Patrimônio.

**Critérios de aceite:**

- [ ] Ao confirmar uma simulação de compra financiada como financiamento real, o saldo devedor deve ser refletido automaticamente como passivo no módulo Patrimônio (RF-35).
- [ ] A parcela mensal deve poder ser lançada como despesa recorrente na categoria correspondente (RF-09, RF-10).

---

### 1.10 Recursos transversais — Notificações, Exportação e API Pública

> Não são uma aba própria; funcionam em conjunto com os demais módulos.

#### RF-48 — Notificações e alertas

**Enunciado EARS:** Event-driven. WHEN ocorre um evento monitorado (fatura próxima do vencimento, meta ultrapassada ou novo documento na watchlist) THE SYSTEM SHOULD gerar uma notificação para o usuário, respeitando suas preferências de canal.

**Critérios de aceite:**

- [ ] Deve notificar o usuário quando: a fatura do cartão estiver próxima do vencimento (RF-13), uma meta geral ou por categoria for ultrapassada (RF-14, RF-15), um novo documento for identificado para uma empresa da watchlist (RF-34), ou uma despesa recorrente (RF-09, campo `recorrente`) estiver próxima da data de vencimento.
- [ ] O usuário deve poder habilitar/desabilitar cada tipo de notificação individualmente.
- [ ] As notificações in-app devem ficar acessíveis num histórico (central de notificações) por, no mínimo, 30 dias.

#### RF-49 — Canal de envio

**Enunciado EARS:** Optional feature. WHERE o usuário habilita o canal push ou e-mail THE SYSTEM MAY enviar as notificações também por esse canal, além do in-app.

**Critérios de aceite:**

- [ ] Notificações in-app são obrigatórias (MVP); push (mobile) e e-mail são canais opcionais, configuráveis pelo usuário.
- [ ] O envio por push deve usar um serviço de terceiros (ex.: Firebase Cloud Messaging — ver seção 5).

#### RF-50 — Exportação de dados pessoais

**Enunciado EARS:** Event-driven. WHEN o usuário solicita a exportação dos seus lançamentos financeiros THE SYSTEM SHALL gerar o arquivo em CSV ou PDF no período filtrado.

**Critérios de aceite:**

- [ ] Deve permitir exportar lançamentos financeiros (Administração Financeira) em CSV e em PDF (extrato formatado).
- [ ] Deve permitir filtrar a exportação por período (mês, ano ou intervalo customizado).
- [ ] A exportação em PDF deve incluir um resumo (totais por categoria, saldo do período) além do detalhamento.
- [ ] Atende também ao direito de portabilidade de dados da LGPD (RNF-02).

#### RF-51 — Relatório mensal automático

**Enunciado EARS:** Event-driven. WHEN o mês vira THE SYSTEM MAY gerar e enviar automaticamente o relatório mensal em PDF ao usuário, se essa opção estiver habilitada.

**Critérios de aceite:**

- [ ] Deve gerar e enviar automaticamente, no início de cada mês, um resumo em PDF (reaproveitando o motor de RF-50) com renda, gasto, patrimônio líquido e score de saúde financeira do mês anterior.
- [ ] Deve ser enviado pelo canal configurado pelo usuário (RF-49 — e-mail).
- [ ] O usuário deve poder desativar esse relatório automático a qualquer momento.

#### RF-52 — API pública documentada

**Enunciado EARS:** Event-driven. WHEN uma aplicação de terceiros autenticada faz uma requisição a um endpoint público autorizado THE SYSTEM MAY retornar os dados solicitados dentro do escopo concedido pelo usuário.

**Critérios de aceite:**

- [ ] Deve expor um subconjunto de endpoints para uso por aplicações de terceiros autorizadas pelo usuário (ex.: leitura de saldo consolidado, patrimônio).
- [ ] Deve exigir autenticação própria (ex.: API key ou OAuth2), separada do login do usuário no app.
- [ ] Deve ter documentação pública, reaproveitando a documentação OpenAPI/Swagger (RNF-15).
- [ ] Deve ter rate limiting específico para consumidores externos (RNF-13).

#### RF-53 — Webhooks para eventos do usuário

**Enunciado EARS:** Event-driven. WHEN um evento cadastrado em uma assinatura de webhook ocorre THE SYSTEM MAY enviar o payload assinado (HMAC) para a URL cadastrada.

**Critérios de aceite:**

- [ ] Deve permitir que o usuário (ou uma integração autorizada) cadastre uma URL para receber notificações de eventos (ex.: meta atingida, fatura próxima do vencimento).
- [ ] O payload do webhook deve ser assinado (HMAC) para permitir verificação de autenticidade pelo receptor.
- [ ] Deve reaproveitar os mesmos gatilhos de RF-48.
- [ ] Deve registrar tentativas de entrega e permitir reenvio manual em caso de falha.

---

### 1.11 Módulo — Painel Administrativo

> Aba visível apenas para usuários com papel de **administrador**. Não aparece na navegação de um usuário comum, e o acesso é bloqueado no backend (não só escondido na interface).

#### RF-54 — Controle de acesso administrativo

**Enunciado EARS:** Unwanted behavior. IF um usuário sem papel de administrador tentar acessar um endpoint administrativo THEN THE SYSTEM SHALL retornar erro de acesso negado (HTTP 403).

**Critérios de aceite:**

- [ ] Deve existir um papel de usuário **administrador**, distinto do usuário comum.
- [ ] O acesso a qualquer rota/endpoint administrativo deve ser validado no backend por papel (RBAC) — nunca apenas ocultado na interface.
- [ ] Usuários sem papel de administrador que tentarem acessar um endpoint administrativo devem receber erro de acesso negado (HTTP 403).
- [ ] A promoção de um usuário a administrador deve ser feita apenas por outro administrador (ou via configuração inicial do sistema), nunca pelo cadastro público (RF-01).
- [ ] Todo acesso ao painel administrativo deve ser registrado no log de auditoria (RNF-18).

#### RF-55 — Listagem e busca de usuários

**Enunciado EARS:** Event-driven. WHEN um administrador aplica um filtro de busca na listagem de usuários THE SYSTEM SHOULD retornar os usuários correspondentes, sem exibir dados financeiros individuais.

**Critérios de aceite:**

- [ ] Deve listar os usuários cadastrados com informações não sensíveis: nome, e-mail, data de cadastro, perfil de investidor (RF-03) e status da conta.
- [ ] Deve permitir buscar/filtrar por nome, e-mail, perfil de investidor ou status.
- [ ] **Não** deve exibir dados financeiros individuais dos usuários (renda, gastos, patrimônio) — apenas metadados de conta e métricas agregadas de uso (RB-22).
- [ ] A listagem deve ser paginada.

#### RF-56 — Dashboard: distribuição de perfil de investidor

**Enunciado EARS:** Event-driven. WHEN um administrador abre o dashboard de perfil de investidor THE SYSTEM MAY exibir a distribuição dos usuários por perfil, filtrável por período de cadastro.

**Critérios de aceite:**

- [ ] Deve exibir gráfico dinâmico (pizza ou barras) com a distribuição dos usuários por resultado do quiz de perfil de investidor (RF-03) — ex.: iniciante/avançado ou conservador/moderado/arrojado.
- [ ] Deve permitir filtrar por período de cadastro.
- [ ] Deve atualizar automaticamente conforme novos usuários completam o quiz.

#### RF-57 — Dashboard: uso por módulo/aba

**Enunciado EARS:** Event-driven. WHEN um administrador seleciona um período no dashboard de uso THE SYSTEM MAY exibir o número de acessos e de usuários únicos por módulo nesse período.

**Critérios de aceite:**

- [ ] Deve exibir gráfico dinâmico com número de acessos e de usuários únicos por módulo (Administração Financeira, Simulador, Relatórios de Empresas, Patrimônio, Score, etc.) num período selecionável.
- [ ] Deve destacar o módulo mais e o menos utilizado no período selecionado.
- [ ] Os dados devem vir do registro de eventos de uso (RF-59), sempre agregados — nunca expondo, nesse gráfico, o comportamento individual nominal de um usuário.

#### RF-58 — Dashboard: usuários mais recorrentes (engajamento)

**Enunciado EARS:** Event-driven. WHEN um administrador abre o dashboard de engajamento THE SYSTEM MAY exibir as métricas DAU/WAU/MAU e os usuários inativos há mais tempo do que o limite configurado.

**Critérios de aceite:**

- [ ] Deve exibir métricas de engajamento: usuários ativos por dia/semana/mês (DAU/WAU/MAU), frequência média de uso, e usuários inativos há mais de N dias (limite configurável).
- [ ] Deve exibir, de forma agregada, quais módulos os usuários mais recorrentes mais utilizam.
- [ ] Deve exibir gráfico de evolução do engajamento ao longo do tempo.

#### RF-59 — Registro de eventos de uso (base para os dashboards)

**Descrição:** motor de coleta que alimenta os dashboards RF-57 e RF-58.

**Enunciado EARS:** Event-driven. WHEN um usuário acessa qualquer módulo do sistema THE SYSTEM SHOULD registrar, de forma assíncrona, um evento de uso (usuário, módulo, ação, timestamp), sem conteúdo financeiro.

**Critérios de aceite:**

- [ ] O sistema deve registrar, de forma assíncrona (sem impactar a performance percebida pelo usuário — RNF-04), um evento a cada vez que o usuário acessa um módulo/aba.
- [ ] O evento deve conter apenas: usuário (id), módulo, ação e timestamp — nunca conteúdo financeiro sensível (RB-23).
- [ ] A política de privacidade do sistema deve informar que dados de uso agregados são coletados para fins de melhoria do produto e vistos, de forma agregada, por administradores (transparência LGPD).
- [ ] O usuário deve poder solicitar a exclusão desses dados de uso junto com a exclusão de conta (RF-05).

---

### 1.12 Módulo — Contas Compartilhadas (Casal/Família)

> Aba/extensão opcional de Administração Financeira: permite que dois usuários vinculem suas contas para dividir despesas comuns, mantendo os dados individuais de cada um privados por padrão.

#### RF-60 — Vínculo de conta compartilhada entre dois usuários

**Enunciado EARS:** Event-driven. WHEN um usuário convida outro usuário para uma conta compartilhada e o convite é aceito THE SYSTEM MAY criar o vínculo entre as duas contas.

**Critérios de aceite:**

- [ ] Deve permitir que um usuário convide outro usuário cadastrado (por e-mail) para uma conta compartilhada.
- [ ] O vínculo só é criado após o usuário convidado aceitar o convite.
- [ ] Qualquer um dos dois usuários deve poder desfazer o vínculo a qualquer momento, sem apagar o histórico de despesas já compartilhadas.
- [ ] Dados individuais (renda, gastos não marcados como compartilhados) permanecem privados por padrão — só o que for explicitamente marcado como compartilhado (RF-61) é visível ao outro usuário.

#### RF-61 — Divisão de despesas compartilhadas

**Enunciado EARS:** Event-driven. WHEN um usuário marca uma despesa como compartilhada numa conta vinculada THE SYSTEM MAY dividir o valor entre os dois usuários e atualizar o saldo "quem deve quem".

**Critérios de aceite:**

- [ ] Deve permitir marcar uma despesa (RF-09) como compartilhada, escolhendo divisão igual (50/50) ou percentual customizado.
- [ ] Deve manter um saldo consolidado "quem deve quem" entre os dois usuários vinculados, atualizado a cada despesa compartilhada incluída, editada ou excluída.
- [ ] Deve permitir registrar um "acerto de contas" (pagamento entre os usuários) que zera ou reduz o saldo pendente.
- [ ] O saldo compartilhado deve ser visível para ambos os usuários vinculados, com o detalhamento das despesas que o compõem.

---

### 1.13 Módulo — Simulador de Aposentadoria e Previdência

> Aba independente na navegação principal. Projeta o patrimônio do usuário na aposentadoria a partir de aportes mensais e compara modalidades de previdência privada.

#### RF-62 — Simulação de aposentadoria

**Enunciado EARS:** Event-driven. WHEN o usuário informa idade atual, idade-alvo de aposentadoria, aporte mensal e taxa de rentabilidade esperada THE SYSTEM MAY projetar o patrimônio acumulado na data-alvo e a renda mensal estimada que ele sustenta.

**Critérios de aceite:**

- [ ] Deve permitir informar idade atual, idade-alvo de aposentadoria, aporte mensal e taxa de rentabilidade esperada (ou sugerida a partir de RF-23).
- [ ] Deve reaproveitar o motor de juros compostos (RF-22/RB-10) para projetar o patrimônio acumulado até a data-alvo.
- [ ] Deve estimar a renda mensal que o patrimônio projetado sustentaria (ex.: regra dos 4% ou parâmetro configurável).
- [ ] Deve exibir aviso de que a projeção é educativa, sujeita a variação de rentabilidade real, inflação e mudanças na legislação previdenciária.

#### RF-63 — Comparador de modalidades de previdência (PGBL x VGBL x carteira própria)

**Enunciado EARS:** Event-driven. WHEN o usuário solicita a comparação entre PGBL, VGBL e carteira própria para os mesmos parâmetros de aporte THE SYSTEM MAY exibir o valor líquido estimado de cada modalidade ao final do prazo, considerando a tributação simplificada de cada uma.

**Critérios de aceite:**

- [ ] Deve comparar três modalidades — PGBL, VGBL e carteira própria (via RF-22) — usando os mesmos parâmetros de aporte, prazo e rentabilidade.
- [ ] Deve aplicar uma tabela de tributação simplificada e configurável para cada modalidade (regressiva/progressiva), deixando explícito que é uma simplificação educativa, não cálculo tributário definitivo.
- [ ] Deve indicar em qual situação (ex.: dedução no IR anual) o PGBL costuma ser mais vantajoso, sem constituir recomendação personalizada.

---

### 1.14 Módulo — Calculadora de Imposto de Renda sobre Investimentos

> Aba independente na navegação principal. Estima o IR devido sobre as operações simuladas/registradas no sistema e ajuda o usuário a se organizar para a declaração anual — não substitui um contador nem a Receita Federal.

#### RF-64 — Estimativa de IR devido sobre operações simuladas

**Enunciado EARS:** Event-driven. WHEN o usuário solicita a estimativa de IR para uma simulação ou operação registrada THE SYSTEM MAY calcular o imposto estimado conforme o tipo de aplicação (renda fixa, ações, FIIs, day trade) e o prazo, e indicar a próxima data de vencimento do DARF quando aplicável.

**Critérios de aceite:**

- [ ] Deve calcular a estimativa de IR para renda fixa (tabela regressiva por prazo), ações/FIIs em operação comum (isenção até limite mensal configurável para ações) e day trade (alíquota fixa configurável).
- [ ] Deve usar uma tabela de alíquotas interna, versionada e configurável — não depende de API externa da Receita Federal.
- [ ] Quando houver IR a recolher via DARF, deve indicar a data-limite de vencimento (último dia útil do mês seguinte) como lembrete, sem gerar ou enviar o DARF.
- [ ] Deve exibir aviso de que a estimativa é educativa e não substitui a apuração de um contador ou o e-CAC da Receita Federal.

#### RF-65 — Exportação de informe de rendimentos consolidado

**Enunciado EARS:** Event-driven. WHEN o usuário solicita o informe de rendimentos de um ano-calendário THE SYSTEM MAY gerar um documento consolidado com os rendimentos e o IR estimado apurado no sistema para apoiar a declaração anual.

**Critérios de aceite:**

- [ ] Deve consolidar, por ano-calendário, os rendimentos simulados/registrados e o IR estimado (RF-64) num único documento exportável (reaproveita RF-50).
- [ ] Deve deixar explícito, no próprio documento, que se trata de um resumo auxiliar gerado pelo FinNova, não um informe oficial de instituição financeira.

---

### 1.15 Extensão — Score de Saúde Financeira: Benchmark anônimo

#### RF-66 — Benchmark anônimo com usuários do mesmo perfil

**Enunciado EARS:** Event-driven. WHEN o usuário abre a comparação de benchmark na tela de score THE SYSTEM MAY exibir a posição do usuário frente à média agregada de usuários do mesmo perfil de investidor, sem identificar nenhum usuário individualmente.

**Critérios de aceite:**

- [ ] Deve exibir, na tela de score (RF-42), a comparação entre os indicadores do usuário (ex.: % da renda poupada, score) e a média agregada de usuários do mesmo perfil de investidor (RF-03).
- [ ] A comparação deve usar apenas médias/percentis agregados de um grupo com tamanho mínimo (ex.: 30 usuários) — nunca dados nem indicadores de um usuário individual identificável (RB-26).
- [ ] O usuário deve poder desativar essa comparação nas configurações de privacidade, sem perder acesso ao restante do score.

---

### 1.16 Módulo — Gamificação e Conquistas

> Recurso transversal e opcional (Could have): reforça o engajamento do usuário sem interferir nos cálculos financeiros dos demais módulos.

#### RF-67 — Badges/conquistas por metas atingidas

**Enunciado EARS:** Event-driven. WHEN o usuário atinge uma meta (geral, por categoria ou nomeada) ou mantém um comportamento positivo por um período THE SYSTEM MAY conceder a conquista/badge correspondente e notificar o usuário.

**Critérios de aceite:**

- [ ] Deve conceder conquistas ao atingir metas gerais/por categoria (RF-14/15), metas nomeadas (RF-40) ou marcos de uso (ex.: "3 meses seguidos dentro do orçamento").
- [ ] Deve exibir uma tela com as conquistas obtidas e as próximas conquistas disponíveis (progresso).
- [ ] A concessão de uma conquista deve gerar uma notificação (RF-48).
- [ ] Conquistas são apenas cosméticas/motivacionais — nunca alteram cálculos financeiros, score (RF-41) ou permissões do usuário.

## 2. Requisitos Não Funcionais (RNF)

*Descrevem como o sistema se comporta: restrições e qualidades do produto.*

| ID | Categoria | Prioridade | Requisito | Enunciado EARS |
|---|---|---|---|---|
| RNF-01 | Segurança | Must have | Dados sensíveis (senha, dados financeiros) devem trafegar via HTTPS e ser armazenados de forma criptografada | Ubiquitous. THE SYSTEM SHALL transmitir dados sensíveis via HTTPS e armazená-los criptografados, com senhas protegidas por hash e salt. |
| RNF-02 | Privacidade / LGPD | Should have | Tratamento de dados financeiros pessoais em conformidade com a LGPD, permitindo ao usuário exportar ou excluir seus dados | Ubiquitous. THE SYSTEM SHALL permitir que o usuário, a qualquer momento, exporte seus dados pessoais de forma imediata (RF-50) e solicite a exclusão deles, concluída em até 15 dias corridos (RF-05). |
| RNF-03 | Usabilidade | Should have | Interface responsiva, funcional em navegador desktop e em tela mobile | Ubiquitous. THE SYSTEM SHALL permitir o registro de um lançamento financeiro em, no máximo, 3 passos, em telas desktop e mobile. |
| RNF-04 | Performance | Must have | Simulações de investimento e dashboards devem retornar resultado rapidamente, mesmo com múltiplos cenários/meses comparados | Ubiquitous. THE SYSTEM SHALL responder a simulações e dashboards em menos de 3s em 95% das requisições (P95). |
| RNF-05 | Compatibilidade | Must have | O mesmo backend deve atender simultaneamente o cliente web e o cliente mobile | Ubiquitous. THE SYSTEM SHALL atender simultaneamente o cliente web e o cliente mobile a partir do mesmo backend. |
| RNF-06 | Escalabilidade / extensibilidade | Should have | Arquitetura modular, permitindo adicionar novas abas sem reescrever módulos existentes | Ubiquitous. THE SYSTEM SHALL permitir a adição de um novo módulo funcional sem exigir alteração de código dos módulos existentes. |
| RNF-07 | Manutenibilidade | Must have | Código organizado em camadas, com cobertura de testes automatizados nas regras de cálculo financeiro | Ubiquitous. THE SYSTEM SHALL manter cobertura de testes automatizados de, no mínimo, 80% nas regras de cálculo financeiro. |
| RNF-08 | Disponibilidade | Could have | Sistema acessível sempre que o usuário tentar utilizá-lo | Ubiquitous. THE SYSTEM SHALL manter disponibilidade mínima de 99,5% no mês. |
| RNF-09 | Atualidade de dados de mercado | Should have | Indicadores oficiais e cotações não devem ficar defasados além de um limite definido, com a defasagem sempre visível | Ubiquitous. THE SYSTEM SHALL exibir indicadores oficiais com defasagem máxima de 24h e cotações com defasagem máxima de 15 minutos, sempre visível ao usuário. |
| RNF-10 | Ciclo de vida de dados externos | Should have | Metadados de documentos e indicadores sincronizados de fontes externas devem ter expurgo automático conforme política de retenção (RB-12), sem exigir ação manual | Ubiquitous. THE SYSTEM SHALL expurgar metadados e indicadores sincronizados de fontes externas 12 meses após a sincronização, sem exigir ação manual. |
| RNF-11 | Acessibilidade | Should have | Interface deve seguir as diretrizes WCAG 2.1 nível AA | Ubiquitous. THE SYSTEM SHALL atender ao nível AA das diretrizes WCAG 2.1 em contraste, navegação por teclado e leitura por leitor de tela. |
| RNF-12 | Observabilidade | Should have | Backend deve ter logging estruturado e monitoramento de erros em produção, com alertas para falhas críticas | Ubiquitous. THE SYSTEM SHALL registrar logs estruturados e reportar 100% dos erros não tratados em produção a um serviço de monitoramento. |
| RNF-13 | Proteção da API | Must have | Endpoints devem ter rate limiting para mitigar abuso e ataques de força bruta (complementa RF-02) | Ubiquitous. THE SYSTEM SHALL limitar cada cliente a, no máximo, 100 requisições por minuto por endpoint sensível. |
| RNF-14 | Backup e recuperação | Should have | Banco de dados deve ter backup automático periódico com plano de recuperação testado | Ubiquitous. THE SYSTEM SHALL executar backup automático diário do banco de dados, com RPO de 24h e RTO de 4h. |
| RNF-15 | Documentação de API | Should have | A API deve ter documentação viva gerada automaticamente, mantida sincronizada com o código | Ubiquitous. THE SYSTEM SHALL disponibilizar documentação OpenAPI/Swagger sincronizada com a versão publicada da API. |
| RNF-16 | Qualidade contínua | Must have | Pipeline de CI deve rodar testes automatizados e lint em cada pull request, bloqueando merge em caso de falha | Ubiquitous. THE SYSTEM SHALL bloquear o merge de um pull request quando os testes automatizados ou o lint falharem no pipeline de CI. |
| RNF-17 | Versionamento de API | Must have | A API deve ser versionada desde o início para permitir evolução sem quebrar clientes existentes | Ubiquitous. THE SYSTEM SHALL expor todos os endpoints sob um prefixo de versão (ex.: `/api/v1`). |
| RNF-18 | Auditoria | Should have | Ações sensíveis devem gerar registro de auditoria imutável — somente inserção, nunca alteração ou exclusão —, com usuário, ação e data/hora (incorpora a antiga RB-19) | Event-driven. WHEN uma ação sensível é executada (exclusão de conta, alteração de dado financeiro, exportação de dados) THE SYSTEM SHALL gerar um registro de auditoria imutável com usuário, ação e data/hora, permitindo somente inserção (nunca alteração ou exclusão). |
| RNF-19 | Personalização visual | Could have | O sistema deve oferecer tema claro e escuro, com a preferência salva por usuário | Optional feature. WHERE o usuário seleciona o tema escuro THE SYSTEM SHALL aplicar e persistir esse tema em todas as telas. |
| RNF-20 | Internacionalização (i18n) | Should have | A interface deve suportar português (padrão) e inglês, com todos os textos externalizados desde o início | Ubiquitous. THE SYSTEM SHALL disponibilizar toda a interface em português e em inglês, sem texto fixo no código. |
| RNF-21 | Isolamento administrativo | Should have | Rotas administrativas devem ficar isoladas, com verificação de papel no backend em toda requisição — nunca apenas ocultadas na interface (incorpora a antiga RB-21) | Ubiquitous. THE SYSTEM SHALL exigir, no backend, verificação de papel de administrador em toda requisição às rotas sob o prefixo `/api/v1/admin`. |
| RNF-22 | Modo offline (mobile) | Could have | Lançamentos feitos no cliente mobile sem conexão devem ser sincronizados automaticamente ao voltar a conexão, sem perda de dados | State-driven. WHILE o cliente mobile estiver sem conexão THE SYSTEM SHALL armazenar localmente os lançamentos realizados.<br>Event-driven. WHEN o cliente mobile recupera a conexão após operar offline THE SYSTEM SHALL sincronizar os lançamentos pendentes com o backend em até 60 segundos, sem duplicar ou perder registros. |
| RNF-23 | Segurança de integrações | Could have | O payload de todo webhook deve ser assinado com HMAC usando um segredo exclusivo por integração (incorpora a antiga RB-20) | Ubiquitous. THE SYSTEM SHALL assinar o payload de todo webhook com HMAC, usando um segredo exclusivo por integração. |

> **Critério de prioridade dos RNF (MoSCoW):** *Must have* — necessário para entregar os RF *Must have*: citado por spec aprovada (SPEC-001, SPEC-002), declarado como restrição ou item obrigatório na stack (`/docs/01-visao/visao.md`, seção 3) ou exigido pela disciplina (CI bloqueando merge); *Should have* — qualidade relevante, cuja funcionalidade associada não é *Must have* (ex.: RNF-02 depende de RF-05 e RF-50); *Could have* — pós-MVP.

> **Mensurável:** todo RNF acima carrega um número ou condição verificável (percentual, tempo, contagem) — sem isso, vira bullet de proposta, não requisito testável.

## 3. Regras de Negócio (RB)

*Descrevem políticas e restrições do domínio.*

| ID | Regra | Origem |
|---|---|---|
| RB-01 | Todo valor de renda ou despesa lançado deve ser maior que zero (bônus/PLR pode ser zero) | RF-06, RF-07, RF-08, RF-09 |
| RB-02 | Cada despesa pertence a exatamente uma categoria | RF-10 |
| RB-03 | ~~Saldo, dashboards e progresso de metas são recalculados automaticamente a cada inclusão, edição ou exclusão de lançamento~~ **Reclassificada → RF-09/RF-11** (comportamento do sistema, não regra do domínio) | RF-11 |
| RB-04 | Limite disponível do cartão = limite total − fatura do ciclo atual | RF-13 |
| RB-05 | Renda total do mês = renda fixa + renda variável do mês + bônus/PLR recebido no mês | RF-06, RF-07, RF-08, RF-18 |
| RB-06 | Bônus/PLR anual é integralmente atribuído ao mês de referência informado, sem diluição automática | RF-08 |
| RB-07 | Simulações de renda fixa usam juros compostos indexados a CDI, Selic ou IPCA conforme o produto | RF-20 |
| RB-08 | Toda projeção de renda variável deve ser exibida como estimativa, sem garantia de retorno | RF-21 |
| RB-09 | O resultado do quiz de perfil define a experiência exibida no simulador | RF-03 |
| RB-10 | M = P × (1 + i)ⁿ + Σ aportes capitalizados; taxa convertida entre mês/ano por equivalência composta, nunca proporcional simples | RF-22 |
| RB-11 | ~~Quando a API oficial de indicadores falhar, usa-se o último valor em cache com aviso visual de defasagem — nunca um valor zerado ou inventado~~ **Reclassificada → RF-23** (tratamento de falha do sistema, cláusula IF/THEN) | RF-23 |
| RB-12 | Documentos completos (PDF) nunca são armazenados — apenas linkados; metadados e indicadores extraídos são mantidos em cache por no máximo 12 meses e depois expurgados | RF-30, RF-32, RF-33 |
| RB-13 | Patrimônio líquido = soma dos ativos − soma dos passivos, recalculado a cada mudança em Administração Financeira, Simulador de Investimentos, Compras Financiadas ou lançamento manual | RF-35 |
| RB-14 | No mapa de calor patrimonial, a cor do passivo é proporcional à sua taxa de juros e a cor do ativo é proporcional à sua rentabilidade (mais rentável = verde mais escuro) | RF-37 |
| RB-15 | O score de saúde financeira é educativo, não constitui recomendação financeira, e sua fórmula de ponderação deve ser documentada e configurável | RF-41 |
| RB-16 | Ao confirmar uma compra financiada como real, o saldo devedor vira passivo automático no Patrimônio | RF-47 |
| RB-17 | O stress test de renda é uma simulação isolada — nunca altera dados reais do usuário | RF-39 |
| RB-18 | O progresso de uma meta nomeada é sempre igual ao valor atual do ativo vinculado a ela | RF-40 |
| RB-19 | ~~Todo registro de auditoria é imutável — somente inserção, nunca alteração ou exclusão~~ **Reclassificada → RNF-18** (restrição técnica) | RNF-18 |
| RB-20 | ~~O payload de todo webhook deve ser assinado com HMAC usando um segredo exclusivo por integração~~ **Reclassificada → RNF-23** (restrição técnica de segurança) | RF-53 |
| RB-21 | ~~Acesso a qualquer rota/endpoint administrativo é validado no backend por papel (role=administrador); nunca apenas escondido na interface~~ **Reclassificada → RNF-21** (restrição técnica de segurança) | RF-54 |
| RB-22 | O painel administrativo nunca exibe dados financeiros individuais de um usuário específico — apenas metadados de conta e métricas agregadas de uso | RF-55, RF-57 |
| RB-23 | Eventos de uso não armazenam conteúdo financeiro — apenas usuário, módulo, ação e timestamp | RF-59 |
| RB-24 | O saldo "quem deve quem" de uma conta compartilhada é recalculado a cada despesa compartilhada incluída, editada, excluída ou acerto de contas registrado | RF-61 |
| RB-25 | A estimativa de IR usa tabela de alíquotas interna e configurável, variando por tipo de aplicação e prazo — nunca chamada em tempo real à Receita Federal | RF-64 |
| RB-26 | O benchmark anônimo nunca expõe dados ou indicadores de um usuário individual identificável — apenas médias/percentis de grupos com tamanho mínimo definido | RF-66 |

> **Reclassificação:** uma regra de negócio descreve uma política do domínio que existiria mesmo sem o sistema. RB-03 e RB-11 descreviam comportamento do sistema (passaram para os RF indicados) e RB-19, RB-20 e RB-21 descreviam restrições técnicas (passaram para RNF). Os IDs foram mantidos, sem renumeração, para preservar a rastreabilidade.

---

## 4. Modelo de Dados (visão geral)

```
Usuario (id, nome, email, senha_hash, perfil_investidor, idioma, tema, papel[usuario|administrador])
  1─N Conta            (id, usuario_id, nome, tipo, saldo_inicial)
  1─N Cartao           (id, usuario_id, nome, limite, dia_fechamento, dia_vencimento)
  1─N Categoria        (id, usuario_id | null p/ padrão, nome, cor, ativa)
  1─N RendaFixa        (id, usuario_id, conta_id | cartao_id, descricao, valor, ativa_desde)
  1─N RendaVariavel    (id, usuario_id, conta_id | cartao_id, descricao, valor, data)
  1─N BonusPLR         (id, usuario_id, conta_id | cartao_id, valor, periodicidade[mensal|anual], mes_referencia)
  1─N Despesa          (id, usuario_id, conta_id | cartao_id, categoria_id, valor, data, recorrente)
  1─N MetaGeral        (id, usuario_id, tipo[renda|gasto], valor, vigente_desde)
  1─N MetaCategoria    (id, usuario_id, categoria_id, valor_maximo, vigente_desde)
  1─N Simulacao        (id, usuario_id, indicador_oficial_id | null, tipo, parametros, resultado, criada_em)
  1─N MetaFinanceira   (id, usuario_id, valor_alvo, prazo, rendimento_estimado)
  1─N Ativo            (id, usuario_id, tipo[conta|investimento|manual], descricao, valor, rentabilidade, origem[automatico|manual])
  1─N Passivo          (id, usuario_id, tipo[fatura|financiamento|divida_manual], descricao, valor, taxa_juros, origem[automatico|manual])
  1─N ScoreSaude       (id, usuario_id, valor, fatores[json], calculado_em)
  1─N CompraFinanciada (id, usuario_id, descricao, valor_bem, entrada, parcelas, taxa_juros, status[simulacao|ativo|quitado])
  1─N Notificacao      (id, usuario_id, tipo, mensagem, lida, criada_em)
  1─N MetaNomeada      (id, usuario_id, ativo_id, nome, categoria, valor_alvo, prazo)
  1─N AuditLog         (id, usuario_id, acao, entidade, entidade_id, criado_em)  -- imutável
  1─N WebhookSubscription (id, usuario_id, url, eventos[json], segredo_hmac, ativo)
  1─N EventoUso        (id, usuario_id, modulo, acao, criado_em)

IndicadorOficial (id, tipo[selic|cdi|ipca|tesouro_direto], titulo, taxa, data_referencia, atualizado_em)  -- cache local (RF-23, ADR-003)

EmpresaAberta (id, ticker, cnpj, razao_social, setor)
  1─N DocumentoCVM     (id, empresa_id, tipo[DFP|ITR|FRE|IPE], periodo_referencia, data_entrega, status, url_documento_oficial, sincronizado_em)
  1─N IndicadorFinanceiro (id, empresa_id, tipo[receita_liquida|lucro_liquido|patrimonio_liquido|...], periodo, valor, sincronizado_em)
  1─N Watchlist        (id, usuario_id, empresa_id, criada_em)

ConteudoEducacional (id, termo, categoria, texto, nivel[iniciante|avancado])

ContaCompartilhada  (id, usuario_a_id, usuario_b_id, criada_em, status[pendente|ativa|desfeita])
  1─N DespesaCompartilhada (id, conta_compartilhada_id, despesa_id, usuario_pagou_id, divisao[igual|percentual], percentual_pagador)
  1─N AcertoConta     (id, conta_compartilhada_id, usuario_pagou_id, valor, criado_em)

Badge (id, usuario_id, tipo, conquistada_em)
```

> `Simulacao.tipo` é estendido para incluir `aposentadoria` (RF-62), `previdencia_comparador` (RF-63) e `ir_estimativa` (RF-64) — reaproveita a tabela genérica existente, sem novas entidades específicas por simulação.

> `EventoUso` alimenta os dashboards administrativos (RF-57, RF-58) e nunca contém dado financeiro (RB-23); consultas do painel administrativo sempre agregam por módulo/período, sem expor o comportamento individual nominal de um usuário (RB-22).

> `DocumentoCVM` e `IndicadorFinanceiro` guardam apenas metadados/números e um link externo — nunca o binário do PDF (RB-12) — e têm expurgo automático 12 meses após `sincronizado_em` (RF-33). `Ativo` e `Passivo` alimentam RF-35 e RF-37; entradas com `origem=automatico` são espelhos somente-leitura de Conta/Simulacao/Fatura/CompraFinanciada, recalculados a cada mudança na origem (RB-13).

## 5. Interfaces Externas / Integrações

| Sistema | Tipo | Uso |
|---|---|---|
| Banco Central do Brasil — SGS (`api.bcb.gov.br/dados/serie`) | API pública oficial | Selic, CDI e IPCA para simulações de renda fixa (RF-20, RF-23) |
| Tesouro Transparente (`www.tesourotransparente.gov.br`) | API pública oficial | Taxas e preços de títulos do Tesouro Direto (RF-20, RF-23) |
| Provedor de dados de mercado (a definir — provedor homologado ou agregador de dados da B3) | API externa | Cotação e histórico de ações/FIIs para renda variável (RF-21, RF-24) |
| Portal de Dados Abertos da CVM (`dados.cvm.gov.br`) | Download público (CSV/ZIP) | Metadados de documentos e indicadores estruturados de DFP/ITR/IPE (RF-30, RF-32) |
| RAD/ENET — CVM (`rad.cvm.gov.br`) | Link externo (não é API de dados) | Acesso do usuário ao documento oficial completo (RF-31) |
| Firebase Cloud Messaging (ou similar) | API externa | Envio de notificações push (RF-49) |
| Serviço de e-mail transacional (ex.: SES/SendGrid) | API externa | Envio de notificações por e-mail (RF-49) |
| Sentry (ou similar) | SaaS de observabilidade | Monitoramento de erros em produção (RNF-12) |
| Banco Central do Brasil — PTAX (`olinda.bcb.gov.br/olinda/servico/PTAX`) | API pública oficial | Taxas de câmbio para simulação em moeda estrangeira (RF-28) |

## 6. Premissas e Dependências

- As simulações são projeções educativas; o sistema não executa operações reais nem oferece recomendação de investimento.
- Os lançamentos financeiros (renda e despesa) são inseridos manualmente pelo usuário (sem Open Finance no MVP).
- Indicadores de renda fixa (Selic, CDI, IPCA, Tesouro Direto) usam as APIs públicas oficiais do Banco Central (SGS) e do Tesouro Transparente — não exigem contrato comercial.
- Cotações de ações e FIIs **não** têm API pública gratuita oficial da B3; será necessário contratar/homologar um provedor de dados de mercado ou usar um agregador — decisão técnica pendente antes de implementar RF-24.
- Bônus/PLR anual não é diluído automaticamente nos dashboards mensais; aparece integralmente no mês de referência.
- O sistema não republica o conteúdo integral dos relatórios (PDF) das empresas — apenas metadados, indicadores estruturados (dados abertos de reuso livre) e link direto para a fonte oficial, evitando questão de direitos autorais sobre o texto redigido pela empresa emissora.
- Metadados e indicadores sincronizados da CVM são retidos por no máximo 12 meses (RF-33); após esse prazo, uma nova consulta refaz a sincronização com a fonte oficial.
- O Simulador de Compras Financiadas passou de "módulo futuro" para o backlog do MVP (Could have), a pedido do usuário.
- A regra de cores do mapa de calor patrimonial (RF-37 — passivo por taxa de juros, ativo por rentabilidade) é um padrão sugerido e pode ser ajustada após validação com o usuário final.
- A API pública e os webhooks (RF-52, RF-53) são recursos adicionais opcionais — não bloqueiam o núcleo do app caso fiquem para depois do MVP.
- Internacionalização (RNF-20) sendo aplicada desde o início evita retrabalho de extrair textos hardcoded mais tarde.
- Contas Compartilhadas (RF-60/61) dependem de vínculo manual entre dois usuários já cadastrados — não há convite para não-usuários nem integração com conta conjunta bancária real.
- A estimativa de IR (RF-64) e o comparador de previdência (RF-63) usam tabelas de alíquotas simplificadas e configuráveis internamente — não substituem apuração de contador nem consulta ao e-CAC da Receita Federal, e não constituem aconselhamento tributário.
- O benchmark anônimo (RF-66) só é exibido quando o grupo de comparação atinge o tamanho mínimo definido; abaixo disso, a comparação fica oculta para preservar o anonimato.
- Gamificação (RF-67) é puramente cosmética/motivacional e não deve, em nenhuma hipótese, influenciar cálculos financeiros, o score (RF-41) ou permissões de acesso.

## 7. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Cálculo financeiro incorreto (juros, IR, agregação de renda) | Alto — perda de confiança do usuário | Testes automatizados nas regras de cálculo (RNF-07) e validação contra simuladores de referência |
| Indisponibilidade da fonte de indicadores | Médio — simulação sem dados atualizados | Cache local do último valor conhecido e aviso da data de referência |
| Escopo do MVP inflar com módulos/abas futuras | Médio — atraso na entrega | Manter backlog priorizado por MoSCoW e congelar escopo do MVP por aba |
| Tratamento inadequado de dados pessoais | Alto — risco legal (LGPD) | Criptografia, HTTPS e funcionalidades de exportação/exclusão (RNF-01, RNF-02) |
| Usuário interpretar projeção como garantia | Médio | Avisos explícitos de projeção em toda simulação (RB-08) |
| Bônus/PLR anual distorcer gráfico mensal (pico artificial) | Baixo/Médio — leitura equivocada do dashboard | Indicar visualmente no gráfico quando o mês contém bônus/PLR |
| Ausência de API pública gratuita e oficial da B3 para cotações | Alto — RF-24 pode não sair do papel sem provedor definido | Pesquisar e homologar provedor de dados de mercado antes do sprint de renda variável; ter fallback manual (RF-21) |
| Instabilidade/rate limit da API do Banco Central (SGS) em picos de uso | Médio — simulação com dado desatualizado | Cache local (RF-23) e atualização assíncrona, não bloqueando a simulação |
| CVM alterar a estrutura/endereço do RAD-ENET (já ocorreu em jul/2026) e quebrar links salvos | Médio — links de RF-31 param de funcionar | Rotina periódica de verificação de links (RF-31) e, como os dados expiram em 12 meses (RF-33), o link é re-obtido na próxima sincronização |
| Rota de "Download Múltiplo" da CVM exigir credencial própria | Baixo — não bloqueia o MVP | Usar os arquivos públicos em CSV/ZIP do portal de dados abertos (sem necessidade de credencial) como fonte primária para RF-32 |
| Excesso de módulos aumentar complexidade e atraso de entrega | Médio/Alto — MVP não sai no prazo | Priorizar rigorosamente por MoSCoW (ver backlog em /docs/01-visao/visao.md) e tratar módulos "Could have" como pós-MVP se necessário |
| Notificações em excesso gerarem fadiga/desengajamento do usuário | Médio — usuário desativa tudo ou abandona o app | Configuração granular por tipo de notificação (RF-48) e limites de frequência |
| Score de saúde financeira ser interpretado como aconselhamento financeiro | Médio — risco reputacional/regulatório | Aviso explícito de caráter educativo em toda exibição do score (RB-15) |
| Regra de cor do mapa de calor patrimonial não refletir a expectativa do usuário final | Baixo | Validar com testes de usabilidade antes de fechar a regra definitiva (ver premissa correspondente) |
| Webhook mal configurado/exposto vazar dados sensíveis do usuário | Médio — risco de segurança/privacidade | Assinatura HMAC obrigatória (RNF-23), escopo mínimo de dados no payload e possibilidade de revogar a URL cadastrada |
| Manter conteúdo em PT e EN sincronizado aumentar o esforço de manutenção | Baixo/Médio | Biblioteca de i18n com fallback para PT-BR; revisão de tradução apenas no conteúdo essencial no MVP |
| Painel administrativo expor dados financeiros sensíveis de usuários | Alto — risco de privacidade/LGPD | Restringir a metadados e métricas agregadas (RB-22), aplicar as mesmas proteções de RNF-01 e registrar todo acesso em auditoria (RNF-18) |
| Falha de autorização permitir usuário comum acessar rotas administrativas | Alto — vazamento de dados de todos os usuários | Validação de papel obrigatória no backend em toda rota admin (RNF-21), coberta por testes automatizados dedicados |
| Estimativa de IR (RF-64) divergir do valor real apurado pelo usuário/contador | Médio — decisão financeira baseada em número impreciso | Tabela de alíquotas versionada e revisável, aviso explícito de caráter educativo em toda tela de IR (mesmo padrão de RB-15) |
| Divisão de despesas compartilhadas gerar disputa entre os dois usuários vinculados (valor ou percentual contestado) | Baixo/Médio — insatisfação, abandono do recurso | Histórico completo e auditável de cada despesa compartilhada e acerto de contas, com valores sempre visíveis aos dois usuários |
| Grupo de benchmark pequeno demais permitir reidentificação indireta de um usuário | Médio — risco de privacidade | Tamanho mínimo de grupo obrigatório para exibir a comparação (RB-26), sem exceção configurável abaixo do limite |

## 8. Glossário

| Termo | Definição |
|---|---|
| PLR | Participação nos Lucros e Resultados; bonificação vinculada ao desempenho da empresa/funcionário |
| CDI | Certificado de Depósito Interbancário; principal referência de rentabilidade da renda fixa privada no Brasil |
| Selic | Taxa básica de juros da economia brasileira |
| IPCA | Índice de Preços ao Consumidor Amplo; índice oficial de inflação |
| CDB | Certificado de Depósito Bancário; título de renda fixa emitido por bancos |
| Tesouro Direto | Programa de venda de títulos públicos federais a pessoas físicas |
| FII | Fundo de Investimento Imobiliário |
| IR | Imposto de Renda incidente sobre o rendimento de aplicações financeiras |
| Renda fixa (dashboard) | Renda recorrente e previsível do usuário (ex.: salário) |
| Renda variável (dashboard) | Renda não recorrente ou de valor incerto (ex.: freelas, comissões) |
| Renda fixa (investimento) | Investimento cuja regra de remuneração é conhecida no momento da aplicação |
| Renda variável (investimento) | Investimento cujo retorno não é previsível, sujeito à oscilação de mercado |
| SGS | Sistema Gerenciador de Séries Temporais do Banco Central; API oficial de indicadores econômicos (Selic, CDI, IPCA, entre outros) |
| B3 | Bolsa de valores oficial do Brasil (Brasil Bolsa Balcão); não expõe API pública gratuita de cotações |
| Ticker | Código curto que identifica um ativo negociado em bolsa (ex.: PETR4, MXRF11) |
| CVM | Comissão de Valores Mobiliários; órgão regulador do mercado de capitais brasileiro |
| DFP | Demonstrações Financeiras Padronizadas; relatório financeiro anual obrigatório das empresas de capital aberto |
| ITR | Informações Trimestrais; relatório financeiro trimestral obrigatório das empresas de capital aberto |
| FRE | Formulário de Referência; documento anual com informações detalhadas sobre a empresa, administração e riscos |
| IPE | Informações Periódicas e Eventuais; categoria de documentos que as empresas enviam à CVM, além das demonstrações financeiras |
| RAD/ENET | Sistema oficial da CVM onde as empresas enviam e o público consulta os documentos de divulgação obrigatória |
| Perfil de investidor | Classificação do usuário quanto a conhecimento e tolerância a risco |
| LGPD | Lei Geral de Proteção de Dados (Lei nº 13.709/2018) |
| MVP | Minimum Viable Product; menor versão funcional que entrega valor |
| Patrimônio líquido | Diferença entre o total de ativos e o total de passivos de uma pessoa |
| Ativo | Bem ou direito que gera valor ou pode ser convertido em dinheiro (ex.: saldo em conta, investimento) |
| Passivo | Obrigação financeira ou dívida (ex.: fatura em aberto, financiamento) |
| Treemap | Gráfico que representa proporção através de retângulos, com tamanho e cor codificando valores |
| Volatilidade | Medida estatística (desvio padrão) da variação de retorno de um ativo ao longo do tempo |
| Índice de Sharpe | Métrica de retorno ajustado ao risco: (retorno do ativo − taxa livre de risco) / volatilidade |
| Taxa livre de risco | Retorno de um investimento considerado sem risco de crédito (no Brasil, geralmente a Selic) |
| WCAG | Web Content Accessibility Guidelines; diretrizes internacionais de acessibilidade para conteúdo web |
| Rate limiting | Técnica que limita o número de requisições que um cliente pode fazer a uma API em um período |
| CI/CD | Continuous Integration / Continuous Deployment; práticas de integração e entrega contínua de software |
| OpenAPI/Swagger | Padrão de documentação de APIs REST, gerado automaticamente a partir do código |
| Tabela Price | Sistema de amortização de financiamento com parcelas mensais fixas |
| PTAX | Taxa de câmbio oficial divulgada pelo Banco Central do Brasil |
| Webhook | Mecanismo de notificação HTTP automática entre sistemas quando um evento ocorre |
| HMAC | Hash-based Message Authentication Code; usado para assinar e verificar a autenticidade de mensagens |
| i18n | Abreviação de "internationalization"; suporte de um sistema a múltiplos idiomas |
| Onboarding | Processo de introdução guiada de um novo usuário a um produto |
| Audit log | Registro imutável de ações realizadas no sistema, usado para auditoria e rastreabilidade |
| RBAC | Role-Based Access Control; modelo de controle de acesso baseado em papéis (ex.: usuário comum vs. administrador) |
| PGBL | Plano Gerador de Benefício Livre; plano de previdência privada com dedução no IR (declaração completa), tributação sobre o valor total resgatado |
| VGBL | Vida Gerador de Benefício Livre; plano de previdência privada sem dedução no IR, tributação apenas sobre o rendimento |
| DARF | Documento de Arrecadação de Receitas Federais; guia usada para recolher impostos como o IR sobre operações de renda variável |
| DAU / WAU / MAU | Daily/Weekly/Monthly Active Users; métricas de usuários ativos por dia, semana ou mês, usadas para medir engajamento |

### 8.1 Termos do domínio (vocabulário obrigatório)

Nomes usados em código, specs e documentação, alinhados às classes de `/docs/modelo-dominio.md` (regra C-14 de `CLAUDE.md`).

| Termo | Classe | Definição |
|---|---|---|
| Usuário | `Usuario` | Pessoa cadastrada que usa a plataforma; dona dos lançamentos e simulações |
| Conta | `Conta` | Conta bancária ou carteira do usuário, com saldo inicial e saldo atual |
| Cartão | `Cartao` | Cartão de crédito do usuário, com limite, fechamento e vencimento |
| Categoria | `Categoria` | Classificação de despesas; **padrão** (comum a todos, sem dono) ou **personalizada** (de um usuário) |
| Lançamento | `Renda` ou `Despesa` | Registro de entrada ou saída de dinheiro informado pelo usuário |
| Renda | `Renda` | Entrada de dinheiro do usuário: renda fixa, renda variável ou bônus/PLR |
| Despesa | `Despesa` | Saída de dinheiro, ligada a exatamente uma categoria; **recorrente** ou **pontual** |
| Renda total do mês | `Renda` (`calcularContribuicaoMensal()`) | Soma das contribuições mensais da renda fixa, da renda variável do mês e do bônus/PLR recebido no mês (RB-05) |
| Simulação | `Simulacao` | Projeção educativa de um investimento, guardada com seus parâmetros; de renda fixa ou de renda variável no V1 |
| Indicador oficial | `IndicadorOficial` | Taxa oficial (Selic, CDI, IPCA ou título do Tesouro Direto) guardada em cache com data de referência |
| Indicador financeiro | `IndicadorFinanceiro` | Número extraído das demonstrações de uma empresa aberta (CVM); não confundir com indicador oficial |
| Data de referência | atributo de `IndicadorOficial` | Data a que a taxa oficial se refere; exibida em toda simulação que a usa |
| Taxa equivalente composta | operação de `Simulacao` | Conversão de taxa entre períodos por `(1 + i)^n − 1`, nunca por divisão simples (RB-10) |
| Aporte mensal | atributo de `Simulacao` | Valor investido ao fim de cada mês da simulação |
| Comparação de cenários | operação sobre `Simulacao` | Exibição lado a lado de duas ou mais simulações do mesmo usuário (RF-25) |
