# Plano — SPEC-040: Enviar resumo mensal automático optativo

## Escopo executado

- Geração do PDF do mês anterior com renda, gasto, patrimônio e score.
- Envio pelo canal de e-mail configurado; opt-in e desativação a qualquer momento.
- Idempotência por titular e competência; falha registrada sem sucesso falso.

## Camadas e arquivos

- Aplicação: `backend/app/application/monthly_summary.py` (`MonthlySummaryService`, `previous_month`).
- Job: `run_daily_monthly_summary` no ciclo de vida da API e `backend/app/jobs/monthly_summary.py`.
- Infraestrutura: `backend/app/infrastructure/pdf.py` (extraído de `main.py`).
- Persistência: `ReportSettingsRecord`, `MonthlySummaryRecord`; migração 035.
- API: `/api/v1/auth/profile/reports`, `/api/v1/auth/financial/monthly-summaries`.
- Web: `ReportsAndChannels` (aba Minha conta).
- Testes: `backend/tests/test_spec040_061_channels_summary.py`.

## Riscos e limites

- Patrimônio e score dependem de registros do mês (snapshot/score); ausentes são declarados no PDF.
- Sem retentativa: uma falha não é reenviada automaticamente.
