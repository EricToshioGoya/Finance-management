# Implementação — SPEC-026: projeção em moeda estrangeira

**Data:** 2026-10-30  
**Política autorizada:** BRL, USD e EUR; USD/EUR usam PTAX de venda do BCB em referência local datada. BRL usa paridade 1. A variação cambial anual é uma hipótese separada, informada pelo usuário.

## Entrega

- A simulação persiste a projeção na moeda original e em BRL, sem comprar moeda ou movimentar patrimônio.
- USD e EUR exigem uma referência PTAX local disponível e com menos de 24 horas; ausência ou vencimento retornam erro, sem taxa inventada.
- BRL dispensa PTAX e mantém taxa 1.
- Retorno anual do ativo e variação anual esperada do câmbio são calculados e exibidos separadamente.
- O resultado identifica fonte, data de referência, regra e aviso de risco cambial.

## Verificações

Os testes cobrem USD com PTAX de 5 BRL/unidade, BRL com paridade, recusa de moeda inválida/ausência de PTAX e isolamento das simulações por titular. A CI PostgreSQL cobre persistência e migration.
