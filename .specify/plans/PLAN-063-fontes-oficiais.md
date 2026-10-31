# Plano — Fontes oficiais e ciclo do cartão (OPEN-04, 10, 12, 23, 27)

Decisões aprovadas pelo responsável em 2026-10-31 e registradas em `docs/08-specs/questoes-abertas.md` e no ADR-009. Execução em quatro PRs, cada um com merge após CI verde.

## PR A — Registro e política PTAX (SPEC-026)

- Documentação: ADR-009, registro das cinco OPEN, arquitetura DA-03.
- Aplicação: `backend/app/application/exchange_rates.py` passa a contar dias úteis desde a data de referência (relógio injetado, America/Sao_Paulo); `stale`/`notice` de 2 a 5 dias úteis; `503 ptax_stale` acima disso.
- Apresentação: `ForeignCurrencySimulationOutput` com `stale` e `notice`.
- Testes: `backend/tests/test_c02_spec026_ptax_policy.py`.

## PR B — Sincronização diária (SPEC-007, SPEC-026)

- Infraestrutura: adaptadores SGS (432, 4389, 13522), PTAX (Olinda) e Tesouro Transparente (CSV), com transporte injetável e lista fechada de hosts.
- Aplicação: `indicator_sync` com regra de referência igual ou mais recente, novas tentativas (5, 15, 45 min) e registro de execução.
- Agendamento no `lifespan` às 07:00 e `python -m app.jobs.indicator_sync`.
- Persistência: tabela para taxas do Tesouro Direto (migration).
- Testes: dublês por provedor; remove o `xfail` de SPEC-007-R03/R04/R06.

## PR C — Sincronização semanal CVM (SPEC-012, 027, 053, 054)

- Adaptador de Dados Abertos CVM (cadastro e índices DFP/ITR/IPE).
- Identidade CNPJ + tipo + data de referência + versão; reapresentação substitui a efetiva sem novo alerta.
- Aviso da watchlist (SPEC-027-R05) para documento novo efetivo.
- Agendamento domingo 03:00 e `python -m app.jobs.cvm_sync`.

## PR D — Ciclo do cartão (SPEC-020, SPEC-059)

- Domínio puro: competência da fatura por dia de fechamento (29–31 → último dia do mês) e divisão de parcelas com resíduo na 1ª.
- Persistência: `credit_cards.alert_threshold` (70–100, padrão 80) e grupo de parcelamento em `expenses` (migration).
- Fatura e limite disponível com parcelas futuras; UI de cadastro do cartão e de despesa parcelada.

## Riscos

- O ambiente de desenvolvimento não alcança os hosts oficiais (proxy 403); os formatos seguem os contratos públicos documentados e a primeira execução real deve ser verificada na implantação.
- Mudança de formato externo: a rotina registra falha e mantém o último valor (C-08).
