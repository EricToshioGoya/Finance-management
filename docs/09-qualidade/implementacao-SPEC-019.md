# SPEC-019 — Exportar extrato pessoal CSV/PDF

## Contrato implementado

O titular autenticado e com e-mail confirmado baixa o próprio extrato por `GET /api/v1/auth/financial/exports/csv` ou `/pdf`. Período é um entre: `month=AAAA-MM`, `year=AAAA` ou `start=AAAA-MM-DD&end=AAAA-MM-DD`. O servidor não recebe um ID de usuário e sempre deriva o titular da sessão. A sessão de acesso existente expira em 15 minutos (ADR-007); portanto, o download protegido deixa de ser autorizado quando a sessão expira. Não há URL pública que contenha token financeiro, evitando vazamento por histórico, Referer ou logs.

CSV usa UTF-8, cabeçalho, datas, tipo, descrição, categoria e valor. Descrições iniciadas por `=`, `+`, `-` ou `@` são prefixadas por apóstrofo para não virar fórmula. PDF traz período, saldo, resumo por categoria e detalhes, possui xref válido e paginação. Período vazio é explícito. A visão inclui despesas pontuais/recorrentes, receitas pontuais/recorrentes e bônus; não altera saldos nem se torna fonte de verdade.

## Privacidade e limites

Downloads são resposta anexada com autorização de curta duração na sessão atual, não link reutilizável. Usuário B não recebe dados de A; filtros não aceitam identificador de titular. Não há retenção de conteúdo do arquivo nem auditoria persistente nesta SPEC porque a trilha mínima de eventos/auditoria pertence à SPEC-060 seguinte. A exportação contempla lançamentos financeiros disponíveis, não todos os dados pessoais: portabilidade integral continua OPEN-29. Não foi escolhido armazenamento externo, e-mail ou URL pública.

## Interface e testes

A tela autenticada oferece datas inicial/final e botões CSV/PDF. A prévia isolada não gera arquivos. `backend/tests/test_spec019_statement_export.py` cobre PDF/CSV, fórmula, saldo +70, filtros mês/ano/intervalo, isolamento de titular, autenticação, períodos inválidos, vazio e xref. A CI deve validar PostgreSQL, cobertura e navegador no commit do PR.
