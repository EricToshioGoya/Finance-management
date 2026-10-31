# Implementação — SPEC-053: indicadores contábeis CVM

**Data:** 2026-10-28  
**Recorte autorizado:** PETR4 e VALE3; receita líquida, lucro líquido e patrimônio líquido; Exercício 2025 e 2º trimestre de 2026; unidade única R$ mil.

## Entrega

- Migration `017_cvm_financial_indicators` cria `financial_indicators` e semeia somente valores estruturados. Não há coluna, download ou cache de PDF.
- `GET /api/v1/companies/{company_id}/financial-indicators` exige sessão, aceita os filtros fechados `metric` e `period_kind` e devolve fonte, diretório CVM, datas, unidade e status.
- A interface mostra tabela rolável, alternativa textual e barras de evolução. O gráfico utiliza apenas `effective=true`.
- A publicação anterior de lucro trimestral de VALE3 é mantida com `status=restated`; a publicação posterior é a revisão efetiva. Não há soma entre as duas.

## Fonte e limite

O rótulo de origem é **Dados Abertos CVM — catálogo local de referência**, apontando para os diretórios públicos de DFP/ITR. Os valores são fixtures versionadas para demonstrar o contrato acadêmico, não uma promessa de sincronização em tempo real ou substituto da consulta oficial. A rotina de expurgo de 12 meses e a sincronização operacional pertencem à SPEC-054.

## Evidências de teste

`backend/tests/test_spec053_financial_indicators.py` cobre sessão obrigatória, três métricas/dois períodos, fonte/unidade, filtros inválidos, empresa inexistente e reapresentação não somada. As verificações de lint, formato, cobertura, build, testes do cliente e documentação são executadas antes da publicação da branch.
