# Decisões pendentes — FinNova

SPEC-019: nesta entrega, download é anexado à sessão autenticada de 15 minutos já definida no ADR-007; não há URL pública financeira. Esta decisão atende ao acesso temporário do extrato técnico, sem resolver portabilidade integral, retenção ou compartilhamento de OPEN-29. [Registro](../09-qualidade/implementacao-SPEC-019.md).

SPEC-018, decisão confirmada pelo responsável em 2026-10-28: excluir imediatamente na base ativa, revogar sessões, preservar auditoria sem identificação e reaplicar exclusões antes de liberar restauração. OPEN-05/15/19/29 resolvidas apenas para esse contrato técnico; retenção legal/operacional e demais Specs não são resolvidas por extensão. [Registro](../09-qualidade/implementacao-SPEC-018.md).

SPEC-060, decisão confirmada pelo responsável em 2026-10-28: registrar somente usuário/módulo/ação/instante em tarefa de fundo; em falha, não repetir nem alterar o resultado do usuário; na exclusão, anonimizar eventos/auditoria; e não publicar edição operacional da trilha. OPEN-05/15/19/26 ficam resolvidas somente neste recorte técnico; retenção legal, fila/retry, notificações e dashboards administrativos continuam abertos. [Registro](../09-qualidade/implementacao-SPEC-060.md).

SPEC-011, decisão confirmada pelo responsável em 2026-10-28: primeiro administrador por e-mail em configuração local, efetivado somente após confirmação e sem administrador anterior; cadastro público não recebe papel e não há rota de promoção nesta unidade. A listagem usa paginação de até 100, busca textual, `status=active` e `profile=unassigned`, sem campos financeiros. OPEN-05/13/15 ficam resolvidas apenas para esse contrato técnico. [Registro](../09-qualidade/implementacao-SPEC-011.md).

SPEC-003, decisão confirmada pelo responsável em 2026-10-28: cinco respostas de 0 a 2 para conhecimento, reação a queda de 15%, horizonte, liquidez e volatilidade; soma 0–3 classifica conservador, 4–6 moderado e 7–10 arrojado. O perfil é privado, pode ser refeito e fornece apenas orientação textual ao simulador. OPEN-11/15 ficam resolvidas somente para este contrato técnico. [Registro](../09-qualidade/implementacao-SPEC-003.md).

SPEC-012, decisão confirmada pelo responsável em 2026-10-28: catálogo local inicial com PETR4 e VALE3, metadados DFP/ITR/FRE/IPE e links HTTPS oficiais da RAD/ENET; nenhum PDF é baixado ou armazenado. A disponibilidade do endereço é verificada manualmente sob demanda, limitada ao host oficial permitido. OPEN-10/15/27 ficam resolvidas somente para este contrato técnico; sincronização automática e expurgo seguem pendentes nas Specs próprias. [Registro](../09-qualidade/implementacao-SPEC-012.md).

SPEC-053, decisão confirmada pelo responsável em 2026-10-28: catálogo local de referência para PETR4 e VALE3, com receita líquida, lucro líquido e patrimônio líquido em Exercício 2025 e 2º trimestre de 2026, sempre em R$ mil. A fonte exibida é Dados Abertos CVM com diretório DFP/ITR, data de referência e sincronização; uma reapresentação fica auditável, mas somente a publicação mais recente é efetiva no gráfico e não há soma. OPEN-10/15/27 ficam resolvidas apenas para este contrato; sincronização externa e expurgo automático continuam em SPEC-054. [Registro](../09-qualidade/implementacao-SPEC-053.md).

SPEC-054, decisão confirmada pelo responsável em 2026-10-29: rotina interna diária às 03:00 de America/Sao_Paulo, com expurgo em `synced_at <= agora − 12 meses de calendário`. Ela remove somente metadados e indicadores públicos, grava contagens/instante/status sem conteúdo sensível e recompõe a fixture local em nova consulta; não realiza chamada CVM nem afeta dados pessoais. OPEN-04/05/15/27 ficam resolvidas somente para este contrato; agendador distribuído, integração externa e observabilidade operacional permanecem abertos. [Registro](../09-qualidade/implementacao-SPEC-054.md).

SPEC-023, decisão confirmada pelo responsável em 2026-10-29: catálogo local versionado de PETR4 e MXRF11, identificado como referência local e válido por no máximo 24 horas após `referenced_at`. A consulta não chama a B3 nem agregador; ticker inválido/desconhecido é identificável e referência vencida/indisponível devolve erro 503 com autorização explícita para valor/rentabilidade manual no consumidor. OPEN-10/15/19 ficam resolvidas somente para este contrato; fonte homologada, atualização automática e operação de dados de mercado continuam abertas. [Registro](../09-qualidade/implementacao-SPEC-023.md).

SPEC-028, decisão confirmada pelo responsável em 2026-10-29: consolidar apenas saldo de contas reais e faturas abertas, mais ativos/passivos manuais próprios com valor positivo e taxa anual opcional. Simulações nunca viram patrimônio, financiamentos aguardam SPEC-038 e não há snapshot histórico neste recorte. Mutações exigem sessão e e-mail confirmado; consulta e itens são isolados por titular. OPEN-15/19/21/28 ficam resolvidas somente para este contrato técnico. [Registro](../09-qualidade/implementacao-SPEC-028.md).

SPEC-034, decisão confirmada pelo responsável em 2026-10-29: score educativo de 0 a 100 com pesos persistidos 35/25/25/15 para gasto/renda, reserva líquida, dívida/fatura e metas. Faixas são crítico, atenção, saudável e excelente; reserva considera contas correntes/poupança/dinheiro; sem meta o fator é neutro e renda zero não gera nota. A consulta recalcula e mantém uma entrada mensal. OPEN-11/15/21 ficam resolvidas somente para este contrato. [Registro](../09-qualidade/implementacao-SPEC-034.md).

SPEC-039, decisão confirmada pelo responsável em 2026-10-29: central somente in-app, quatro tipos (`invoice_due`, `budget_goal_exceeded`, `watchlist_document`, `recurring_expense_due`), preferência global e individual por tipo, deduplicação por titular/tipo/chave opaca de origem, leitura apenas pelo titular e retenção mínima de 30 dias. O recorte não define antecedência automática, e-mail/push, fila/retry ou resumo mensal. OPEN-11/15/26 ficam resolvidas somente para este contrato técnico; os produtores e canais posteriores continuam condicionais. [Registro](../09-qualidade/implementacao-SPEC-039.md).

SPEC-025, decisão confirmada pelo responsável em 2026-10-29: calcular retorno diário simples no histórico local de preços, exigir ao menos três observações consecutivas, usar desvio padrão amostral e anualizar por √252; converter Selic anual local para taxa diária composta e anualizar o Sharpe. Volatilidade zero retorna status explícito e Sharpe nulo. Arrojado recebe acesso padrão; conservador e moderado podem optar e a preferência fica persistida. OPEN-03/10/15/20 ficam resolvidas somente para este contrato técnico; não há cotação em tempo real, recomendação ou garantia de retorno. [Registro](../09-qualidade/implementacao-SPEC-025.md).

SPEC-026, decisão confirmada pelo responsável em 2026-10-30: suportar BRL, USD e EUR; BRL tem paridade 1 e não aceita hipótese cambial, USD/EUR usam exclusivamente PTAX de venda do BCB armazenada como referência local de até 24 horas. Sem referência disponível/válida, a simulação falha; retorno do ativo e variação cambial anual informada pelo usuário são riscos separados. OPEN-03/10/15/23 ficam resolvidas somente para este contrato técnico. [Registro](../09-qualidade/implementacao-SPEC-026.md).

SPEC-027, decisão confirmada pelo responsável em 2026-10-30: watchlist pessoal limitada a 50 empresas do catálogo local; alerta apenas in-app para documento ativo novo, deduplicado por usuário/documento; reapresentados/substituídos não alertam e não há coleta CVM, e-mail ou push neste recorte. [Registro](../09-qualidade/implementacao-SPEC-027.md).

Registro central OPEN. Responsáveis e decisões são atribuídos pelo grupo; esta revisão não inventa aprovação. A lista preserva OPEN-01 da SPEC-001. Uma pendência impede implementar a parte que depende dela, não toda tarefa independente.

| ID | Decisão | Impacto | Estado |
|---|---|---|---|
| OPEN-01 | Expiração do JWT, refresh, revogação e logout | SPEC-001; RF-02 | Adotado tecnicamente em ADR-007; revisão formal pendente |
| OPEN-02 | Algoritmo/custo de hash, identidade de cliente para rate limit e janela/duração de bloqueio de login | SPEC-001; RNF-01, RNF-13 | Adotado tecnicamente em ADR-007; revisão formal pendente |
| OPEN-03 | Precisão interna, arredondamento monetário e tolerância de comparação numérica | SPEC-002; RB-10, RB-28 | Adotado tecnicamente em ADR-002 nesta implementação; revisão formal pendente; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-045 (centavo com o pagador), SPEC-046 a 048 |
| OPEN-04 | Comportamento/intervalo do agendador de cache e verificação da última publicação disponível | ADR-003; RF-23 | Aberto |
| OPEN-05 | Prazo de exclusão/exportação, retenção, anonimização e recuperação de backup sem reintroduzir dados excluídos | RF-05, RF-50, RB-19; RNF-02, RNF-14, RNF-18 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-040, 044, 049, 050 |
| OPEN-06 | Ambiente e perfil de carga para P95 < 3s; medição da disponibilidade mensal de 99,5% | RNF-04, RNF-08 | Parcial: perfil sequencial do motor definido/medido em SPEC-002; aplicação/disponibilidade pendentes |
| OPEN-07 | Produtos, tributação configurável/versionada, taxas e convenções de calendário para resultado líquido | RF-20, RF-63, RF-64; futura SPEC-004 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-046 a 048 (tabela interna versionada 2026-10) |
| OPEN-08 | Recorte final do MVP e ordem de web/mobile, administração e recursos opcionais | Visão; mapa de Specs | Parcial: web em ADR-007; MVP/mobile pendentes; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-052 (tour); mobile segue pendente |
| OPEN-09 | IDE/agente, camadas efetivamente ativas e evidência de teste da política | Governança de agentes | Aberto |
| OPEN-10 | Fontes externas, contratos, fonte de cotação, unidade/periodicidade e referências dos indicadores | RF-23, RF-24; RNF-09 | Aberto |
| OPEN-11 | Critérios de quiz, score, alertas, conquistas e amostra de benchmark | RF-03, RF-41, RF-66, RF-67 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-050, 051, 062 |
| OPEN-12 | Ciclo de cartão, pagamento de fatura, parcelas e tratamento de registro de financiamento | RF-13, RF-45 a RF-47 | Aberto |
| OPEN-13 | Política de promoção/criação inicial de administrador, se a promoção virar funcionalidade | RF-54; exige novo RF para promoção | Aberto |
| OPEN-14 | Pesquisa de alternativas existentes com fontes atuais | Benchmark do problema; RF-66 não substitui pesquisa | Parcial: benchmark em [docs/01-visao/benchmark.md](../01-visao/benchmark.md) (2026-10-18); validação do grupo com fontes atuais pendente |
| OPEN-15 | Detalhes de contrato ainda ausentes para consumidores; autenticação, confirmação de e-mail e motor têm contratos próprios. Preservar login de RF-02 e prefixo de ADR-001 | SPEC-001, SPEC-002, SPEC-013, SPEC-015 | Parcial: autenticação em ADR-007; motor em ADR-002; confirmação em ADR-008; HTTP dos consumidores pendente |
| OPEN-16 | Confirmar origem e aprovação da política de cadastro incorporada à RB-27, incluindo mínimo de 8 caracteres; definir equivalência/normalização de e-mail antes de impor unicidade sem distinção de caixa | RF-01, RB-27, SPEC-001; vínculo anterior à Spec não comprova aprovação humana | Adotado tecnicamente em ADR-007; revisão formal pendente |

Para resolver, registrar responsável, decisão, data e links para issue/PR reais, atualizar baseline e Spec afetadas no mesmo PR e pedir revisão. Aprovação não deve ser preenchida automaticamente.

## Implementação solicitada em 2026-10-15

O pedido do usuário nesta sessão autoriza implementar SPEC-001 e enviar à branch existente. ADR-007 registra escolhas técnicas adotadas para viabilizar essa entrega, sem afirmar aprovação formal do grupo ou reconstruir uma ata histórica ausente. Outros OPEN continuam em aberto; web responsiva não encerra o planejamento mobile/MVP.

## Pendências da integração

| ID | Decisão | Impacto | Estado |
|---|---|---|---|
| OPEN-17 | Selecionar provedor transacional, remetente/domínio, fila/outbox, configuração de entrega/retry e evidência operacional | RF-69, RF-70; SPEC-015, SPEC-016 | Aberto; SPEC-015 fornece adaptador HTTPS e falha segura, sem configuração de provedor; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-061 (despachante HTTPS configurável, sem provedor fixado); operação segue pendente |
| OPEN-18 | Adequar bloqueio por conta exigido pela main ao rate limit implementado; incluir testes e mitigação de abuso | RF-02, SPEC-001 | Solução técnica implementada nesta entrega: cinco falhas/15min, contagem por endereço normalizado, erro genérico e Retry-After; ver ADR-007 e registro de testes |

OPEN-01: a política técnica atual já usa access de 15min, refresh rotativo e sessão absoluta de 7 dias, com logout revogável. Não está mais tecnicamente indefinida; revisão formal histórica continua separada. OPEN-05 deve preservar prazos explícitos da baseline main; restauração não pode reintroduzir contas apagadas. Autorização desta sessão cobre integração e documentação, sem fingir aprovação histórica do grupo nem autorizar código adicional.

## Decisões identificadas ao detalhar o catálogo completo

O pedido atual autoriza gerar todas as Specs no lote. Não equivale a aprovação formal das regras ausentes nem das alterações de baseline. Para cada OPEN registrar decisão, responsável real, data e evidência antes de implementar o comportamento dependente.

| ID | Decisão necessária | Impacto | Estado |
|---|---|---|---|
| OPEN-19 | Conciliar inconsistências herdadas: RF-23/RNF-09 versus ADR-003 (cache vencido/referência), RF-35 versus RB-13 (simulado/real), RB-18 (valor/progresso), aliases de entidade, antigos UCs, prazo de token normativo versus proposta e retenção versus auditoria imutável | Specs consumidoras e baseline; registrar alteração aprovada, não escolher silenciosamente | Aberto |
| OPEN-20 | Comparações/métricas: base percentual, zero, moeda/prazo/tributação compatíveis; janela de retornos, desvio e anualização; critério de vantagem financeira | SPEC-010, SPEC-025, SPEC-037 | Aberto |
| OPEN-21 | Competência e histórico: recorrência/edição retroativa, geração mensal, saldo acumulado versus mensal, snapshots, intervalos, metas zero e escalas visuais | SPEC-006, SPEC-020 a SPEC-022, SPEC-024, SPEC-028 a SPEC-034, SPEC-040, SPEC-043, SPEC-049, SPEC-055 a SPEC-059 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-040, 049, 062 |
| OPEN-22 | Cálculos de expansão: sistema de amortização, encargos, confirmação/atualização de dívida; retirada na aposentadoria; regimes previdenciários e calendário tributário | SPEC-036 a SPEC-038, SPEC-046 a SPEC-048; sem fixar legislação/alíquotas nesta etapa | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-046 a 048 |
| OPEN-23 | Câmbio: moedas, PTAX compra/venda, data-base, fallback, projeção cambial e compatibilidade de períodos | SPEC-026 | Aberto |
| OPEN-24 | API pública: modelo de credencial própria, concessão/revogação/escopos, subconjunto de endpoints e rate limits de terceiros | SPEC-041 | Aberto |
| OPEN-25 | Webhooks: HMAC/canonicalização, segredo/rotação, URL permitida/SSRF, reenvios, duplicidade e registro de tentativas | SPEC-042 | Aberto |
| OPEN-26 | Eventos e notificações: gatilhos/antecedência, identidade/deduplicação/retry, falhas de coleta, política in-app/opt-out, canais externos, retenção e disparo mensal | SPEC-027, SPEC-039, SPEC-040, SPEC-042, SPEC-051, SPEC-060, SPEC-061 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-040, 051, 061 |
| OPEN-27 | CVM: contratos de cadastro/DFP/ITR/FRE/IPE, contas/unidades, reapresentações, identidade de documento, periodicidade de verificação de links e doze meses de calendário | SPEC-012, SPEC-027, SPEC-053, SPEC-054 | Aberto |
| OPEN-28 | Patrimônio: fechar a contradição entre investimento simulado/registrado em RF-35 e apenas patrimônio real em RB-13; origem de investimento real não modelada integralmente | SPEC-028 e consumidores; proibido considerar projeção um ativo entregue | Aberto |
| OPEN-29 | Portabilidade/exclusão/arquivos: alcance além de lançamentos, links temporários, expiração/retentativas, titularidade compartilhada e dados de auditoria/backups | SPEC-018, SPEC-019, SPEC-049; complementar OPEN-05 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-049 (download direto, sem link temporário) |
| OPEN-30 | Conteúdo/UI: acervo e revisão de PT/EN, termos sem verbete, fluxo inicial sem quiz, estado de tour e limites/formatos de entrada ainda sem contrato | SPEC-013, SPEC-035, SPEC-052; complementar OPEN-15 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-052 |
| OPEN-31 | Compartilhamento/mobile: convites e visibilidade após rompimento, conflitos de edição/arredondamento/acertos; política de sincronização offline e isolamento local | SPEC-044, SPEC-045, SPEC-006, SPEC-056 a SPEC-059; RNF-22/24 | Aberto; parcial: recorte aprovado pelo responsável em 2026-10-31 — SPEC-044, 045 |
| OPEN-32 | Verificação operacional transversal: ambiente de carga/disponibilidade, serviço de monitoramento, backup/restore, acesso a chaves e proteção de branch; não criar Spec isolada por RNF | RNF-08/12/14/16 aplicáveis nas entregas; complementar OPEN-06/09 | Aberto |
| OPEN-33 | Confirmar o recorte Must have antigo versus RF-68 a RF-74 e calendário; priorizar módulos opcionais sem confundir catálogo completo com promessa do semestre | Mapa completo; complementar OPEN-08 | Aberto |

Os números 5 falhas/15min, 24h/30min/60s, 12 meses CVM e 15 dias de exclusão já constam da baseline. Contradições sobre aprovação/semântica são OPEN-19; os valores não foram substituídos por novos padrões. Fluxos sem decisão não estão liberados por terem documento preenchido.


## Implementação da próxima unidade do mapa — 2026-10-23

O usuário solicitou aplicar a próxima Spec após SPEC-001: ordem 2, SPEC-002. A issue #13 e o ADR-002 registram escolhas técnicas de precisão/retorno/erros e perfil do motor para OPEN-03/06/15. Isso autoriza esta implementação, preservando o comportamento matemático de RB-10/RB-28; não assina decisões históricas do grupo. OPEN-06 permanece parcial para carga ponta a ponta e disponibilidade, e OPEN-15 não declara rotas de consumidores ainda ausentes.


## Implementação da SPEC-015 — 2026-10-23

O pedido do usuário para aplicar a próxima Spec do mapa autorizou a implementação técnica da confirmação de e-mail. O ADR-008 registra o contrato HTTP, digest/finalidade/expiração, consumo atômico e adaptador HTTPS. OPEN-17 não foi marcado como resolvido: escolher e operar o provedor, remetente/domínio, fila e retentativas exige evidência externa.

## Implementação da SPEC-017 — 2026-10-24

O usuário solicitou implementar a próxima unidade da ordem do mapa após SPEC-015: SPEC-017. O contrato técnico de listar e revogar sessões próprias foi registrado nesta Spec e no ADR-007, sem substituir decisões formais históricas ausentes. OPEN-15 permanece parcial para consumidores fora de autenticação; OPEN-32 continua para evidências operacionais.

## Implementação da SPEC-014 — 2026-10-24

O usuário solicitou continuar pela próxima unidade da ordem do mapa após SPEC-017: SPEC-014. O contrato técnico de perfil, e-mail pendente e preferências persistidas foi registrado na Spec e na implementação, sem alegar aprovação formal histórica. OPEN-17 continua para o provedor operacional de e-mail; OPEN-32 permanece para evidências operacionais.

## Implementação da SPEC-016 — 2026-10-25

O pedido do usuário autorizou a implementação técnica de recuperação e alteração de senha. O contrato usa token opaco com digest e TTL de 30 minutos, resposta pública genérica e revogação atômica das sessões. OPEN-17 continua aberto para selecionar e operar o provedor de entrega; a implementação não presume esse provedor.

## Implementação da SPEC-055 — 2026-10-25

O pedido do usuário autorizou a implementação técnica de categorias. O catálogo padrão é fixo e a ocultação é somente por titular; categorias pessoais recebem cor e unicidade por titular. OPEN-21 continua aberto para recorrência, edição retroativa, históricos e módulos consumidores ainda não implementados.

## Recortes aprovados em 2026-10-31

As políticas abaixo foram propostas pelo agente de codificação e aprovadas pelo responsável na sessão de 2026-10-31 para implementar as Specs restantes. Cada Spec registra a decisão na seção 13; as OPEN permanecem abertas para revisão e aceite formal do grupo.

- SPEC-044/045 (OPEN-31/03): convite genérico, um vínculo ativo, expiração em 7 dias, histórico somente leitura; divisão 50/50 ou percentual somando 100%, centavo com quem pagou, acerto limitado e idempotente.
- SPEC-046/047/048 (OPEN-07/22/03): retirada padrão de 4% a.a.; tabelas regressivas de previdência e renda fixa, progressiva por alíquota informada; ações 15% com isenção até R$ 20 mil/mês, FIIs e day trade 20%; DARF no último dia útil do mês seguinte (feriados nacionais fixos e Sexta-feira Santa).
- SPEC-049 (OPEN-05/21/29): resumo anual em JSON/CSV/PDF com aviso de não oficialidade; ano sem dados retorna 404.
- SPEC-050/051/052 (OPEN-05/08/11/26/30): grupo mínimo de 30; três conquistas cosméticas; tour de quatro etapas com roteiro por perfil.
- SPEC-061/040 (OPEN-17/26/05/21): canais opt-in com despachante HTTPS configurável; resumo mensal opt-in, um envio por mês, falha registrada.
- SPEC-062 (OPEN-11/21): perfis do quiz, contas sem perfil à parte, filtro por cadastro no fuso de São Paulo.
