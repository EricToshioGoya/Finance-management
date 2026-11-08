# Catálogo de Dívida Técnica — FinNova

- **Status:** vivo; atualizar no mesmo PR que cria, paga ou reavalia um item.
- **Última atualização:** 2026-11-07
- **Referências:** quadrante de Fowler (deliberada/inadvertida × prudente/imprudente); catálogo de refatorações de Fowler; `estrategia-de-testes.md`, seção 10.

Cada item novo é aberto também como issue com o template `.github/ISSUE_TEMPLATE/divida-tecnica.md`. A prioridade combina risco e frequência de mudança da área. O pagamento segue a regra de refatoração: PR próprio, um passo por commit, testes existentes inalterados e suíte completa verde entre os passos.

## 1. Itens

| ID | Item | Tipo | Quadrante | Impacto | Prioridade | Situação |
|---|---|---|---|---|---|---|
| DT-01 | Bloco de autenticação repetido nas rotas de `main.py` | Implementação (duplicação) | Inadvertida, prudente | Cada rota nova copiava 3 linhas; risco de esquecer a verificação | Alta | Paga em 2026-11-07: dependência `CurrentUser` em 99 rotas. Restam 13 rotas que validam a entrada antes de autenticar ou usam a sessão (`sharing_user`, `owner_id`, sessões) |
| DT-02 | Gravação com conflito de unicidade copiada (409 e idempotência) | Implementação (duplicação) | Inadvertida, imprudente (uma cópia foi criada por agente) | Correção de um caso não chegava aos outros (despesa sem tratamento de envio paralelo) | Alta | Paga em 2026-11-07: `_commit_or_conflict` e `_commit_or_existing` substituem 10 cópias; notificação e snapshot mantêm variações próprias |
| DT-03 | `AuthService` concentra identidade, lançamentos, patrimônio, planejamento e notificações | Design (viola SRP e ADR-001) | Deliberada, imprudente ("não temos tempo para projetar") | 2.655 linhas e 108 métodos; mudanças em uma área arriscam outras | Alta | Em pagamento: rendas e bônus movidos para `rendas.py` (`OperacoesRenda`). Próximos: despesas e cartões, patrimônio, metas, notificações, planejamento; depois separar dependências (serviços independentes em vez de herança) |
| DT-04 | `main.py` com 151 rotas e dependências definidas dentro de `create_app` | Design (acoplamento) | Deliberada, imprudente | 2.489 linhas; rotas não podem ser movidas para `APIRouter` sem antes tirar as dependências do closure | Alta | Aberta. Passos: (1) mover `Service`, `CurrentUser` e serviços para `presentation/dependencias.py` lendo `request.app.state`; (2) um `APIRouter` por módulo, um PR por módulo |
| DT-05 | `frontend/src/main.tsx` reúne sessão, navegação e telas | Design | Inadvertida, prudente | 902 linhas; testes só via Playwright | Média | Aberta. Extrair hook de sessão e o shell de navegação |
| DT-06 | Verificação de tipos só no domínio | Implementação (testes faltantes) | Deliberada, prudente | Erros de tipo em aplicação e apresentação só aparecem em execução | Média | Em pagamento: `mypy` em `app/domain` na CI e no pre-commit (2 erros reais corrigidos). Ampliar para `app/application` |
| DT-07 | Regras de negócio em `application/` testáveis só com banco | Design | Inadvertida, prudente | Pirâmide com 36% de testes unitários | Média | Aberta; avança junto com DT-03 (extrair cálculos puros para `app/domain`) |
| DT-08 | Complexidade não era medida | Implementação | Inadvertida, prudente | Funções longas sem alerta | Baixa | Paga em 2026-11-07: ruff `C90` (máximo 10), `SIM`, `PLR0912`, `PLR0915`; `statement_entries` e `simulate_stress` divididas |
| DT-09 | `npm audit` do mobile não bloqueante | Implementação (dependências) | Deliberada, prudente | Vulnerabilidades altas e críticas no ferramental do Expo SDK | Baixa | Aberta; resolver na próxima atualização do Expo SDK |

## 2. Prevenção em vigor

- Revisão em três camadas (`docs/combinados.md`, seção 2): ferramentas determinísticas (CI e pre-commit), revisor IA quando houver (aceite ou rejeição registrados no PR) e revisão humana, que decide o merge.
- Pre-commit (`.pre-commit-config.yaml`): ruff, mypy, unitários sem banco, lint do frontend, testes do mobile e verificadores documentais.
- CI: aviso para PR acima de 400 linhas e varredura de segredos (gitleaks).
- Instruções do agente versionadas (`CLAUDE.md`, `AGENTS.md`) e spec aberta na revisão (C-01, C-02).

## 3. Métricas

| Métrica | Fonte |
|---|---|
| Defeitos que escaparam da revisão | Issues `bug` com fase "Produção" ou "Testes" no template de defeito |
| Retrabalho em código recente | Commits `fix` que alteram arquivos modificados nos 30 dias anteriores |
| Aceitação dos comentários de IA | Seção "Revisor IA" do template de PR (aceitos × rejeitados) |
| Tamanho dos PRs | Aviso do job `revisao` na CI |
| Dívida aberta | Itens com situação "Aberta" ou "Em pagamento" nesta tabela |
