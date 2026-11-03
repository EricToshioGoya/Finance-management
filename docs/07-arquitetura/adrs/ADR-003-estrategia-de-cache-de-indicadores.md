# ADR-003: Estratégia de Cache e Resiliência para Indicadores Oficiais (SGS / Tesouro)

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova
* **Revisão:** 2026-11-03 — política de cache defasado alinhada ao RF-23 e à regra C-08 por decisão do responsável (OPEN-19); entidade renomeada para `IndicadorOficial`, conforme o glossário.

## Contexto e Problema
O módulo de simulação depende de taxas oficiais como Selic, CDI e IPCA (RF-23). As APIs do Banco Central (SGS) e do Tesouro Transparente podem sofrer instabilidade ou rate limit. De acordo com a RB-11 e RNF-09, a aplicação não deve inventar taxa ou substituí-la por zero. Cache verificado há no máximo 24 horas é apresentado como atual; após esse prazo, ou na falha da atualização, o último valor em cache é usado com aviso visual de defasagem (RF-23, C-08). Somente a ausência de qualquer valor em cache produz erro informado ou cenário manual explicitamente escolhido.

## Decisão Considerada
Implementar um **Cache Local em Banco de Dados com Atualização Assíncrona e Fallback Decoupled**.

1. **Rotina de Sincronização:** Um agendador em segundo plano consulta as APIs externas e atualiza o cache de `IndicadorOficial` (tabela `market_indicators`).
2. **Consulta em Simulações:** As simulações consultam **exclusivamente o banco local**, eliminando a dependência síncrona de chamadas HTTP externas no momento da simulação.
3. **Resiliência:** Se a atualização falhar, mantém o registro sem renovar a data de verificação e continua usando o último valor. Passadas 24 horas da última verificação da fonte (RNF-09), o valor é marcado como defasado e exibido com aviso visual, nunca de forma silenciosa (RF-23, C-08). Exibe coleta e referência econômica separadamente. Sem nenhum valor em cache, informa a indisponibilidade; nunca usa zero nem taxa inventada.
4. **Políticas próprias:** a PTAX segue o limite aprovado no ADR-009 (OPEN-23) e as cotações de mercado seguem a SPEC-023 (referência defasada permite entrada manual explícita).

## Alternativas Consideradas
* **Requisição HTTP síncrona na hora do cálculo:** Descartada pois violaria a latência do RNF-04 (P95 < 3s) e quebraria o sistema durante instabilidades da API do Banco Central.

## Consequências
### Positivas:
* Reduz dependência síncrona externa; latência e disponibilidade de 99,5% continuam exigindo medição (OPEN-06).
* Proteção contra indisponibilidade de órgãos governamentais.

### Negativas:
* Necessidade de gerenciar a rotina de job/cron e monitorar falhas de atualização de cache.
