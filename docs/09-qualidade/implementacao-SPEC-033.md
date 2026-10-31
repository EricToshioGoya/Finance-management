# SPEC-033 — Metas nomeadas vinculadas a ativo real

## Recorte e decisões técnicas

A meta é registrada para um **ativo manual real** (`net_worth_items.kind=asset`) próprio do titular, vinculado por chave estrangeira com exclusão em cascata. Cada ativo pode apoiar várias metas; nenhum valor de meta é contabilizado novamente no patrimônio. Contas bancárias não são associadas diretamente neste primeiro recorte: são origens de patrimônio distintas do cadastro manual de ativo da SPEC-028. A extensão para contas e regras de equivalência permanece em OPEN-19/OPEN-21.

O titular define nome, categoria de cinco opções (`emergency`, `travel`, `home`, `education`, `other`), valor-alvo positivo em BRL, prazo futuro e taxa anual hipotética de retorno (0–100% a.a., padrão explícito de 0%). Nome da meta é criptografado em repouso como nomes de ativos. A aplicação **não infere taxa histórica**, não realiza aporte nem movimentação financeira.

Progresso absoluto, conforme RB-18, é o **valor atual do ativo**, lido a cada consulta e não persistido na meta; percentual informativo é `ativo / alvo × 100`. Percentuais acima de 100 são mostrados numericamente; a barra visual é limitada a 100%. Se o ativo alcançar o alvo, aporte projetado é zero. Data vencida com saldo insuficiente produz `projection_status=overdue` e aporte `null`, sem divisão por zero.

O prazo em meses é contado pelos meses civis de America/Sao_Paulo, arredondando fração positiva para cima. A projeção usa exclusivamente `app.domain.financeiro.aporte_necessario` (SPEC-024/RF-26), que considera aportes no fim do mês. O resultado é estimativa, não garantia nem indicação de ação financeira. Taxa positiva só é usada quando explicitamente fornecida.

## Persistência e API

Migração Alembic `028_named_asset_goals` segue a `027_investment_allocation`. Tabela `named_asset_goals` tem FKs para `users` e `net_worth_items` com ON DELETE CASCADE, sem coluna com saldo de ativo. Todas as operações são privadas, exigem sessão e e-mail verificado:

- `GET /api/v1/auth/financial/named-asset-goals` — listar metas próprias, valores atuais, projeções, percentuais e status
- `POST /api/v1/auth/financial/named-asset-goals` — criar meta com ativo existente do próprio titular, HTTP 201
- `DELETE /api/v1/auth/financial/named-asset-goals/{goal_id}` — excluir somente meta, HTTP 204; ativo permanece

Ativo inexistente, de outro titular ou passivo é recusado igualmente com 404, sem revelar titularidade; alvo zero e data passada com 422. Excluir o ativo real exclui as metas ligadas a ele, preservando integridade referencial. Valores do ativo são reconsultados após edição.

## Interface, testes e pendências

A interface PT/EN contém formulário, seleção de ativo manual, barra de progresso acessível, valores, projeção e remoção explícita da meta. O teste `backend/tests/test_spec033_named_asset_goals.py` verifica R$250/R$1000 = 25%, edição de ativo, múltiplas metas no mesmo ativo, ausência de duplicação patrimonial, exclusão e isolamento.

**OPEN-15/19/21 seguem com decisões formais pendentes** para categorização extensível, vínculo a outras classes de ativos e arredondamento de prazos. Desempenho P95, recuperação operacional e acessibilidade mobile exigem validações próprias. A aprovação técnica fica condicionada ao CI do PR; sem merge na main antes da autorização do responsável.
