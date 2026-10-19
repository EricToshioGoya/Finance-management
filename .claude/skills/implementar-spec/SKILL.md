---
name: implementar-spec
description: Implementa uma spec aprovada do FinNova seguindo plano, tarefas, código e testes rastreados por ID de cláusula, e verifica o resultado. Usar somente para specs com status Aprovada, de preferência em um contexto novo do agente.
---

# Implementar uma spec aprovada

Etapas 3 a 7 do fluxo SDD (`CLAUDE.md`, seção 2). Recomenda-se iniciar uma sessão nova do agente, carregando apenas esta skill, o `CLAUDE.md` e a spec, para que o contexto de redação da spec não influencie a implementação.

## Pré-condições

- A spec tem status **Aprovada** em `docs/08-specs/` e no mapa.
- Todas as specs de que ela depende (coluna "Depende de" do mapa) estão implementadas.
- Existe uma issue com critério de aceite; a branch segue `feature/<id-da-issue>-descricao-curta`.
- Nenhum `OPEN-xx` da spec bloqueia uma cláusula a implementar. Se bloquear, parar e perguntar ao autor.

## Passos

1. **Plano:** criar `.specify/plans/PLAN-NNN.md` com camadas afetadas (ADR-001), arquivos, dependências novas e riscos.
2. **Tarefas:** criar `.specify/tasks/TASKS-NNN.md` com passos pequenos e verificáveis, cada um ligado às cláusulas que atende.
3. **Testes primeiro:** um teste por cláusula `SHALL`, com o ID no nome ou na docstring (ex.: `test_spec002_r02_...`), usando valores de referência independentes da implementação.
4. **Implementação:** código em `src/`, testes em `tests/`. Regra de negócio apenas na camada de domínio, sem FastAPI, SQLAlchemy nem I/O (`CLAUDE.md` C-05).
5. **Verificação:** rodar lint, testes e cobertura (comandos em `CLAUDE.md`, seção 5) e montar a tabela `Cláusula | Teste | Resultado`.
6. **Revisão:** responder "o código implementa a spec?" cláusula por cláusula, inclusive verificando que nenhuma regra foi inventada.
7. **PR:** rascunho com `Closes #N`, spec e mapa atualizados no mesmo PR (C-01) e declaração do uso do agente: o que foi gerado e o que foi revisado (C-13).

## Proibições

- Alterar requisito, spec aprovada ou ADR sem pedido explícito do autor.
- Usar `float` em cálculo financeiro ou converter taxa por divisão simples (C-03, C-04).
- Instalar dependência estrutural nova sem ADR.
- Enfraquecer, pular ou apagar teste para deixar o CI verde.
