# Issues do MVP — FinNova

14 issues cobrindo os requisitos de prioridade **Must Have** do MVP (módulos de Conta e Acesso, Administração Financeira Essencial e Simulador Essencial, conforme especificado em `/docs/03-requisitos/requisitos.md`). Copie cada bloco para "New Issue" no GitHub, ou use os comandos `gh issue create` no fim do arquivo se preferir criar tudo pelo terminal.

Labels sugeridas por módulo: `modulo:conta-acesso`, `modulo:adm-financeira`, `modulo:simulador`, mais `prioridade:must-have`.

---

### 1. [RF-01] Cadastro de usuário

**Labels:** `RF`, `modulo:conta-acesso`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário envia o formulário de cadastro com nome, e-mail e senha válidos THE SYSTEM SHALL criar a conta e armazenar a senha com hash.

**Critérios de aceite:** ver RF-01 em `/docs/03-requisitos/requisitos.md`.

---

### 2. [RF-02] Login e autenticação

**Labels:** `RF`, `modulo:conta-acesso`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário envia POST /login com credenciais válidas THE SYSTEM SHALL retornar um token de sessão.

**Critérios de aceite:** ver RF-02 em `/docs/03-requisitos/requisitos.md`.

---

### 3. [RF-06] Cadastro de renda fixa mensal

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário cadastra uma renda fixa mensal THE SYSTEM SHALL considerá-la automaticamente no cálculo de saldo do mês corrente e dos meses seguintes.

**Critérios de aceite:** ver RF-06 em `/docs/03-requisitos/requisitos.md`.

---

### 4. [RF-07] Cadastro de renda variável

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário registra um lançamento de renda variável THE SYSTEM SHALL somá-lo à renda total do mês correspondente.

**Critérios de aceite:** ver RF-07 em `/docs/03-requisitos/requisitos.md`.

---

### 5. [RF-08] Cadastro de bônus e PLR

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário cadastra um bônus/PLR com periodicidade anual e mês de referência THE SYSTEM SHALL somar integralmente o valor à renda total do mês informado, sem diluí-lo pelos demais meses.

**Critérios de aceite:** ver RF-08 em `/docs/03-requisitos/requisitos.md`.

---

### 6. [RF-09] Cadastro de despesas por categoria

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário registra uma despesa com valor, categoria e data válidos THE SYSTEM SHALL persistir o lançamento e atualizar a listagem e os dashboards imediatamente.

**Critérios de aceite:** ver RF-09 em `/docs/03-requisitos/requisitos.md`.

---

### 7. [RF-10] Categorias padrão e personalizadas de gastos

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário cria uma categoria personalizada THE SYSTEM SHALL disponibilizá-la, junto às categorias padrão, para uso em novos lançamentos.

**Critérios de aceite:** ver RF-10 em `/docs/03-requisitos/requisitos.md`.

---

### 8. [RF-11] Edição e exclusão de lançamentos

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário edita ou exclui um lançamento THE SYSTEM SHALL recalcular automaticamente o saldo, os dashboards e o progresso das metas.

**Critérios de aceite:** ver RF-11 em `/docs/03-requisitos/requisitos.md`.

---

### 9. [RF-12] Cadastro de contas bancárias e cartões de crédito

**Labels:** `RF`, `modulo:adm-financeira`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário cadastra uma conta bancária ou cartão de crédito THE SYSTEM SHALL disponibilizá-lo para vínculo com lançamentos.

**Critérios de aceite:** ver RF-12 em `/docs/03-requisitos/requisitos.md`.

---

### 10. [RF-20] Simulação de investimento em renda fixa

**Labels:** `RF`, `modulo:simulador`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário solicita uma simulação de renda fixa com valor inicial, aporte mensal e prazo THE SYSTEM SHALL calcular e retornar o valor bruto e o valor líquido de IR ao final do prazo.

**Critérios de aceite:** ver RF-20 em `/docs/03-requisitos/requisitos.md`.

---

### 11. [RF-21] Simulação de investimento em renda variável

**Labels:** `RF`, `modulo:simulador`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário informa um ticker ou valor investido para simulação de renda variável THE SYSTEM SHALL retornar a evolução estimada do investimento, identificada como projeção.

**Critérios de aceite:** ver RF-21 em `/docs/03-requisitos/requisitos.md`.

---

### 12. [RF-22] Calculadora de juros compostos (motor genérico)

**Labels:** `RF`, `modulo:simulador`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário informa valor inicial, valor mensal, taxa de juros e período THE SYSTEM SHALL calcular o montante final usando juros compostos, com taxa equivalente entre as periodicidades informadas.

**Critérios de aceite:** ver RF-22 em `/docs/03-requisitos/requisitos.md`.

---

### 13. [RF-23] Integração com indicadores oficiais (Selic, CDI, IPCA, Tesouro Direto)

**Labels:** `RF`, `modulo:simulador`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN uma simulação de renda fixa é solicitada THE SYSTEM SHALL obter a taxa do indicador oficial correspondente (Selic, CDI, IPCA ou Tesouro Direto) a partir do cache local mais recente.

**Critérios de aceite:** ver RF-23 em `/docs/03-requisitos/requisitos.md`.

---

### 14. [RF-25] Comparador de cenários de investimento

**Labels:** `RF`, `modulo:simulador`, `prioridade:must-have`

**Enunciado EARS:** Event-driven. WHEN o usuário seleciona duas ou mais simulações para comparação THE SYSTEM SHALL exibir os resultados finais lado a lado com a diferença percentual entre eles.

**Critérios de aceite:** ver RF-25 em `/docs/03-requisitos/requisitos.md`.

---

## Comandos `gh issue create` (opcional)

Rode a partir da raiz do repositório, com o GitHub CLI autenticado (`gh auth login`):

```bash
gh issue create --title "[RF-01] Cadastro de usuário" --label "RF,modulo:conta-acesso,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário envia o formulário de cadastro com nome, e-mail e senha válidos THE SYSTEM SHALL criar a conta e armazenar a senha com hash.

Critérios de aceite: ver RF-01 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-02] Login e autenticação" --label "RF,modulo:conta-acesso,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário envia POST /login com credenciais válidas THE SYSTEM SHALL retornar um token de sessão.

Critérios de aceite: ver RF-02 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-06] Cadastro de renda fixa mensal" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário cadastra uma renda fixa mensal THE SYSTEM SHALL considerá-la automaticamente no cálculo de saldo do mês corrente e dos meses seguintes.

Critérios de aceite: ver RF-06 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-07] Cadastro de renda variável" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário registra um lançamento de renda variável THE SYSTEM SHALL somá-lo à renda total do mês correspondente.

Critérios de aceite: ver RF-07 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-08] Cadastro de bônus e PLR" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário cadastra um bônus/PLR com periodicidade anual e mês de referência THE SYSTEM SHALL somar integralmente o valor à renda total do mês informado, sem diluí-lo pelos demais meses.

Critérios de aceite: ver RF-08 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-09] Cadastro de despesas por categoria" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário registra uma despesa com valor, categoria e data válidos THE SYSTEM SHALL persistir o lançamento e atualizar a listagem e os dashboards imediatamente.

Critérios de aceite: ver RF-09 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-10] Categorias padrão e personalizadas de gastos" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário cria uma categoria personalizada THE SYSTEM SHALL disponibilizá-la, junto às categorias padrão, para uso em novos lançamentos.

Critérios de aceite: ver RF-10 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-11] Edição e exclusão de lançamentos" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário edita ou exclui um lançamento THE SYSTEM SHALL recalcular automaticamente o saldo, os dashboards e o progresso das metas.

Critérios de aceite: ver RF-11 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-12] Cadastro de contas bancárias e cartões de crédito" --label "RF,modulo:adm-financeira,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário cadastra uma conta bancária ou cartão de crédito THE SYSTEM SHALL disponibilizá-lo para vínculo com lançamentos.

Critérios de aceite: ver RF-12 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-20] Simulação de investimento em renda fixa" --label "RF,modulo:simulador,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário solicita uma simulação de renda fixa com valor inicial, aporte mensal e prazo THE SYSTEM SHALL calcular e retornar o valor bruto e o valor líquido de IR ao final do prazo.

Critérios de aceite: ver RF-20 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-21] Simulação de investimento em renda variável" --label "RF,modulo:simulador,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário informa um ticker ou valor investido para simulação de renda variável THE SYSTEM SHALL retornar a evolução estimada do investimento, identificada como projeção.

Critérios de aceite: ver RF-21 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-22] Calculadora de juros compostos (motor genérico)" --label "RF,modulo:simulador,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário informa valor inicial, valor mensal, taxa de juros e período THE SYSTEM SHALL calcular o montante final usando juros compostos, com taxa equivalente entre as periodicidades informadas.

Critérios de aceite: ver RF-22 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-23] Integração com indicadores oficiais (Selic, CDI, IPCA, Tesouro Direto)" --label "RF,modulo:simulador,prioridade:must-have" \
  --body "Event-driven. WHEN uma simulação de renda fixa é solicitada THE SYSTEM SHALL obter a taxa do indicador oficial correspondente (Selic, CDI, IPCA ou Tesouro Direto) a partir do cache local mais recente.

Critérios de aceite: ver RF-23 em /docs/03-requisitos/requisitos.md."

gh issue create --title "[RF-25] Comparador de cenários de investimento" --label "RF,modulo:simulador,prioridade:must-have" \
  --body "Event-driven. WHEN o usuário seleciona duas ou mais simulações para comparação THE SYSTEM SHALL exibir os resultados finais lado a lado com a diferença percentual entre eles.

Critérios de aceite: ver RF-25 em /docs/03-requisitos/requisitos.md."
