# SPEC-012 — Catálogo local de empresas e documentos CVM

## Política confirmada

Em 2026-10-28, o responsável autorizou um catálogo local inicial, sem sincronização externa automática: PETR4 e VALE3, com metadados de DFP, ITR, FRE e IPE. Cada item aponta para a RAD/ENET da CVM; o FinNova não baixa, hospeda nem armazena PDF.

## Entrega

- Busca autenticada por ticker, CNPJ e razão social, com sugestões e ficha cadastral.
- Listagem filtrável por tipo e intervalo de entrega, com assunto, período, data e status.
- Links HTTPS restritos ao host oficial da CVM e abertos em nova aba pela interface.
- Verificação manual sob demanda com `HEAD`, que guarda apenas `unchecked`, `available` ou `broken` e o instante da verificação.

## Evidência

`backend/tests/test_spec012_company_catalogue.py` cobre busca, catálogo vazio, filtros, ausência de conteúdo binário, URL oficial permitida e verificação sem SSRF. A migration `016_public_cvm_catalogue` cria somente as tabelas de metadados.

Sincronização automática, indicadores estruturados e expurgo de doze meses não fazem parte desta entrega; são tratados pelas Specs seguintes. O resultado final depende da CI do PR.
