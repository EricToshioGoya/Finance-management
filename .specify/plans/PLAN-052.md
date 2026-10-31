# Plano — SPEC-052: Guiar primeiro acesso com tour opcional

## Escopo executado

- Tour no primeiro acesso cobrindo receita, despesa, quiz e simulador.
- Pular a qualquer momento e reabrir pela ajuda.
- Roteiro didático ou resumido conforme o perfil, sem inventar perfil.

## Camadas e arquivos

- Persistência: `OnboardingTourRecord`; migração `034_engagement_features.py`.
- Aplicação: `EngagementFeaturesService.tour/update_tour`.
- API: `GET|PUT /api/v1/auth/profile/tour`.
- Web: `OnboardingTour` (Visão geral) e `ReopenTour` (aba Aprender).
- Testes: `backend/tests/test_spec050_052_engagement.py`.

## Riscos e limites

- O tour é exibido na aba Visão geral, que exige e-mail confirmado para as funções financeiras.
