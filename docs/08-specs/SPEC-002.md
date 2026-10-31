# SPEC-002: Motor de Cálculo de Juros Compostos e Equivalência de Taxas

**Estado:** implementação autorizada pelo pedido explícito do usuário para aplicar a próxima Spec do mapa em 2026-10-23, após SPEC-001. Motor implementado; ver [registro de execução](../09-qualidade/implementacao-SPEC-002.md). Política técnica de OPEN-03/15 e perfil parcial de OPEN-06 registrados em ADR-002. Aprovação formal do mapa/grupo permanece separada.

## 1. Identificação

- **ID:** SPEC-002
- **Nome:** Motor de Cálculo de Juros Compostos e Equivalência de Taxas
- **Objetivo:** calcular montante bruto, juros e evolução com aportes mensais no fim do período e taxas equivalentes.
- **Valor entregue:** fornecer cálculo verificável e reutilizável para as simulações, sem duplicar regras financeiras.

## 2. Rastreabilidade

- **RF:** RF-22, cobertura parcial do núcleo matemático; RF-20 é consumidor futuro. Veja [requisitos](../03-requisitos/requisitos.md).
- **RB:** RB-10 (equivalência e juros compostos), RB-28 (parâmetros não negativos).
- **RNF:** RNF-04, RNF-07 e RNF-16, verificação na seção 10.
- **Fluxos:** [UC-08](../04-casos-de-uso/UC-08-calcular-juros-compostos.md); UC-09 como consumidor futuro.
- **Domínio:** ResultadoCalculo; MotorJurosCompostos como serviço puro no [modelo](../05-modelo-de-dominio/modelo-de-dominio.md). Simulacao não é o motor.
- **Arquitetura:** DA-02 e ADR-002, em [arquitetura](../07-arquitetura/arquitetura.md).

## 3. Escopo

**Incluído:** juros compostos; aportes no fim do mês; conversão anual → mensal e mensal → anual por equivalência; anos → meses para execução; equivalência de períodos meses/anos inteiros; série mensal e resumo bruto; validação de parâmetros e resultados determinísticos.

**Fora do escopo:** interface, seletores, ajuda contextual, apresentação de gráfico/tabela e integração da origem da taxa (SPEC-013 planejada no mapa); obtenção de indicador oficial (SPEC-007); tributação (SPEC-004); persistência, sessão e integração de produto (SPEC-008/SPEC-009). A série retornada fornece dados para tabela e gráfico, mas não implementa a interface de RF-22.

## 4. Dependências

Não depende de login nem de outra Spec funcional: é a unidade técnica habilitadora justificada pelo ADR-002. Política numérica e contrato de domínio adotados tecnicamente em ADR-002 no atendimento ao pedido atual (OPEN-03/15). OPEN-06 tem perfil sequencial definido para o motor; carga ponta a ponta/disponibilidade continuam abertas. A autorização de implementação não é tratada como aprovação formal do mapa/grupo. Consumidores dependem do motor, não o contrário.

## 5. Comportamento esperado

**Pré-condições:** política numérica de ADR-002; entrada informa valor inicial, aporte mensal, percentual da taxa e sua periodicidade, prazo inteiro positivo e sua unidade. Não há dependência de sessão.

**Fluxo principal:**

1. Validar valores monetários e taxa não negativos, números finitos, prazo inteiro positivo e unidades reconhecidas.
2. Converter percentual em fração: entrada 12 significa 12%, fração 0,12.
3. Normalizar taxa para mês por $i_m=(1+i_a)^{1/12}-1$ quando anual. Conversão inversa usa $i_a=(1+i_m)^{12}-1$.
4. Normalizar anos para meses por $n=anos\times12$; entradas de 1 ano e 12 meses são equivalentes. Não aceitar prazo fracionário para representar meses em anos.
5. Para cada mês, calcular juros sobre saldo anterior e só depois adicionar o aporte: $J_k=S_{k-1}i_m$; $S_k=S_{k-1}+J_k+A$.
6. Retornar série mensal e resumo: total investido = inicial + soma dos aportes; juros = montante − total investido, conforme precisão aprovada.

**Alternativas:** taxa zero produz juros zero; inicial/aporte zero são válidos. **Exceções:** parâmetros inválidos produzem erro conceitual sem resultado, persistência ou efeito externo; `ErroCalculo` expõe campo/código conforme ADR-002, sem valor informado. Limites de capacidade Decimal geram limite_numerico, sem resultado parcial.

**Pós-condições:** resultado bruto e série coerentes, sem alteração de saldo/patrimônio e sem acesso externo. Mesmas entradas e mesma política numérica produzem o mesmo resultado.

### Cláusulas EARS rastreáveis desta revisão

| Cláusula | Comportamento normativo | Critério | Teste planejado |
|---|---|---|---|
| SPEC-002-R01 | WHEN calcular sob a condição de inicial R$ 1.000,00, aporte zero, taxa anual 12% e 12 meses THE SYSTEM SHALL obter montante exibível R$ 1.120,00 e taxa mensal aproximadamente 0,9488792935%, usando tolerância de OPEN-03. | CA-001 | T-R01 |
| SPEC-002-R02 | WHEN calcular sob a condição de inicial zero, aporte R$ 100,00, taxa mensal 1% e 2 meses THE SYSTEM SHALL obter R$ 100,00 no mês 1 e R$ 201,00 no mês 2. | CA-002 | T-R02 |
| SPEC-002-R03 | WHEN calcular sob a condição de inicial R$ 100,00, aporte R$ 10,00, taxa zero e 2 meses THE SYSTEM SHALL obter investido e montante R$ 120,00 e juros zero; com inicial/aporte zero, obter resultado zero. | CA-003 | T-R03 |
| SPEC-002-R04 | WHEN validar sob a condição de valor/taxa negativo, número não finito, unidade inválida ou prazo zero/fracionário THE SYSTEM SHALL rejeitar sem resultado nem efeito externo. | CA-004 | T-R04 |
| SPEC-002-R05 | WHEN calcular sob a condição de entradas equivalentes de 1 ano e 12 meses THE SYSTEM SHALL obter a mesma série/resumo segundo OPEN-03. | CA-005 | T-R05 |
| SPEC-002-R06 | WHEN converter para anual sob a condição de taxa mensal de 1% THE SYSTEM SHALL obter aproximadamente 12,6825030132%; ao converter de volta, obter 1% dentro da tolerância aprovada, nunca 12% anual por proporção simples. | CA-006 | T-R06 |
| SPEC-002-R07 | WHEN conferir série e resumo sob a condição de cálculo válido THE SYSTEM SHALL haver um registro por mês, aportes ao fim do período e identidades de INV-004 satisfeitas. | CA-007 | T-R07 |
| SPEC-002-R08 | WHEN repetir o cálculo sob a condição de mesmas entradas e política THE SYSTEM SHALL obter resultado idêntico sem banco, rede, relógio, sessão ou alteração de dados reais. | CA-008 | T-R08 |

## 6. Regras e invariantes

- **INV-001:** conversão de taxa usa equivalência composta, nunca divisão/multiplicação proporcional simples.
- **INV-002:** moeda usa Decimal, conforme ADR-002; não utiliza float binário. Potências/raízes usam contexto próprio de 50 dígitos, conforme ADR-002/OPEN-03. O arredondamento a centavos HALF_UP é somente de consumo, sem recapitalização.
- **INV-003:** cada aporte entra depois dos juros do mês, nunca rende no próprio mês de entrada.
- **INV-004:** total investido, juros, montante e série obedecem às identidades da seção 5 dentro da política numérica aprovada.
- **INV-005:** motor não acessa banco, HTTP, relógio ou sessão, não altera dados reais e é determinístico.
- **INV-006:** entrada inválida não produz resultado nem efeitos externos.

## 7. Modelo de domínio envolvido

MotorJurosCompostos recebe parâmetros de cálculo e produz ResultadoCalculo, objeto de valor com resumo (investido, juros e montante) e série mensal (saldo inicial, aporte, juros e saldo final). Valores monetários não negativos e prazo inteiro positivo seguem RB-28. A série tem um registro por mês executado. Simulacao é registro da aplicação consumidora, não uma entidade criada pelo motor. Não há relacionamento persistente ou modelo físico definido aqui; contrato de objetos imutáveis implementado em ADR-002 para OPEN-15.

## 8. Impacto arquitetural

ADR-002 exige motor no domínio puro, sem ORM, FastAPI ou biblioteca externa. Aplicação converte contratos de transporte em parâmetros e encaminha resultado; infraestrutura cuida de indicador/persistência fora do motor. Clientes web/mobile exibem os resultados por contratos de aplicação e não duplicam a regra. Esta Spec não cria endpoint, interface ou integração externa. DA-02 justifica a unidade técnica, em vez de uma Spec genérica de backend.

## 9. Contratos necessários

**Entradas implementadas:** `MotorJurosCompostos.calcular` recebe argumentos nomeados `valor_inicial`, `aporte_mensal`, `taxa_percentual` em Decimal, `periodicidade_taxa` mensal/anual, `prazo` int positivo e `unidade_prazo` meses/anos. String/float/bool não viram Decimal implicitamente. `converter_taxa(taxa_percentual, origem, destino)` devolve percentual, preservando a unidade de entrada/saída (1 significa 1%).

**Saídas implementadas:** `ResultadoCalculo` imutável com `prazo_meses`, `taxa_mensal_percentual`, `total_investido`, `total_juros`, `montante` e `serie` tuple de `ResultadoMensal` (mes, saldo_inicial, aporte, juros, saldo_final). Valores financeiros são Decimal internos, não arredondados a centavos. `arredondar_moeda` aplica a política de consumo em centavos.

**Erros conceituais:** valor negativo, número não finito, prazo não inteiro/não positivo ou unidade inválida. Decisão técnica em ADR-002: `ErroCalculo(ValueError)` expõe campo/código sem valor informado. Códigos: decimal_obrigatorio, numero_nao_finito, valor_negativo, prazo_invalido, unidade_invalida e limite_numerico. OPEN-03 usa 50 dígitos, HALF_UP e tolerância de máximo(1e-40 absoluto, 1e-40 relativo) para referências internas; taxas aproximadas citadas nos exemplos usam 1e-10 ponto percentual. Não arredondar mês a mês. Não há contrato HTTP ou persistência nesta entrega.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada | Evidência exigida |
|---|---|---|
| RNF-04 | Medir duração do motor com prazos/volumes no perfil aprovado em OPEN-06; medir também requisição completa na Spec consumidora | Distribuição de tempos e P95; P95 do motor não comprova sozinho P95 da aplicação < 3s |
| RNF-07 | Testes numéricos de referência, limites e erros; medir cobertura de linhas >= 80% no código de regras financeiras; inspecionar isolamento do domínio | Relatório de testes/cobertura e revisão de dependências |
| RNF-16 | Executar testes e lint no PR e verificar bloqueio de merge com check obrigatório falhando | Evidência de CI e proteção configurada, sem presumir que o workflow documental já cobre testes de aplicação |

QT-04, QT-07 e QT-10 do [plano de qualidade](../09-qualidade/plano-qualidade.md) complementam esta verificação. Evidências executadas constam no [registro de implementação](../09-qualidade/implementacao-SPEC-002.md). O perfil do motor não fecha RNF-04 da aplicação nem configura proteção de branch.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** inicial R$ 1.000,00, aporte zero, taxa anual 12% e 12 meses, **Quando** calcular, **Então** obter montante exibível R$ 1.120,00 e taxa mensal aproximadamente 0,9488792935%, usando tolerância de OPEN-03.
- **CA-002** — **Dado** inicial zero, aporte R$ 100,00, taxa mensal 1% e 2 meses, **Quando** calcular, **Então** obter R$ 100,00 no mês 1 e R$ 201,00 no mês 2.
- **CA-003** — **Dado** inicial R$ 100,00, aporte R$ 10,00, taxa zero e 2 meses, **Quando** calcular, **Então** obter investido e montante R$ 120,00 e juros zero; com inicial/aporte zero, obter resultado zero.
- **CA-004** — **Dado** valor/taxa negativo, número não finito, unidade inválida ou prazo zero/fracionário, **Quando** validar, **Então** rejeitar sem resultado nem efeito externo.
- **CA-005** — **Dado** entradas equivalentes de 1 ano e 12 meses, **Quando** calcular, **Então** obter a mesma série/resumo segundo OPEN-03.
- **CA-006** — **Dado** taxa mensal de 1%, **Quando** converter para anual, **Então** obter aproximadamente 12,6825030132%; ao converter de volta, obter 1% dentro da tolerância aprovada, nunca 12% anual por proporção simples.
- **CA-007** — **Dado** cálculo válido, **Quando** conferir série e resumo, **Então** haver um registro por mês, aportes ao fim do período e identidades de INV-004 satisfeitas.
- **CA-008** — **Dado** mesmas entradas e política, **Quando** repetir o cálculo, **Então** obter resultado idêntico sem banco, rede, relógio, sessão ou alteração de dados reais.

## 12. Casos de teste derivados

| Teste | Critérios / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | CA-001; INV-001, INV-002 | Referência anual de 12% e política Decimal aprovada |
| T-002 | CA-002, CA-007; INV-003, INV-004 | Conferir cada mês e totais com aportes ao fim |
| T-003 | CA-003; INV-004 | Taxa zero; inicial/aporte ambos zero; ausência de aporte |
| T-004 | CA-004; INV-006 | Cada valor negativo; não finitos; unidade inválida; prazo zero, negativo e fracionário |
| T-005 | CA-005, CA-006; INV-001, INV-002 | Meses/anos; taxas nos dois sentidos; ida e volta com tolerância |
| T-006 | CA-007; INV-004 | Conferir série, total investido, juros e montante contra cálculo independente |
| T-007 | CA-008; INV-005 | Repetibilidade e inspeção de isolamento de dependências/efeitos externos |
| T-008 | RNF-04, RNF-07, RNF-16 | Perfil de desempenho após OPEN-06, cobertura, revisão de camadas, CI de testes/lint e bloqueio de merge |

Testes executáveis em `backend/tests/unit/test_spec002.py`, nomeados por SPEC-002-R01 a R08. Rastreabilidade e resultados no registro de execução.

| T-R01 | SPEC-002-R01; CA-001 | Executar cenário de CA-001 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R02 | SPEC-002-R02; CA-002 | Executar cenário de CA-002 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R03 | SPEC-002-R03; CA-003 | Executar cenário de CA-003 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R04 | SPEC-002-R04; CA-004 | Executar cenário de CA-004 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R05 | SPEC-002-R05; CA-005 | Executar cenário de CA-005 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R06 | SPEC-002-R06; CA-006 | Executar cenário de CA-006 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R07 | SPEC-002-R07; CA-007 | Executar cenário de CA-007 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R08 | SPEC-002-R08; CA-008 | Executar cenário de CA-008 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |

## 13. Questões em Aberto

- OPEN-03 — decisão técnica adotada em ADR-002: 50 dígitos, contexto próprio, centavos HALF_UP somente no consumo e tolerâncias explícitas; revisão formal do grupo não é presumida.
- OPEN-06 — perfil sequencial do motor em ADR-002 e script reproduzível com registro de ambiente; carga ponta a ponta e disponibilidade continuam abertas.
- OPEN-15 — contrato de domínio implementado em ADR-002; não há contrato HTTP nesta entrega. Integração de consumidores continua nas Specs correspondentes.

Consultar [registro central](questoes-abertas.md). RF-22 só estará totalmente entregue com a integração e interface da SPEC-013; aprovar o motor não equivale a aprovar RF-22 inteiro.

## 14. Definition of Done da Spec

- [ ] Mapa revisado e aprovado pelo grupo, com responsável, data e evidência reais.
- [ ] Questões OPEN que afetam esta entrega resolvidas e refletidas na baseline antes da aprovação desta Spec.
- [ ] Spec revisada e aprovada individualmente, após o mapa.
- [x] Todos os critérios funcionais do motor implementados, com invariantes cobertos pelos testes; ver registro de execução.
- [x] Suíte automatizada do motor e regressão executadas e aprovadas; evidência por commit/CI no registro. Verificação operacional de RNF-04/RNF-16 permanece separada.
- [ ] Todos os RNFs aplicáveis verificados pelos métodos da seção 10.
- [ ] Nenhuma divergência conhecida entre implementação e Spec; divergências da baseline explicitamente analisadas.

A implementação funcional e seus testes são registrados separadamente das aprovações humanas e das verificações operacionais ainda pendentes. Se surgir conflito, registrar a divergência e corrigir a implementação para respeitar a baseline ou propor alteração da baseline para aprovação humana. Não alterar comportamento silenciosamente.

### Revisão documental do lote

Revisão em 2026-10-22 autorizada para documentação. Mantidos conteúdo original, IDs CA/INV/T e limites de implementação; adicionada rastreabilidade por cláusulas. Esta revisão não executa código nem substitui aprovação individual do grupo. [Cobertura completa](cobertura-requisitos.md).
