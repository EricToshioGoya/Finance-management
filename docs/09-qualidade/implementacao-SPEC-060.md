# SPEC-060 — Eventos de uso e auditoria

## Decisão autorizada

Em 2026-10-28, o responsável autorizou: evento mínimo assíncrono, sem retry automático; falha de coleta não bloqueia nem confirma uma ação financeira; exclusão de conta anonimiza eventos e auditorias; e a trilha não é exposta para edição operacional.

## Contrato implementado

`POST /api/v1/auth/usage-events` requer sessão válida e aceita exclusivamente `module` (`dashboard`, `simulator`, `financial` ou `profile`) e `action` (`opened` ou `viewed`). Retorna `202` e enfileira uma tarefa de fundo que abre sua própria sessão de banco. A tabela `usage_events` tem somente identificador técnico, `user_id`, módulo, ação e instante UTC — não possui payload, descrição ou valor financeiro.

O cliente registra a abertura do painel como melhor esforço, sem aguardar o resultado. A mensagem visível informa a coleta agregada para melhoria do produto e que administradores não veem conteúdo financeiro. A futura SPEC-011 é responsável por qualquer visão administrativa agregada.

`audit_logs` é escrito internamente para mudança de senha, revogação global de sessões e exclusão de conta. Não há endpoint de consulta, alteração ou exclusão operacional. Senhas, tokens, IPs, conteúdo financeiro e corpos HTTP não entram na trilha.

## Exclusão e limites

Ao excluir uma conta, eventos e auditorias relacionados têm `user_id` tornado nulo antes da remoção do usuário. Isso preserva a evidência operacional sem manter associação identificável. A política não afirma retenção legal, backup, dashboard administrativo, fila, alerta ou retentativa: esses temas permanecem abertos nas Specs que os consomem.

## Testes

`backend/tests/test_spec060_usage_events_audit.py` cobre autenticação, vocabulário fechado, ausência de payload financeiro, instante UTC, ausência de rota de mutação, auditoria de senha e anonimização na exclusão. O pipeline deve executar a suíte PostgreSQL, lint/formatação e cobertura antes da revisão do PR.
