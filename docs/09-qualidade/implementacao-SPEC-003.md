# SPEC-003 — Quiz de perfil de investidor

## Política confirmada

Em 2026-10-28, o responsável confirmou cinco perguntas: conhecimento, reação a queda temporária de 15%, horizonte, liquidez e tolerância à volatilidade. Cada resposta vale 0, 1 ou 2; a soma classifica 0–3 como conservador, 4–6 como moderado e 7–10 como arrojado.

## Entrega

- `GET /api/v1/auth/investor-profile/quiz` apresenta as cinco perguntas autenticadas.
- `PUT /api/v1/auth/investor-profile` valida as cinco respostas, persiste e permite substituir o perfil.
- `GET /api/v1/auth/investor-profile` retorna somente o perfil do titular.
- A calculadora autenticada inclui a orientação textual correspondente, sem bloquear cálculos ou recomendar produtos.
- O cliente web apresenta o quiz acessível por rádio, com textos PT/EN.

## Evidência

`backend/tests/test_spec003_investor_quiz.py` cobre autenticação, perguntas, respostas inválidas sem alteração, três faixas, refazer, isolamento entre titulares e orientação no cálculo. A migração `015_investor_profile_quiz` mantém o valor em domínio fechado.

O estado final depende da CI do PR; esta página não a declara aprovada antecipadamente.
