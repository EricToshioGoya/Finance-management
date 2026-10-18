# FinNova — Casos de Uso do Usuário

## Visão geral

Este documento descreve os casos de uso disponíveis para o usuário da plataforma FinNova, incluindo o gerenciamento da conta, a administração financeira pessoal, as simulações de investimentos, os relatórios de empresas, o acompanhamento do patrimônio e os recursos transversais.

Os identificadores `UC-NN` são sequenciais entre este documento (UC-01 a UC-27) e `casos-de-uso-administrador.md` (UC-28 a UC-41). Os casos de uso do fluxo principal do MVP estão descritos em texto, com fluxos e exceções, em `casos-de-uso-detalhados.md`.

## Diagrama

![Diagrama de casos de uso do usuário](casos-de-uso-usuario.png)

Fonte editável (PlantUML): `casos-de-uso-usuario.puml`. Para regenerar a imagem após editar a fonte, a partir de `/docs/04-casos-de-uso/`:

```bash
java -jar plantuml.jar -tpng casos-de-uso-usuario.puml
```

## Atores

- **Usuário**: utiliza a plataforma para administrar suas finanças, consultar informações e realizar simulações.
- **Usuário vinculado (conta compartilhada)**: papel assumido por um usuário cadastrado que participa de uma associação de conta compartilhada para divisão de despesas.
- **API Banco Central (SGS) e Tesouro Transparente**: fornece indicadores oficiais para as simulações.
- **Portal de Dados Abertos da CVM / RAD-ENET**: fornece dados e documentos oficiais de empresas.
- **Serviço de notificação (push / e-mail)**: entrega notificações e alertas ao usuário.

## Casos de uso

### Conta e Acesso

| ID | Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- | --- |
| UC-01 | Cadastrar-se | RF-01 | Permite criar uma conta na plataforma. |
| UC-02 | Autenticar-se | RF-02 | Permite acessar a plataforma com uma conta cadastrada. |
| UC-03 | Responder quiz de perfil de investidor | RF-03 | Coleta informações para identificar o perfil de investidor do usuário. |
| UC-04 | Excluir conta e dados | RF-05 | Permite solicitar a exclusão da conta e dos dados associados. |

### Administração Financeira

| ID | Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- | --- |
| UC-05 | Registrar renda fixa, variável e bônus/PLR | RF-06, RF-07, RF-08 | Permite registrar diferentes fontes e tipos de renda. |
| UC-06 | Gerenciar categorias de gasto | RF-10 | Permite criar, editar e organizar categorias de despesas. |
| UC-07 | Gerenciar contas e cartões | RF-12, RF-13 | Permite cadastrar e administrar contas e cartões financeiros. |
| UC-08 | Definir metas de renda e de gasto | RF-14, RF-15 | Permite definir objetivos para receitas e despesas. |
| UC-09 | Consultar dashboards financeiros | RF-16 a RF-19 | Exibe uma visão consolidada da situação financeira do usuário. |
| UC-10 | Dividir despesa compartilhada | RF-60, RF-61 | Permite dividir uma despesa com um usuário vinculado à conta compartilhada. |
| UC-11 | Registrar despesa por categoria | RF-09, RF-11 | Registra uma despesa e associa a ela uma categoria. |

### Simulador de Investimentos

| ID | Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- | --- |
| UC-12 | Comparar cenários de investimento | RF-25 | Usuário | Permite comparar os resultados de diferentes cenários de investimento. |
| UC-13 | Simular investimento em renda fixa | RF-20 | Usuário; API Banco Central e Tesouro Transparente | Simula a evolução de um investimento de renda fixa. |
| UC-14 | Simular investimento em renda variável | RF-21 | Usuário; API Banco Central e Tesouro Transparente | Simula cenários de investimento em renda variável. |
| UC-15 | Projetar objetivo financeiro | RF-26 | Usuário | Permite projetar a evolução necessária para atingir um objetivo financeiro. |
| UC-16 | Obter indicador oficial (Selic, CDI, IPCA) | RF-23 | API Banco Central e Tesouro Transparente | Obtém os indicadores oficiais usados nas simulações. |
| UC-17 | Calcular juros compostos | RF-22 | Usuário | Calcula a evolução dos valores aplicados com base em juros compostos. |
| UC-18 | Usar último valor em cache | RF-23 | Sistema | Usa o último valor conhecido quando a API oficial estiver indisponível. |

### Relatórios de Empresas

| ID | Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- | --- |
| UC-19 | Buscar empresa listada em bolsa | RF-29 | Usuário | Permite localizar uma empresa listada na bolsa de valores. |
| UC-20 | Consultar documentos oficiais da empresa | RF-30, RF-31 | Portal de Dados Abertos da CVM / RAD-ENET | Permite consultar documentos oficiais e acessar seus links de origem. |
| UC-21 | Gerenciar watchlist de empresas | RF-34 | Usuário | Permite acompanhar uma lista personalizada de empresas. |

### Patrimônio e Score

| ID | Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- | --- |
| UC-22 | Simular cenário hipotético ("e se...") | RF-39 | Permite avaliar cenários hipotéticos para o patrimônio e a vida financeira. |
| UC-23 | Consultar score de saúde financeira | RF-41, RF-42 | Exibe uma avaliação consolidada da saúde financeira do usuário. |
| UC-24 | Consultar patrimônio e mapa de calor | RF-35, RF-37 | Exibe o patrimônio do usuário e sua distribuição em um mapa de calor. |

### Recursos Transversais

| ID | Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- | --- |
| UC-25 | Receber notificações e alertas | RF-48, RF-49 | Serviço de notificação (push / e-mail) | Entrega notificações e alertas relevantes ao usuário. |
| UC-26 | Exportar dados pessoais | RF-50 | Usuário | Permite exportar os dados pessoais mantidos pela plataforma. |
| UC-27 | Consultar conteúdo educacional | RF-43, RF-44 | Usuário | Permite acessar conteúdos de educação financeira. |

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
- **RF-23 / RNF-09 — Usar último valor em cache:** na falha da API oficial, o sistema usa o último valor conhecido com aviso de defasagem, nunca um valor zerado. A defasagem máxima é de 24 horas e deve estar sempre visível.
- **RB-12 / RNF-10 — Consultar documentos:** o sistema nunca hospeda o PDF; guarda apenas metadados e o link oficial, e expurga os dados sincronizados em 12 meses, conforme o **RF-33**.
- **RB-24 — Dividir despesa compartilhada:** o saldo de "quem deve a quem" é recalculado a cada inclusão, edição, exclusão ou acerto de contas.
- **RNF-01 / RNF-13 — Autenticação:** as senhas são armazenadas com hash e salt, o tráfego utiliza HTTPS e há rate limiting contra força bruta.
- **RNF-02 — Exportar dados:** em conformidade com a LGPD, o usuário pode exportar ou excluir seus dados a qualquer momento.
- **RNF-03 — Registrar lançamento:** o registro de um lançamento financeiro deve ocorrer em no máximo três passos, tanto na web quanto no mobile.

## Relações de Associação e Papéis

O **Usuário vinculado (conta compartilhada)** representa o papel que qualquer **Usuário** autenticado assume quando estabelece um vínculo através da entidade associativa `ContaCompartilhada` (`RF-60`, `RF-61`). Os demais casos de uso são executados pelo **Usuário** individualmente.
