# SPEC-038 — Confirmação de financiamento real (recorte técnico)

## Comportamento implementado

A **simulação SPEC-036** permanece estritamente sem efeitos financeiros. Para registrar uma dívida real o usuário autenticado e com e-mail verificado deve enviar uma **operação diferente e explícita**, `POST /api/v1/auth/financial/financing/confirm`, com os parâmetros de preço, entrada, parcelas e taxa efetiva anual, o texto exato `CONFIRMAR FINANCIAMENTO REAL` e cabeçalho `Idempotency-Key` (1–128 caracteres). A interface apresenta aviso claro e uma segunda confirmação antes do envio.

Uma única transação do banco registra a `confirmed_financings` com origem rastreável e criptografia do nome. O valor inicial financiado é apresentado uma só vez como **passivo real** pelo agregador de patrimônio (origem `financing`), sem inserir também um passivo manual duplicado. O contrato Price é recalculado no servidor a partir dos valores enviados: simulações nunca são tratadas como prova de contrato. Entrada igual ou acima do preço é recusada.

**Idempotência e autorização:** a chave é única por titular, inclusive sob concorrência. Repetição com a mesma chave e os mesmos parâmetros retorna o mesmo registro; parâmetros divergentes retornam 409. Titulares diferentes não compartilham chaves nem registros. Todos os campos são validados antes da escrita e o commit só ocorre após todas as gravações. Erros de categoria ou conta causam 404 e nenhuma dívida ou despesa é persistida.

## Opção de despesa recorrente

Somente quando habilitada explicitamente, a confirmação também exige **conta financeira do próprio titular, categoria existente e data da primeira parcela**. Na mesma transação é criada uma entrada em `expenses` com `recurring=true`, identificada e vinculada ao financiamento por `expense_id`; o valor é a prestação Price estimada. A funcionalidade atual de despesas representa uma entrada inicial marcada como recorrente, **não gera automaticamente todas as parcelas futuras**. O saldo inicial do passivo **não diminui automaticamente** quando a despesa é lançada, para não presumir quitação ou reconciliação contábil não aprovada.

As tabelas `confirmed_financings` e `expenses` mantêm vínculos auditáveis e criação atômica. A informação `confirmed_at` registra o instante da operação. O endpoint `GET /api/v1/auth/financial/financing/confirmed` lista apenas as operações do titular. A interface PT/EN exibe histórico de dívidas confirmadas.

## Limitações e decisões pendentes

**OPEN-12, OPEN-15, OPEN-21 e OPEN-22 permanecem abertas**: o regime Price, o cronograma de baixa e juros efetivos, reversões, edição contratual e reconciliação não estão formalmente homologados. Portanto este recorte **congela o saldo devedor inicial** até eventual mecanismo de atualização aprovado. A obrigação real pode ter CET/IOF, seguro ou tarifas que não entram na parcela Price estimada. Não se inventam baixa automática, movimentação bancária ou passivo adicional. O vínculo `expense_id` é preservado enquanto a despesa existir; não se deve apagar o registro de origem sem processo de reversão.

Validações técnicas: migration Alembic `029_confirmed_financings`, testes `backend/tests/test_spec038_real_financing.py`, suíte CI incluindo PostgreSQL, lint e navegador. Auditoria operacional, recuperação de backup, cliente Expo, performance P95 e decisão humana final não são presumidas concluídas.
