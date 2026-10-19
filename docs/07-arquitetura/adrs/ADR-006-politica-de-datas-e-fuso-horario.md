# ADR-006: Política de Datas e Fuso Horário

* **Status:** Aceito
* **Data:** 2026-10-19
* **Decisores:** Equipe de Arquitetura FinNova
* **Drivers atendidos:** DA-11

## Contexto e Problema
Várias regras do FinNova dependem de data e hora: a renda total do mês e o mês de referência do bônus/PLR (RB-05, RB-06), o bloqueio de login por 15 minutos (RF-02), a expiração do token (ADR-005), a defasagem máxima de 24h dos indicadores (RNF-09) e o expurgo após 12 meses (RF-33). Servidores, banco e clientes podem estar em fusos diferentes, e uma divergência faz uma despesa cair no mês errado ou libera um bloqueio antes da hora.

## Decisão
1. **Instantes** (data e hora de eventos: criação de registros, tentativas de login, sincronizações, expiração de token) são gravados em **UTC**, com fuso explícito (`timestamptz` no PostgreSQL), e todas as janelas de tempo são calculadas em UTC.
2. **Datas de calendário** informadas pelo usuário (data de uma despesa ou renda) são guardadas como data, sem hora, no calendário do usuário.
3. O **mês de competência** e as datas exibidas são calculados no fuso **America/Sao_Paulo**.
4. O domínio recebe o relógio como dependência (nunca lê o relógio do sistema diretamente), para que os testes usem relógio congelado.

## Alternativas Consideradas
* **Gravar tudo no horário de Brasília:** descartada, porque depende do fuso configurado em cada servidor e quebra se a hospedagem estiver no exterior ou se o horário de verão voltar.
* **Gravar data e hora sem fuso:** descartada, porque torna ambíguo o instante real e impede comparar eventos de servidores diferentes.

## Consequências
### Positivas:
* Comparações e janelas de tempo são consistentes entre servidores, banco e clientes.
* O mês de competência é sempre o do calendário brasileiro, como o usuário espera.
* Viradas de dia e de mês são testáveis com relógio congelado.

### Negativas:
* Toda exibição precisa converter de UTC para America/Sao_Paulo.
* Mudar esta política depois exige migrar todas as datas já gravadas — por isso o ADR.
