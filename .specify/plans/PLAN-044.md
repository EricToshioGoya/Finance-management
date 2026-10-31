# Plano — SPEC-044: Aceitar e desfazer vínculo entre dois usuários

## Escopo executado

- Convite por e-mail sem enumeração, aceite, recusa, cancelamento e expiração em 7 dias.
- Um vínculo ativo por usuário; qualquer membro desfaz o vínculo.
- Histórico de vínculos encerrados disponível, somente leitura.

## Camadas e arquivos

- Domínio/persistência: `SharedLinkRecord` em `backend/app/infrastructure/models.py`; migração `032_shared_accounts.py`.
- Aplicação: `backend/app/application/sharing.py` (`SharingService`).
- Apresentação: rotas `/api/v1/auth/sharing*` em `backend/app/main.py`; schemas `Sharing*`.
- Web: aba Compartilhado (`frontend/src/Sharing.tsx`).
- Testes: `backend/tests/test_spec044_045_sharing.py`.

## Riscos e limites

- Concorrência no aceite: os dois usuários são bloqueados (`FOR UPDATE`) antes de ativar o vínculo, evitando dois vínculos ativos simultâneos.
- Expiração é avaliada sob demanda nas operações (sem job agendado).
