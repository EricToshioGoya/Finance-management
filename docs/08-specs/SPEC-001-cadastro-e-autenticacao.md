# SPEC-001: Cadastro de Usuário e Autenticação de Sessão

* **Status:** Aprovada
* **Data:** 2026-10-08
* **Revisão:** 2026-10-18 — correção da rastreabilidade, inclusão das cláusulas EARS (seção 5) e dos cenários 4 e 5.
* **Revisão:** 2026-10-18 (Semana 4) — cláusulas R09 e R10 do bloqueio por tentativas inválidas (decisão da OPEN-02) e cenários 6 e 7 ([#32](https://github.com/EricToshioGoya/Finance-management/issues/32)).
* **Autor:** Equipe FinNova / SDD

---

## 1. Identificação
* **ID:** SPEC-001
* **Nome:** Cadastro de Usuário e Autenticação de Sessão
* **Objetivo:** Permitir que novos usuários se cadastrem com credenciais seguras e realizem login para obter um token de sessão (JWT) de acesso ao sistema.
* **Valor Entregue:** Estabelece o mecanismo fundamental de identidade, segurança e controle de acesso necessário para todas as funcionalidades personalizadas da plataforma.

---

## 2. Rastreabilidade (Baseline)
* **Requisitos Funcionais:** RF-01 (Cadastro de usuário), RF-02 (Login e autenticação)
* **Regras de Negócio:** nenhuma RB do catálogo se aplica diretamente; as restrições de credenciais derivam dos critérios de aceite de RF-01 e RF-02.
* **Requisitos Não Funcionais:** RNF-01 (Criptografia hash + salt em senhas, tráfego HTTPS), RNF-13 (Rate limiting), RNF-17 (Prefixagem `/api/v1`)
* **Casos de Uso:** UC-01 (Cadastrar-se), UC-02 (Autenticar-se) — ver `docs/04-casos-de-uso/casos-de-uso-detalhados.md`
* **Entidades do Domínio:** `Usuario`
* **Drivers e ADRs:** DA-01 e DA-05 (`docs/07-arquitetura/arquitetura.md`); ADR-001 (Arquitetura monolítica modular em camadas). Uso de JWT definido na stack (`docs/01-visao/visao.md`, seção 3).

---

## 3. Escopo

### Incluído
* Endpoint `POST /api/v1/auth/register` para criação de conta com nome, e-mail válido e senha.
* Armazenamento seguro de senha utilizando algoritmo de hash com salt (ex: Bcrypt/Argon2).
* Endpoint `POST /api/v1/auth/login` para autenticação.
* Geração e retorno de token de sessão JWT assinado após login bem-sucedido.
* Validação de formato de e-mail e unicidade de cadastro.
* Limitação de taxa de requisições nos dois endpoints (RNF-13).
* Bloqueio temporário de 15 minutos após 5 tentativas de login inválidas consecutivas para o mesmo e-mail (RF-02, OPEN-02).

### Fora do Escopo
* Recuperação de senha por e-mail ou reset de credenciais (tratado em Spec futura).
* Login social (OAuth2 com Google/Apple).
* Quiz de perfil de investidor (tratado na SPEC-003).
* Refresh token e logout (ver OPEN-03).

---

## 4. Comportamento e Fluxos

### Pré-condições
* Nenhuma para o cadastro (`POST /register`) e login (`POST /login`).

### Fluxo Principal 1: Cadastro de Usuário
1. O cliente envia uma requisição `POST /api/v1/auth/register` com `nome`, `email` e `senha`.
2. O sistema valida se o e-mail atende ao formato RFC 5322 e se a senha cumpre os requisitos mínimos (mínimo de 8 caracteres).
3. O sistema verifica se o e-mail já está cadastrado no banco de dados.
4. O sistema gera o hash da senha com salt e persiste o novo registro da entidade `Usuario`.
5. O sistema responde com código HTTP `201 Created` e os dados públicos do usuário (sem retornar o hash da senha).

### Fluxo Principal 2: Autenticação (Login)
1. O cliente envia uma requisição `POST /api/v1/auth/login` com `email` e `senha`.
2. O sistema busca o usuário pelo e-mail e verifica o hash da senha.
3. Se válido, o sistema gera um token JWT contendo o `usuario_id` no payload e tempo de expiração configurado.
4. O sistema retorna HTTP `200 OK` contendo o `access_token` e o tipo `bearer`.

### Fluxos Alternativos e Exceções
* **E-mail duplicado (409 Conflict):** Se o e-mail já existir na base, o sistema rejeita com mensagem clara.
* **Credenciais inválidas (401 Unauthorized):** Se a senha estiver incorreta ou e-mail não existir, o sistema retorna erro 401 sem revelar qual dos campos falhou.
* **Dados malformatados (422 Unprocessable Entity):** Se e-mail ou senha forem inválidos sintaticamente.
* **Excesso de requisições (429 Too Many Requests):** Se o cliente ultrapassar o limite do RNF-13.
* **Bloqueio por tentativas inválidas (429 Too Many Requests):** Após 5 tentativas de login inválidas consecutivas para o mesmo e-mail, novas tentativas para esse e-mail são rejeitadas por 15 minutos com mensagem genérica, exista ou não a conta (R09, R10).

---

## 5. Requisitos da Spec (EARS)

Cada cláusula `SHALL` tem ao menos um teste automatizado que cita o seu ID (ver `docs/10-qualidade/estrategia-de-testes.md`).

| ID | Tipo EARS | Cláusula | Origem | Teste previsto |
|---|---|---|---|---|
| SPEC-001-R01 | Event-driven | WHEN o cliente envia `POST /api/v1/auth/register` com nome, e-mail válido, senha de no mínimo 8 caracteres e e-mail ainda não cadastrado THE SYSTEM SHALL persistir o `Usuario` com a senha em hash com salt e responder `201 Created` com os dados públicos, sem o hash. | RF-01, RNF-01 | Integração — Cenário 1 |
| SPEC-001-R02 | Unwanted behavior | IF o e-mail informado no cadastro já estiver cadastrado THEN THE SYSTEM SHALL responder `409 Conflict` sem criar registro. | RF-01 | Integração — Cenário 2 |
| SPEC-001-R03 | Unwanted behavior | IF o e-mail não atender ao formato RFC 5322 ou a senha tiver menos de 8 caracteres THEN THE SYSTEM SHALL responder `422 Unprocessable Entity` sem criar registro. | RF-01 | Integração — Cenário 5 |
| SPEC-001-R04 | Event-driven | WHEN o cliente envia `POST /api/v1/auth/login` com credenciais válidas THE SYSTEM SHALL responder `200 OK` com um `access_token` JWT, contendo `usuario_id` e expiração, e `token_type` igual a `bearer`. | RF-02 | Integração — Cenário 3 |
| SPEC-001-R05 | Unwanted behavior | IF o e-mail não existir ou a senha estiver incorreta THEN THE SYSTEM SHALL responder `401 Unauthorized` com a mesma mensagem genérica nos dois casos. | RF-02 | Integração — Cenário 4 |
| SPEC-001-R06 | Ubiquitous | THE SYSTEM SHALL nunca armazenar nem registrar em log a senha em texto plano. | RNF-01 | Unitário (hash) e integração (inspeção do registro e dos logs) |
| SPEC-001-R07 | State-driven | WHILE um cliente tiver excedido 100 requisições no último minuto em um endpoint de autenticação THE SYSTEM SHALL rejeitar novas requisições desse cliente nesse endpoint com `429 Too Many Requests`. | RNF-13 | Integração |
| SPEC-001-R08 | Ubiquitous | THE SYSTEM SHALL expor os endpoints de autenticação sob o prefixo `/api/v1`. | RNF-17 | Integração (rotas) |
| SPEC-001-R09 | Unwanted behavior | IF ocorrerem 5 tentativas de login inválidas consecutivas para o mesmo e-mail, sem login bem-sucedido entre elas, THEN THE SYSTEM SHALL bloquear novas tentativas de login para esse e-mail por 15 minutos, esteja ele cadastrado ou não. | RF-02, INV-03 | Integração — Cenários 6 e 7 |
| SPEC-001-R10 | State-driven | WHILE o e-mail informado estiver bloqueado THE SYSTEM SHALL responder `429 Too Many Requests` com mensagem genérica a toda tentativa de login para esse e-mail, inclusive com a senha correta. | RF-02, INV-03 | Integração — Cenários 6 e 7 |

---

## 6. Invariantes (Regras Invioláveis)
* **INV-01:** Senhas em texto plano jamais podem ser armazenadas no banco de dados ou registradas em logs.
* **INV-02:** Um e-mail cadastrado deve ser único em todo o sistema.
* **INV-03:** Todas as respostas de erro de autenticação devem ser genéricas para prevenir enumeração de usuários.

---

## 7. Critérios de Aceitação (Dado / Quando / Então)

### Cenário 1: Cadastro com sucesso (R01)
* **Dado** que o e-mail "usuario@finnova.com" ainda não está cadastrado no sistema
* **Quando** uma requisição `POST /api/v1/auth/register` for enviada com nome "João Silva", e-mail "usuario@finnova.com" e senha "SenhaForte123"
* **Então** o sistema deve retornar status HTTP `201 Created`, salvar a senha com hash e registrar a conta no banco de dados.

### Cenário 2: Tentativa de cadastro com e-mail duplicado (R02)
* **Dado** que o e-mail "usuario@finnova.com" já existe na base de dados
* **Quando** uma nova requisição de cadastro for enviada usando o e-mail "usuario@finnova.com"
* **Então** o sistema deve retornar status HTTP `409 Conflict` e não deve criar nenhum novo registro.

### Cenário 3: Login bem-sucedido (R04)
* **Dado** um usuário previamente cadastrado com e-mail "usuario@finnova.com" e senha "SenhaForte123"
* **Quando** for enviada uma requisição `POST /api/v1/auth/login` com as credenciais corretas
* **Então** o sistema deve retornar status HTTP `200 OK` contendo um token JWT válido na chave `access_token`.

### Cenário 4: Login com credenciais inválidas (R05)
* **Dado** um usuário cadastrado com e-mail "usuario@finnova.com"
* **Quando** for enviada uma requisição de login com senha incorreta e, em seguida, outra com o e-mail "inexistente@finnova.com"
* **Então** o sistema deve retornar `401 Unauthorized` nas duas requisições, com corpo de resposta idêntico.

### Cenário 5: Cadastro com dados malformados (R03)
* **Dado** que nenhum usuário está cadastrado
* **Quando** uma requisição de cadastro for enviada com e-mail "usuario-sem-arroba" ou senha "curta"
* **Então** o sistema deve retornar `422 Unprocessable Entity` e não deve criar nenhum registro.

### Cenário 6: Bloqueio após 5 tentativas inválidas (R09, R10)
* **Dado** um usuário cadastrado com e-mail "usuario@finnova.com" e senha "SenhaForte123"
* **Quando** forem enviadas 5 requisições de login seguidas com senha incorreta e, em seguida, uma requisição com a senha correta
* **Então** a sexta requisição deve retornar `429 Too Many Requests` com mensagem genérica; e o mesmo comportamento, com corpo de resposta idêntico, deve ocorrer para o e-mail "inexistente@finnova.com".

### Cenário 7: Fim do bloqueio (R09, R10)
* **Dado** que o e-mail "usuario@finnova.com" foi bloqueado há mais de 15 minutos
* **Quando** for enviada uma requisição de login com a senha correta
* **Então** o sistema deve retornar `200 OK` com o `access_token`.

---

## 8. Questões em Aberto
* **OPEN-01:** Qual será o tempo padrão de expiração do Token JWT (ex: 60 minutos ou 24 horas)? *(Decisão pendente de configuração de ambiente)*.
* **OPEN-02:** O RF-02 exige bloquear o acesso após N tentativas inválidas. Qual é o valor de N, por quanto tempo dura o bloqueio e ele se aplica à conta ou ao cliente? *(Complementar ao rate limiting da R07)*. **Resolvida (rev-1):** N = 5 tentativas inválidas consecutivas; bloqueio de 15 minutos; aplica-se à conta (o rate limiting da R07 continua valendo por cliente). Ver RF-02. **Formalizada e refinada na Semana 4** (#32) nas cláusulas R09 e R10: o bloqueio passa a valer para o e-mail informado, exista ou não a conta (e não só para contas existentes), e a resposta durante o bloqueio é `429` com mensagem genérica, para não revelar contas (INV-03).
* **OPEN-03:** A stack prevê JWT com access e refresh token, e o RF-02 exige manter a sessão até o logout ou a expiração. Refresh token e logout entram nesta spec ou em uma spec própria?
