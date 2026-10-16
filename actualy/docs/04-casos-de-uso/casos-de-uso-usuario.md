# FinNova — Casos de Uso do Usuário

## Visão geral

Este documento descreve os casos de uso disponíveis para o usuário da plataforma FinNova, incluindo o gerenciamento da conta, a administração financeira pessoal, as simulações de investimentos, os relatórios de empresas, o acompanhamento do patrimônio e os recursos transversais.

## Diagrama

![Diagrama de casos de uso do usuário](casos-de-uso-usuario.png)

## Atores

- **Usuário**: utiliza a plataforma para administrar suas finanças, consultar informações e realizar simulações.
- **Usuário vinculado (conta compartilhada)**: papel assumido por um usuário cadastrado que participa de uma associação de conta compartilhada para divisão de despesas.
- **API Banco Central (SGS) e Tesouro Transparente**: fornece indicadores oficiais para as simulações.
- **Portal de Dados Abertos da CVM / RAD-ENET**: fornece dados e documentos oficiais de empresas.
- **Serviço de notificação (push / e-mail)**: entrega notificações e alertas ao usuário.

## Casos de uso

### Conta e Acesso

| Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- |
| Cadastrar-se | RF-01 | Permite criar uma conta na plataforma. |
| Autenticar-se | RF-02 | Permite acessar a plataforma com uma conta cadastrada. |
| Responder quiz de perfil de investidor | RF-03 | Coleta informações para identificar o perfil de investidor do usuário. |
| Excluir conta e dados | RF-05 | Permite solicitar a exclusão da conta e dos dados associados. |

### Administração Financeira

| Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- |
| Registrar renda fixa, variável e bônus/PLR | RF-06, RF-07, RF-08 | Permite registrar diferentes fontes e tipos de renda. |
| Gerenciar categorias de gasto | RF-10 | Permite criar, editar e organizar categorias de despesas. |
| Gerenciar contas e cartões | RF-12, RF-13 | Permite cadastrar e administrar contas e cartões financeiros. |
| Definir metas de renda e de gasto | RF-14, RF-15 | Permite definir objetivos para receitas e despesas. |
| Consultar dashboards financeiros | RF-16 a RF-19 | Exibe uma visão consolidada da situação financeira do usuário. |
| Dividir despesa compartilhada | RF-60, RF-61 | Permite dividir uma despesa com um usuário vinculado à conta compartilhada. |
| Registrar despesa por categoria | RF-09, RF-11 | Registra uma despesa e associa a ela uma categoria. |

### Simulador de Investimentos

| Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- |
| Comparar cenários de investimento | RF-25 | Usuário | Permite comparar os resultados de diferentes cenários de investimento. |
| Simular investimento em renda fixa | RF-20 | Usuário; API Banco Central e Tesouro Transparente | Simula a evolução de um investimento de renda fixa. |
| Simular investimento em renda variável | RF-21 | Usuário; API Banco Central e Tesouro Transparente | Simula cenários de investimento em renda variável. |
| Projetar objetivo financeiro | RF-26 | Usuário | Permite projetar a evolução necessária para atingir um objetivo financeiro. |
| Obter indicador oficial (Selic, CDI, IPCA) | RF-23 | API Banco Central e Tesouro Transparente | Obtém os indicadores oficiais usados nas simulações. |
| Calcular juros compostos | RF-22 | Usuário | Calcula a evolução dos valores applied com base em juros compostos. |
| Usar último valor em cache | RB-11 | Sistema | Usa o último valor conhecido quando a API oficial estiver indisponível. |

### Relatórios de Empresas

| Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- |
| Buscar empresa listada em bolsa | RF-29 | Usuário | Permite localizar uma empresa listada na bolsa de valores. |
| Consultar documentos oficiais da empresa | RF-30, RF-31 | Portal de Dados Abertos da CVM / RAD-ENET | Permite consultar documentos oficiais e acessar seus links de origem. |
| Gerenciar watchlist de empresas | RF-34 | Usuário | Permite acompanhar uma lista personalizada de empresas. |

### Patrimônio e Score

| Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- |
| Simular cenário hipotético ("e se...") | RF-39 | Permite avaliar cenários hipotéticos para o patrimônio e a vida financeira. |
| Consultar score de saúde financeira | RF-41, RF-42 | Exibe uma avaliação consolidada da saúde financeira do usuário. |
| Consultar patrimônio e mapa de calor | RF-35, RF-37 | Exibe o patrimônio do usuário e sua distribuição em um mapa de calor. |

### Recursos Transversais

| Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- |
| Receber notificações e alertas | RF-48, RF-49 | Serviço de notificação (push / e-mail) | Entrega notificações e alertas relevantes ao usuário. |
| Exportar dados pessoais | RF-50 | Usuário | Permite exportar os dados pessoais mantidos pela plataforma. |
| Consultar conteúdo educacional | RF-43, RF-44 | Usuário | Permite acessar conteúdos de educação financeira. |

## Relações entre os casos de uso

- **Dividir despesa compartilhada** estende **Registrar despesa por categoria**.
- **Comparar cenários de investimento** inclui **Simular investimento em renda fixa**.
- **Simular investimento em renda fixa** e **Simular investimento em renda variável** incluem **Obter indicador oficial (Selic, CDI, IPCA)** e **Calcular juros compostos**, quando aplicável.
- **Usar último valor em cache** estende **Obter indicador oficial (Selic, CDI, IPCA)** quando a consulta à fonte oficial falha.
- **Consultar score de saúde financeira** inclui **Consultar patrimônio e mapa de calor**.
- **Consultar documentos oficiais da empresa** depende do **Portal de Dados Abertos da CVM / RAD-ENET**.
- **Receber notificações e alertas** utiliza o **Serviço de notificação (push / e-mail)**.
- Todos os casos de uso, exceto **Cadastrar-se**, exigem que o usuário esteja autenticado.

## Regras de negócio e requisitos não funcionais

- **RF-02 — Pré-condição:** todos os casos de uso, exceto **Cadastrar-se**, exigem usuário autenticado.
- **RB-07 / RB-10 — Simular renda fixa:** a indexação à CDI/Selic/IPCA segue o produto; a taxa convertida por equivalência composta, nunca proporcional simples.
- **RB-11 / RNF-09 — Usar último valor em cache:** na falha da API oficial, o sistema usa o último valor conhecido com aviso de defasagem, nunca um valor zerado. A defasagem máxima é de 24 horas e deve estar sempre visível.
- **RB-12 / RNF-10 — Consultar documentos:** o sistema nunca hospeda o PDF; guarda apenas metadados e o link oficial, e expurga os dados sincronizados em 12 meses, conforme o **RF-33**.
- **RB-24 — Dividir despesa compartilhada:** o saldo de "quem deve a quem" é recalculado a cada inclusão, edição, exclusão ou acerto de contas.
- **RNF-01 / RNF-13 — Autenticação:** as senhas são armazenadas com hash e salt, o tráfego utiliza HTTPS e há rate limiting contra força bruta.
- **RNF-02 — Exportar dados:** em conformidade com a LGPD, o usuário pode exportar ou excluir seus dados a qualquer momento.
- **RNF-03 — Registrar lançamento:** o registro de um lançamento financeiro deve ocorrer em no máximo três passos, tanto na web quanto no mobile.

## Relações de Associação e Papéis

O **Usuário vinculado (conta compartilhada)** representa o papel que qualquer **Usuário** autenticado assume quando estabelece um vínculo através da entidade associativa `ContaCompartilhada` (`RF-60`, `RF-61`). Os demais casos de uso são executados pelo **Usuário** individualmente.
