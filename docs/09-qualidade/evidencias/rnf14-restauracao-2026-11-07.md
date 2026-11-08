# Evidência RNF-14 — backup e restauração local de 2026-11-07

Comandos (raiz do repositório, PostgreSQL 16.15, banco com migrations até `039_cvm_ipe_protocol_identity`):

1. `scripts/backup.sh`: `pg_dump` em formato custom para `.local/backups/` (fora do Git, permissão 700).
2. `scripts/verificar-restauracao.sh <arquivo.dump>`: cria um banco isolado, executa `pg_restore`, compara a contagem de linhas de todas as tabelas com a origem e remove o banco isolado ao final.

| Verificação | Resultado |
|---|---|
| Restauração em banco isolado | 56 tabelas e 156 linhas iguais à origem (usuários, contas, despesas e rendas sintéticas criados pela API) |
| Versão do schema restaurado | `039_cvm_ipe_protocol_identity`, igual à origem |
| Tempo de restauração (RTO observado) | < 1 s (meta: 4 h) |
| Caso negativo | Uma despesa excluída na origem depois do backup: o script aponta `expenses` 92 × 93 e termina com código 1 |
| Limpeza | Nenhum banco `finnova_restauracao_*` permanece após a execução |

## Exclusões depois do backup (OPEN-05)

Restaurar um backup anterior a uma exclusão de conta reintroduziria os dados excluídos. A API reaplica o diário de exclusões (`DeletionJournal`, SPEC-018) na inicialização e não atende requisições se a reaplicação falhar. Por isso, o procedimento de recuperação é: restaurar o banco, manter o arquivo do diário (`FINNOVA_DELETION_JOURNAL_PATH`) e iniciar a API.

## Limites

- Volume pequeno e sintético: o seed parou no limite de 100 escritas por minuto (RNF-13). O RTO real depende do volume de produção.
- RPO de 24 h exige agendamento diário do `scripts/backup.sh` (ex.: cron) e cópia para armazenamento externo. Isso depende do ambiente de produção, ainda não definido (OPEN-32).
- Esta evidência não declara o RNF-14 atendido em operação; comprova apenas o procedimento de backup e restauração.
