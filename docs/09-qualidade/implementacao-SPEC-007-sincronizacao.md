# Implementação — SPEC-007: sincronização com fontes oficiais

Decisão: OPEN-04/OPEN-10 e OPEN-23 aprovadas pelo responsável em 2026-10-31; [ADR-009](../07-arquitetura/adrs/ADR-009-integracao-com-fontes-oficiais.md).

## O que foi entregue

- Adaptadores em `backend/app/infrastructure/official_sources.py`: SGS (séries 432, 4389 e 13522, % a.a.), PTAX de venda do boletim de fechamento (USD e EUR) e CSV `PrecoTaxaTesouroDireto` do Tesouro Transparente. Somente HTTPS para a lista fechada de hosts, timeout de 20 s e transporte injetável.
- Serviço `backend/app/application/indicator_sync.py`: cada item é independente; o cache só é substituído por referência igual ou mais recente; `checked_at` registra a última verificação bem-sucedida; formato inesperado ou falha de transporte mantém o último valor (C-08). Itens com falha são repetidos após 5, 15 e 45 minutos.
- PTAX: consulta o último dia útil anterior e recua até 5 dias úteis quando não há boletim de fechamento (feriado).
- Tesouro Direto: apenas a data-base mais recente; taxa zero (título fora de venda) não é publicada. Tabela `treasury_bond_rates` (migration 036) e `GET /api/v1/auth/financial/treasury-bonds`, exibida na aba Investimentos.
- Agendamento às 07:00 de America/Sao_Paulo no `lifespan`, ativado por `FINNOVA_OFFICIAL_SOURCES_SYNC=true`. O padrão da aplicação é desligado, para que testes não chamem fontes externas (C-17); desde 2026-11-01 o `scripts/prepare-local.py` grava `true` no `.env` local e o E2E da CI grava `false` explicitamente. Execução manual: `cd backend && uv run --frozen python -m app.jobs.indicator_sync`.

## Evidências

- `backend/tests/test_c02_spec007_indicator_sync.py`: dublês no formato documentado de cada provedor (C-17), cobrindo SPEC-007-R03 a R06 e SPEC-026-R04.

## Limites

- O ambiente de desenvolvimento deste registro não alcança os hosts oficiais (proxy 403); os formatos seguem a documentação pública e a primeira execução real deve ser verificada no ambiente de implantação.
- Observabilidade operacional (alertas de falha) segue em OPEN-32; a rotina registra cada execução no logger `finnova.indicator_sync`.
