# SPEC-018 — Exclusão de conta

Política confirmada pelo responsável nesta sessão em 2026-10-28: exclusão imediata na base ativa, revogação de todas as sessões, auditoria sem identificação e reaplicação de exclusões antes de liberar restauração. Não é aprovação histórica nem parecer legal. Entrega isolada da main; não inclui SPEC-019/060/011/003 do PR #50.

## Contrato e interface

- GET `/api/v1/auth/account/deletion-preview`: sessão obrigatória; dados apagados, prazo, retenções e backups.
- DELETE `/api/v1/auth/account`: senha atual + texto exato `EXCLUIR MINHA CONTA`. Não recebe ID de outro titular. Sucesso 204 remove cookie, todas as sessões e dados dependentes. Senha incorreta 401, texto inválido 422, falha de persistência 503 sem confirmação falsa. Rate limit no endpoint sensível.
- Web PT/EN: revisão antes da confirmação, cancelamento sem DELETE, limpeza de senha/texto após tentativa, retorno ao login e limpeza de estado pessoal após sucesso. Prévia fictícia não executa exclusão real.

Perfil, credenciais, preferências, sessões/tokens, contas/cartões, receitas, despesas, categorias, metas e simulações são apagados respeitando dependências. Sem alteração de dados de outro titular. Eventos de uso não existem na baseline main; a futura SPEC-060 deverá integrar esta política.

## Registro independente e restauração

`FINNOVA_DELETION_JOURNAL_PATH`: SQLite persistente FORA do backup PostgreSQL, com permissões restritas, transações e synchronous FULL. Padrão de desenvolvimento: `../.local/account-deletions.sqlite3`, a partir de backend. Guarda HMAC do UUID usando a chave existente, não nome/e-mail/UUID direto. É marcador técnico pseudonimizado restrito, não anonimização absoluta. Auditoria separada contém ação e instante, sem ator/alvo.

O marcador é persistido ANTES da exclusão. Se o PostgreSQL falhar depois disso, retorna 503; a intenção confirmada bloqueia acesso e será reaplicada no startup, de forma idempotente. Não há promessa de transação distribuída.

Restauração: parar TODAS as instâncias; preservar registro independente MAIS RECENTE e `FINNOVA_DATA_KEY`; restaurar PostgreSQL isolado sem substituir o registro por backup antigo; iniciar aplicação, que reaplica exclusões antes de servir; validar health antes de liberar tráfego. Falha na reconciliação ou banco com usuários e registro ausente bloqueia startup. Não restaurar sob processos em execução.

Instalação vazia inicializa registro automaticamente. Atualização de banco preexistente sem histórico de exclusões exige preparação única do registro vazio pelo operador ANTES de habilitar a função; nunca inicializar vazio para contornar registro perdido. Produção exige volume durável compartilhado entre instâncias, backup independente atualizado e proteção da chave. Um registro substituído por cópia antiga não é detectável apenas pelo PostgreSQL; preservação independente é pré-condição operacional.

Não foi inventado prazo legal ou descarte de backup: o projeto acadêmico não configura retenção identificável legal. Exclusão na base ativa é imediata (dentro da meta de 15 dias); cópias antigas não podem reintroduzir acesso. Retenção física de backups, RPO/RTO, ensaio de infraestrutura e deploy continuam evidências operacionais separadas.

## Testes e evidências

`backend/tests/test_spec018_account_deletion.py`: CA-001/003/005 exclusão/revogação/restauração; CA-002/004 senha/texto inválidos e falhas; CA-006 prévia; isolamento, cascata, cookie, múltiplas sessões, registro idempotente e startup sem registro. `frontend/tests/spec018.spec.ts`: revisar/cancelar, erro de senha, exclusão, recarga sem sessão e análise automática WCAG AA do formulário.

Local: lint backend/frontend, build frontend e 86 testes puros aprovados; teste unitário do registro aprovado. Integração PostgreSQL, cobertura >=90% e navegador dependem dos checks do commit atual do PR; não reutilizar evidência de outro commit nem presumir conformidade operacional.
