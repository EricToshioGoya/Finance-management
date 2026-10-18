# FinNova — Casos de Uso Detalhados (Fluxo Principal do MVP)

- **Status:** rascunho
- **Última atualização:** 2026-10-18

Descrição textual, com fluxos e exceções, dos casos de uso que compõem o fluxo principal do MVP: o usuário se cadastra, entra na plataforma, registra uma despesa e simula um investimento em renda fixa. Os identificadores seguem as tabelas de `casos-de-uso-usuario.md`.

---

## UC-01 — Cadastrar-se

| Item | Descrição |
|---|---|
| Ator principal | Usuário (ainda não cadastrado) |
| Requisitos | RF-01, RNF-01, RNF-13, RNF-17 |
| Spec | SPEC-001 |
| Pré-condições | Nenhuma. |
| Gatilho | O usuário escolhe criar uma conta. |

**Fluxo principal**

1. O usuário informa nome, e-mail e senha.
2. O sistema valida o formato do e-mail e o tamanho mínimo da senha (8 caracteres).
3. O sistema verifica que o e-mail ainda não está cadastrado.
4. O sistema armazena a senha com hash e salt e cria o usuário.
5. O sistema confirma o cadastro, sem exibir a senha nem o hash.

**Fluxos alternativos e exceções**

- **3a. E-mail já cadastrado:** o sistema rejeita o cadastro com mensagem clara e não cria registro (HTTP 409).
- **2a. Dados inválidos:** e-mail malformado ou senha curta; o sistema indica o campo inválido (HTTP 422).
- **Excesso de requisições:** o cliente que ultrapassar o limite do RNF-13 recebe HTTP 429.

**Pós-condição:** existe um `Usuario` com e-mail único e senha protegida por hash.

---

## UC-02 — Autenticar-se

| Item | Descrição |
|---|---|
| Ator principal | Usuário cadastrado |
| Requisitos | RF-02, RNF-01, RNF-13, RNF-17 |
| Spec | SPEC-001 |
| Pré-condições | O usuário possui cadastro (UC-01). |
| Gatilho | O usuário solicita acesso informando e-mail e senha. |

**Fluxo principal**

1. O usuário informa e-mail e senha.
2. O sistema localiza o usuário pelo e-mail e confere a senha contra o hash.
3. O sistema emite um token de sessão (JWT) com o identificador do usuário e prazo de expiração.
4. O usuário passa a acessar os demais casos de uso autenticado.

**Fluxos alternativos e exceções**

- **2a. E-mail inexistente ou senha incorreta:** o sistema responde com a mesma mensagem genérica nos dois casos, sem revelar qual campo falhou (HTTP 401).
- **2b. Tentativas inválidas repetidas:** o acesso da conta é bloqueado por 15 minutos após 5 tentativas inválidas consecutivas (RF-02; SPEC-001, OPEN-02).
- **Excesso de requisições:** HTTP 429 (RNF-13).

**Pós-condição:** o cliente possui um token válido até a expiração ou o logout.

---

## UC-11 — Registrar despesa por categoria

| Item | Descrição |
|---|---|
| Ator principal | Usuário autenticado |
| Requisitos | RF-09, RF-10, RF-11, RF-12, RB-01, RB-02, RNF-03 |
| Spec | a definir |
| Pré-condições | Usuário autenticado (UC-02). |
| Gatilho | O usuário escolhe registrar uma nova despesa. |

**Fluxo principal**

1. O usuário informa valor, categoria e data da despesa.
2. Opcionalmente, o usuário vincula a despesa a uma conta ou a um cartão (RF-12) e a marca como recorrente ou pontual (RF-09).
3. O sistema valida que o valor é maior que zero (RB-01) e que há exatamente uma categoria (RB-02).
4. O sistema persiste a despesa.
5. O sistema recalcula saldo, dashboards e progresso de metas (RF-11) e exibe a despesa na listagem imediatamente.

**Fluxos alternativos e exceções**

- **3a. Valor menor ou igual a zero:** o sistema rejeita o registro e indica o campo.
- **3b. Categoria ou data ausente:** o sistema rejeita o registro e indica o campo obrigatório.
- **Ponto de extensão — despesa compartilhada:** se houver conta compartilhada ativa, o usuário pode dividir a despesa (UC-10).

**Restrição de usabilidade:** o registro deve ser concluído em, no máximo, 3 passos na web e no mobile (RNF-03).

**Pós-condição:** a despesa está registrada e todos os valores derivados foram recalculados.

---

## UC-13 — Simular investimento em renda fixa

| Item | Descrição |
|---|---|
| Ator principal | Usuário autenticado |
| Atores secundários | API Banco Central (SGS) e Tesouro Transparente, de forma indireta, via cache |
| Requisitos | RF-20, RF-22, RF-23, RB-07, RB-10, RNF-04, RNF-09 |
| Specs | SPEC-002 (motor de cálculo); tributação na SPEC-004 (futura) |
| Inclui | UC-16 (Obter indicador oficial) e UC-17 (Calcular juros compostos) |
| Estendido por | UC-18 (Usar último valor em cache) |
| Pré-condições | Usuário autenticado (UC-02). |
| Gatilho | O usuário abre o simulador de renda fixa. |

**Fluxo principal**

1. O usuário escolhe o produto (CDB, Tesouro ou poupança) e informa valor inicial, aporte mensal e prazo.
2. O sistema obtém, no cache local, a taxa do indicador oficial do produto (UC-16) e a pré-preenche, com a data de referência.
3. O usuário mantém a taxa sugerida ou informa uma taxa manual.
4. O sistema executa o motor de juros compostos (UC-17), com conversão de taxa por equivalência composta (RB-10).
5. O sistema exibe a evolução mês a mês, o valor bruto e, quando aplicável, o valor líquido de IR, junto com a data de referência do indicador.

**Fluxos alternativos e exceções**

- **2a. Cache desatualizado por falha da fonte oficial:** o sistema usa o último valor conhecido e exibe aviso de defasagem, nunca um valor zerado (UC-18, RF-23).
- **2b. Nenhum valor do indicador no cache:** cenário não coberto pelos requisitos atuais; registrado como questão em aberto abaixo.
- **4a. Entrada inválida** (valor negativo ou prazo igual a zero): o sistema rejeita a simulação e indica o campo (SPEC-002, R06).

**Pós-condição:** o usuário visualiza a projeção, identificada como simulação educativa e não como recomendação.

**Questão em aberto:** como o sistema deve se comportar na primeira execução, antes de qualquer sincronização do indicador (bloquear a simulação ou exigir taxa manual)?
