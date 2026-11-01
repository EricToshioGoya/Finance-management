# Implementação — SPEC-027: watchlist e alerta de documento

**Data:** 2026-10-30  
**Política autorizada:** lista pessoal de no máximo 50 empresas; alerta in-app para documento ativo novo, deduplicado por titular/documento.

A entrega persiste favoritos do titular, lista e remove apenas vínculos próprios. O alerta usa a central in-app existente, não armazena PDF, não consulta CVM ao vivo e não alerta reapresentações/substituições.

## Atualização de 2026-10-31 — sincronização semanal CVM (OPEN-27, ADR-009)

- `backend/app/infrastructure/official_sources.py` (`CvmSources`): cadastro `cad_cia_aberta.csv` e índices anuais DFP/ITR/IPE (lê apenas o CSV de índice dentro do ZIP; demonstrações e PDFs não são lidos).
- `backend/app/application/cvm_sync.py`: cadastro atualiza razão social e setor só de companhias já catalogadas (o cadastro CVM não traz ticker). Identidade de documento = CNPJ + tipo + data de referência + versão (restrição `uq_official_document_identity`, migration 037). Versão nova vira a efetiva (`restated`), a anterior `replaced`, sem novo alerta; versão antiga recebida depois fica `replaced`. Só documento inédito (`active`) gera aviso da watchlist. Entram apenas documentos entregues nos últimos 12 meses de calendário; link fora do host oficial é trocado pela consulta RAD da companhia.
- Agendamento domingo às 03:00 de America/Sao_Paulo com `FINNOVA_OFFICIAL_SOURCES_SYNC=true`, com as novas tentativas do ADR-009; execução manual `python -m app.jobs.cvm_sync`.
- Complemento de 2026-11-01 (aprovado pelo responsável): IPE é identificado por CNPJ + protocolo de entrega + versão (`cvm_protocol`, índice único parcial `uq_official_ipe_identity`, migration 039). Dois IPE no mesmo dia com protocolos distintos são documentos distintos e geram alertas distintos; nova versão do mesmo protocolo é reapresentação, sem novo alerta. DFP e ITR mantêm CNPJ + tipo + data de referência + versão.
