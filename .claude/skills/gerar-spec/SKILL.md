---
name: gerar-spec
description: Redige uma spec SDD do FinNova (docs/08-specs/SPEC-NNN-*.md) a partir de uma linha aprovada do Mapa de Specs, com cláusulas EARS identificadas, critérios Dado/Quando/Então e questões em aberto. Usar antes de qualquer implementação de funcionalidade nova.
---

# Gerar uma spec

Etapa 2 do fluxo SDD (`CLAUDE.md`, seção 2). A spec é o contrato que o agente de implementação vai seguir.

## Pré-condição

A spec consta de `docs/08-specs/MAPA-DE-SPECS.md`. Se não constar, parar e usar a skill `gerar-mapa-specs`.

## Entradas

- A linha da spec no mapa (base principal, drivers, ADRs, dependências, `OPEN`).
- Os requisitos, casos de uso, cláusulas `DOM-xx` e ADRs citados nessa linha.
- Modelo de estrutura: `docs/08-specs/SPEC-001-cadastro-e-autenticacao.md`.

## Estrutura obrigatória

1. **Identificação:** ID, nome, objetivo e valor entregue; cabeçalho com status **Rascunho**, data e autor.
2. **Rastreabilidade:** RF, RB, RNF, UC, entidades do domínio, drivers e ADRs.
3. **Escopo:** incluído e fora do escopo.
4. **Comportamento e fluxos:** pré-condições, fluxo principal, alternativos e exceções.
5. **Requisitos da spec (EARS):** tabela `ID | Tipo EARS | Cláusula | Origem | Teste previsto`, com IDs `SPEC-NNN-Rxx`. Uma obrigação por cláusula.
6. **Invariantes:** `INV-xx`.
7. **Critérios de aceitação:** cenários Dado/Quando/Então com valores concretos, cada um citando as cláusulas que verifica.
8. **Questões em aberto:** `OPEN-xx` para todo ponto que a baseline não decide.

## Regras

- Não inventar regra: o que a baseline não define vira `OPEN-xx` e pergunta ao autor.
- Todo RNF da base principal aparece em ao menos um critério ou cláusula.
- Valores monetários e taxas em `Decimal` (`CLAUDE.md` C-03); conversão de taxa por equivalência composta (C-04).
- Termos e nomes de classe conforme o glossário e o modelo de domínio (C-14).
- A spec só passa a **Aprovada** após revisão humana; atualizar o status também no mapa.
