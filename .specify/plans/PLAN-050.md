# Plano — SPEC-050: Comparar score por grupo anônimo

## Escopo executado

- Comparação com média e mediana agregadas do grupo do mesmo perfil.
- Mínimo de 30 pessoas; abaixo disso, nada é exibido.
- Opt-out nas configurações de privacidade, sem perder o score.

## Camadas e arquivos

- Persistência: `PrivacySettingsRecord`; migração `034_engagement_features.py`.
- Aplicação: `EngagementFeaturesService.benchmark/privacy` em `backend/app/application/engagement_features.py`.
- API: `/api/v1/auth/financial/health-score/benchmark` e `/api/v1/auth/profile/privacy`.
- Web: `ScoreBenchmark` (aba Visão geral).
- Testes: `backend/tests/test_spec050_052_engagement.py`.

## Riscos e limites

- Custo: a taxa de poupança é calculada por membro do grupo a cada consulta; aceitável no volume atual.
- Privacidade: somente agregados; tamanho do grupo não é revelado abaixo do mínimo (RB-26).
