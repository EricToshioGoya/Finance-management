# Mapa de Specs — Recorte V1

- **Status:** Aprovado
- **Data:** 2026-10-18
- **Issue:** [#36](https://github.com/EricToshioGoya/Finance-management/issues/36)
- **Escopo:** recorte V1, composto pelos requisitos funcionais de prioridade Must have (`docs/03-requisitos/requisitos.md`, tabela 1.1)

O mapa define quais specs compõem o recorte V1, a base de cada uma na baseline (requisitos, casos de uso, modelo de domínio, drivers e ADRs), a dependência entre elas e a ordem de implementação. Concentra também as questões em aberto (`OPEN-XX`) e as decisões pendentes que bloqueiam ou condicionam cada spec.

Nenhuma spec é implementada antes de constar deste mapa com status **Aprovada** (`CLAUDE.md`, seção 2).

---

## 1. Convenções

| Item | Convenção |
|---|---|
| Ordem | Sequência de implementação. Uma spec só é implementada após as specs de que depende. |
| Numeração | Os números já atribuídos são preservados (SPEC-001 e SPEC-002). SPEC-003 e SPEC-004 estão reservadas (seção 3). |
| Status | **Aprovada:** revisada e liberada para implementação. **Rascunho:** em redação ou revisão. **A escrever:** prevista no mapa, sem arquivo. **Implementada:** código e testes integrados à `main`. |
| Arquivo | `docs/08-specs/SPEC-NNN-descricao-curta.md`, com a estrutura mínima: identificação, rastreabilidade, escopo, comportamento, cláusulas EARS, invariantes, critérios Dado/Quando/Então e questões em aberto. |

---

## 2. Mapa do recorte V1

| Ordem | Spec | Base principal | Drivers e ADRs | Depende de | Status | `OPEN` ou decisão pendente |
|---|---|---|---|---|---|---|
| 1 | SPEC-005 Fundação arquitetural (camadas, prefixo `/api/v1`, CI) | RNF-05, RNF-06, RNF-16, RNF-17 | DA-01, DA-07, DA-09; ADR-001, ADR-002 | — | A escrever | — |
| 2 | [SPEC-002](SPEC-002-motor-de-juros-compostos.md) Motor de juros compostos | RF-22, RB-10, RNF-07; UC-17; `Simulacao.calcularEvolucao()` | DA-02; ADR-002 | — (domínio puro) | Aprovada | SPEC-002 OPEN-01 e OPEN-02 (decididas, seção 4) |
| 3 | [SPEC-001](SPEC-001-cadastro-e-autenticacao.md) Cadastro e autenticação | RF-01, RF-02, RNF-01, RNF-13, RNF-17; UC-01, UC-02; `Usuario` | DA-05, DA-06; ADR-001, ADR-005 | 005 | Aprovada | SPEC-001 OPEN-01 e OPEN-03 |
| 4 | SPEC-006 Contas, cartões e categorias | RF-10, RF-12, RB-02; DOM-01, DOM-02 | DA-06, DA-07; ADR-005 | 001 | A escrever | — |
| 5 | SPEC-007 Lançamentos de renda | RF-06, RF-07, RF-08, RB-01, RB-05, RB-06 | DA-06, DA-07, DA-08 | 006 | A escrever | RB-29 ([#27](https://github.com/EricToshioGoya/Finance-management/issues/27)) |
| 6 | SPEC-008 Despesas, edição e exclusão de lançamentos | RF-09, RF-11, RB-01, RB-02; UC-11 | DA-06, DA-07, DA-08 | 006 | A escrever | RB-28 ([#26](https://github.com/EricToshioGoya/Finance-management/issues/26)) |
| 7 | SPEC-009 Indicadores oficiais em cache | RF-23, RNF-09; UC-16, UC-18, UC-37; `IndicadorOficial` | DA-03; ADR-003 | 005 | A escrever | Tecnologia das rotinas agendadas; OPEN-UC13-01 a 03 |
| 8 | SPEC-010 Simulação de renda fixa | RF-20, RB-07, RNF-04; DOM-09; UC-13 | DA-02, DA-03, DA-06; ADR-002, ADR-003 | 002, 009, 001 | A escrever | OPEN-UC13-04; valor líquido de IR depende da SPEC-004 |
| 9 | SPEC-011 Simulação de renda variável | RF-21, RB-08; UC-14 | DA-02, DA-06; ADR-002 | 002, 001 | A escrever | Provedor de cotações (RF-24) |
| 10 | SPEC-012 Comparador de cenários | RF-25; DOM-10; UC-12 | DA-02, DA-03 | 010, 011 | A escrever | — |

**Observações**

- A SPEC-002 precede a SPEC-001 porque é domínio puro (ADR-002): não depende de banco, API nem autenticação, e pode ser implementada e testada isoladamente.
- O RNF-04 (P95 abaixo de 3s) é verificado na SPEC-010, em que a simulação passa pela API; a SPEC-002 cobre o RNF-07 (cobertura mínima de 80% nas regras de cálculo).
- O RNF-16 só bloqueia o merge após a configuração da proteção da branch `main` no GitHub (`docs/09-seguranca/governanca-agentes.md`, seção 3).

---

## 3. Specs reservadas fora do recorte V1

| Spec | Base principal | Motivo da reserva |
|---|---|---|
| SPEC-003 Quiz de perfil de investidor | RF-03; UC-03 | Já citada na SPEC-001 (fora do escopo); RF-03 não é Must have. |
| SPEC-004 Tributação (estimativa de IR) | RF-64, RB-25 | Já citada no UC-13; necessária para o valor líquido da SPEC-010. |

---

## 4. Questões em aberto e decisões pendentes consolidadas

Lista única dos pontos não decididos que afetam o recorte V1. A decisão é registrada na origem (spec, issue ou ADR); esta tabela apenas aponta a situação.

| ID | Origem | Questão | Afeta | Situação |
|---|---|---|---|---|
| SPEC-001 OPEN-01 | SPEC-001 | Tempo de expiração do token JWT | SPEC-001, ADR-005 | Aberta |
| SPEC-001 OPEN-03 | SPEC-001 | Refresh token e logout nesta spec ou em spec própria | SPEC-001 | Aberta |
| SPEC-002 OPEN-01 | SPEC-002 | Política de arredondamento monetário | SPEC-002, SPEC-010 | Decidida em 2026-10-18: cálculo com `Decimal` sem arredondamento intermediário; arredondamento apenas na saída, 2 casas decimais, `ROUND_HALF_UP`. Registro na spec pela [#38](https://github.com/EricToshioGoya/Finance-management/issues/38). |
| SPEC-002 OPEN-02 | SPEC-002 | O valor total investido inclui o valor inicial | SPEC-002, SPEC-010 | Decidida em 2026-10-18: inclui o valor inicial. Registro na spec pela [#38](https://github.com/EricToshioGoya/Finance-management/issues/38). |
| RB-27 | `docs/modelo-dominio.md` | Quantas contas compartilhadas um usuário pode ter | Fora do V1 (RF-60, RF-61) | Aberta — [#25](https://github.com/EricToshioGoya/Finance-management/issues/25) |
| RB-28 | `docs/modelo-dominio.md` | Despesa recorrente: registro único ou uma instância por mês | SPEC-008 | Aberta — [#26](https://github.com/EricToshioGoya/Finance-management/issues/26) |
| RB-29 | `docs/modelo-dominio.md` | A alteração da renda fixa afeta os meses anteriores | SPEC-007 | Aberta — [#27](https://github.com/EricToshioGoya/Finance-management/issues/27) |
| OPEN-UC13-01 | UC-13 (PR [#34](https://github.com/EricToshioGoya/Finance-management/pull/34)) | Mapeamento produto → indicador e tratamento da poupança | SPEC-009, SPEC-010 | Aberta |
| OPEN-UC13-02 | UC-13 (PR [#34](https://github.com/EricToshioGoya/Finance-management/pull/34)) | Sincronização concluída sem dado novo da fonte | SPEC-009 | Aberta |
| OPEN-UC13-03 | UC-13 (PR [#34](https://github.com/EricToshioGoya/Finance-management/pull/34)) | Aplicação do expurgo do RNF-10 ao `IndicadorOficial` | SPEC-009 | Aberta |
| OPEN-UC13-04 | UC-13 (PR [#34](https://github.com/EricToshioGoya/Finance-management/pull/34)) | Contrato HTTP da simulação (rota e códigos de erro) | SPEC-010 | Aberta |
| ARQ-11 provedor | `arquitetura.md`, seção 11 | Provedor de cotações de ações e FIIs | SPEC-011 (RF-24) | Aberta — ADR futuro |
| ARQ-11 agendador | `arquitetura.md`, seção 11 | Tecnologia das rotinas agendadas | SPEC-009 (RF-23) | Aberta — ADR futuro |

---

## 5. Registro de aprovação

| Data | Responsável | Decisão |
|---|---|---|
| 2026-10-18 | Eric Toshio Goya ([@EricToshioGoya](https://github.com/EricToshioGoya)) | Aprovação da ordem, dos identificadores e das dependências da seção 2; decisão de SPEC-002 OPEN-01 e OPEN-02. |

O rascunho do mapa foi gerado com assistência do Claude Code a partir da baseline e revisado pelo responsável antes da aprovação (`CLAUDE.md` C-13).

---

## 6. Manutenção

- O mapa é atualizado no mesmo PR que cria uma spec, altera seu status ou resolve uma questão da seção 4.
- Uma spec nova fora deste mapa exige a inclusão prévia no mapa e nova aprovação humana.
- O roteiro de atualização está na skill `.claude/skills/gerar-mapa-specs/SKILL.md`.
