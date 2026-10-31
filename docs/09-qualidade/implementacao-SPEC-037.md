# SPEC-037 — Comparar financiamento e compra após investir

## Contrato técnico provisório — OPEN-20/22

A comparação reaproveita **o motor Price da SPEC-036** e a projeção pura do motor de juros compostos da **SPEC-002**, sem recalcular parcelas na interface e sem gravar passivo ou investimento.

Hipóteses **expressas** na entrada e na saída:

- O preço nominal do bem permanece fixo no horizonte (sem valorização, inflação ou descontos).
- Cenário A: entrada aplicada na compra no mês 0; aquisição imediata; parcelas Price pagas por `installments` meses, usando taxa efetiva anual de financiamento convertida para mensal por equivalência composta.
- Cenário B: a **mesma entrada** fica investida no mês 0; a **parcela Price arredondada** é investida ao fim de cada mês durante `horizon_months`. Taxa efetiva anual de investimento informada pelo usuário é hipotética, não há retorno garantido. O saldo projetado é calculado uma vez com o motor da SPEC-002, sem juros proporcionais.
- Primeiro mês em que o saldo projetado alcança o preço fixo é a primeira posse possível por compra à vista. Caso não alcance o preço no horizonte, posse e capital aplicado até o alvo são `null` e o veredito `not_comparable`; não se anuncia uma compra garantida.
- Compra financiada tem posse no mês 0; a compra à vista pode acontecer meses depois. Não são alternativas equivalentes em utilidade ou risco.
- **Indicador limitado de custo nominal da aquisição:** quando ambas as compras são viáveis, comparar `total_pago_financiado_incluindo_entrada - preço_à_vista_fixo`. O sinal gera `invest_then_buy`, `finance_now` ou `tie` **apenas pelo preço nominal**. Aportes ao investimento até atingir o alvo e ganhos hipotéticos são mostrados separadamente; não se confunde depósito/investimento com gasto de aquisição. A diferença de custos não constitui recomendação financeira global.

Fora do recorte: CET/IOF, seguros, encargos, tributos do investimento, taxas de administração, valorização/depreciação, liquidez, inflação, risco ou rendimento variável, custo de aluguel/uso enquanto aguarda, valor presente e custo de oportunidade da posse. **OPEN-20 e OPEN-22 permanecem pendentes** para política formal de comparação financeira e encargos; as hipóteses técnicas não presumem aprovação do grupo.

## API, integração, validações

`POST /api/v1/auth/financial/financing/compare` requer token de titular válido e e-mail confirmado, Pydantic estrito e seis parâmetros: `asset_value`, `down_payment`, `installments`, `financing_annual_rate`, `investment_annual_rate` e `horizon_months`. Prazos de 1 a 600 meses; taxa nominal anual informada entre 0–100% no contrato; entrada não ultrapassa o preço. Resultado inclui parcela/aumento da poupança hipotética, cronograma-resumo financeiro, meses até cada posse, saldo em horizonte, total aportado e indicador limitado de custo nominal. Resposta carrega hipóteses em `assumptions` e `simulated_only=true`. Não existe migração nem persistência pessoal.

A lógica reside em `backend/app/domain/financing_comparison.py` (pura, sem I/O, ORM ou FastAPI). A interface PT/EN `frontend/src/FinancingComparison.tsx` é responsiva, traz campos validados, exibe os cenários lado a lado, explica o horizonte e alerta explicitamente para ausência de posse no período escolhido.

Testes em `backend/tests/unit/test_spec037_financing_comparison_engine.py` e `backend/tests/test_spec037_financing_comparison_api.py` exercitam taxa zero e custo igual, horizonte insuficiente, valor/juros/entrada, resposta 422, e-mail não confirmado, isolamento e ausência de efeitos no patrimônio. O CI GitHub Actions é exigido; mobile/Expo, P95 operacional e revisão regulatória permanecem pendentes.
