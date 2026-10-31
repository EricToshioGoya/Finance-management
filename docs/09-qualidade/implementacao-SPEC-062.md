# SPEC-062 — Consultar distribuição de perfis no painel

## Decisão autorizada

Política proposta pelo agente e aprovada pelo responsável em 2026-10-31: perfis do quiz da SPEC-003; contas sem quiz em categoria própria; filtro por data de cadastro inclusiva no fuso de São Paulo; percentuais sobre usuários com perfil (2 casas, HALF_EVEN); consulta em tempo real, com recarga da tela a cada 60 segundos.

## Contrato implementado

`GET /api/v1/admin/investor-profiles?start&end` → `{start, end, total_users, profiled_users, without_profile, items[{profile, count, percentage}], generated_at}`. 401 sem sessão, 403 `admin_access_denied` para usuário comum, 422 `invalid_period` para início após o fim. A saída não contém identificadores, e-mails nem respostas individuais.

## Testes

- `test_SPEC_062_R01_R03_aggregated_distribution_by_quiz_result`: contagens 2/0/1, percentuais 66,67/0/33,33 e ausência de dados individuais.
- `test_SPEC_062_R02_only_administrators_receive_the_chart`: 401 e 403.
- `test_SPEC_062_R04_filters_by_registration_period`: cadastro às 23h30 de São Paulo conta no dia local; período inválido retorna 422.
- `test_SPEC_062_R05_updates_when_a_new_user_completes_the_quiz`: contagem muda após o quiz.

## Limites

Não há cache nem materialização: para bases grandes, uma consulta agregada por requisição é suficiente no recorte atual. Revisão formal do grupo pendente.
