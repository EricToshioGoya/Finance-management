# Implementação — SPEC-034: score de saúde financeira

**Data:** 2026-10-29  
**Política autorizada:** score educativo 0–100; pesos persistidos gasto/renda 35%, reserva 25%, dívida 25% e metas 15%.

## Entrega

- `GET /api/v1/auth/financial/health-score` calcula e persiste uma observação por competência mensal.
- Reserva usa apenas contas correntes, poupança e dinheiro; projeções não participam.
- A resposta traz faixa, dois fatores mais fracos, sugestão genérica, histórico e versão da regra.
- Renda zero retorna erro explícito, sem nota arbitrária. Os pesos estão em `health_score_rules`, não fixos no código.

## Verificações

`test_spec034_health_score.py` cobre cálculo repetível, histórico mensal, caráter educativo, renda zero e sessão obrigatória. A CI executa PostgreSQL, cobertura e cliente web.

## Complemento — interface web e isolamento (PR da branch feature/34-health-score-ui)

A fórmula e os pesos persistidos de 35/25/25/15 já existiam na implementação de 2026-10-29. Este complemento **não redefine pesos, faixas ou cálculo** e não cria nova tabela ou migração.

- Painel autenticado `frontend/src/HealthScore.tsx`: nota em destaque no gauge 0–100, classificação traduzida em PT/EN, mês opcional, dois fatores mais fracos com sugestões genéricas traduzidas, evolução mensal em gráfico de linha com tabela textual acessível e identificação da versão da regra
- Atualização ao retornar ao painel e após eventos de mutação financeira do frontend, bem como botão para recálculo explícito; a consulta existente calcula e atualiza a observação mensal da competência escolhida
- O endpoint financeiro agora aplica a mesma exigência de e-mail confirmado dos demais dados sensíveis, retornando 403 aos titulares não verificados
- Sem renda ou regra disponível, a interface comunica a impossibilidade e não inventa nota; permanece o aviso de caráter exclusivamente educativo

Testes adicionais em `backend/tests/test_spec034_health_score_ui_contract.py` verificam titularidade, leitura mensal idempotente e 403 por e-mail não confirmado. O teste antigo de renda zero foi atualizado para confirmar o e-mail antes de avaliar a falta de renda.

**Limitações:** o histórico contém competências efetivamente calculadas, não há preenchimento fictício de meses ausentes. Os eventos automáticos abrangem mutações feitas pelo frontend; mudanças feitas por outra sessão são atualizadas quando o usuário volta ao painel ou usa o botão. A revisão formal das OPEN-11/15/21, benchmark operacional e teste visual mobile dedicado ainda não estão concluídos.
