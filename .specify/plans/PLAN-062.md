# Plano — SPEC-062: Consultar distribuição de perfis no painel

## Escopo executado

- Distribuição agregada por perfil do quiz (conservador, moderado, arrojado) e contagem separada de contas sem perfil.
- Filtro por período de cadastro (datas inclusivas em America/Sao_Paulo).
- Acesso exclusivo de administrador; atualização automática da tela a cada 60 s.

## Camadas e arquivos

- Aplicação: `backend/app/application/profile_distribution.py` (`ProfileDistributionService`).
- Apresentação: `GET /api/v1/admin/investor-profiles` em `backend/app/main.py`; schemas `ProfileDistributionOutput` e `ProfileDistributionItemOutput`.
- Web: `AdminProfileDistribution` em `frontend/src/Extras.tsx`, exibido na aba Administração.
- Testes: `backend/tests/test_spec062_profile_distribution.py`.

## Riscos e limites

- Sem migração: usa `users.investor_profile` e `users.created_at` existentes.
- Percentual calculado apenas sobre usuários com perfil; a contagem sem perfil é exibida à parte para não distorcer o gráfico.
