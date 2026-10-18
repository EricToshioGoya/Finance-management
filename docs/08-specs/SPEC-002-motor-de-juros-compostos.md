# SPEC-002: Motor de Cálculo de Juros Compostos e Equivalência de Taxas

* **Status:** Aprovada
* **Data:** 2026-10-08
* **Revisão:** 2026-10-18 — correção da rastreabilidade, alinhamento da validação da taxa ao RF-22, correção do valor de referência do Cenário 1 e inclusão das cláusulas EARS (seção 5).
* **Autor:** Equipe FinNova / SDD

---

## 1. Identificação
* **ID:** SPEC-002
* **Nome:** Motor de Cálculo de Juros Compostos e Equivalência de Taxas
* **Objetivo:** Fornecer um motor genérico de cálculo financeiro isolado no domínio para apurar montantes acumulados, rendimentos e tabelas de evolução com aportes mensais recorrentes.
* **Valor Entregue:** Serve como o núcleo matemático reaproveitável para todas as simulações da aplicação (Renda Fixa, Renda Variável, Aposentadoria e Compras Financiadas).

---

## 2. Rastreabilidade (Baseline)
* **Requisitos Funcionais:** RF-22 (Calculadora de juros compostos), RF-20 (Simulação em Renda Fixa)
* **Regras de Negócio:** RB-07 (Indexação composta), RB-10 (Fórmula de juros compostos e equivalência de taxa: $i_{mensal} = (1 + i_{anual})^{1/12} - 1$). A RB-01 não se aplica: trata de lançamentos de renda e despesa; as validações de entrada desta spec derivam dos critérios de aceite do RF-22.
* **Requisitos Não Funcionais:** RNF-04 (Desempenho P95 < 3s), RNF-07 (Testes automatizados com cobertura de 80%+ nas regras financeiras)
* **Casos de Uso:** UC-17 (Calcular juros compostos), UC-13 (Simular investimento em renda fixa) — ver `docs/04-casos-de-uso/casos-de-uso-detalhados.md`
* **Entidades do Domínio:** `Simulacao` (Objeto de Valor/Engine)
* **Drivers e ADRs:** DA-02 (`docs/07-arquitetura/arquitetura.md`); ADR-002 (Motor de Cálculo no Domínio Puro isolado de ORM e Web)

---

## 3. Escopo

### Incluído
* Implementação do cálculo de montante composto com aportes ao final de cada período.
* Conversão automatizada e composta de taxa anual para taxa mensal ($i_{mensal} = (1 + i_{anual})^{1/12} - 1$).
* Conversão automatizada de prazos em anos para meses ($n = anos \times 12$).
* Geração da evolução detalhada mês a mês contendo: saldo inicial, aporte do mês, juros rendidos no mês e saldo final acumulado.
* Retorno consolidado: Valor Total Investido (soma dos aportes), Total de Juros Ganhos e Montante Final Bruto.

### Fora do Escopo
* Dedução de Imposto de Renda ou taxas de custódia (tratado na SPEC-004 de tributação).
* Persistência do resultado no banco de dados (o motor realiza o cálculo em memória; a gravação do histórico é feita pela camada de serviço/aplicação).

---

## 4. Comportamento e Fluxos

### Entrada de Dados
* `valor_inicial`: Decimal (>= 0)
* `aporte_mensal`: Decimal (>= 0)
* `taxa_juros`: Decimal (>= 0, conforme RF-22)
* `tipo_taxa`: Enum (`MENSAL`, `ANUAL`)
* `periodo`: Integer (> 0)
* `tipo_periodo`: Enum (`MESES`, `ANOS`)

### Processamento do Cálculo
1. O motor valida se os valores informados são não-negativos e se o período é maior que zero.
2. Se `tipo_taxa == ANUAL`, converte a taxa para mensal usando a fórmula de equivalência composta:
   $$i = (1 + i_{anual})^{1/12} - 1$$
3. Se `tipo_periodo == ANOS`, converte o período para meses: $n = periodo \times 12$.
4. Executa a iteração mês a mês de $k = 1$ até $n$:
   * $Juros_k = SaldoAcumulado_{k-1} \times i$
   * $SaldoAcumulado_k = SaldoAcumulado_{k-1} + Juros_k + AporteMensal$
5. Agrupa os totais acumulados e retorna a estrutura imutável com a série temporal e o resumo.

---

## 5. Requisitos da Spec (EARS)

Cada cláusula `SHALL` tem ao menos um teste unitário que cita o seu ID (ver `docs/10-qualidade/estrategia-de-testes.md`).

| ID | Tipo EARS | Cláusula | Origem | Teste previsto |
|---|---|---|---|---|
| SPEC-002-R01 | Ubiquitous | THE SYSTEM SHALL calcular o saldo de cada mês como $Saldo_k = Saldo_{k-1} + Saldo_{k-1} \times i + AporteMensal$, com o aporte aplicado no fim do período. | RF-22, RB-10 | Unitário — Cenário 2 |
| SPEC-002-R02 | Event-driven | WHEN a taxa for informada como anual THE SYSTEM SHALL convertê-la para mensal por $i = (1 + i_{anual})^{1/12} - 1$. | RF-22, RB-10 | Unitário — Cenário 1 |
| SPEC-002-R03 | Event-driven | WHEN o período for informado em anos THE SYSTEM SHALL convertê-lo para meses por $n = periodo \times 12$. | RF-22 | Unitário |
| SPEC-002-R04 | Ubiquitous | THE SYSTEM SHALL retornar a série mensal com saldo inicial, aporte, juros e saldo final de cada mês. | RF-22 | Unitário — Cenário 2 |
| SPEC-002-R05 | Ubiquitous | THE SYSTEM SHALL retornar o valor total investido, o total de juros ganhos e o montante final bruto. | RF-22 | Unitário — Cenários 1 e 2 |
| SPEC-002-R06 | Unwanted behavior | IF `valor_inicial`, `aporte_mensal` ou `taxa_juros` for negativo, ou `periodo` for menor ou igual a zero, THEN THE SYSTEM SHALL lançar `ValueError` sem executar o cálculo. | RF-22 | Unitário — Cenário 3 |
| SPEC-002-R07 | Ubiquitous | THE SYSTEM SHALL representar valores monetários e taxas com `Decimal`, nunca com `float`. | INV-02 | Unitário (tipos do resultado) e revisão |

---

## 6. Invariantes (Regras Invioláveis)
* **INV-01:** Proibido o uso de conversão de taxa por divisão simples ($i_{anual} / 12$). Toda conversão temporal DEVE ser por taxa equivalente composta.
* **INV-02:** O cálculo não pode utilizar tipos de ponto flutuante binário padrão (`float`) para valores monetários. É obrigatório o uso de precisão decimal exata (`Decimal` em Python).

---

## 7. Critérios de Aceitação (Dado / Quando / Então)

### Cenário 1: Cálculo simples sem aporte com taxa anual (R02, R05)
* **Dado** um aporte inicial de R$ 1.000,00, sem aportes mensais, taxa anual de 12% e período de 12 meses
* **Quando** o motor de cálculo for executado
* **Então** a taxa mensal convertida por equivalência deve ser ~0,948879% a.m. e o montante final ao término de 12 meses deve ser R$ 1.120,00 após arredondamento para centavos (política de arredondamento em OPEN-01).

### Cenário 2: Cálculo com aportes mensais (R01, R04, R05)
* **Dado** valor inicial de R$ 0,00, aporte mensal de R$ 100,00, taxa mensal de 1% e prazo de 2 meses
* **Quando** o motor de cálculo for executado
* **Então** o saldo ao final do Mês 1 deve ser R$ 100,00 e o saldo final do Mês 2 deve ser R$ 201,00 (R$ 100 do mês 1 + R$ 1 de juros + R$ 100 do aporte do mês 2).

### Cenário 3: Validação de entradas inválidas (R06)
* **Dado** uma solicitação de cálculo contendo um período de 0 meses, valor inicial negativo ou taxa negativa
* **Quando** o motor for acionado
* **Então** deve lançar uma exceção de domínio `ValueError` indicando parâmetros inválidos sem prosseguir com o cálculo.

---

## 8. Questões em Aberto
* **OPEN-01:** Política de arredondamento: quantas casas decimais, qual modo (ex.: `ROUND_HALF_EVEN` ou `ROUND_HALF_UP`) e em que momento arredondar (a cada mês ou apenas no resultado final)?
* **OPEN-02:** O "Valor Total Investido" inclui o valor inicial ou apenas os aportes mensais? O RF-22 e esta spec citam apenas "aportes".
