# Implementação — SPEC-054: expurgo do cache CVM

**Data:** 2026-10-29  
**Política autorizada:** todos os dias às 03:00 em America/Sao_Paulo, remover cache público cujo `synced_at` seja menor ou igual ao instante equivalente a doze meses de calendário antes do relógio atual.

## Entrega

- O ciclo do backend calcula o próximo horário diário no fuso de São Paulo e chama o serviço de expurgo com relógio injetável.
- A transação remove somente `official_documents` e `financial_indicators`; empresas públicas, usuários, contas, lançamentos, patrimônio e PDFs não são tocados.
- `cvm_cache_purge_runs` guarda instante, duas contagens e `completed`. A linha só é persistida junto ao commit das remoções, portanto uma falha não declara sucesso.
- Se as consultas existentes encontrarem o cache público daquela empresa vazio, recriam somente os metadados/indicadores da referência local aprovada. Não existe download, PDF ou chamada CVM em tempo real.

## Verificações

`test_spec054_cvm_cache_purge.py` verifica a fronteira inclusiva de 12 meses, preservação imediatamente posterior, contagens agregadas, reconstrução em nova consulta e o limite de 29 de fevereiro. O CI executa a suíte completa com PostgreSQL e navegador; o ambiente local ainda pode não disponibilizar esses serviços.
