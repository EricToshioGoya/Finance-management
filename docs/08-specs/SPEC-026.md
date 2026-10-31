# SPEC-026: Projetar investimento em moeda estrangeira

**Estado:** implementada tecnicamente em 2026-10-30; política de câmbio confirmada pelo responsável, com CI como evidência técnica.

## 1. Identificação

- **ID:** SPEC-026
- **Nome:** Projetar investimento em moeda estrangeira
- **Objetivo:** Obter PTAX por adaptador; validar moeda/período; projetar ativo; aplicar hipótese cambial distinta; mostrar valores e riscos separados.
- **Valor entregue:** projeção na moeda original e BRL com PTAX referenciada.

## 2. Rastreabilidade

- **Baseline:** [requisitos](../03-requisitos/requisitos.md); [visão](../01-visao/visao.md); [personas](../02-personas/personas.md).
- **RF:** RF-28.
- **RB:** RB-08, RB-10, RB-29.
- **RNF:** RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20.
- **Fluxo:** Fluxo de câmbio RF-28; [catálogo de casos](../04-casos-de-uso/casos-de-uso-usuario.md) e [administração](../04-casos-de-uso/casos-de-uso-administrador.md). IDs UC só são usados quando existentes; fluxo nomeado é rastreável ao RF.
- **Modelo:** Simulacao e referência cambial; [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-01, DA-02, DA-03, DA-07, DA-09; ADR-001, ADR-002, ADR-003; [arquitetura/ADRs](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** projetar investimento em moeda estrangeira; entradas, saídas e casos das seções 5/9/11. Cobertura exata dos critérios da baseline em [cobertura](cobertura-requisitos.md).

**Fora do escopo:** demais capacidades do [mapa](mapa-specs.md), implementação de módulos dependentes e decisões não estabelecidas. Não executar investimentos reais, integrar Open Finance ou gerar código nesta revisão.

Política confirmada: BRL, USD e EUR; USD/EUR usam PTAX de venda BCB no cache local datado, BRL usa paridade 1; não há fallback quando a referência estiver ausente/vencida. Variação cambial anual é hipótese explícita do usuário.

## 4. Dependências

[SPEC-002](SPEC-002.md), [SPEC-007](SPEC-007.md), [SPEC-015](SPEC-015.md). As dependências devem estar entregues para o fluxo que as consome; nenhum código é presumido pronto pela existência do arquivo.

Decisões bloqueantes: OPEN-03, OPEN-10, OPEN-15, OPEN-23. Dependência condicional é descrita no escopo; não pode criar ciclo com o consumidor.

## 5. Comportamento esperado

**Pré-condições:** fórmulas e parâmetros de cálculo aprovados; decisões bloqueantes resolvidas para o recorte.

**Fluxo principal:**

1. Obter PTAX por adaptador.
2. validar moeda/período.
3. projetar ativo.
4. aplicar hipótese cambial distinta.
5. mostrar valores e riscos separados.

**Alternativa observável:** Com cotação de teste 5 BRL/unidade, valor 100 e retornos zero, mostrar 100 na origem e 500 BRL, identificando taxa de teste.

**Exceções:** Moeda não suportada ou PTAX ausente não autoriza taxa inventada.

**Pós-condições:** projeção na moeda original e BRL com PTAX referenciada; preservação dos invariantes. Erro não produz confirmação de resultado inexistente.

### Cláusulas EARS

Cada cláusula local é referenciada na tabela de testes; funcionalidades opcionais só passam a integrar a entrega após seleção do recorte.

| Cláusula | Enunciado normativo | Origem / critério |
|---|---|---|
| SPEC-026-R01 | WHEN ocorrer o fluxo válido de projetar investimento em moeda estrangeira THE SYSTEM SHALL entregar projeção na moeda original e BRL com PTAX referenciada. | CA-001 |
| SPEC-026-R02 | IF ocorrer a condição de erro descrita na seção 5 THEN THE SYSTEM SHALL recusá-la preservando INV-001 e INV-002. | CA-002 |
| SPEC-026-R03 | WHEN o fluxo de projetar investimento em moeda estrangeira alcançar o comportamento de RF-28/C01 THE SYSTEM SHALL atender ao comportamento: permitir informar um valor em moeda estrangeira (ex.: USD, EUR — lista a definir) e converter para BRL usando a taxa de câmbio oficial. | CA-003 |
| SPEC-026-R04 | WHEN o fluxo de projetar investimento em moeda estrangeira alcançar o comportamento de RF-28/C02 THE SYSTEM SHALL atender ao comportamento: a taxa de câmbio deve ser obtida via API **PTAX do Banco Central do Brasil** (`olinda.bcb.gov.br/olinda/servico/PTAX`). | CA-004 |
| SPEC-026-R05 | WHEN o fluxo de projetar investimento em moeda estrangeira alcançar o comportamento de RF-28/C03 THE SYSTEM SHALL atender ao comportamento: permitir simular a evolução de um investimento em moeda estrangeira considerando tanto a rentabilidade do ativo quanto a variação cambial esperada (informada pelo usuário). | CA-005 |
| SPEC-026-R06 | WHEN o fluxo de projetar investimento em moeda estrangeira alcançar o comportamento de RF-28/C04 THE SYSTEM SHALL atender ao comportamento: deixar explícito que a variação cambial é uma fonte adicional de risco/retorno, distinta da rentabilidade do ativo em si. | CA-006 |
| SPEC-026-R07 | WHEN o fluxo de projetar investimento em moeda estrangeira alcançar o comportamento de RF-28/C05 THE SYSTEM SHALL atender ao comportamento: o resultado deve ser exibido tanto na moeda original quanto convertido para BRL. | CA-007 |

## 6. Regras e invariantes

- **INV-001:** Conversão não é compra de moeda nem operação real.
- **INV-002:** Identificadores e filtros não permitem ler/alterar dados de outro titular; compartilhamento limita-se ao aceite e escopo explícitos. Erro não confirma alteração parcial.
- **INV-003:** Decisões OPEN bloqueantes não são substituídas por valores, regras ou provedores inventados.

Regras herdadas: RB-08: Toda projeção de renda variável deve ser exibida como estimativa, sem garantia de retorno; RB-10: M = P × (1 + i)ⁿ + Σ aportes capitalizados; taxa convertida entre mês/ano por equivalência composta, nunca proporcional simples; RB-29: Lançamentos e simulações pessoais são acessíveis somente ao proprietário autenticado, salvo compartilhamento aceito e explicitamente autorizado. Toda validação ocorre no servidor. Reclassificações históricas para RF/RNF mantêm rastreabilidade, não criam nova regra de domínio.

## 7. Modelo de domínio envolvido

Simulacao e referência cambial. A Simulacao guarda parâmetros, hipóteses, prazo e resultado; o motor retorna valores derivados sem alterar saldo ou patrimônio. Entradas específicas estão na seção 9, fórmulas e calendários ausentes nas OPEN locais. Regras configuráveis devem ter versão identificável no resultado.

Não inventar tabelas, classes de estratégia ou colunas nesta etapa; aplicação e domínio mantêm a separação do modelo conceitual.

## 8. Impacto arquitetural

Capacidade: Projetar investimento em moeda estrangeira. Cliente web/mobile apresenta entradas, confirmação/erro e resultado; não decide permissão nem duplica cálculo. Aplicação valida acesso, coordena transações e chama domínio/adaptadores. Domínio preserva regras sem FastAPI/ORM/I/O (ADR-001/ADR-002). Infraestrutura executa persistência e integrações necessárias, respeitando o escopo.

Nenhuma integração externa adicional é escolhida nesta revisão; quando o fluxo consome taxa, e-mail ou notificação, usa o contrato da Spec provedora.

ADRs relacionados: ADR-001, ADR-002, ADR-003. Sessão vigente é ADR-007; proposta sem estado de ADR-005 é histórica. Persistência por capacidade inclui migration e verificações futuras, sem criação de banco nesta tarefa.

## 9. Contratos necessários

| Direção | Conteúdo conceitual |
|---|---|
| Entrada | valor/moeda, rentabilidade, câmbio esperado e prazo |
| Saída | projeção na moeda original e BRL com PTAX referenciada |
| Erro | Moeda não suportada ou PTAX ausente não autoriza taxa inventada. |

Identificadores, filtros e autorizações são verificados no servidor. Rotas, nomes JSON, limites, paginação e códigos não definidos dependem de OPEN-15; contratos externos dependem das OPEN locais. Prefixo HTTP futuro segue /api/v1 (ADR-001). Contratos de sessão existentes do ADR-007 não são alterados por esta Spec. A descrição acima não afirma endpoints publicados.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada e evidência exigida |
|---|---|
| RNF-04 (Performance) | Medir P95 < 3s no fluxo completo com perfil/ambiente aprovado em OPEN-06; registrar distribuição. |
| RNF-05 (Compatibilidade) | Exercitar mesmo contrato em web e cliente mobile; web responsiva sozinha não prova aplicativo Expo. |
| RNF-06 (Escalabilidade / extensibilidade) | Revisar dependências/camadas e extensão sem reescrever módulos existentes. |
| RNF-07 (Manutenibilidade) | Conferir resultados independentes e cobertura >=80% das regras financeiras exercidas. |
| RNF-09 (Atualidade de dados de mercado) | Relógio/fonte simulados: referência, coleta, dados ausentes e limites 24h/15min; fechar OPEN-19. |
| RNF-11 (Acessibilidade) | Validar teclado/toque, contraste e leitor de tela conforme WCAG 2.1 AA; alternativa textual para gráficos. |
| RNF-13 (Proteção da API) | Testar limite de 100 pedidos/minuto por endpoint sensível; distinguir bloqueio por conta e limite externo de OPEN-24. |
| RNF-15 (Documentação de API) | Comparar contratos aprovados e documentação OpenAPI da futura versão; não declarar rota nova existente. |
| RNF-16 (Qualidade contínua) | Executar testes/lint no PR e comprovar checks obrigatórios bloqueando falha; não presumir proteção remota. |
| RNF-17 (Versionamento de API) | Conferir prefixo /api/v1 nos contratos HTTP futuros e preservar compatibilidade aprovada. |
| RNF-20 (Internacionalização (i18n)) | Revisar textos/erros em PT/EN externalizados; fallback não pode ocultar ausência de tradução. |

RNFs são associados ao comportamento e verificados na implementação/operação; não se declara conformidade por preenchimento documental. Ver [plano](../09-qualidade/plano-qualidade.md) e OPEN-32 para ambiente e evidências.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** o recorte habilitado, dependências prontas e entradas de referência, **Quando** executar o fluxo principal, **Então** observar: Com cotação de teste 5 BRL/unidade, valor 100 e retornos zero, mostrar 100 na origem e 500 BRL, identificando taxa de teste.
- **CA-002** — **Dado** a condição inválida ou não autorizada, **Quando** tentar executar a operação, **Então** observar: Moeda não suportada ou PTAX ausente não autoriza taxa inventada.

- **CA-003** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-28/C01, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir informar um valor em moeda estrangeira (ex.: USD, EUR — lista a definir) e converter para BRL usando a taxa de câmbio oficial.

- **CA-004** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-28/C02, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: A taxa de câmbio deve ser obtida via API **PTAX do Banco Central do Brasil** (`olinda.bcb.gov.br/olinda/servico/PTAX`).

- **CA-005** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-28/C03, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve permitir simular a evolução de um investimento em moeda estrangeira considerando tanto a rentabilidade do ativo quanto a variação cambial esperada (informada pelo usuário).

- **CA-006** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-28/C04, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: Deve deixar explícito que a variação cambial é uma fonte adicional de risco/retorno, distinta da rentabilidade do ativo em si.

- **CA-007** — **Dado** fórmulas e parâmetros de cálculo aprovados, entradas válidas e política aprovada de RF-28/C05, **Quando** exercitar esse comportamento no fluxo desta Spec, **Então** verificar: O resultado deve ser exibido tanto na moeda original quanto convertido para BRL.

## 12. Casos de teste derivados

| Teste | Cláusula / critério / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | SPEC-026-R01; CA-001; INV-001, INV-002 | Fixture específica: Com cotação de teste 5 BRL/unidade, valor 100 e retornos zero, mostrar 100 na origem e 500 BRL, identificando taxa de teste. |
| T-002 | SPEC-026-R02; CA-002; INV-001, INV-002, INV-003 | Negativa: Moeda não suportada ou PTAX ausente não autoriza taxa inventada. Fechar política OPEN antes de testar resultado ainda indefinido. |
| T-003 | SPEC-026-R03; CA-003 | RF-28/C01: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir informar um valor em moeda estrangeira (ex.: USD, EUR — lista a definir) e converter para BRL usando a taxa de câmbio oficial. |
| T-004 | SPEC-026-R04; CA-004 | RF-28/C02: preparar entradas e limites da baseline, executar comportamento e conferir assertion: A taxa de câmbio deve ser obtida via API **PTAX do Banco Central do Brasil** (`olinda.bcb.gov.br/olinda/servico/PTAX`). |
| T-005 | SPEC-026-R05; CA-005 | RF-28/C03: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve permitir simular a evolução de um investimento em moeda estrangeira considerando tanto a rentabilidade do ativo quanto a variação cambial esperada (informada pelo usuário). |
| T-006 | SPEC-026-R06; CA-006 | RF-28/C04: preparar entradas e limites da baseline, executar comportamento e conferir assertion: Deve deixar explícito que a variação cambial é uma fonte adicional de risco/retorno, distinta da rentabilidade do ativo em si. |
| T-007 | SPEC-026-R07; CA-007 | RF-28/C05: preparar entradas e limites da baseline, executar comportamento e conferir assertion: O resultado deve ser exibido tanto na moeda original quanto convertido para BRL. |
| T-008 | INV-001, INV-002, INV-003; RNF-04, RNF-05, RNF-06, RNF-07, RNF-09, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20 | Executar métodos da seção 10, fronteiras, acesso cruzado/erros aplicáveis e inspeção de efeitos. Fixtures sintéticas, relógio injetado e dublês de fonte externa; evidência por requisito. |

Testes são planejados, não implementados ou executados nesta revisão. Os exemplos não fecham fórmulas, calendários ou regras ainda em OPEN. Cada teste futuro deve citar a cláusula desta Spec e o requisito correspondente.

## 13. Questões em Aberto

- OPEN-03 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-10 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-15 — decisão necessária: consultar definição e estado no registro central; bloqueia o comportamento desta unidade que dela dependa.
- OPEN-23 — decisão necessária: Câmbio: moedas, PTAX compra/venda, data-base, fallback, projeção cambial e compatibilidade de períodos / SPEC-026.

[Registro central](questoes-abertas.md). Antes de implementar, registrar decisão e refletir alterações de comportamento na baseline e nesta Spec; se não houver decisão, conservar o bloqueio explícito.

## 14. Definition of Done da Spec

- [ ] Mapa e recorte revisados pelo grupo, com evidência real.
- [ ] Decisões OPEN bloqueantes resolvidas e baseline conciliada antes de implementar a parte dependente.
- [ ] Esta versão revisada individualmente, sem aprovação histórica presumida.
- [x] Todas as cláusulas/CA implementadas e todos os INV preservados.
- [x] Testes de unidade/integração implementados; a evidência final está na CI do PR.
- [ ] RNFs verificados pelos métodos da seção 10, inclusive operação quando aplicável.
- [ ] Sem divergência conhecida entre código, Spec e baseline; corrigir implementação ou propor alteração para decisão humana.

Documento completo não significa capacidade pronta. A conclusão requer comportamento, verificação e revisão reais.
