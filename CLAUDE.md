# CLAUDE.md — Constituição do Projeto FinNova

- **Versão:** v0 (rascunho)
- **Última atualização:** 2026-10-31
- **Escopo:** regras que valem para qualquer pessoa ou agente de codificação (Claude Code, Cursor) que altere este repositório.

---

## 1. Contexto

FinNova é uma plataforma web e mobile que conecta o controle financeiro pessoal à simulação de investimentos (ver `docs/01-visao/visao.md`).

Fontes de verdade, em ordem de precedência:

1. Requisitos: `docs/03-requisitos/requisitos.md` (RF, RNF, RB e glossário).
2. Specs: `docs/08-specs/SPEC-*.md` (cláusulas EARS com ID).
3. Decisões de arquitetura: `docs/07-arquitetura/arquitetura.md` e `docs/07-arquitetura/adrs/`.
4. Modelo de domínio: `docs/05-modelo-de-dominio/modelo-de-dominio.md` (versão vigente; `docs/modelo-dominio.md` e `docs/uml/` são histórico).
5. Combinados de trabalho: `docs/combinados.md`.

Stack definida: Python 3.12+ com FastAPI, Pydantic e SQLAlchemy/Alembic; PostgreSQL; React + TypeScript + Vite (web); React Native com Expo (mobile, versão mínima em `mobile/`). Detalhes em `docs/07-arquitetura/arquitetura.md`, seção 5.

---

## 2. Workflow obrigatório (Spec-Driven Development)

1. **Issue** com critério de aceite e responsável.
2. **Spec** em `docs/08-specs/`, com cláusulas EARS identificadas (`SPEC-NNN-Rxx`).
3. **Plano** em `.specify/plans/PLAN-NNN.md`: como a spec será implementada (camadas, arquivos, riscos).
4. **Tasks** em `.specify/tasks/TASKS-NNN.md`: lista ordenada de passos pequenos e verificáveis.
5. **Implementação** em `src/` e **testes** em `tests/`.
6. **Verificação:** testes passando, lint limpo e revisão com a pergunta "o código implementa a spec?".
7. **Pull Request** vinculado à issue (`Closes #N`), com a spec atualizada no mesmo PR.

Convenções:

- **Branch:** `feature/<id-da-issue>-descricao-curta` (ex.: `feature/12-cadastro-usuario`). Correções de documentação: `docs/<id>-descricao`.
- **Commit:** formato curto `tipo: descrição` (tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`), com referência à issue (`#N`) no corpo ou no título.

---

## 3. Regras não negociáveis

| ID | Regra | Origem |
|---|---|---|
| C-01 | Spec e código mudam no mesmo PR. Código sem spec correspondente não é aceito. | Disciplina (regra dura) |
| C-02 | Toda cláusula `SHALL` de uma spec tem ao menos um teste automatizado que cita o ID da cláusula. | Disciplina; `docs/10-qualidade/estrategia-de-testes.md` |
| C-03 | Valores monetários e taxas usam `Decimal`; `float` é proibido em cálculo financeiro. | SPEC-002 INV-002 |
| C-04 | Conversão de taxa entre períodos é sempre por equivalência composta; nunca `i_anual / 12`. | RB-10, SPEC-002 INV-001 |
| C-05 | A camada de domínio não importa FastAPI, SQLAlchemy nem faz I/O. | ADR-002 |
| C-06 | Senhas são armazenadas com hash e salt; nunca em texto plano, nem em logs. | RNF-01, SPEC-001 INV-001 |
| C-07 | Toda rota `/api/v1/admin/*` valida o papel de administrador no backend. | RNF-21 |
| C-08 | Simulações leem indicadores apenas do cache local; na falha da fonte, usam o último valor com aviso, nunca zero. | RF-23, ADR-003 |
| C-09 | Documentos completos (PDF) da CVM nunca são armazenados; apenas metadados e link oficial. | RB-12, ADR-004 |
| C-10 | Nenhum segredo (senha, token, chave de API) é versionado; usar variáveis de ambiente. | `docs/09-seguranca/seguranca-ssdlc.md` |
| C-11 | Todos os endpoints ficam sob o prefixo `/api/v1`. | RNF-17 |
| C-12 | A branch `main` só recebe alterações via PR; o merge exige testes e lint verdes na CI (`.github/workflows/ci.yml`). | RNF-16, `docs/combinados.md` |
| C-13 | O uso de agente de IA é declarado na descrição do PR (o que foi gerado e o que foi revisado). | Contrato do curso (integridade) |
| C-14 | Código, specs e documentação usam apenas os termos do glossário (`requisitos.md`, seção 8) e os nomes de classe do modelo de domínio; um termo novo entra primeiro no glossário. | `docs/modelo-dominio.md` |
| C-15 | Data e hora são gravadas em UTC; o mês de competência e as datas exibidas usam America/Sao_Paulo; o domínio recebe o relógio por injeção. | RNF-25, ADR-006 |
| C-16 | Toda criação de lançamento aceita chave de idempotência; um reenvio com a mesma chave não cria registro duplicado. | RNF-24, `docs/07-arquitetura/arquitetura.md` DA-10 |
| C-17 | Testes automatizados nunca chamam serviço externo real; usam dublês. | `docs/10-qualidade/estrategia-de-testes.md`, seção 5 |

---

## 4. Instruções para o agente de codificação

- Antes de codar, ler a issue, a spec e as cláusulas EARS envolvidas.
- Se a spec for ambígua ou incompleta, **não inventar regra**: registrar em "Questões em aberto" da spec e perguntar ao autor.
- Não alterar requisitos, specs ou ADRs sem pedido explícito do autor.
- Nomes de domínio seguem o modelo de domínio, em português e sem acento (`Usuario`, `Simulacao`, `PatrimonioItem`), e o vocabulário segue o glossário (regra C-14).
- Documentação em português do Brasil.
- Dependências estruturais novas (framework, banco, fila, provedor externo) exigem ADR.

---

## 5. Comandos

- Preparar ambiente local: `scripts/setup-local.sh` (segredos locais, certificado HTTPS, dependências, PostgreSQL e migrations).
- Executar: `scripts/start-local.sh` (API e web em `https://localhost:8443`).
- Backend (em `backend/`): `uv run --frozen ruff check .`, `uv run --frozen ruff format --check .`, `uv run --frozen alembic upgrade head` e `uv run --frozen pytest -q --cov=app --cov-fail-under=90`.
- Frontend (em `frontend/`): `npm run lint`, `npm run build` e `npm test` (Playwright; exige a API HTTPS ativa).
- Mobile (em `mobile/`): `npm run typecheck`, `npm test` e `npx expo start`.
- Documentação: `python scripts/verificar-documentacao.py` após qualquer mudança em `docs/`.
- Testes de backend nomeiam a cláusula: `test_SPEC_NNN_Rxx_...` (C-02).

---

## 6. Estrutura do repositório

```
.
├── CLAUDE.md            # esta constituição
├── README.md            # visão geral e orientação para quem chega
├── .specify/            # plans/ e tasks/ derivados das specs
├── .github/workflows/   # CI: backend (PostgreSQL), frontend e verificador documental
├── backend/             # app/domain (puro), app/application, app/infrastructure, app/presentation, migrations, tests
├── frontend/            # React + TypeScript + Vite; testes Playwright em frontend/tests
├── mobile/              # React Native + Expo (login, resumo, despesa, avisos)
├── scripts/             # setup/execução local, smoke e verificador de documentação
└── docs/                # documentação viva (visão → specs → qualidade)
```
