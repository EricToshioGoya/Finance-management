# Implementação — SPEC-036: simular compra financiada e amortização

## Recorte técnico sujeito a OPEN-12/22

Foi implementado o sistema de amortização **Price** como opção *provisória de simulação* para a RF-45. O usuário fornece valor do bem, entrada, 1–600 parcelas e taxa efetiva anual hipotética de 0 a 100% a.a. (sem sugestão de mercado nem provedor de taxa). A conversão anual→mensal reutiliza `converter_taxa` da SPEC-002, por equivalência composta, nunca por divisão linear de 12.

A prestação Price antes de arredondar é `P × i × (1+i)^n / ((1+i)^n - 1)`, sendo `P = bem - entrada` e `i` a taxa mensal decimal equivalente. Para taxa zero, cada parcela é `P / n`. Para entrada igual ao bem, o saldo financiado e as parcelas são zero. A última parcela usa o saldo residual exato para quitá-lo. Juros, principal, pagamentos, saldo e total são calculados com `Decimal` e expostos em centavos; os centavos da tabela são exibição, não realimentam o cálculo. Em razão do arredondamento por linha, a soma visual das linhas pode diferir em centavos do total interno.

**Não são considerados IOF, seguros, encargos, CET, taxas bancárias, atualização monetária ou antecipação de parcelas.** Portanto o cálculo *não* estima o custo efetivo total ou a oferta de nenhum banco. A taxa é explicitamente informada e nunca presumida de mercado. A decisão formal de usar Price, incluir encargos e permitir outros sistemas permanece em OPEN-12/22 e não deve ser dada como aprovada por esta entrega.

## Contratos e isolamento

O motor puro está em `backend/app/domain/financing.py`, com testes em `backend/tests/unit/test_spec036_amortization_engine.py`.

`POST /api/v1/auth/financial/financing/simulate` requer sessão autenticada, titular com e-mail confirmado, corpo JSON de quatro parâmetros e responde com `schedule` parcela por parcela, `total_interest`, `total_installments`, `total_paid` **incluindo a entrada**, `installment_amount`, `financed_amount`, `monthly_rate`, `amortization_system=price`, `includes_fees=false` e `simulated_only=true`. Entradas inválidas retornam 422. Não existe tabela ou migration nesta SPEC: simular não gera despesa, passivo, amortização real nem registra uma compra (INV-001). A SPEC-038 será responsável pela confirmação explícita, sujeita às decisões em aberto.

`frontend/src/Financing.tsx` fornece formulário responsivo PT/EN e cronograma completo acessível por teclado, com visualização inicial das primeiras 24 linhas e opção de mostrar todas. A explicação de juros utiliza o tooltip da central da SPEC-035.

`backend/tests/test_spec036_financing.py` cobre autenticação, confirmação de e-mail, saída de referência, entradas inválidas, repetibilidade sem efeitos e integridade do patrimônio real. A aprovação técnica exige os workflows do PR e a decisão formal do grupo continua em aberto.
