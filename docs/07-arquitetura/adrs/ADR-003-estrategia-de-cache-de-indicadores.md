# ADR-003: Estratégia de Cache e Resiliência para Indicadores Oficiais (SGS / Tesouro)

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova

## Contexto e Problema
O módulo de simulação depende de taxas oficiais como Selic, CDI e IPCA (RF-23). As APIs do Banco Central (SGS) e do Tesouro Transparente podem sofrer instabilidade ou rate limit. De acordo com o RF-23 (cláusula IF/THEN, que incorpora a antiga RB-11) e o RNF-09, a aplicação nunca pode falhar ou retornar taxa zerada se a API do governo estiver fora do ar, aceitando uma defasagem máxima de 24 horas.

## Decisão Considerada
Implementar um **Cache Local em Banco de Dados com Atualização Assíncrona e Fallback Decoupled**.

1. **Rotina de Sincronização:** Um agendador em segundo plano consulta as APIs externas e atualiza a tabela `IndicadorFinanceiroCache`.
2. **Consulta em Simulações:** As simulações consultam **exclusivamente o banco local**, eliminando a dependência síncrona de chamadas HTTP externas no momento da simulação.
3. **Resiliência:** Se a atualização em segundo plano falhar, o sistema mantém o último valor e injeta um indicador visual de alerta com a data/hora do último dado coletado.

## Alternativas Consideradas
* **Requisição HTTP síncrona na hora do cálculo:** Descartada pois violaria a latência do RNF-04 (P95 < 3s) e quebraria o sistema durante instabilidades da API do Banco Central.

## Consequências
### Positivas:
* Simulações extremamente rápidas e alta disponibilidade (RNF-08 de 99,5%).
* Proteção contra indisponibilidade de órgãos governamentais.

### Negativas:
* Necessidade de gerenciar a rotina de job/cron e monitorar falhas de atualização de cache.
