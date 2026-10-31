# SPEC-044 — Aceitar e desfazer vínculo entre dois usuários

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31 (OPEN-31): resposta genérica ao convite; no máximo um vínculo ativo; convite válido por 7 dias; recusa pelo convidado e cancelamento pelo convidante; histórico compartilhado preservado e visível aos dois após o fim, somente leitura.

## Contrato implementado

`GET /api/v1/auth/sharing`; `POST /api/v1/auth/sharing/invitations` (202); `POST /api/v1/auth/sharing/invitations/{id}/accept` (200), `/decline` e `/cancel` (204); `POST /api/v1/auth/sharing/links/{id}/end` (204). Erros: 401 sessão, 403 e-mail não verificado, 404 convite/vínculo de terceiro, 409 expirado ou vínculo já ativo, 422 auto-convite.

## Testes

- `test_SPEC_044_R01_R03_R04_link_is_created_only_after_acceptance`
- `test_SPEC_044_R02_self_unknown_and_third_party_never_create_link`
- `test_SPEC_044_R02_invitation_expires_and_single_active_link`
- `test_SPEC_044_R02_decline_and_cancel`
- `test_SPEC_044_R05_either_member_ends_link_preserving_history`
- `test_SPEC_044_R06_individual_data_stays_private`
- `test_SPEC_044_045_require_verified_email`

## Limites

Sem notificação por e-mail do convite (depende de OPEN-17/SPEC-061); o convidado vê o convite na própria aba. Revisão formal do grupo pendente.
