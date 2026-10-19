# Governança de Agentes de IA — FinNova

- **Status:** vigente a partir do merge do PR da issue #37
- **Data:** 2026-10-18
- **Issue:** [#37](https://github.com/EricToshioGoya/Finance-management/issues/37)
- **Relacionados:** `CLAUDE.md` (C-10, C-12, C-13), `docs/09-seguranca/seguranca-ssdlc.md`, `docs/10-qualidade/estrategia-de-testes.md`

Descreve o ambiente de agente de codificação adotado, as camadas de controle ativas, a matriz de permissões e o resultado dos testes da política. Princípio adotado: **testar antes de confiar** — nenhuma regra é considerada ativa sem teste registrado na seção 5.

---

## 1. Ambiente

| Item | Definição |
|---|---|
| Ferramenta | Claude Code (CLI, aplicativo desktop e web), única ferramenta de agente adotada pela equipe. |
| Arquivo de instruções | `CLAUDE.md` na raiz do repositório. |
| Configuração versionada | `.claude/settings.json` (permissões e hooks), `.claude/hooks/` e `.claude/skills/`. |
| Configuração local | `.claude/settings.local.json`, ignorada pelo Git, para preferências individuais. |
| MCP | Não adotado. O projeto ainda não possui banco nem serviço externo que justifique um servidor MCP (seção 7). |

---

## 2. Camadas de controle

O controle é feito em camadas independentes, de modo que a falha de uma não comprometa as demais.

| Camada | Mecanismo | Arquivo | Estado |
|---|---|---|---|
| 1. Instruções do repositório | Constituição do projeto, regras não negociáveis e skills do fluxo SDD | `CLAUDE.md`, `.claude/skills/` | Ativa |
| 2. Hook do agente | Permissões allow/ask/deny e hook `PreToolUse` que bloqueia ou pede confirmação antes da execução | `.claude/settings.json`, `.claude/hooks/politica_comandos.py` | Ativa a partir da sessão do Claude Code iniciada após o merge |
| 3. Git hook local | `pre-commit` que barra arquivos e conteúdos de segredo | `.githooks/pre-commit` | Ativa em cada clone após `git config core.hooksPath .githooks` |
| 4. CI e revisão | Verificação de links, varredura de segredos, lint e testes em todo PR; revisão humana | `.github/workflows/ci.yml`, `docs/combinados.md` | CI ativo após o merge; o bloqueio do merge depende da proteção da branch `main` (seção 3) |

---

## 3. Ações do responsável pelo repositório

Configurações que não podem ser versionadas e dependem de permissão de administrador no GitHub:

- [ ] Proteger a branch `main` (*Settings → Branches → Branch protection rules*): exigir pull request, exigir os jobs do CI (`Links da documentação`, `Varredura de segredos`, `Lint e testes (Python)`) e exigir 1 aprovação.
- [ ] Ativar *Secret scanning* e *Push protection* (*Settings → Code security*), quando disponíveis para o repositório.
- [ ] Em cada clone local, executar `git config core.hooksPath .githooks`.

---

## 4. Matriz de permissões do agente

| Decisão | Ação | Onde é aplicada |
|---|---|---|
| **deny** | Ler, editar ou citar em comando os arquivos `.env`, `.env.*` (exceto `.env.example`) e `mcp.env` | Hook e `permissions.deny` |
| **deny** | `DROP TABLE`, `DROP DATABASE`, `DROP SCHEMA` e `TRUNCATE` | Hook |
| **deny** | `git push` forçado (`--force`, `--force-with-lease`, `-f` ou refspec com `+`) | Hook e `permissions.deny` |
| **deny** | `rm` recursivo forçado (`-rf`, `-fr`, `-r -f`) | Hook e `permissions.deny` |
| **ask** | Instalação de dependência (`pip install`, `python -m pip install`, `uv pip install`, `npm install`, `npm i`, `npm ci`) | Hook e `permissions.ask` |
| **ask** | `git push` não forçado | Hook e `permissions.ask` |
| **ask** | Migração de banco (`alembic upgrade`, `alembic downgrade`, `alembic stamp`) | Hook e `permissions.ask` |
| **allow** | Leitura do repositório, `git status`, `git diff`, `git log`, `pytest`, `ruff check` e verificação de links | `permissions.allow` |
| Padrão | Demais ações | Modo de permissão da sessão do Claude Code |

Uma regra **deny** prevalece sobre **ask** e **allow**. O hook avalia o comando completo, inclusive comandos encadeados com `&&`, `;` ou `|`.

---

## 5. Testes da política

Executados em 2026-10-18, antes da ativação.

### 5.1 Hook do agente (camada 2)

Teste por entrada padrão, com cargas JSON no formato do evento `PreToolUse`:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push"}}' | python3 .claude/hooks/politica_comandos.py
```

| Ferramenta | Entrada | Esperado | Obtido |
|---|---|---|---|
| Read | `/repo/.env` | deny | deny |
| Read | `/repo/mcp.env` | deny | deny |
| Read | `/repo/.env.local` | deny | deny |
| Read | `/repo/.env.example` | sem decisão | sem decisão |
| Read | `/repo/docs/visao.md` | sem decisão | sem decisão |
| Edit | `/repo/.env` | deny | deny |
| Bash | `cat .env` | deny | deny |
| Bash | `cp config/mcp.env /tmp/x` | deny | deny |
| Bash | `cat .env.example` | sem decisão | sem decisão |
| Bash | `node -e 'console.log(process.env.HOME)'` | sem decisão | sem decisão |
| Bash | `source .venv/bin/activate && pytest` | sem decisão | sem decisão |
| Bash | `psql -c 'DROP TABLE usuario'` | deny | deny |
| Bash | `psql -c 'truncate despesa'` | deny | deny |
| Bash | `git push --force origin main` | deny | deny |
| Bash | `git push -f` | deny | deny |
| Bash | `git push --force-with-lease origin x` | deny | deny |
| Bash | `git push origin +main` | deny | deny |
| Bash | `rm -rf src` | deny | deny |
| Bash | `cd x && rm -fr build` | deny | deny |
| Bash | `rm -r -f build` | deny | deny |
| Bash | `rm arquivo.txt` | sem decisão | sem decisão |
| Bash | `pip install requests` | ask | ask |
| Bash | `python3 -m pip install -e '.[dev]'` | ask | ask |
| Bash | `npm install react` | ask | ask |
| Bash | `npm i` | ask | ask |
| Bash | `git push -u origin feature/38-motor` | ask | ask |
| Bash | `git -C repo push origin x` | ask | ask |
| Bash | `alembic upgrade head` | ask | ask |
| Bash | `alembic revision -m x` | sem decisão | sem decisão |
| Bash | `git status && git log --oneline -3` | sem decisão | sem decisão |
| Bash | `pytest -q` | sem decisão | sem decisão |
| Glob | `**/*.md` | sem decisão | sem decisão |

**Resultado:** 32 de 32 casos conforme o esperado. Entrada que não é JSON válido encerra sem decisão e com código 0, sem interromper o agente.

### 5.2 Git hook local (camada 3)

Executado em repositório temporário, com o hook ativado por `core.hooksPath`:

| Caso | Esperado | Obtido |
|---|---|---|
| Commit de `.env` | bloqueado | bloqueado |
| Commit de `mcp.env` | bloqueado | bloqueado |
| Commit de arquivo com cabeçalho de chave privada | bloqueado | bloqueado |
| Commit de arquivo com token no formato do GitHub | bloqueado | bloqueado |
| Commit de `.env.example` | permitido | permitido |
| Commit de arquivo comum | permitido | permitido |

### 5.3 CI (camada 4)

| Verificação | Execução local | Resultado |
|---|---|---|
| `python3 scripts/verificar_links.py` | Repositório completo | 0 links quebrados |
| `python3 scripts/verificar_links.py` | Diretório de teste com 1 link quebrado | Link apontado; código de saída 1 |
| Varredura de segredos | Arquivos versionados | Nenhuma ocorrência |
| Sintaxe do workflow | Leitura do YAML | Jobs `documentacao`, `segredos` e `backend` reconhecidos |

A execução no GitHub Actions é confirmada no primeiro PR após a criação do workflow.

---

## 6. Limitações conhecidas

- **Heurística por expressão regular:** o hook reconhece os padrões da seção 4, mas não interpreta o shell. Comandos ofuscados podem escapar; por isso as camadas 3 e 4 continuam necessárias.
- **Falso positivo:** um texto que contenha um padrão bloqueado, como uma mensagem de commit que cite `.env`, também é bloqueado. Nesses casos, a ação é feita pelo responsável, fora do agente.
- **Carga do hook:** o Claude Code lê a configuração de hooks no início da sessão; alterações em `.claude/settings.json` valem a partir da sessão seguinte.
- **Git hook ignorável:** `git commit --no-verify` contorna a camada 3. A barreira final é o CI com a branch protegida.
- **Escopo da ferramenta:** as camadas 1 e 2 valem apenas para o Claude Code. Outra ferramenta de agente exige configuração própria e atualização deste documento.

---

## 7. Adoção futura de MCP

Caso um servidor MCP seja adotado (por exemplo, acesso ao PostgreSQL de desenvolvimento):

1. Registrar a decisão em ADR, por se tratar de dependência estrutural (`CLAUDE.md`, seção 4).
2. Declarar o servidor em `.mcp.json` com variáveis `${VAR}`, sem valor de segredo.
3. Manter as credenciais em `mcp.env`, já ignorado pelo Git e bloqueado pelo hook.
4. Conceder privilégio mínimo: usuário de banco somente leitura e apenas no ambiente de desenvolvimento.
5. Atualizar as seções 1, 2 e 4 e repetir os testes da seção 5.

---

## 8. Skills do fluxo SDD

| Skill | Etapa | Uso |
|---|---|---|
| `gerar-mapa-specs` | Mapa de Specs | Criar ou atualizar `docs/08-specs/MAPA-DE-SPECS.md` a partir da baseline. |
| `gerar-spec` | Spec | Redigir uma spec a partir de uma linha aprovada do mapa. |
| `implementar-spec` | Plano, tarefas, implementação e verificação | Implementar uma spec aprovada, de preferência em contexto novo do agente. |

As skills ficam em `.claude/skills/<nome>/SKILL.md` e são carregadas pelo Claude Code quando a tarefa corresponde à descrição de cada uma.
