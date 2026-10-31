# SPEC-011 — Painel administrativo e metadados de usuários

## Política autorizada

Em 2026-10-28, o responsável autorizou o bootstrap local por `FINNOVA_INITIAL_ADMIN_EMAIL`. Cadastro público nunca aceita papel; o primeiro administrador só é promovido após confirmar o e-mail configurado e se não houver outro administrador. Esta Spec não publica promoção contínua de usuários.

## Contrato implementado

`GET /api/v1/admin/users` exige sessão válida com papel `administrador`, verificado no backend. Sem sessão retorna `401`; titular comum retorna `403` com `admin_access_denied`. A resposta é paginada e aceita `page`, `page_size` (1–100), `query`, `status=active` e `profile=unassigned`.

Cada item contém apenas id técnico, nome, e-mail, instante UTC de cadastro, perfil de investidor `null` e status `active`. O perfil será preenchido pela SPEC-003. Não há relações, lançamentos, valores, patrimônio, senha, hash ou token na resposta. Todo acesso bem-sucedido acrescenta a ação interna `admin_users_listed` à auditoria; nenhuma rota de alteração da trilha é publicada.

## Interface e testes

O cliente mostra a lista somente quando a sessão retornada tem papel administrativo; essa ocultação é apenas experiência de uso, pois a autorização permanece no servidor. `backend/tests/test_spec011_admin_users.py` cobre bootstrap após confirmação, negação 401/403, paginação, busca, filtros, metadados mínimos, auditoria e tentativa de injetar papel no cadastro. A CI do PR executa PostgreSQL, cobertura, lint, build e navegador.
