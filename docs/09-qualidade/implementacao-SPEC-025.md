# Implementação — SPEC-025: volatilidade e Sharpe histórico

**Data:** 2026-10-29  
**Política autorizada:** retornos diários simples, desvio amostral, anualização por √252 e Selic diária por equivalência composta.

## Entrega

- Métricas determinísticas usam somente histórico local fresco de cotações e Selic válida.
- São exigidos três fechamentos e intervalos de até três dias; série incompatível não gera resultado.
- Volatilidade zero devolve estado explícito e Sharpe nulo.
- O endpoint de métricas exige sessão e acesso avançado: padrão para perfil arrojado, opt-in para conservador/moderado.
- A simulação variável aceita ticker opcional e persiste as métricas quando habilitadas.
- Toda resposta inclui período, versão da regra e ressalva de que dados históricos não garantem futuro.

## Verificações

Os testes cobrem opt-in, perfil arrojado, integração com simulação, fonte local, ticker inválido e volatilidade zero. A CI PostgreSQL fornece a evidência de integração.
