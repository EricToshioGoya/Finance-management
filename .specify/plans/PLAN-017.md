# Plano — SPEC-017: consultar, renovar e encerrar sessões

## Decisões de implementação

- A migration 004_session_management registra o instante UTC de criação de cada sessão técnica já persistida; expiração e revogação continuam na mesma entidade de infraestrutura.
- GET /api/v1/auth/sessions devolve apenas sessões ativas do titular autenticado, com id, início, expiração e marcação da sessão atual. Não devolve access token, refresh token ou digest.
- POST /api/v1/auth/sessions/{id}/revoke encontra a sessão pelo par titular/id. ID inexistente e ID de outro titular retornam o mesmo 404 session_not_found; repetir a revogação de uma sessão própria é idempotente.
- POST /api/v1/auth/sessions/revoke-all revoga todas as sessões do titular, inclusive a atual, remove o cookie de refresh e informa a quantidade revogada.
- A renovação com rotação, replay que revoga a família e logout da sessão atual permanecem os contratos da SPEC-001/ADR-007. Os novos POSTs participam do limite compartilhado por IP e endpoint sensível.
- Cliente web lista as sessões ativas, permite encerrar uma ou todas e limpa o estado local quando a sessão atual é revogada. O demo usa somente uma sessão fictícia em memória.

## Fora do recorte

Identificação do dispositivo, localização, notificações de login, app Expo, recuperação/alteração de senha e operação de backup/monitoramento pertencem a outras Specs e OPENs.
