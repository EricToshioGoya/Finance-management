# Mapa completo de Specs — FinNova

**Estado:** rascunho para revisão, 2026-10-22. Baseline de origem: commit `bcdd4cde11100cf26d1343033b9226f1fa70271a`. O usuário autorizou gerar o catálogo e todas as Specs neste lote. Isso altera a sequência sugerida no PDF (uma por vez), mas não inventa aprovação formal do mapa ou das decisões abertas. Não há implementação nova nesta branch.

Foram preservados SPEC-001 a SPEC-017. Specs amplas foram delimitadas e o restante distribuído em unidades adicionais por comportamento. ID é identidade, não posição de execução. A ordem abaixo é topológica e não muda prioridades MoSCoW: opcionais só entram no recorte após decisão humana (OPEN-08/33).

## Análise da baseline

- Comportamentos: identidade e ciclo de conta, receitas/despesas/saldo, cálculo/projeção, fontes de mercado/CVM, metas/patrimônio/score, educação, comunicação/exportação, administração e integrações/compartilhamento.
- Invariantes: titularidade no servidor (RB-29), simulação separada do patrimônio real (RB-13/17), taxa equivalente composta e aportes ao fim do mês (RB-10/28), dados mínimos no painel/eventos (RB-22/23), sem PDF CVM (RB-12).
- Arquitetura: monólito em camadas/backend comum (ADR-001), domínio puro (ADR-002), cache sem HTTP síncrono (ADR-003), links/expurgo CVM (ADR-004), titularidade/papel (ADR-005), UTC e competência brasileira (ADR-006), sessão persistida/refresh/logout (ADR-007).
- RNFs são associados às Specs, incluindo recuperação operacional e compatibilidade; não foram criadas Specs de backend, banco ou RNF isolado.
- Lacunas/inconsistências: OPEN-19 a OPEN-33 complementam as anteriores. Cache vencido, patrimônio simulado, aliases, métricas/calendários, retenção/auditoria e prazo normativo versus proposta exigem decisão explícita. Revisões históricas não provam conformidade atual.

## Situação de implementação — 2026-10-31

Fonte: campo **Estado** de cada Spec em `docs/08-specs/` e registros em `docs/09-qualidade/`, conforme cópia do repositório do grupo em 2026-10-31. Este repositório ainda não contém código em `src/` nem testes em `tests/`; a implementação existe apenas no repositório do grupo. Nenhuma Spec possui aprovação formal do grupo.

### Resumo

| Situação | Qtd. | Specs |
|---|---|---|
| Implementada tecnicamente, aguardando revisão humana e/ou CI | 21 | 001, 002, 003, 011, 012, 014, 015, 016, 017, 018, 023, 025, 026, 027, 028, 034, 039, 053, 054, 055, 060 |
| Implementada, com validação automatizada registrada no PR | 2 | 042, 043 |
| Implementação em andamento ou em validação em branch/PR, sem merge confirmado | 7 | 019, 029, 030, 031, 032, 033, 035 |
| Implementação provisória ou recorte técnico, com decisões OPEN pendentes | 4 | 036, 037, 038, 041 |
| Rascunho, sem implementação | 28 | 004, 005, 006, 007, 008, 009, 010, 013, 020, 021, 022, 024, 040, 044, 045, 046, 047, 048, 049, 050, 051, 052, 056, 057, 058, 059, 061, 062 |

Total: 62 Specs; 34 com implementação (completa, em andamento ou provisória) e 28 pendentes.

### Specs com implementação sem registro em `docs/09-qualidade/`

SPEC-014, SPEC-015, SPEC-016, SPEC-017, SPEC-029, SPEC-042, SPEC-043 e SPEC-055.

### Detalhamento das Specs incluídas após 2026-10-23

- SPEC-003: implementada em branch de trabalho; política de quiz confirmada pelo responsável em 2026-10-28. [Registro](../09-qualidade/implementacao-SPEC-003.md).
- SPEC-011: implementação técnica autorizada em 2026-10-28; revisão formal do grupo pendente. [Registro](../09-qualidade/implementacao-SPEC-011.md).
- SPEC-012: implementada em branch de trabalho; recorte local confirmado pelo responsável em 2026-10-28. [Registro](../09-qualidade/implementacao-SPEC-012.md).
- SPEC-018: implementação isolada autorizada em 2026-10-28. [Registro](../09-qualidade/implementacao-SPEC-018.md).
- SPEC-019: implementação isolada em andamento. [Registro](../09-qualidade/implementacao-SPEC-019.md).
- SPEC-023: implementada tecnicamente em 2026-10-29. [Registro](../09-qualidade/implementacao-SPEC-023.md).
- SPEC-025: implementação técnica autorizada em 2026-10-29; aguardando CI e revisão humana. [Registro](../09-qualidade/implementacao-SPEC-025.md).
- SPEC-026: implementada tecnicamente em 2026-10-30; política de câmbio confirmada pelo responsável. [Registro](../09-qualidade/implementacao-SPEC-026.md).
- SPEC-027: implementada tecnicamente em 2026-10-30. [Registro](../09-qualidade/implementacao-SPEC-027.md).
- SPEC-028: implementada tecnicamente em 2026-10-29. [Registro](../09-qualidade/implementacao-SPEC-028.md).
- SPEC-029: implementação em andamento na branch `feature/29-net-worth-history`; execução do CI pendente.
- SPEC-030: em validação na branch `feature/30-net-worth-heatmap` (PR #67). [Registro](../09-qualidade/implementacao-SPEC-030.md).
- SPEC-031: em validação no PR #68 (`feature/31-portfolio-allocation`). [Registro](../09-qualidade/implementacao-SPEC-031.md).
- SPEC-032: implementação técnica no PR #69 (`feature/32-financial-stress`); OPEN-03/OPEN-21 pendentes. [Registro](../09-qualidade/implementacao-SPEC-032.md).
- SPEC-033: implementação técnica no PR #70 (`feature/33-named-asset-goals`). [Registro](../09-qualidade/implementacao-SPEC-033.md).
- SPEC-034: implementada tecnicamente em 2026-10-29. [Registro](../09-qualidade/implementacao-SPEC-034.md).
- SPEC-035: em validação na branch `feature/35-education-help`; conteúdo editorial sujeito a OPEN-30. [Registro](../09-qualidade/implementacao-SPEC-035.md).
- SPEC-036: implementação provisória na branch `feature/36-financing-amortization`; OPEN-12/22 pendentes. [Registro](../09-qualidade/implementacao-SPEC-036.md).
- SPEC-037: implementação provisória na branch `feature/37-finance-vs-invest`; OPEN-20/22 pendentes. [Registro](../09-qualidade/implementacao-SPEC-037.md).
- SPEC-038: recorte técnico na branch `feature/38-confirm-real-financing`; OPEN-12/15/21/22 pendentes. [Registro](../09-qualidade/implementacao-SPEC-038.md).
- SPEC-039: implementada tecnicamente em 2026-10-29; aguardando CI e revisão humana. [Registro](../09-qualidade/implementacao-SPEC-039.md).
- SPEC-041: implementação técnica em `feature/41-authorized-read-api`; recorte de chave API de leitura provisório; OPEN-24/15 pendentes. [Registro](../09-qualidade/implementacao-SPEC-041.md).
- SPEC-042: implementada em 2026-10-31; validação automatizada registrada no PR da implementação.
- SPEC-043: implementada em 2026-10-31; validação automatizada registrada no PR da implementação.
- SPEC-053: implementada tecnicamente em 2026-10-28. [Registro](../09-qualidade/implementacao-SPEC-053.md).
- SPEC-054: implementada tecnicamente em 2026-10-29. [Registro](../09-qualidade/implementacao-SPEC-054.md).
- SPEC-060: implementação técnica autorizada em 2026-10-28; revisão formal do grupo pendente. [Registro](../09-qualidade/implementacao-SPEC-060.md).

### Registro anterior — 2026-10-23

- SPEC-001: implementação funcional web e bloqueio concluídos na feature/spec001-completa; PR #12 permanece separado.
- SPEC-002: motor puro implementado na feature/13-motor-spec002; evidências no [registro](../09-qualidade/implementacao-SPEC-002.md).
- SPEC-015: implementada tecnicamente; o adaptador exige configuração HTTPS e OPEN-17 ainda cobre provedor, remetente, domínio e operação.
- SPEC-017: implementada tecnicamente na branch feature/17-sessoes; lista sessões próprias sem tokens, permite revogação individual/global e preserva rotação/logout de SPEC-001.
- SPEC-014: implementada tecnicamente na branch feature/19-perfil-preferencias; edita nome, mantém e-mail pendente até confirmação e persiste preferências por titular.
- SPEC-016: implementada tecnicamente na branch feature/21-recuperacao-senha; recupera/troca senha com token de 30 minutos, reautenticação e revogação de sessões.
- SPEC-055: implementada tecnicamente na branch feature/22-categorias; entrega catálogo padrão, categorias pessoais e ocultação isolada por titular.

As demais posições e dependências abaixo são preservadas. Estado de branch não implica merge na main ou aprovação formal do grupo. A interface de calculadora continua na SPEC-013.

## Ordem e rastreabilidade

| Ordem | ID / capacidade verificável | RF | RB | RNF | UC / fluxo e entidades | Drivers e ADR | Depende de |
|---|---|---|---|---|---|---|---|
| 1 | SPEC-001 Cadastro e autenticação | RF-01, RF-02 | RB-27, RB-29 | RNF-01, RNF-05, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-01, UC-02; Usuario e sessão técnica | DA-01, DA-05, DA-06, DA-09; ADR-001, ADR-005, ADR-007 | Sem Spec anterior; OPEN-01, OPEN-02, OPEN-08, OPEN-15, OPEN-16, OPEN-18 |
| 2 | SPEC-002 Motor puro de juros compostos | RF-22 | RB-10, RB-28 | RNF-04, RNF-07, RNF-16 | UC-08; ResultadoCalculo e motor puro | DA-02, DA-07, DA-09; ADR-002 | Sem Spec anterior; OPEN-03, OPEN-06, OPEN-15 |
| 3 | SPEC-015 Confirmar posse do e-mail | RF-69 | RB-27, RB-29 | RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | UC-24; Usuario e token temporário de infraestrutura | DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-001; OPEN-15, OPEN-17, OPEN-19 |
| 4 | SPEC-017 Consultar, renovar e encerrar sessões | RF-73, RF-74 | RB-29 | RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | UC-28, UC-29; Usuario e sessões técnicas, família de refresh | DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-001; OPEN-15, OPEN-18 |
| 5 | SPEC-014 Editar perfil e preferências persistidas | RF-68, RF-72 | RB-27, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-19, RNF-20 | UC-23, UC-27; Usuario e PreferenciasUsuario | DA-01, DA-05, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-001, SPEC-015; OPEN-15, OPEN-17 |
| 6 | SPEC-016 Recuperar e alterar senha com revogação | RF-70, RF-71 | RB-27, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | UC-25, UC-26; Usuario e tokens/sessões de infraestrutura | DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-001, SPEC-015, SPEC-017; OPEN-15, OPEN-17, OPEN-19 |
| 7 | SPEC-055 Gerir categorias padrão e pessoais | RF-10 | RB-02, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | UC-07; Categoria, Usuario e Despesa | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-001, SPEC-015; OPEN-15, OPEN-21 |
| 8 | SPEC-005 Cadastrar contas e cartões do titular | RF-12 | RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | UC-07; Usuario, Conta e Cartao | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-001, SPEC-015; OPEN-12, OPEN-15, OPEN-21 |
| 9 | SPEC-056 Registrar receita recorrente mensal | RF-06 | RB-01, RB-05, RB-29 | RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25 | UC-05; Usuario, Conta e ReceitaRecorrente | DA-01, DA-06, DA-07, DA-09, DA-10, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-005; OPEN-12, OPEN-15, OPEN-21 |
| 10 | SPEC-057 Registrar receita pontual por competência | RF-07 | RB-01, RB-05, RB-29 | RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25 | UC-05; Usuario, Conta e ReceitaPontual | DA-01, DA-06, DA-07, DA-09, DA-10, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-005; OPEN-12, OPEN-15, OPEN-21 |
| 11 | SPEC-058 Registrar bônus ou PLR mensal/anual | RF-08 | RB-01, RB-05, RB-06, RB-29 | RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25 | UC-05; Usuario e BonusPLR | DA-01, DA-06, DA-07, DA-09, DA-10, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-005; OPEN-12, OPEN-15, OPEN-21 |
| 12 | SPEC-059 Registrar despesa pontual ou recorrente | RF-09 | RB-01, RB-02, RB-29 | RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25 | UC-06; Usuario, Conta, Cartao, Categoria e Despesa | DA-01, DA-06, DA-07, DA-09, DA-10, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-005, SPEC-055; OPEN-12, OPEN-15, OPEN-21 |
| 13 | SPEC-006 Editar lançamentos e consultar saldo coerente | RF-11 | RB-01, RB-02, RB-05, RB-06, RB-29 | RNF-01, RNF-03, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-22, RNF-24, RNF-25 | UC-05, UC-06; edição de RF-11; Renda, ReceitaRecorrente, ReceitaPontual, BonusPLR, Despesa, Conta | DA-01, DA-06, DA-07, DA-08, DA-09, DA-10, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-005, SPEC-055, SPEC-056, SPEC-057, SPEC-058, SPEC-059; OPEN-12, OPEN-15, OPEN-21 |
| 14 | SPEC-007 Consultar indicador oficial válido em cache | RF-23 | RB-11 | RNF-01, RNF-05, RNF-06, RNF-08, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | UC-20 e consulta por UC-09; IndicadorMercadoCache (aliases históricos em OPEN-19) | DA-01, DA-03, DA-07, DA-09, DA-11; ADR-001, ADR-003, ADR-006 | SPEC-001; OPEN-04, OPEN-10, OPEN-15, OPEN-19 |
| 15 | SPEC-004 Tributação de produto na projeção | RF-20, RF-64 | RB-07, RB-25, RB-28 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-09; fluxo tributário de RF-64; Simulacao e resultado bruto; tabela tributária conceitual | DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002 | SPEC-002; OPEN-07, OPEN-03, OPEN-15 |
| 16 | SPEC-008 Executar simulação rastreável de renda fixa | RF-20 | RB-07, RB-10, RB-28, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-09; Usuario, Simulacao e IndicadorMercadoCache | DA-01, DA-02, DA-03, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-003, ADR-005, ADR-007 | SPEC-001, SPEC-002, SPEC-004, SPEC-007, SPEC-015; OPEN-07, OPEN-10, OPEN-15, OPEN-19 |
| 17 | SPEC-009 Projetar investimentos de renda variável | RF-21 | RB-08, RB-28, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-10; Usuario e Simulacao | DA-01, DA-02, DA-03, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-003, ADR-005, ADR-007 | SPEC-001, SPEC-002, SPEC-015; OPEN-03, OPEN-10, OPEN-15, OPEN-19 |
| 18 | SPEC-013 Operar calculadora de juros com explicação | RF-22, RF-44 | RB-10, RB-28, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-08; ResultadoCalculo e IndicadorMercadoCache | DA-01, DA-02, DA-03, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-003, ADR-005, ADR-007 | SPEC-001, SPEC-002, SPEC-007, SPEC-015; OPEN-03, OPEN-10, OPEN-15, OPEN-19 |
| 19 | SPEC-010 Comparar simulações existentes | RF-25 | RB-08, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-11; Usuario e Simulacao | DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-008, SPEC-009; OPEN-15, OPEN-20 |
| 20 | SPEC-020 Consultar fatura e limite disponível | RF-13 | RB-04, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | UC-07; Cartao e Despesa | DA-01, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-005, SPEC-059; OPEN-12, OPEN-15, OPEN-21 |
| 21 | SPEC-021 Definir metas de orçamento e acompanhar progresso | RF-14, RF-15, RF-19 | RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Fluxos de metas RF-14/15/19; MetaGeral, MetaCategoria, Categoria, Renda e Despesa | DA-01, DA-02, DA-06, DA-07, DA-08, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007 | SPEC-006; OPEN-11, OPEN-15, OPEN-21 |
| 22 | SPEC-022 Consultar dashboards financeiros por período | RF-16, RF-17, RF-18 | RB-05, RB-06, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Fluxos de dashboards RF-16 a RF-18; Renda, Despesa, Conta e Categoria | DA-01, DA-02, DA-06, DA-07, DA-08, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007 | SPEC-006; OPEN-06, OPEN-15, OPEN-21 |
| 23 | SPEC-024 Projetar aporte para objetivo financeiro | RF-26 | RB-10, RB-28, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-12; MetaFinanceira e ResultadoCalculo | DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-002, SPEC-006; OPEN-03, OPEN-15, OPEN-21 |
| 24 | SPEC-018 Excluir conta e dados pessoais | RF-05 | RB-29 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | UC-04; Usuario e vínculos pessoais de todos os módulos | DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-001, SPEC-017; OPEN-05, OPEN-15, OPEN-19, OPEN-29 |
| 25 | SPEC-019 Exportar extrato pessoal CSV/PDF | RF-50 | RB-29 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | UC-15; Usuario, Renda, Despesa, Conta e Categoria | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-006; OPEN-05, OPEN-15, OPEN-29 |
| 26 | SPEC-060 Coletar eventos e auditar ações sensíveis | RF-59 | RB-23 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | UC-22; EventoUso e AuditLog | DA-01, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-001; OPEN-05, OPEN-15, OPEN-19, OPEN-26 |
| 27 | SPEC-011 Proteger painel e consultar metadados de usuários | RF-54, RF-55 | RB-22, RB-27 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-21 | UC-17, UC-18; Usuario, papel e AuditLog | DA-01, DA-05, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-001, SPEC-060; OPEN-05, OPEN-13, OPEN-15 |
| 28 | SPEC-003 Classificar perfil por quiz | RF-03 | RB-09, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-03; Usuario e perfil de investidor | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-001; OPEN-11, OPEN-15 |
| 29 | SPEC-012 Pesquisar empresas e abrir documentos oficiais | RF-29, RF-30, RF-31 | RB-12 | RNF-01, RNF-05, RNF-06, RNF-08, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-13 e UC-20; EmpresaAberta e DocumentoCVM | DA-01, DA-04, DA-07, DA-09; ADR-001, ADR-004 | SPEC-001, SPEC-015; OPEN-10, OPEN-15, OPEN-27 |
| 30 | SPEC-053 Consultar indicadores contábeis CVM por período | RF-32 | RB-12 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-13, UC-20; EmpresaAberta e IndicadorFinanceiro | DA-01, DA-02, DA-04, DA-07, DA-09; ADR-001, ADR-002, ADR-004 | SPEC-012; OPEN-10, OPEN-15, OPEN-27 |
| 31 | SPEC-054 Expurgar cache CVM após 12 meses | RF-33 | RB-12 | RNF-01, RNF-05, RNF-06, RNF-10, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | UC-21; DocumentoCVM e IndicadorFinanceiro | DA-01, DA-04, DA-07, DA-09, DA-11; ADR-001, ADR-004, ADR-006 | SPEC-012, SPEC-053; OPEN-04, OPEN-05, OPEN-15, OPEN-27 |
| 32 | SPEC-023 Consultar cotação e histórico de ações/FIIs | RF-24 | RB-08 | RNF-01, RNF-05, RNF-06, RNF-09, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-10; fluxo de RF-24; Cotação como dado de integração e Simulacao consumidora | DA-01, DA-03, DA-07, DA-09; ADR-001, ADR-003 | SPEC-001, SPEC-015; OPEN-10, OPEN-15, OPEN-19 |
| 33 | SPEC-028 Consolidar patrimônio real e itens manuais | RF-35 | RB-13, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | UC-14; Conta, Cartao, Ativo, Passivo e PatrimonioItem | DA-01, DA-02, DA-06, DA-07, DA-08, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-005, SPEC-020; OPEN-15, OPEN-19, OPEN-21, OPEN-28 |
| 34 | SPEC-034 Calcular e explicar score de saúde financeira | RF-41, RF-42 | RB-15, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | UC-14; ScoreSaude, Usuario e fatores de orçamento/patrimônio | DA-01, DA-02, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007 | SPEC-020, SPEC-021, SPEC-028; OPEN-11, OPEN-15, OPEN-21 |
| 35 | SPEC-039 Gerar alertas e histórico in-app | RF-48 | RB-29 | RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | UC-15; Notificacao, Usuario e eventos dos módulos | DA-01, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-001, SPEC-014; OPEN-11, OPEN-15, OPEN-26 |
| 36 | SPEC-025 Exibir volatilidade e Sharpe histórico | RF-27 | RB-08, RB-10, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-10, UC-11; Simulacao e histórico de Cotação | DA-01, DA-02, DA-03, DA-07, DA-09; ADR-001, ADR-002, ADR-003 | SPEC-003, SPEC-007, SPEC-009, SPEC-010, SPEC-023; OPEN-03, OPEN-10, OPEN-15, OPEN-20 |
| 37 | SPEC-026 Projetar investimento em moeda estrangeira | RF-28 | RB-08, RB-10, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo de câmbio RF-28; Simulacao e referência cambial | DA-01, DA-02, DA-03, DA-07, DA-09; ADR-001, ADR-002, ADR-003 | SPEC-002, SPEC-007, SPEC-015; OPEN-03, OPEN-10, OPEN-15, OPEN-23 |
| 38 | SPEC-027 Manter watchlist e avisar novo documento | RF-34 | RB-12, RB-29 | RNF-01, RNF-05, RNF-06, RNF-10, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20 | UC-13; fluxo watchlist; Usuario, Watchlist, EmpresaAberta e DocumentoCVM | DA-01, DA-04, DA-06, DA-07, DA-09; ADR-001, ADR-004, ADR-005, ADR-007 | SPEC-012, SPEC-039; OPEN-15, OPEN-26, OPEN-27 |
| 39 | SPEC-029 Consultar evolução mensal do patrimônio | RF-36 | RB-13, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | UC-14; PatrimonioItem, Ativo e Passivo | DA-01, DA-02, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007 | SPEC-028; OPEN-15, OPEN-21 |
| 40 | SPEC-030 Visualizar mapa de calor patrimonial | RF-37 | RB-13, RB-14, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-14; PatrimonioItem, Ativo e Passivo | DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-028; OPEN-15, OPEN-21 |
| 41 | SPEC-031 Comparar alocação atual e alvo | RF-38 | RB-13, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-14; Ativo e classes patrimoniais | DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-028; OPEN-15, OPEN-21 |
| 42 | SPEC-032 Simular stress financeiro isolado | RF-39 | RB-17, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-14; fluxo de stress RF-39; Simulacao, Ativo, Passivo e orçamento | DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002 | SPEC-006, SPEC-028; OPEN-03, OPEN-15, OPEN-21 |
| 43 | SPEC-033 Acompanhar metas nomeadas por ativo | RF-40 | RB-18, RB-29 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20 | UC-14; fluxo metas nomeadas; MetaNomeada, MetaFinanceira e Ativo | DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-024, SPEC-028; OPEN-15, OPEN-19, OPEN-21 |
| 44 | SPEC-035 Buscar conteúdo educativo e ajuda contextual | RF-43, RF-44 | RB-09 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-15, RNF-16, RNF-17, RNF-20 | UC-15; ConteudoEducacional e perfil de Usuario | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-003; OPEN-11, OPEN-15, OPEN-30 |
| 45 | SPEC-036 Simular compra financiada e amortização | RF-45 | RB-10, RB-28, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo de compra financiada RF-45; CompraFinanciada, Simulacao e Parcela | DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002 | SPEC-002, SPEC-015; OPEN-03, OPEN-12, OPEN-15, OPEN-22 |
| 46 | SPEC-037 Comparar financiamento e compra após investir | RF-46 | RB-10, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo comparativo RF-46; CompraFinanciada e Simulacao | DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002 | SPEC-002, SPEC-036; OPEN-03, OPEN-15, OPEN-20, OPEN-22 |
| 47 | SPEC-038 Registrar financiamento real a partir da confirmação | RF-47 | RB-16, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | Fluxo de confirmação RF-47; CompraFinanciada, Passivo e Despesa | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-028, SPEC-036, SPEC-059; OPEN-12, OPEN-15, OPEN-21, OPEN-22 |
| 48 | SPEC-041 Disponibilizar API para integrações autorizadas | RF-52 | RB-29 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | Fluxo de API pública RF-52; Usuario e concessão de acesso de integração (conceitual) | DA-01, DA-05, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-006, SPEC-028; OPEN-15, OPEN-24 |
| 49 | SPEC-042 Entregar eventos por webhook assinado | RF-53 | RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-23 | Fluxo webhook RF-53; WebhookSubscription, Usuario e registro de tentativa | DA-01, DA-05, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-039; OPEN-15, OPEN-25, OPEN-26 |
| 50 | SPEC-043 Consultar uso por módulo e engajamento | RF-57, RF-58 | RB-22, RB-23 | RNF-01, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-21, RNF-25 | UC-19; EventoUso e Usuario | DA-01, DA-02, DA-05, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-005, ADR-006, ADR-007 | SPEC-011, SPEC-060; OPEN-05, OPEN-11, OPEN-15, OPEN-21 |
| 51 | SPEC-044 Aceitar e desfazer vínculo entre dois usuários | RF-60 | RB-29 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | UC-16; Usuario e ContaCompartilhada | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-001, SPEC-015; OPEN-05, OPEN-15, OPEN-31 |
| 52 | SPEC-045 Dividir despesas e registrar acertos | RF-61 | RB-24, RB-29 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20 | UC-16; ContaCompartilhada, Despesa, DespesaCompartilhada e AcertoConta | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-044, SPEC-059; OPEN-03, OPEN-05, OPEN-15, OPEN-31 |
| 53 | SPEC-046 Projetar aposentadoria e renda estimada | RF-62 | RB-10, RB-28, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo aposentadoria RF-62; Simulacao e ResultadoCalculo | DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002 | SPEC-002, SPEC-007, SPEC-015; OPEN-03, OPEN-07, OPEN-15, OPEN-22 |
| 54 | SPEC-047 Comparar previdência PGBL/VGBL/carteira | RF-63 | RB-10, RB-25, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo previdência RF-63; Simulacao e regras tributárias conceituais | DA-01, DA-02, DA-07, DA-09; ADR-001, ADR-002 | SPEC-002, SPEC-004, SPEC-046; OPEN-03, OPEN-07, OPEN-15, OPEN-22 |
| 55 | SPEC-048 Estimar imposto de operações e lembrete DARF | RF-64 | RB-25, RB-29 | RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | Fluxo tributário RF-64; Simulacao e operação registrada conceitual; regra tributária | DA-01, DA-02, DA-07, DA-09, DA-11; ADR-001, ADR-002, ADR-006 | SPEC-004, SPEC-009; OPEN-03, OPEN-07, OPEN-15, OPEN-22 |
| 56 | SPEC-049 Exportar resumo anual auxiliar de rendimentos | RF-65 | RB-25, RB-29 | RNF-01, RNF-02, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-18, RNF-20, RNF-25 | Fluxo informe anual RF-65; Simulacao e resultados tributários | DA-01, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-019, SPEC-048; OPEN-05, OPEN-15, OPEN-21, OPEN-29 |
| 57 | SPEC-050 Comparar score por grupo anônimo | RF-66 | RB-26, RB-29 | RNF-01, RNF-02, RNF-04, RNF-05, RNF-06, RNF-07, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-14; Usuario, perfil e ScoreSaude | DA-01, DA-02, DA-06, DA-07, DA-09; ADR-001, ADR-002, ADR-005, ADR-007 | SPEC-003, SPEC-034; OPEN-05, OPEN-11, OPEN-15 |
| 58 | SPEC-051 Conceder conquistas sem efeito financeiro | RF-67 | RB-15, RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-14, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo conquistas RF-67; Badge, Usuario e metas | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-021, SPEC-033, SPEC-039; OPEN-11, OPEN-15, OPEN-26 |
| 59 | SPEC-052 Guiar primeiro acesso com tour opcional | RF-04 | RB-09 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-15, RNF-16, RNF-17, RNF-20 | Fluxo onboarding RF-04; Usuario e perfil de experiência | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-003, SPEC-006, SPEC-008, SPEC-013; OPEN-08, OPEN-15, OPEN-30 |
| 60 | SPEC-061 Entregar notificação em canal opcional | RF-49 | RB-29 | RNF-01, RNF-05, RNF-06, RNF-08, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-15; Notificacao, Usuario e PreferenciasUsuario | DA-01, DA-07, DA-09; ADR-001 | SPEC-039, SPEC-015; OPEN-15, OPEN-17, OPEN-26 |
| 61 | SPEC-040 Enviar resumo mensal automático optativo | RF-51 | RB-29 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20, RNF-25 | UC-15; relatório mensal; Renda, Despesa, PatrimonioItem, ScoreSaude e Notificacao | DA-01, DA-06, DA-07, DA-09, DA-11; ADR-001, ADR-005, ADR-006, ADR-007 | SPEC-019, SPEC-028, SPEC-034, SPEC-039, SPEC-061; OPEN-05, OPEN-15, OPEN-21, OPEN-26 |
| 62 | SPEC-062 Consultar distribuição de perfis no painel | RF-56 | RB-09, RB-22 | RNF-01, RNF-05, RNF-06, RNF-11, RNF-12, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | UC-19; Usuario e perfil de investidor | DA-01, DA-06, DA-07, DA-09; ADR-001, ADR-005, ADR-007 | SPEC-003, SPEC-011; OPEN-11, OPEN-15, OPEN-21 |

## Objetivo, valor e justificativa da ordem

| Spec | Objetivo | Valor entregue | Justificativa da posição |
|---|---|---|---|
| SPEC-001 | Cadastro e autenticação | identidade e sessão | Estabelece comportamento consumido sem dependência funcional anterior; decisões OPEN continuam bloqueantes |
| SPEC-002 | Motor puro de juros compostos | cálculo determinístico | Estabelece comportamento consumido sem dependência funcional anterior; decisões OPEN continuam bloqueantes |
| SPEC-015 | Confirmar posse do e-mail | estado pendente/verificado ou erro sem consumo indevido | Consome SPEC-001 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-017 | Consultar, renovar e encerrar sessões | lista sem tokens, novo acesso renovado ou confirmação de revogação | Consome SPEC-001 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-014 | Editar perfil e preferências persistidas | perfil próprio atualizado ou e-mail pendente e preferências reaplicadas | Consome SPEC-001, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-016 | Recuperar e alterar senha com revogação | senha protegida atualizada e sessões revogadas | Consome SPEC-001, SPEC-015, SPEC-017 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-055 | Gerir categorias padrão e pessoais | categorias padrão/pessoais disponíveis e histórico preservado | Consome SPEC-001, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-005 | Cadastrar contas e cartões do titular | contas/cartões disponíveis para vínculo | Consome SPEC-001, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-056 | Registrar receita recorrente mensal | receita recorrente nas competências vigentes | Consome SPEC-005 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-057 | Registrar receita pontual por competência | entrada atribuída ao mês correspondente | Consome SPEC-005 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-058 | Registrar bônus ou PLR mensal/anual | contribuição mensal/anuária identificada | Consome SPEC-005 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-059 | Registrar despesa pontual ou recorrente | despesa registrada e agregações refletidas | Consome SPEC-005, SPEC-055 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-006 | Editar lançamentos e consultar saldo coerente | lançamento atualizado/removido e totais recalculados | Consome SPEC-005, SPEC-055, SPEC-056, SPEC-057, SPEC-058, SPEC-059 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-007 | Consultar indicador oficial válido em cache | valor, unidade, periodicidade, referência e estado de disponibilidade | Consome SPEC-001 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-004 | Tributação de produto na projeção | imposto estimado e resultado líquido identificado | Consome SPEC-002 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-008 | Executar simulação rastreável de renda fixa | projeção bruta/líquida com hipóteses e indicador referenciado | Consome SPEC-001, SPEC-002, SPEC-004, SPEC-007, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-009 | Projetar investimentos de renda variável | evolução estimada identificada como projeção | Consome SPEC-001, SPEC-002, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-013 | Operar calculadora de juros com explicação | tabela mensal, gráfico, resumo e ajuda da taxa | Consome SPEC-001, SPEC-002, SPEC-007, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-010 | Comparar simulações existentes | resultados lado a lado, diferenças percentuais e maior resultado | Consome SPEC-008, SPEC-009 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-020 | Consultar fatura e limite disponível | fatura, limite disponível e alerta de proximidade | Consome SPEC-005, SPEC-059 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-021 | Definir metas de orçamento e acompanhar progresso | metas vigentes, barras de progresso e sinais de ultrapassagem | Consome SPEC-006 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-022 | Consultar dashboards financeiros por período | gráficos por categoria, saldo e renda versus gasto | Consome SPEC-006 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-024 | Projetar aporte para objetivo financeiro | aporte mensal necessário e alerta de inviabilidade | Consome SPEC-002, SPEC-006 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-018 | Excluir conta e dados pessoais | conta sem novos acessos e exclusão/anonimização rastreável | Consome SPEC-001, SPEC-017 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-019 | Exportar extrato pessoal CSV/PDF | arquivo do titular, PDF com resumo e detalhes | Consome SPEC-006 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-060 | Coletar eventos e auditar ações sensíveis | evento de uso assíncrono mínimo e auditoria protegida | Consome SPEC-001 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-011 | Proteger painel e consultar metadados de usuários | lista paginada de metadados e auditoria do acesso | Consome SPEC-001, SPEC-060 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-003 | Classificar perfil por quiz | perfil classificado e experiência adaptada | Consome SPEC-001 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-012 | Pesquisar empresas e abrir documentos oficiais | sugestões, ficha, metadados e links oficiais | Consome SPEC-001, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-053 | Consultar indicadores contábeis CVM por período | tabela/gráfico com valores estruturados e fonte | Consome SPEC-012 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-054 | Expurgar cache CVM após 12 meses | cache sem registros expirados e execução registrada | Consome SPEC-012, SPEC-053 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-023 | Consultar cotação e histórico de ações/FIIs | preço, variação diária, histórico e referência temporal | Consome SPEC-001, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-028 | Consolidar patrimônio real e itens manuais | ativos/passivos consolidados e patrimônio líquido | Consome SPEC-005, SPEC-020 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-034 | Calcular e explicar score de saúde financeira | nota 0..100, fatores, classificação e histórico mensal | Consome SPEC-020, SPEC-021, SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-039 | Gerar alertas e histórico in-app | notificação própria com histórico por ao menos 30 dias | Consome SPEC-001, SPEC-014 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-025 | Exibir volatilidade e Sharpe histórico | volatilidade/Sharpe com período e ressalva | Consome SPEC-003, SPEC-007, SPEC-009, SPEC-010, SPEC-023 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-026 | Projetar investimento em moeda estrangeira | projeção na moeda original e BRL com PTAX referenciada | Consome SPEC-002, SPEC-007, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-027 | Manter watchlist e avisar novo documento | lista pessoal e notificação do evento | Consome SPEC-012, SPEC-039 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-029 | Consultar evolução mensal do patrimônio | séries de ativos, passivos e patrimônio líquido | Consome SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-030 | Visualizar mapa de calor patrimonial | treemap ou bolhas com tamanho, cor e detalhes | Consome SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-031 | Comparar alocação atual e alvo | distribuição percentual e desvios | Consome SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-032 | Simular stress financeiro isolado | meses de sustentação, alerta e comparação de dois cenários | Consome SPEC-006, SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-033 | Acompanhar metas nomeadas por ativo | progresso e aporte mensal projetado | Consome SPEC-024, SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-035 | Buscar conteúdo educativo e ajuda contextual | verbete curto, sugestões e tooltip na tela atual | Consome SPEC-003 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-036 | Simular compra financiada e amortização | tabela de amortização e total pago | Consome SPEC-002, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-037 | Comparar financiamento e compra após investir | custos, prazos até posse e comparação | Consome SPEC-002, SPEC-036 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-038 | Registrar financiamento real a partir da confirmação | passivo de saldo devedor e parcela opcional como despesa | Consome SPEC-028, SPEC-036, SPEC-059 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-041 | Disponibilizar API para integrações autorizadas | dados dentro do escopo e documentação pública | Consome SPEC-006, SPEC-028 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-042 | Entregar eventos por webhook assinado | payload HMAC, histórico de tentativas e reenvio manual | Consome SPEC-039 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-043 | Consultar uso por módulo e engajamento | acessos/usuários únicos por módulo, DAU/WAU/MAU e evolução | Consome SPEC-011, SPEC-060 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-044 | Aceitar e desfazer vínculo entre dois usuários | vínculo aceito por dois titulares e histórico preservado | Consome SPEC-001, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-045 | Dividir despesas e registrar acertos | saldo quem deve quem e detalhamento para dois membros | Consome SPEC-044, SPEC-059 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-046 | Projetar aposentadoria e renda estimada | patrimônio na data-alvo e renda mensal estimada | Consome SPEC-002, SPEC-007, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-047 | Comparar previdência PGBL/VGBL/carteira | valores líquidos comparáveis e contexto de dedução educativo | Consome SPEC-002, SPEC-004, SPEC-046 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-048 | Estimar imposto de operações e lembrete DARF | IR estimado e prazo de DARF quando aplicável | Consome SPEC-004, SPEC-009 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-049 | Exportar resumo anual auxiliar de rendimentos | documento consolidado auxiliar com rendimentos e imposto estimado | Consome SPEC-019, SPEC-048 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-050 | Comparar score por grupo anônimo | média/percentil agregado do grupo ou comparação oculta | Consome SPEC-003, SPEC-034 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-051 | Conceder conquistas sem efeito financeiro | conquista, progresso e notificação | Consome SPEC-021, SPEC-033, SPEC-039 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-052 | Guiar primeiro acesso com tour opcional | tour adaptado com acesso às funções principais | Consome SPEC-003, SPEC-006, SPEC-008, SPEC-013 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-061 | Entregar notificação em canal opcional | tentativa e resultado de entrega externa | Consome SPEC-039, SPEC-015 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-040 | Enviar resumo mensal automático optativo | PDF do mês anterior e estado de envio | Consome SPEC-019, SPEC-028, SPEC-034, SPEC-039, SPEC-061 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |
| SPEC-062 | Consultar distribuição de perfis no painel | distribuição agregada por resultado do quiz | Consome SPEC-003, SPEC-011 já anteriores nesta ordem; decisões OPEN continuam bloqueantes |

## Arquivos individuais e revisão

- [SPEC-001 — Cadastro e autenticação](SPEC-001.md)
- [SPEC-002 — Motor puro de juros compostos](SPEC-002.md)
- [SPEC-003 — Classificar perfil por quiz](SPEC-003.md)
- [SPEC-004 — Tributação de produto na projeção](SPEC-004.md)
- [SPEC-005 — Cadastrar contas e cartões do titular](SPEC-005.md)
- [SPEC-006 — Editar lançamentos e consultar saldo coerente](SPEC-006.md)
- [SPEC-007 — Consultar indicador oficial válido em cache](SPEC-007.md)
- [SPEC-008 — Executar simulação rastreável de renda fixa](SPEC-008.md)
- [SPEC-009 — Projetar investimentos de renda variável](SPEC-009.md)
- [SPEC-010 — Comparar simulações existentes](SPEC-010.md)
- [SPEC-011 — Proteger painel e consultar metadados de usuários](SPEC-011.md)
- [SPEC-012 — Pesquisar empresas e abrir documentos oficiais](SPEC-012.md)
- [SPEC-013 — Operar calculadora de juros com explicação](SPEC-013.md)
- [SPEC-014 — Editar perfil e preferências persistidas](SPEC-014.md)
- [SPEC-015 — Confirmar posse do e-mail](SPEC-015.md)
- [SPEC-016 — Recuperar e alterar senha com revogação](SPEC-016.md)
- [SPEC-017 — Consultar, renovar e encerrar sessões](SPEC-017.md)
- [SPEC-018 — Excluir conta e dados pessoais](SPEC-018.md)
- [SPEC-019 — Exportar extrato pessoal CSV/PDF](SPEC-019.md)
- [SPEC-020 — Consultar fatura e limite disponível](SPEC-020.md)
- [SPEC-021 — Definir metas de orçamento e acompanhar progresso](SPEC-021.md)
- [SPEC-022 — Consultar dashboards financeiros por período](SPEC-022.md)
- [SPEC-023 — Consultar cotação e histórico de ações/FIIs](SPEC-023.md)
- [SPEC-024 — Projetar aporte para objetivo financeiro](SPEC-024.md)
- [SPEC-025 — Exibir volatilidade e Sharpe histórico](SPEC-025.md)
- [SPEC-026 — Projetar investimento em moeda estrangeira](SPEC-026.md)
- [SPEC-027 — Manter watchlist e avisar novo documento](SPEC-027.md)
- [SPEC-028 — Consolidar patrimônio real e itens manuais](SPEC-028.md)
- [SPEC-029 — Consultar evolução mensal do patrimônio](SPEC-029.md)
- [SPEC-030 — Visualizar mapa de calor patrimonial](SPEC-030.md)
- [SPEC-031 — Comparar alocação atual e alvo](SPEC-031.md)
- [SPEC-032 — Simular stress financeiro isolado](SPEC-032.md)
- [SPEC-033 — Acompanhar metas nomeadas por ativo](SPEC-033.md)
- [SPEC-034 — Calcular e explicar score de saúde financeira](SPEC-034.md)
- [SPEC-035 — Buscar conteúdo educativo e ajuda contextual](SPEC-035.md)
- [SPEC-036 — Simular compra financiada e amortização](SPEC-036.md)
- [SPEC-037 — Comparar financiamento e compra após investir](SPEC-037.md)
- [SPEC-038 — Registrar financiamento real a partir da confirmação](SPEC-038.md)
- [SPEC-039 — Gerar alertas e histórico in-app](SPEC-039.md)
- [SPEC-040 — Enviar resumo mensal automático optativo](SPEC-040.md)
- [SPEC-041 — Disponibilizar API para integrações autorizadas](SPEC-041.md)
- [SPEC-042 — Entregar eventos por webhook assinado](SPEC-042.md)
- [SPEC-043 — Consultar uso por módulo e engajamento](SPEC-043.md)
- [SPEC-044 — Aceitar e desfazer vínculo entre dois usuários](SPEC-044.md)
- [SPEC-045 — Dividir despesas e registrar acertos](SPEC-045.md)
- [SPEC-046 — Projetar aposentadoria e renda estimada](SPEC-046.md)
- [SPEC-047 — Comparar previdência PGBL/VGBL/carteira](SPEC-047.md)
- [SPEC-048 — Estimar imposto de operações e lembrete DARF](SPEC-048.md)
- [SPEC-049 — Exportar resumo anual auxiliar de rendimentos](SPEC-049.md)
- [SPEC-050 — Comparar score por grupo anônimo](SPEC-050.md)
- [SPEC-051 — Conceder conquistas sem efeito financeiro](SPEC-051.md)
- [SPEC-052 — Guiar primeiro acesso com tour opcional](SPEC-052.md)
- [SPEC-053 — Consultar indicadores contábeis CVM por período](SPEC-053.md)
- [SPEC-054 — Expurgar cache CVM após 12 meses](SPEC-054.md)
- [SPEC-055 — Gerir categorias padrão e pessoais](SPEC-055.md)
- [SPEC-056 — Registrar receita recorrente mensal](SPEC-056.md)
- [SPEC-057 — Registrar receita pontual por competência](SPEC-057.md)
- [SPEC-058 — Registrar bônus ou PLR mensal/anual](SPEC-058.md)
- [SPEC-059 — Registrar despesa pontual ou recorrente](SPEC-059.md)
- [SPEC-060 — Coletar eventos e auditar ações sensíveis](SPEC-060.md)
- [SPEC-061 — Entregar notificação em canal opcional](SPEC-061.md)
- [SPEC-062 — Consultar distribuição de perfis no painel](SPEC-062.md)

## Decomposição dos IDs existentes

SPEC-005 mantém contas/cartões (RF-12); categorias (RF-10) passam a SPEC-055. SPEC-006 mantém edição/consistência de saldo (RF-11); criação recorrente/pontual/bônus/despesa passa a SPEC-056 a SPEC-059. SPEC-011 mantém acesso/listagem (RF-54/55); coleta de RF-59 passa a SPEC-060. SPEC-012 mantém busca/documentos/links (RF-29 a RF-31); números e expurgo passam a SPEC-053/054. Isso preserva identidade e reduz tamanho sem remover requisitos. SPEC-004 continua parcial para tributação de produto; SPEC-048 cobre RF-64 completo. SPEC-014 a SPEC-017 preservam perfil/preferências, confirmação, senhas e sessões.

RF-22 divide núcleo (SPEC-002) e experiência integrada (SPEC-013). RF-44 divide ajuda da taxa (SPEC-013) e conteúdo/tooltips gerais (SPEC-035). Caminho ticker de SPEC-009 depende condicionalmente de SPEC-023; cenário manual não. Alertas SPEC-039 recebem eventos dos produtores sem exigir que todos existam para validar sua central. Fatura/financiamento são origens condicionais de patrimônio; cadastro de itens manuais e conta não exige desenvolver todas as origens. Referências históricas de UC não substituem os catálogos atuais.

A interface de conta não verificada deve continuar permitindo confirmação/recuperação/manutenção necessária; a migração de contas existentes depende OPEN-17/19. Login/sessão existentes não significam essas regras implementadas.

## Cobertura e condições de conclusão

[Cobertura RF por RF e critérios](cobertura-requisitos.md) registra os 74 requisitos; [RNFs transversais](cobertura-rnf.md) registra os 25 RNFs e evidência futura. [OPEN](questoes-abertas.md) distingue decisão pendente de contrato já implementado. As 62 Specs estão escritas; Specs com OPEN bloqueante são rascunhos condicionados, não promessas de implementação sem escolhas adicionais. Aprovação formal do grupo: pendente; não há assinatura ou revisão do colega inventada.
