# Implementação — SPEC-023: cotações e histórico de ações/FIIs

**Data:** 2026-10-29  
**Política autorizada:** catálogo local versionado para PETR4 e MXRF11, com referência temporal máxima de 24 horas. Não há cotação em tempo real, integração B3 ou agregador externo neste recorte.

## Entrega

- `GET /api/v1/market/quotes/{ticker}` exige sessão e retorna preço, variação diária, série de fechamentos, data de referência e validade para PETR4/MXRF11.
- A resposta identifica `catalogue_type=local_reference`; histórico é dado passado para cálculo, não previsão nem recomendação.
- Ticker inválido retorna 422 e ticker não catalogado retorna 404. Referência vencida ou indisponível retorna 503, sem preço zero, com `manual_entry_permitted=true`.
- A interface permite a consulta e deixa explícito que a referência é local e datada. O contrato de fallback permite ao futuro consumidor de simulação aceitar valor/rentabilidade manual.

## Verificações

`test_spec023_market_quotes.py` cobre ação, FII, histórico, autenticação, ticker inválido/desconhecido, expiração após 24 horas e indisponibilidade. A CI executa a suíte integrada PostgreSQL e o cliente web. Lint, build e verificação documental também são exigidos no PR.
