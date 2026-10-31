# SPEC-041 — API de integrações autorizadas (recorte técnico)

## Capacidade entregue

Um titular com **sessão válida e e-mail confirmado** pode criar, listar e revogar credenciais de terceiros **diferentes do JWT usado no app**. O cliente externo recebe uma chave aleatória `fnv_...` somente no momento de emissão, e sua persistência contém apenas SHA-256; o nome da integração é cifrado. Cada chave tem data de expiração, escopos explícitos e titular próprio. As chaves nunca aparecem na listagem, logs da aplicação ou contratos de resposta de leitura. A emissão é limitada aos escopos `balance:read` e `net_worth:read`, sem permissão de escrita ou compartilhamento de dados individuais.

### Contratos REST documentados no OpenAPI

Rotas do titular, autenticadas com `Authorization: Bearer <token de sessão>`:

- `GET /api/v1/external/grants` — lista metadados das concessões sem revelar segredo
- `POST /api/v1/external/grants` — `{"name":"Integração","scopes":["balance:read"]}`; retorna uma vez `api_key`, validade e ID
- `DELETE /api/v1/external/grants/{grant_id}` — revoga imediatamente a chave do próprio titular

Rotas de consumo, autenticadas **somente** com `X-FinNova-API-Key: fnv_...`, nunca aceitando apenas o JWT:

- `GET /api/v1/external/balance?competence=YYYY-MM` requer `balance:read`, retorna somente `competence`, `income`, `expenses` e `balance_variation`
- `GET /api/v1/external/net-worth` requer `net_worth:read`, retorna `as_of`, `total_assets`, `total_liabilities` e `net_worth`

Nomes, IDs de contas, lançamentos, cartões e dados de outra pessoa não são exportados. API pública de **documentação** (OpenAPI/Swagger) é diferente de uma API pública sem autenticação: os recursos financeiros continuam privados e só podem ser lidos após consentimento.

## Modelo e limites técnicos provisórios

A credencial é revogável individualmente, dura **no máximo 90 dias** e o consumidor externo é limitado a **30 leituras/minuto por chave**, com contador, janela e bloqueio de linha persistidos em PostgreSQL para consistência entre processos; excedente retorna 429 e `Retry-After: 60`. Revogação, expiração, conta ausente, e-mail não confirmado e ausência de credencial recusam consumo; escopo inválido responde 403. Nenhuma rota externa realiza mutação financeira. Contadores e instante de último uso auxiliam a auditoria técnica. Chaves secretas não são coletadas por query string.

**OPEN-24 e OPEN-15 continuam abertas para decisão formal do grupo:** API key versus OAuth2, cotas definitivas, renovação, limites por aplicativo/organização, consentimento multiusuário, rotação e revogação em massa. O perfil escolhido é somente um recorte conservador e testável, não contrato público final de produção. Exclusão de usuário remove as credenciais vinculadas por FK `ON DELETE CASCADE` e pela rotina de expurgo. RNFs operacionais (P95, monitoramento, revisão LGPD, compatibilidade mobile) ainda requerem evidências.

**Dependência de migrações:** esta branch usa `029_external_api_keys` a partir de `028_named_asset_goals`. Existe também a migração `029_confirmed_financings` no PR #75 (SPEC-038) ainda não mesclado. **É obrigatório reconciliar a árvore Alembic e o parent revision após o primeiro desses PRs ser integrado**; não fazer merge de ambas as branches com dois heads. Isso não afeta o funcionamento ou CI desta branch isolada.

## Evidências

Teste `backend/tests/test_spec041_external_api.py`: concessão por titular verificado, sigilo de chave, escopo limitado, rejeição de JWT como API key, isolamento entre titulares, revogação, expiração, limite de 30/min e sem dados individuais na resposta. Os checks do GitHub Actions devem aprovar lint, testes PostgreSQL, build e navegador. Revisão formal ainda pendente.
