# Plano — SPEC-051: Conceder conquistas sem efeito financeiro

## Escopo executado

- Três conquistas por metas e marcos de uso.
- Tela com obtidas e progresso das próximas.
- Notificação in-app ao conceder, respeitando preferências.

## Camadas e arquivos

- Persistência: `AchievementRecord`; migração `034_engagement_features.py` (também amplia os tipos de notificação).
- Aplicação: `EngagementFeaturesService.achievements`; `NOTIFICATION_KINDS` em `auth.py`.
- API: `GET /api/v1/auth/financial/achievements`.
- Web: `Achievements` (aba Planejamento).
- Testes: `backend/tests/test_spec050_052_engagement.py`.

## Riscos e limites

- Avaliação sob demanda: a conquista surge na próxima consulta, não no instante do evento.
- Concessão concorrente protegida por restrição única.
