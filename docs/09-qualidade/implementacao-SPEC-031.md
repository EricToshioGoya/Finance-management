# SPEC-031 — Comparar alocação real atual e alvo

## Recorte técnico e classificação

Esta entrega considera apenas **ativos reais de investimento** da SPEC-028, nunca simulações. São cinco classes: renda fixa (`fixed_income`), ações (`stocks`), FIIs (`fiis`), poupança (`savings`) e outros (`other`).

- Contas cadastradas como `savings` entram em poupança e `investment` entram em outros, apenas se o saldo real atual for positivo. Contas `checking` e `cash` são excluídas do total investido.
- Ativos manuais não são classificados por nome ou taxa presumida: o titular deve atribuir explicitamente a classe; itens manuais não classificados aparecem em lista separada, fora do denominador até a classificação.
- Passivos e faturas não entram no montante investido.
- Um alvo deve definir as **cinco classes**, cada uma de 0 a 100 com até duas casas decimais e soma **exatamente 100%**. Não há normalização silenciosa; a gravação substitui o conjunto de alvos do titular numa transação.
- A proporção atual é `valor da classe / total investido × 100`. O desvio mostrado em pontos percentuais é `atual - alvo`, com duas casas decimais. Total investido zero retorna percentuais e desvios nulos, não NaN ou 0% fictício.
- Não há recomendação automática de investimentos nem movimentação real decorrente dos alvos.

## Persistência, privacidade e contrato

Migração `027_investment_allocation.py` cria `investment_asset_classes` e `investment_allocation_targets`, associadas ao titular com exclusão em cascata. A classificação está vinculada ao ID do ativo manual existente, sem duplicar valor de patrimônio. Excluir ativo elimina sua classificação.

Rotas, todas em `/api/v1/auth/financial`, exigem sessão válida e e-mail verificado:

- `GET /investment-allocation`: total investido, linhas das cinco classes, percentuais, alvos, desvios e ativos manuais sem classe.
- `PUT /investment-allocation/targets`: objeto `{"targets":{"fixed_income":"50", "stocks":"50", "fiis":"0", "savings":"0", "other":"0"}}`.
- `PUT /investment-allocation/assets/{asset_id}`: `{"asset_class":"stocks"}` para classificar ativo real manual próprio.
- `DELETE /investment-allocation/assets/{asset_id}`: remover associação de classe do titular, sem excluir ativo.

Na interface, barras atuais e alvos, tabela textual, edição da meta, classificação manual e correção/remoção posterior da classificação sem apagar o ativo real. Atualização na abertura, em alterações financeiras e em reentrada na página; sem consulta a preços externos.

## Evidência e pendências

Testes: `backend/tests/test_spec031_investment_allocation.py`, com o cenário 25/75 versus alvos 50/50, atualização real, reclassificação, exclusão de simulações, soma inválida e isolamento entre titulares.

**Decisões provisórias de OPEN-21**: classe padrão das contas tipo investment = outros, contas correntes/dinheiro não investidos e validação estrita de soma 100%. Revisão formal e mobile/benchmark operacional continuam fora deste recorte; não registrar aprovação formal inexistente.

A conclusão técnica só é afirmada após verificar os workflows do PR. Nenhum merge está autorizado nesta entrega.
