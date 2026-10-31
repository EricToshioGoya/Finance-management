# ADR-009: Integração com fontes oficiais (BCB, Tesouro Transparente e CVM)

* **Status:** Aceito
* **Data:** 2026-10-31
* **Decisores:** responsável pelo projeto (aprovação das políticas OPEN-04, OPEN-10, OPEN-23 e OPEN-27 em 2026-10-31)

## Contexto e Problema

As SPEC-007, SPEC-026, SPEC-027 e SPEC-053/054 dependem de dados públicos externos. Até esta data, o cache local era preenchido apenas por fixtures versionadas; nenhuma rotina consultava a fonte oficial. O ADR-003 definiu que simulações leem somente o cache local, mas não fixou provedores, contratos, agenda nem regra de atualização. A regra C-08 da constituição exige que, na falha da fonte, o sistema use o último valor com aviso, nunca zero.

## Decisão

1. **Provedores aceitos** (lista fechada de hosts HTTPS, sem credenciais):

   | Dado | Provedor | Host | Agenda (America/Sao_Paulo) |
   |---|---|---|---|
   | SELIC meta (série 432), CDI (série 4389) e IPCA acumulado em 12 meses (série 13522), em % a.a. | BCB — SGS | `api.bcb.gov.br` | Diária às 07:00 |
   | Taxa de compra dos títulos do Tesouro Direto | Tesouro Transparente — CSV `PrecoTaxaTesouroDireto` | `www.tesourotransparente.gov.br` | Diária às 07:00 |
   | PTAX de venda (USD e EUR) do último dia útil anterior | BCB — PTAX (Olinda) | `olinda.bcb.gov.br` | Diária às 07:00 |
   | Cadastro de companhias e índices DFP/ITR/IPE | CVM — Dados Abertos | `dados.cvm.gov.br` | Semanal, domingo às 03:00 |

2. **Camadas:** cada provedor tem um adaptador em `app/infrastructure/` que só busca e converte (`Decimal`, datas); as regras (data de referência, aviso, identidade de documento) ficam em serviços de `app/application/`. O domínio continua sem I/O (ADR-002).
3. **Cliente HTTP:** `urllib` da biblioteca padrão, com timeout de 20 s, somente HTTPS e somente os hosts da tabela; nenhuma dependência nova.
4. **Agendamento:** tarefas no `lifespan` do FastAPI, no mesmo padrão do expurgo CVM (SPEC-054) e do resumo mensal (SPEC-040), e execução manual por `python -m app.jobs.<rotina>`.
5. **Repetição:** em falha, até 3 novas tentativas, após 5, 15 e 45 minutos; esgotadas, a próxima execução é a do agendamento seguinte.
6. **Atualização do cache:** um valor só substitui o anterior se a data de referência for igual ou mais recente; `checked_at` registra a última verificação bem-sucedida.
7. **Resiliência (C-08):** na falha da fonte, mantém-se o último valor com aviso visível; indicador verificado há mais de 24 horas é marcado como desatualizado (RNF-09). A PTAX aceita até 5 dias úteis desde a data de referência, com aviso a partir do segundo dia útil; acima disso, a simulação em moeda estrangeira é recusada sem taxa inventada. Esta decisão complementa o item 3 do ADR-003 conforme a regra C-08.
8. **CVM:** identidade de documento = CNPJ + tipo + data de referência + versão; reapresentação substitui a versão anterior como efetiva. Apenas metadados e link oficial são armazenados, nunca PDF (ADR-004, C-09).
9. **Testes:** nenhum teste chama a fonte real (C-17); adaptadores recebem um transporte injetável e os testes usam dublês com respostas no formato documentado.

## Alternativas Consideradas

* **Biblioteca HTTP de terceiros (`httpx`/`requests`) em produção:** descartada; o volume é baixo e `urllib` já é usado nos adaptadores de e-mail e webhooks.
* **Agendador externo (cron da plataforma) como única opção:** adiado até a definição de hospedagem (OPEN-32); as rotinas são executáveis por linha de comando para permitir essa troca.
* **Recusar indicador com mais de 24 horas:** descartado por contrariar C-08 e a decisão de 2026-10-31.

## Consequências

### Positivas
* Fecha a origem oficial das SPEC-007-R03/R04/R06, SPEC-026-R04 e SPEC-027-R05.
* Simulações continuam sem chamada externa síncrona (RNF-04).

### Negativas
* Formatos externos podem mudar; a rotina registra falha e mantém o último valor, mas exige monitoramento operacional (OPEN-32).
* Os contratos foram implementados pelos formatos públicos documentados; a primeira execução real deve ser verificada no ambiente de implantação.
