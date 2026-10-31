# UC-08 — Calcular juros compostos

**Ator:** usuário; a aplicação também reutiliza o motor internamente.
**Origem:** RF-22; RB-10, RB-28; RNF-07; SPEC-002; DA-02/ADR-002.
**Objetivo:** calcular montante bruto reproduzível com aporte no fim de cada mês.
**Pré-condições:** entrada possui valor inicial, aporte, taxa com periodicidade e prazo inteiro positivo. Uma chamada interna ao motor não é endpoint público e não exige sessão dentro do domínio.

## Fluxo principal

1. Aplicação recebe parâmetros; um endpoint pessoal verifica autenticação fora do motor.
2. Motor valida valores não negativos, taxa não negativa e prazo positivo (RB-28).
3. Converte percentual para fração decimal, taxa anual para mensal por equivalência e anos para meses.
4. Para cada mês, calcula juros sobre o saldo anterior e adiciona aporte ao fim do período.
5. Retorna resumo e série: total investido = valor inicial + soma dos aportes; juros = montante − total investido.

## Extensões

- 2a. Entrada inválida: produzir erro de validação sem resultado nem persistência.
- 3a. Taxa zero: aceitar; juros são zero e montante é soma do inicial e dos aportes.

**Pós-condição:** resultado bruto, hipóteses e série disponíveis. Nenhum saldo, ativo ou banco é alterado pelo motor. IR e taxas adicionais pertencem à futura SPEC-004. Precisão e arredondamento adotados tecnicamente no ADR-002 para OPEN-03; execução do motor na SPEC-002. Interface e integração pertencem à SPEC-013.
