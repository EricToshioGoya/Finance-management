# Plano — SPEC-014: editar perfil e preferências persistidas

## Decisões de implementação

- A migration 005_profile_preferences acrescenta e-mail pendente cifrado e lookup HMAC único ao usuário, amplia a finalidade de token de confirmação e cria a tabela user_preferences.
- PATCH /api/v1/auth/profile permite alterar nome e iniciar troca de e-mail. A troca exige a senha atual, entrega token opaco no novo endereço e mantém o e-mail ativo até a confirmação.
- GET /api/v1/auth/profile devolve somente o perfil do titular, e-mail pendente e preferências. PATCH /profile/preferences grava idioma, tema e canais; não há campo editável de papel.
- Preferências possuem valores padrão antes do primeiro salvamento, mas passam a ser persistidas no PostgreSQL depois do primeiro PATCH. O cliente carrega o perfil ao restaurar a sessão, aplica idioma/tema e oferece formulários acessíveis.
- Tokens de confirmação continuam guardados apenas por digest. Falha do adaptador de e-mail não grava nome nem e-mail pendente quando a mesma operação contém ambos.

## Fora do recorte

Não há provedor operacional de e-mail, push real, alteração de senha, app Expo, identificação de dispositivo ou auditoria operacional. Esses pontos permanecem nas Specs e OPENs correspondentes.
