# ADR-002: Motor de Cálculo Financeiro e Juros Compostos no Domínio Puro

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova
* **Drivers atendidos:** DA-02, DA-07

## Contexto e Problema
As simulações de investimento (RF-20, RF-21, RF-22) exigem cálculos de juros compostos com conversão de equivalência de taxas (mês/ano) e alíquotas tributárias de IR. Erros nesses cálculos destroem a confiabilidade da plataforma. O requisito RNF-07 exige cobertura mínima de 80% de testes automatizados nas regras financeiras.

## Decisão
Isolar toda a lógica de cálculo financeiro em classes de **Domínio Puro** (sem dependências de SQLAlchemy, FastAPI ou qualquer lib externa).

* O motor recebe entradas primitivas (`Decimal`, `int`) e retorna objetos de valor/DTOs puros de domínio.
* Todas as conversões temporais usam taxa equivalente composta: $i_{mensal} = (1 + i_{anual})^{1/12} - 1$, conforme RB-10.

## Alternativas Consideradas
* **Cálculo via procedimentos armazenados (Triggers/Stored Procedures no PostgreSQL):** Descartado pois dificulta testes unitários ágeis no CI/CD e acopla a regra de negócio ao SGBD.
* **Cálculo no Frontend (React/React Native):** Descartado pois duplicaria a lógica em duas plataformas e impediria o uso consistente via API pública ou relatórios automáticos no backend.

## Consequências
### Positivas:
* Testabilidade extrema: os testes com `pytest` rodam em milissegundos sem precisar subir banco de dados ou mockar requisições HTTP.
* Garantia de acurácia matemática conforme RNF-07 e RNF-04 (P95 < 3s).

### Negativas:
* Exige mapeamento manual ou via adaptadores entre as entidades do ORM e os objetos de valor do motor de cálculo.
