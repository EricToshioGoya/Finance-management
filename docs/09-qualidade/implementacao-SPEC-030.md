# SPEC-030 — Mapa de calor do patrimônio real

## Escopo implementado na branch

A SPEC-030 usa exclusivamente a consolidação real da SPEC-028. O endpoint `GET /api/v1/auth/financial/net-worth/heatmap` exige sessão e e-mail confirmado e retorna `as_of`, `items` (nome, tipo, valor, origem e taxa anual opcional) e `total_absolute`. Não altera o patrimônio e não inclui simulações.

A visualização web é um treemap de uma linha com altura constante; a largura — e portanto a área — de cada item é proporcional a `abs(value)` em relação ao conjunto filtrado. Os filtros são `todos`, `somente ativos` e `somente passivos`; a participação é recalculada no recorte selecionado. Posições com valor zero ficam na tabela e não ocupam área, e o recorte vazio mostra estado explicativo.

Ao passar o mouse ou focar/clicar/tocar em uma célula, o usuário pode acessar nome, valor, tipo e taxa informada. Há tabela textual integral com percentuais para uso com leitor de tela. O controle de taxa ausente **não fabrica rentabilidade**: o item é cinza. Ativos com taxa nula são verdes claros; taxas positivas são verdes mais escuros. Passivos com juros são amarelos a vermelhos conforme a taxa. A escala visual de 0 a 20 pontos percentuais ao ano usa saturação no teto, somente para apresentação; não redefine rentabilidade nem juros nem constitui recomendação financeira. Essa escolha de exibição é provisória e ajustável no refinamento de OPEN-21.

O componente busca posições reais na abertura, ao retornar o foco à janela, periodicamente enquanto a janela estiver visível e após mutações financeiras concluídas pelo cliente. Cálculos hipotéticos não alteram patrimônio; financiamentos reais futuros dependem da SPEC-038. Não existe transação de persistência adicional para o heatmap.

## Testes e revisão

`backend/tests/test_spec030_net_worth_heatmap.py` cobre acesso negado sem e-mail confirmado, isolamento de titulares, ativos 100/300 com taxas 0%/12%, dívida com juros de 20%, valor absoluto total, ausência de taxa, exclusão de cálculos simulados e alteração de item manual.

A validação executável depende dos checks do PR. RNFs de observabilidade operacional, perfil de carga e mobile permanecem sujeitos às condições gerais do projeto; nenhum resultado inexistente deve ser declarado como testado.

**Sem merge automático.** A implementação não afirma resolução formal de todas as OPEN.
