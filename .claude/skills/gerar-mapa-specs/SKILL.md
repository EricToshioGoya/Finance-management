---
name: gerar-mapa-specs
description: Cria ou atualiza o Mapa de Specs do FinNova (docs/08-specs/MAPA-DE-SPECS.md) a partir da baseline. Usar quando uma spec nova for proposta, quando o status de uma spec mudar ou quando uma questão em aberto for resolvida.
---

# Gerar ou atualizar o Mapa de Specs

Etapa 1 do fluxo SDD (`CLAUDE.md`, seção 2). O mapa decide o que será especificado, em que ordem e com qual base. O agente propõe; a aprovação é sempre humana.

## Entradas obrigatórias

1. `docs/03-requisitos/requisitos.md`: tabela 1.1 (prioridade MoSCoW), RF, RNF, RB e glossário.
2. `docs/04-casos-de-uso/`: casos de uso e questões `OPEN-UCxx`.
3. `docs/modelo-dominio.md`: classes, cláusulas `DOM-xx` e dúvidas `RB-27` em diante.
4. `docs/07-arquitetura/arquitetura.md`: drivers `DA-xx`, decisões técnicas e seção 11 (decisões pendentes); ADRs em `docs/07-arquitetura/adrs/`.
5. `docs/08-specs/MAPA-DE-SPECS.md` atual e as specs existentes.

## Passos

1. Delimitar o recorte: por padrão, os RF Must have ainda sem spec implementada.
2. Para cada spec, preencher: base principal (RF, RB, RNF, UC, DOM), drivers e ADRs, dependências, status e `OPEN` relacionados.
3. Preservar os números já atribuídos. Spec nova recebe o próximo número livre; números reservados (seção 3 do mapa) não são reutilizados.
4. Ordenar por dependência: fundação e domínio puro antes de API e persistência.
5. Atualizar a seção 4 (questões em aberto consolidadas) com toda questão nova encontrada nas entradas, apontando a origem.
6. Registrar na seção 5 a linha de aprovação **somente** depois que o responsável aprovar no chat ou na issue, com data e nome.

## Regras

- Não inventar requisito, regra ou identificador que não exista na baseline (`CLAUDE.md`, seção 4).
- Termos conforme o glossário (`CLAUDE.md` C-14).
- O mapa é alterado no mesmo PR que cria a spec ou muda o seu status.
- Ao final, rodar `python3 scripts/verificar_links.py`.
