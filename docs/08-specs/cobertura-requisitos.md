# Cobertura dos requisitos funcionais

Baseline: 74 RFs, preservados. Esta matriz cobre documentação; não afirma código entregue. Cnn significa o enésimo critério de aceite do RF na baseline, na ordem original. Cada linha aponta a unidade responsável, compartilhamentos e critérios locais. Referências a um RF em dependência não contam como cobertura integral.

| RF | Requisito | Spec responsável | Cobertura / critérios | Complementos |
|---|---|---|---|---|
| RF-01 | Cadastro de usuário | [SPEC-001](SPEC-001.md) | CA e T originais; cláusulas EARS de correspondência adicionadas.  | Sem sobreposição de implementação necessária |
| RF-02 | Login e autenticação | [SPEC-001](SPEC-001.md) | CA e T originais; cláusulas EARS de correspondência adicionadas.  | Sem sobreposição de implementação necessária |
| RF-03 | Quiz de perfil de investidor | [SPEC-003](SPEC-003.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-04 | Onboarding guiado | [SPEC-052](SPEC-052.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-05 | Exclusão de conta e dados (direito ao esquecimento) | [SPEC-018](SPEC-018.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-06 | Cadastro de receita recorrente mensal | [SPEC-056](SPEC-056.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-07 | Cadastro de receita pontual | [SPEC-057](SPEC-057.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-08 | Cadastro de bônus e PLR | [SPEC-058](SPEC-058.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-09 | Cadastro de despesas por categoria | [SPEC-059](SPEC-059.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-10 | Categorias padrão e personalizadas de gastos | [SPEC-055](SPEC-055.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-11 | Edição e exclusão de lançamentos | [SPEC-006](SPEC-006.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-12 | Cadastro de contas bancárias e cartões de crédito | [SPEC-005](SPEC-005.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-13 | Controle de fatura de cartão de crédito | [SPEC-020](SPEC-020.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-14 | Meta geral de renda e de gasto | [SPEC-021](SPEC-021.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-15 | Meta de gasto por categoria | [SPEC-021](SPEC-021.md) | C01 → CA-007/T-007; C02 → CA-008/T-008; C03 → CA-009/T-009 | Sem sobreposição de implementação necessária |
| RF-16 | Dashboard: gastos por categoria (pizza) | [SPEC-022](SPEC-022.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-17 | Dashboard: evolução de saldo (linha) | [SPEC-022](SPEC-022.md) | C01 → CA-007/T-007; C02 → CA-008/T-008; C03 → CA-009/T-009 | Sem sobreposição de implementação necessária |
| RF-18 | Dashboard: comparativo renda vs. gasto mensal (barras) | [SPEC-022](SPEC-022.md) | C01 → CA-010/T-010; C02 → CA-011/T-011; C03 → CA-012/T-012; C04 → CA-013/T-013 | Sem sobreposição de implementação necessária |
| RF-19 | Dashboard: progresso de metas | [SPEC-021](SPEC-021.md) | C01 → CA-010/T-010; C02 → CA-011/T-011; C03 → CA-012/T-012; C04 → CA-013/T-013 | Sem sobreposição de implementação necessária |
| RF-20 | Simulação de investimento em renda fixa | [SPEC-008](SPEC-008.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | SPEC-004: imposto/líquido; SPEC-002: bruto; SPEC-007: taxa. SPEC-008 integra todos os critérios |
| RF-21 | Simulação de investimento em renda variável | [SPEC-009](SPEC-009.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-22 | Calculadora de juros compostos (motor genérico) | [SPEC-013](SPEC-013.md) | C01/C04/C05/C07/C09/C13: SPEC-002; demais critérios: SPEC-013. Conversões/limites também testados na integração. | SPEC-002 e SPEC-013; gráfico/tabela e contrato não entregues pelo motor isolado |
| RF-23 | Integração com indicadores oficiais (Selic, CDI, IPCA, Tesouro Direto) | [SPEC-007](SPEC-007.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007; C06 → CA-008/T-008 | Sem sobreposição de implementação necessária |
| RF-24 | Cotação de ações e FIIs via fonte de mercado | [SPEC-023](SPEC-023.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-25 | Comparador de cenários de investimento | [SPEC-010](SPEC-010.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-26 | Projeção de objetivo financeiro | [SPEC-024](SPEC-024.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-27 | Métricas de risco e retorno (volatilidade, Sharpe simplificado) | [SPEC-025](SPEC-025.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-28 | Simulação em moeda estrangeira (câmbio) | [SPEC-026](SPEC-026.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-29 | Busca de empresa | [SPEC-012](SPEC-012.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-30 | Listagem de documentos oficiais (metadados) | [SPEC-012](SPEC-012.md) | C01 → CA-006/T-006; C02 → CA-007/T-007; C03 → CA-008/T-008; C04 → CA-009/T-009 | Sem sobreposição de implementação necessária |
| RF-31 | Acesso ao documento completo via link externo | [SPEC-012](SPEC-012.md) | C01 → CA-010/T-010; C02 → CA-011/T-011; C03 → CA-012/T-012; C04 → CA-013/T-013 | Sem sobreposição de implementação necessária |
| RF-32 | Indicadores financeiros extraídos de dados abertos da CVM | [SPEC-053](SPEC-053.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-33 | Retenção e expurgo automático dos dados sincronizados | [SPEC-054](SPEC-054.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-34 | Watchlist de empresas | [SPEC-027](SPEC-027.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-35 | Consolidação de patrimônio (ativos e passivos) | [SPEC-028](SPEC-028.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-36 | Evolução do patrimônio líquido | [SPEC-029](SPEC-029.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-37 | Mapa de calor patrimonial (ativos e passivos por cor) | [SPEC-030](SPEC-030.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007; C06 → CA-008/T-008; C07 → CA-009/T-009 | Sem sobreposição de implementação necessária |
| RF-38 | Alocação da carteira por classe de ativo | [SPEC-031](SPEC-031.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-39 | Simulador de cenários "E se..." (stress financeiro) | [SPEC-032](SPEC-032.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-40 | Metas nomeadas (objetivos financeiros) | [SPEC-033](SPEC-033.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-41 | Cálculo do score de saúde financeira | [SPEC-034](SPEC-034.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-42 | Exibição e histórico do score | [SPEC-034](SPEC-034.md) | C01 → CA-007/T-007; C02 → CA-008/T-008; C03 → CA-009/T-009 | Sem sobreposição de implementação necessária |
| RF-43 | Central de conteúdo educacional | [SPEC-035](SPEC-035.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-44 | Ajuda contextual (tooltips educativos) | [SPEC-035](SPEC-035.md) | C01 → CA-006/T-006; C02 → CA-007/T-007 | SPEC-013 ajuda da taxa; SPEC-035 fonte única de conteúdo e tooltips gerais |
| RF-45 | Simulação de compra financiada | [SPEC-036](SPEC-036.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-46 | Comparador: financiar vs. investir e comprar depois | [SPEC-037](SPEC-037.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-47 | Registro do financiamento como passivo | [SPEC-038](SPEC-038.md) | C01 → CA-003/T-003; C02 → CA-004/T-004 | Sem sobreposição de implementação necessária |
| RF-48 | Notificações e alertas | [SPEC-039](SPEC-039.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-49 | Canal de envio | [SPEC-061](SPEC-061.md) | C01 → CA-003/T-003; C02 → CA-004/T-004 | Sem sobreposição de implementação necessária |
| RF-50 | Exportação de dados pessoais | [SPEC-019](SPEC-019.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-51 | Relatório mensal automático | [SPEC-040](SPEC-040.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-52 | API pública documentada | [SPEC-041](SPEC-041.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-53 | Webhooks para eventos do usuário | [SPEC-042](SPEC-042.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-54 | Controle de acesso administrativo | [SPEC-011](SPEC-011.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006; C05 → CA-007/T-007 | Sem sobreposição de implementação necessária |
| RF-55 | Listagem e busca de usuários | [SPEC-011](SPEC-011.md) | C01 → CA-008/T-008; C02 → CA-009/T-009; C03 → CA-010/T-010; C04 → CA-011/T-011 | Sem sobreposição de implementação necessária |
| RF-56 | Dashboard: distribuição de perfil de investidor | [SPEC-062](SPEC-062.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-57 | Dashboard: uso por módulo/aba | [SPEC-043](SPEC-043.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-58 | Dashboard: usuários mais recorrentes (engajamento) | [SPEC-043](SPEC-043.md) | C01 → CA-006/T-006; C02 → CA-007/T-007; C03 → CA-008/T-008 | Sem sobreposição de implementação necessária |
| RF-59 | Registro de eventos de uso (base para os dashboards) | [SPEC-060](SPEC-060.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-60 | Vínculo de conta compartilhada entre dois usuários | [SPEC-044](SPEC-044.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-61 | Divisão de despesas compartilhadas | [SPEC-045](SPEC-045.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-62 | Simulação de aposentadoria | [SPEC-046](SPEC-046.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-63 | Comparador de modalidades de previdência (PGBL x VGBL x carteira própria) | [SPEC-047](SPEC-047.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-64 | Estimativa de IR devido sobre operações simuladas | [SPEC-048](SPEC-048.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | SPEC-004 só tributação consumida em renda fixa; SPEC-048 inclui ações/FIIs/day trade e lembrete DARF |
| RF-65 | Exportação de informe de rendimentos consolidado | [SPEC-049](SPEC-049.md) | C01 → CA-003/T-003; C02 → CA-004/T-004 | Sem sobreposição de implementação necessária |
| RF-66 | Benchmark anônimo com usuários do mesmo perfil | [SPEC-050](SPEC-050.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005 | Sem sobreposição de implementação necessária |
| RF-67 | Badges/conquistas por metas atingidas | [SPEC-051](SPEC-051.md) | C01 → CA-003/T-003; C02 → CA-004/T-004; C03 → CA-005/T-005; C04 → CA-006/T-006 | Sem sobreposição de implementação necessária |
| RF-68 | Editar dados do perfil | [SPEC-014](SPEC-014.md) | C01 → CA-003/T-003 | Sem sobreposição de implementação necessária |
| RF-69 | Confirmar titularidade do e-mail | [SPEC-015](SPEC-015.md) | C01 → CA-003/T-003 | Sem sobreposição de implementação necessária |
| RF-70 | Recuperar senha esquecida | [SPEC-016](SPEC-016.md) | C01 → CA-003/T-003 | Sem sobreposição de implementação necessária |
| RF-71 | Alterar senha autenticado | [SPEC-016](SPEC-016.md) | C01 → CA-004/T-004 | Sem sobreposição de implementação necessária |
| RF-72 | Configurar preferências do usuário | [SPEC-014](SPEC-014.md) | C01 → CA-004/T-004 | Sem sobreposição de implementação necessária |
| RF-73 | Consultar e encerrar sessões | [SPEC-017](SPEC-017.md) | C01 → CA-003/T-003 | Sem sobreposição de implementação necessária |
| RF-74 | Renovar sessão e realizar logout | [SPEC-017](SPEC-017.md) | C01 → CA-004/T-004 | Operações atuais em SPEC-001/ADR-007; gestão ampliada em SPEC-017; não reimplementar contrato |

## Critérios de fronteira e lacunas

Todos os RFs têm Spec responsável; cobertura documental completa não elimina OPEN. A baseline é preservada com inconsistências explicitadas no registro OPEN-19/28. Não foram fabricadas fórmulas, tabelas fiscais, provedores ou modelos físicos. O recorte da disciplina versus catálogo total deve ser confirmado em OPEN-08/33. Futuras mudanças de critérios exigem atualizar esta matriz, mapa e Spec afetada no mesmo commit.
