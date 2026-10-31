# SPEC-032 — Simulação isolada de stress financeiro

## Escopo e contrato

A API `POST /api/v1/auth/financial/stress/compare` recebe `minimum_reserve_months` (3–6) e dois cenários independentes (`first`, `second`). Cada cenário declara `kind` = `income_loss`, `income_reduction` ou `emergency_expense`, duração `months` de 1 a 120, e os parâmetros pertinentes: redução percentual, gasto pontual e/ou corte de despesas. A saída inclui as médias reais de renda e despesa, a reserva conservadora, o patrimônio líquido real, meses sustentados, alerta e horizonte. O contrato é documentado no OpenAPI.

**Nenhum dado financeiro real é escrito.** Os cenários são calculados em memória pelo motor puro `app.domain.financial_stress`. Há verificação de sessão e e-mail confirmado, isolamento estrito por titular e rejeição de dados inválidos.

## Recorte provisório e limitações explícitas

- Janela: **três meses civis completos anteriores**, no fuso America/Sao_Paulo, com base em `balance_summary` / `income_summary` da Administração Financeira. Sem gastos reais nos meses observados, HTTP 422 em vez de divisão inválida. Esse prazo é uma hipótese técnica sujeita à revisão de OPEN-21.
- Reserva líquida *conservadora*: saldos de contas `checking`, `savings` e `cash`, limitados inferiormente a zero. Contas `investment`, ativos manuais e patrimônio potencialmente ilíquido não são presumidos disponíveis. O valor do patrimônio líquido total real é exposto **separadamente**; não equivale à reserva disponível.
- Choque de perda total reduz renda a zero durante os meses especificados; redução parcial aplica percentual à renda. Gasto emergencial é descontado uma única vez no instante inicial. Eventual corte de despesa vale por todo o horizonte hipotético. Passado o período de choque, a renda média anterior é retomada. Não há novos juros, inflação ou saques reais.
- O motor simula até **120 meses** e permite sustento fracionário quando o caixa acaba durante um mês. `months_supported=null` e `horizon_reached=true` indicam *não esgotou nesse horizonte*, nunca autonomia infinita. Alertas comparam a reserva inicial com 3–6 meses e a sustentação calculada com o limite escolhido.
- A regra é identificada no resultado como `stress-v1`. Limites/hipóteses podem ser revisados conforme OPEN-03/OPEN-21; não constituem aprovação formal da política de liquidez.

## Interface e verificação

Interface web PT/EN: seleção entre três choques, parâmetros, corte de despesa, limite de reserva, comparação lado a lado e alertas legíveis. O recurso não altera lançamentos, ativos, passivos ou cadastros e não recomenda ação financeira.

Arquivos de teste: `backend/tests/unit/test_spec032_financial_stress.py` verifica o exemplo de reserva 600 e gasto 100 sustentando 6 meses; fronteiras, redução de renda, cortes e gastos emergenciais. `backend/tests/test_spec032_financial_stress.py` verifica o contrato autenticado, despesas reais, isolamento por titular e manutenção do patrimônio antes/depois. A aprovação técnica exige CI, não apenas existência de testes.

**Pendências de política:** detalhamento formal de OPEN-03/OPEN-21, testes mobile específicos e perfil de carga operacional. Sem merge na main antes de autorização.
