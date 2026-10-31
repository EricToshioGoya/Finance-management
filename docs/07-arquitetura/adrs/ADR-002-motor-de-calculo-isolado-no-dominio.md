# ADR-002: Motor de Cálculo Financeiro e Juros Compostos no Domínio Puro

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova

## Contexto e Problema
As simulações de investimento (RF-20, RF-21, RF-22) exigem cálculos de juros compostos com conversão de equivalência de taxas (mês/ano) e alíquotas tributárias de IR. Erros nesses cálculos destroem a confiabilidade da plataforma. O requisito RNF-07 exige cobertura mínima de 80% de testes automatizados nas regras financeiras.

## Decisão Considerada
Isolar toda a lógica de cálculo financeiro em classes de **Domínio Puro** (sem dependências de SQLAlchemy, FastAPI ou qualquer lib externa).

* O motor recebe entradas primitivas (`Decimal`, `int`) e retorna objetos de valor/DTOs puros de domínio.
* Todas as conversões temporais usam taxa equivalente composta: $i_{mensal} = (1 + i_{anual})^{1/12} - 1$, conforme RB-10.

## Alternativas Consideradas
* **Cálculo via procedimentos armazenados (Triggers/Stored Procedures no PostgreSQL):** Descartado pois dificulta testes unitários ágeis no CI/CD e acopla a regra de negócio ao SGBD.
* **Cálculo no Frontend (React/React Native):** Descartado pois duplicaria a lógica em duas plataformas e impediria o uso consistente via API pública ou relatórios automáticos no backend.

## Consequências
### Positivas:
* Testabilidade extrema: os testes com `pytest` rodam em milissegundos sem precisar subir banco de dados ou mockar requisições HTTP.
* Facilita verificar a correção com testes de referência. RNF-07 e RNF-04 (P95 < 3s) são critérios a medir, não garantias produzidas pela arquitetura.

### Negativas:
* Exige mapeamento manual ou via adaptadores entre as entidades do ORM e os objetos de valor do motor de cálculo.


## Esclarecimento de 2026-10-09

O motor puro de SPEC-002 cobre valor bruto, não integração oficial nem tributação completa de RF-20. Decimal evita representar moeda em float binário, mas raízes e potências fracionárias ainda requerem precisão e arredondamento definidos em OPEN-03. Testes devem medir correção, não apenas cobertura.


## Política técnica da implementação SPEC-002 — 2026-10-23

Pedido explícito do usuário para aplicar a próxima Spec do mapa, após SPEC-001. Issue [#13](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/issues/13). As escolhas abaixo viabilizam a implementação, sem atribuir aprovação formal ao grupo.

- **OPEN-03:** contexto Decimal próprio, 50 algarismos significativos, ROUND_HALF_UP, Emin=-999999 e Emax=999999. Não herdar precisão, arredondamento, flags ou traps do chamador nem alterar seu contexto. Não arredondar juros/saldos a centavos a cada mês; manter precisão interna. `arredondar_moeda` quantiza a 0,01 somente na apresentação/consumo. Valores Decimal não finitos são rejeitados antes da aritmética; float, string e bool não são convertidos silenciosamente. Parâmetros fora da capacidade técnica Decimal geram erro de limite numérico, sem resultado parcial. Tolerância interna de referência: máximo entre 1e-40 absoluto e 1e-40 relativo ao valor esperado; exemplos de taxas aproximadas da Spec usam tolerância de 1e-10 ponto percentual. Valores exibíveis usam centavos por HALF_UP. O arredondamento de cada linha exibida pode criar diferenças de centavos na soma visual; consumidores devem reconciliar a partir dos valores internos, sem recapitalizar valores exibidos.
- **OPEN-15 (domínio):** `MotorJurosCompostos.calcular`, com argumentos nomeados `valor_inicial`, `aporte_mensal`, `taxa_percentual`, `periodicidade_taxa` (mensal/anual), `prazo` int positivo e `unidade_prazo` (meses/anos). Taxa de entrada e retorno da conversão são percentuais: 12 significa 12%. Retorno `ResultadoCalculo` imutável: `prazo_meses`, `taxa_mensal_percentual`, `total_investido`, `total_juros`, `montante`, `serie` tuple de `ResultadoMensal` (mes, saldo_inicial, aporte, juros, saldo_final). `converter_taxa` converte percentual mensal/anual nos dois sentidos; identidade é válida. `ErroCalculo`, subtipo de ValueError, expõe somente `campo` e `codigo`, nunca o valor informado. Códigos: decimal_obrigatorio, numero_nao_finito, valor_negativo, prazo_invalido, unidade_invalida e limite_numerico. Não há DTO HTTP nem endpoint nesta Spec.
- **OPEN-06 (recorte do motor):** benchmark sequencial, 5 aquecimentos e 100 amostras por prazo de 12, 120, 360 e 600 meses; inicial 1000, aporte 100, taxa anual 12%. Registrar SO/Python/CPU, P50/P95 por posto mais próximo e tempo em nanossegundos medido fora do domínio. Referência de orçamento do motor: P95 <3s nesse perfil; não é SLA da aplicação, teste concorrente, disponibilidade nem limite de prazo aceito pelo domínio. OPEN-06 continua aberto para ponta a ponta/operação.

Não foram definidos novos limites funcionais de valor/taxa/prazo além de RB-28. A série exige O(n) de tempo/memória; limites operacionais de entradas públicas pertencem ao contrato do consumidor (SPEC-013/OPEN-30). Os tipos adicionais são objetos de valor/erro do motor, sem nova entidade persistida ou alteração de patrimônio. Não há nova dependência nem mudança de camadas.
