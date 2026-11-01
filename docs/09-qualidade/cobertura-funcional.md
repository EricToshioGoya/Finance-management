# Cobertura funcional consolidada

Atualizada em 2026-10-31 após a integração do código do grupo e a implementação das 12 Specs restantes.

SPEC-019: CSV/PDF protegido por sessão, período e isolamento de titular em implementação isolada; [contrato e limites](implementacao-SPEC-019.md). O estado final depende da CI do PR próprio.

SPEC-018: implementação isolada com política confirmada em 2026-10-28. [Contrato e evidências](implementacao-SPEC-018.md). Aprovação final depende dos checks atuais; a tabela histórica não substitui este registro.

| Capacidade | Código atual | Próxima evidência |
|---|---|---|
| Cadastro/login, refresh/logout | Implementado na SPEC-001; RF-74 | Regressão PostgreSQL/HTTPS e navegador executada em 2026-10-23; ver registro SPEC-001 |
| Bloqueio por conta RF-02 | Implementado no complemento SPEC-001 de 2026-10-23; rate limit preservado | 8 testes de regressão PostgreSQL: limite, 15 minutos, reset, concorrência, inexistente, IPs/instâncias e limpeza |
| Perfil, e-mail, senhas, preferências, sessões RF-68 a RF-73 | Implementado nas SPEC-014 a SPEC-017 | `test_spec014` a `test_spec017` na CI; registros factuais criados em 2026-10-31 |
| Exclusão/exportação RF-05/RF-50 | Implementado nas SPEC-018 e SPEC-019 | Registros SPEC-018/019; restauração de backup depende de OPEN-05/32 |
| Painel e autorização RF-54/RNF-21 | Implementado: usuários (SPEC-011), engajamento (SPEC-043) e distribuição de perfis (SPEC-062) | Testes 401/403 por rota administrativa |
| Motor puro de juros compostos | Implementado na SPEC-002, sem I/O; RF-22 parcial | Referências independentes, precisão/contexto, equivalências e benchmark; registro SPEC-002 |
| Contas e cartões RF-12 | Implementado na SPEC-005 | Migração, isolamento por titular e testes de fontes financeiras |
| Receita recorrente RF-06 | Implementado na SPEC-056 | Migração, valor positivo, idempotência e isolamento por titular |
| Receita pontual RF-07 | Implementado na SPEC-057 | Competência, idempotência, isolamento e total mensal |
| Bônus e PLR RF-08 | Implementado na SPEC-058 | Periodicidade, mês anual obrigatório e sem diluição |
| Despesa pontual ou recorrente RF-09 | Implementado na SPEC-059 | Categoria, origem exclusiva, idempotência, recorrência e isolamento por titular |
| Edição de lançamentos e saldo coerente RF-11 | Implementado na SPEC-006 | Edição/exclusão de receitas, bônus e despesas; resumo líquido por competência |
| Calculadora, simulações, orçamento, painel e fatura | Implementado no lote SPEC-004 a SPEC-024; seletores de período da taxa, unidade de prazo e origem da taxa (SPEC-013), diferença percentual e melhor cenário (SPEC-010), gasto por categoria agregado no servidor (SPEC-022) | Testes `test_SPEC_NNN_Rxx` por cláusula; ciclo de fatura por fechamento depende de OPEN-12 |
| Indicadores oficiais, PTAX e Tesouro Direto | Cache local, consulta e sincronização diária às 07:00 (ADR-009): SGS 432/4389/13522, PTAX de venda D-1 útil e taxas do Tesouro Transparente; novas tentativas após 5, 15 e 45 min; ativada por `FINNOVA_OFFICIAL_SOURCES_SYNC=true` ou `python -m app.jobs.indicator_sync` | Primeira execução real no ambiente de implantação (o ambiente de desenvolvimento não alcança os hosts oficiais) e observabilidade (OPEN-32) |
| CI obrigatória | Workflow `.github/workflows/ci.yml` (backend com PostgreSQL, frontend, mobile, segurança, E2E Playwright e verificador documental) em cada PR | Proteção de branch no GitHub ainda depende de configuração do repositório |
| Ciclo do cartão OPEN-12 | Fatura pelo dia de fechamento, parcelas (1 a 48, resíduo na 1ª), limite com parcelas futuras e alerta configurável por cartão (70% a 100%) | Pagamento de fatura e financiamento (fora da OPEN-12) |
| Sincronização CVM | Semanal, domingo 03:00 (ADR-009): cadastro e índices DFP/ITR/IPE, identidade CNPJ+tipo+referência+versão, reapresentação sem novo alerta e aviso da watchlist para documento inédito | Primeira execução real na implantação; identidade de IPE com mesma referência pendente |
| Rastreabilidade C-02 | `scripts/verificar-c02.py`: 201/398 cláusulas citadas por teste; 16 specs de testes agrupados concluídas em 2026-10-31 | Anotar com o ID da cláusula os testes por comportamento das 30 specs restantes |
| Desempenho RNF-04 | `scripts/carga.py`: P95 de 257 a 566 ms local | Medição em produção (OPEN-32) |
| Backup/monitoramento | Requisitos sem evidência operacional | Evidências operacionais próprias (RNF-08/12/14) |
| Compartilhamento, aposentadoria, previdência, IR/DARF, resumo anual, score por grupo, conquistas, tour, canais e resumo mensal | Implementado em 2026-10-31 (SPEC-040, 044 a 052, 061, 062) | Testes `test_SPEC_NNN_Rxx` por cláusula; registros próprios em `docs/09-qualidade/` |
| Interface web | Navegação por abas com telas para todas as APIs (PR #45) | Playwright com axe WCAG AA em `frontend/tests` |
| Aplicativo mobile (Expo) | Versão mínima em `mobile/`: login, resumo do mês, despesa e avisos | Typecheck, testes unitários e bundle Android na CI; teste em dispositivo e push dependem de OPEN-08/17 |

A integração de 2026-10-22 incorporou código existente. O complemento de 2026-10-23 implementou o bloqueio e executou regressão funcional; ver [registro da SPEC-001](implementacao-SPEC-001.md). SPEC-002 foi implementada em seguida, com [evidência própria](implementacao-SPEC-002.md); as capacidades restantes permanecem planejadas.

