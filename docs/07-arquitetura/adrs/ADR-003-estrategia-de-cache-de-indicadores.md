# ADR-003: Estratégia de Cache e Resiliência para Indicadores Oficiais (SGS / Tesouro)

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova

## Contexto e Problema
O módulo de simulação depende de taxas oficiais como Selic, CDI e IPCA (RF-23). As APIs do Banco Central (SGS) e do Tesouro Transparente podem sofrer instabilidade ou rate limit. De acordo com a RB-11 e RNF-09, a aplicação não deve inventar taxa ou substituí-la por zero. Cache verificado há no máximo 24 horas pode ser usado; cache ausente/vencido produz erro informado ou cenário manual explicitamente escolhido.

## Decisão Considerada
Implementar um **Cache Local em Banco de Dados com Atualização Assíncrona e Fallback Decoupled**.

1. **Rotina de Sincronização:** Um agendador em segundo plano consulta as APIs externas e atualiza a tabela `IndicadorFinanceiroCache`.
2. **Consulta em Simulações:** As simulações consultam **exclusivamente o banco local**, eliminando a dependência síncrona de chamadas HTTP externas no momento da simulação.
3. **Resiliência:** Se a atualização falhar, mantém o registro, mas só o usa dentro da validade de 24 horas desde a última verificação da fonte. Exibe coleta e referência econômica separadamente. Sem cache válido, informa a indisponibilidade; não usa cache vencido silenciosamente.

## Alternativas Consideradas
* **Requisição HTTP síncrona na hora do cálculo:** Descartada pois violaria a latência do RNF-04 (P95 < 3s) e quebraria o sistema durante instabilidades da API do Banco Central.

## Consequências
### Positivas:
* Reduz dependência síncrona externa; latência e disponibilidade de 99,5% continuam exigindo medição (OPEN-06).
* Proteção contra indisponibilidade de órgãos governamentais.

### Negativas:
* Necessidade de gerenciar a rotina de job/cron e monitorar falhas de atualização de cache.
