# Tarefas — SPEC-017

- [x] Criar migration aditiva para instante de criação e índice de consulta por titular.
- [x] Listar somente sessões ativas do próprio titular, sem tokens ou digests.
- [x] Revogar uma sessão própria de forma idempotente e sem revelar identificadores de terceiros.
- [x] Revogar todas as sessões, incluindo a atual, e remover o cookie de renovação.
- [x] Incluir os novos endpoints sensíveis no limite de requisições.
- [x] Expor gerenciamento de sessões em português e inglês na interface web e no demo fictício.
- [x] Cobrir lista, posse, idempotência, revogação isolada, refresh revogado e revogação global em PostgreSQL.
- [x] Atualizar Spec, requisitos, ADR, modelo, mapa, README e registro de evidência.
- [ ] Medir disponibilidade, backup/restore, monitoramento e revisão manual de acessibilidade em ambiente operacional (OPEN-32).
