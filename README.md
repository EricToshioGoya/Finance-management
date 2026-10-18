# FinNova — Finance-management

Plataforma web e mobile que une **controle financeiro pessoal** e **simulação de investimentos**: mostra quanto sobra no orçamento e simula quanto esse valor pode render, com taxas oficiais (Selic, CDI, IPCA) e experiência adaptada ao perfil do investidor, seja iniciante ou avançado.

- **Categoria do tema:** sistema de apoio à decisão (principal) e de acompanhamento de progresso (secundária).
- **Status:** documentação nas Fases 1 a 3; implementação ainda não iniciada.

## Contexto acadêmico

Projeto da disciplina **Modelagem e Desenvolvimento de Software** (Mackenzie, semestre 2026-2). É o meu primeiro projeto de software desenvolvido com assistência de IA. O objetivo é aprimorar habilidades em arquitetura de software e levantamento de requisitos, maximizando eficiência e velocidade e evitando retrabalho. O software ajuda o usuário a gerenciar as finanças e a simular investimentos e financiamentos.

## Equipe e papéis

| Integrante | GitHub | Papéis |
|---|---|---|
| Eric Toshio Goya | [@EricToshioGoya](https://github.com/EricToshioGoya) | Repositório e configurações; documentação; backlog e Kanban |

## Como executar

Ainda não há código executável. A partir da Fase 4, esta seção trará os comandos de instalação, execução e testes. Pré-requisitos previstos pela stack:

- Python 3.12+ (backend FastAPI)
- Node.js (clientes React e React Native/Expo)
- Docker e PostgreSQL

## Documentação

| Documento | Conteúdo |
|---|---|
| [Visão](docs/01-visao/visao.md) | Problema, contexto, escopo, stack e roadmap |
| [Benchmark](docs/01-visao/benchmark.md) | Comparação com Mobills, Organizze, Kinvo e Gorila |
| [Personas](docs/02-personas/personas.md) | Público-alvo: iniciante, avançado e administrador |
| [Requisitos](docs/03-requisitos/requisitos.md) | RF, RNF e RB em EARS, modelo de dados e glossário |
| [Casos de uso](docs/04-casos-de-uso/) | Diagramas, tabelas e fluxo principal detalhado |
| [Modelo de domínio](docs/05-modelo-de-dominio/modelo-de-dominio.md) | Classes conceituais e rastreabilidade |
| [Backlog](docs/06-backlog/issues.md) | Issues do MVP (Must have) |
| [Arquitetura](docs/07-arquitetura/arquitetura.md) | Drivers, containers, camadas e ADRs |
| [Specs](docs/08-specs/) | Especificações SDD com cláusulas EARS |
| [Segurança e SSDLC](docs/09-seguranca/seguranca-ssdlc.md) | Ameaças, controles e práticas por etapa |
| [Estratégia de testes](docs/10-qualidade/estrategia-de-testes.md) | Níveis de teste, rastreabilidade e gates de qualidade |
| [Combinados](docs/combinados.md) | Regras de trabalho e revisão |
| [Constituição (CLAUDE.md)](CLAUDE.md) | Workflow obrigatório e regras não negociáveis |

## Estrutura do repositório

```
.
├── CLAUDE.md     # constituição do projeto (SDD)
├── .specify/     # planos e tarefas derivados das specs
├── docs/         # documentação viva
├── src/          # código-fonte (Fase 4)
└── tests/        # testes automatizados (Fase 4)
```

## Como contribuir

1. Abrir ou escolher uma issue com critério de aceite.
2. Criar a branch `feature/<id-da-issue>-descricao-curta`.
3. Seguir o fluxo spec → plano → tarefas → implementação → testes descrito em `CLAUDE.md`.
4. Abrir um PR com `Closes #N`, a spec atualizada e o uso de agente de IA declarado.
