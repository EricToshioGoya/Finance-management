# FinNova — Finance-management

Plataforma web e mobile que une **controle financeiro pessoal** e **simulação de investimentos**: mostra quanto sobra no orçamento e simula quanto esse valor pode render, com taxas oficiais (Selic, CDI, IPCA) e experiência adaptada ao perfil do investidor, seja iniciante ou avançado.

- **Categoria do tema:** sistema de apoio à decisão (principal) e de acompanhamento de progresso (secundária).
- **Status (2026-10-31):** backend FastAPI e cliente web React implementados para as 62 Specs, com CI no GitHub Actions; aplicativo mobile Expo mínimo (login, resumo do mês, lançamento de despesa e avisos); operação em produção ainda pendente. Situação detalhada em [mapa de Specs](docs/08-specs/mapa-specs.md).

## Contexto acadêmico

Projeto da disciplina **Modelagem e Desenvolvimento de Software** (Mackenzie, semestre 2026-2). É o meu primeiro projeto de software desenvolvido com assistência de IA. O objetivo é aprimorar habilidades em arquitetura de software e levantamento de requisitos, maximizando eficiência e velocidade e evitando retrabalho. O software ajuda o usuário a gerenciar as finanças e a simular investimentos e financiamentos.

## Equipe e papéis

| Integrante | GitHub | Papéis |
|---|---|---|
| Eric Toshio Goya | [@EricToshioGoya](https://github.com/EricToshioGoya) | Repositório e configurações; documentação; backlog e Kanban |

## Como executar

Pré-requisitos: Python 3.12+ com [uv](https://docs.astral.sh/uv/), Node.js 24, OpenSSL e Docker (PostgreSQL 16).

```bash
scripts/setup-local.sh   # gera segredos locais e certificado HTTPS, instala dependências, sobe o banco e aplica migrations
scripts/start-local.sh   # inicia a API e o cliente web em https://localhost:8443
```

Testes e lint:

```bash
cd backend && uv run --frozen ruff check . && uv run --frozen pytest -q --cov=app --cov-fail-under=90
cd frontend && npm run lint && npm run build && npm test   # npm test exige a API HTTPS ativa
python scripts/verificar-documentacao.py
cd mobile && npm ci && npm run typecheck && npm test && npx expo start   # app móvel (ajuste extra.apiUrl em app.json)
```

A documentação interativa da API fica em `https://localhost:8443/api/v1/docs`. Variáveis de ambiente estão em `backend/.env.example` (nunca versionar `.env`, regra C-10).

## Documentação

| Documento | Conteúdo |
|---|---|
| [Visão](docs/01-visao/visao.md) | Problema, contexto, escopo e roadmap |
| [Benchmark](docs/01-visao/benchmark.md) | Comparação com Mobills, Organizze, Kinvo e Gorila |
| [Personas](docs/02-personas/personas.md) | Público-alvo: iniciante, avançado e administrador |
| [Requisitos](docs/03-requisitos/requisitos.md) | RF, RNF e RB em EARS, modelo de dados e glossário |
| [Casos de uso](docs/04-casos-de-uso/) | Diagramas, tabelas e fluxo principal detalhado |
| [Modelo de domínio](docs/05-modelo-de-dominio/modelo-de-dominio.md) | Classes, responsabilidades, multiplicidades e entidades implementadas (fonte vigente); a versão anterior está em [docs/modelo-dominio.md](docs/modelo-dominio.md) como histórico |
| [Backlog](docs/06-backlog/issues.md) | Issues do MVP (Must have) |
| [Arquitetura](docs/07-arquitetura/arquitetura.md) | Drivers, decisões técnicas, stack, camadas, atributos de qualidade e ADRs |
| [Specs](docs/08-specs/) | Especificações SDD com cláusulas EARS, mapa, cobertura e questões abertas |
| [Qualidade e evidências](docs/09-qualidade/) | Plano de qualidade, cobertura funcional e registros de implementação por Spec |
| [Segurança e SSDLC](docs/09-seguranca/seguranca-ssdlc.md) | Ameaças, controles e práticas por etapa |
| [Modelo de qualidade](docs/10-qualidade/modelo-de-qualidade.md) | Características ISO/IEC 9126/25010, lacunas, métricas e custo do defeito |
| [Estratégia de testes](docs/10-qualidade/estrategia-de-testes.md) | Pirâmide de testes, suítes de risco, dublês e gates de qualidade |
| [Combinados](docs/combinados.md) | Regras de trabalho e revisão |
| [Constituição (CLAUDE.md)](CLAUDE.md) | Workflow obrigatório e regras não negociáveis |

## Estrutura do repositório

```
.
├── CLAUDE.md     # constituição do projeto (SDD)
├── .specify/     # planos e tarefas derivados das specs
├── .github/      # CI (testes, lint e verificação documental)
├── backend/      # API FastAPI: app/domain (regras puras), app/application, app/infrastructure, migrations, tests
├── frontend/     # cliente web React + TypeScript + Vite e testes Playwright
├── mobile/       # aplicativo React Native com Expo (mesma API /api/v1)
├── scripts/      # preparação local, smoke tests e verificador de documentação
└── docs/         # documentação viva
```

## Como contribuir

1. Abrir ou escolher uma issue com critério de aceite.
2. Criar a branch `feature/<id-da-issue>-descricao-curta`.
3. Seguir o fluxo spec → plano → tarefas → implementação → testes descrito em `CLAUDE.md`.
4. Abrir um PR com `Closes #N`, a spec atualizada e o uso de agente de IA declarado.
