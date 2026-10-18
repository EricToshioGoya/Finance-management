# Combinados de Trabalho — FinNova

- **Versão:** 1.0
- **Última atualização:** 2026-10-18
- **Formação:** projeto individual — Eric Toshio Goya ([@EricToshioGoya](https://github.com/EricToshioGoya))

Regras simples e explícitas para evitar retrabalho e manter o histórico rastreável.

---

## 1. Comunicação

| Item | Combinado |
|---|---|
| Canal oficial | GitHub: issues e pull requests. Decisões e discussões ficam registradas no repositório. |
| Tempo máximo de resposta | Não se aplica (projeto individual). |
| Horário de trabalho | Não se aplica (projeto individual). |

## 2. Qualidade

- Toda alteração entra na `main` por pull request, nunca por commit direto.
- Como não há colega de equipe para revisar, cada PR passa por **auto-revisão com checklist** antes do merge:
  - [ ] O código implementa a spec? Cada cláusula `SHALL` alterada tem teste?
  - [ ] A spec e a documentação em `/docs` foram atualizadas no mesmo PR?
  - [ ] O PR está vinculado à issue (`Closes #N`) e declara o uso de agente de IA?
- Comentários do professor em issues e PRs são respondidos na própria thread.

## 3. Integração

- A branch `main` deve permanecer sempre verde: build, lint e testes passando (RNF-16), a partir da criação do pipeline de CI.
- Branches seguem `feature/<id-da-issue>-descricao-curta`; commits seguem `tipo: descrição` (ver `CLAUDE.md`).

## 4. Divisão de trabalho

- Todas as issues são atribuídas ao autor e acompanhadas no Project (Kanban) com as colunas **A fazer**, **Em andamento**, **Em revisão** e **Concluído**.
- Uma issue só é fechada com evidência: PR vinculado ou commit que a referencia.

## 5. Decisões

- Escolhas importantes de arquitetura ou tecnologia viram um ADR curto (1 página) em `docs/07-arquitetura/adrs/`.
- Ambiguidades de requisito são registradas em "Questões em aberto" da spec correspondente antes de qualquer implementação.
