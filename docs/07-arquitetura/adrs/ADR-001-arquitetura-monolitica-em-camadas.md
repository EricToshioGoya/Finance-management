# ADR-001: Adoção de Arquitetura Monolítica Modular em Camadas com Backend Compartilhado

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova

## Contexto e Problema
O sistema FinNova precisa atender simultaneamente clientes Web (React) e Mobile (React Native - Expo), garantindo reuso do código das regras de negócio, facilidade de manutenção e rápido desenvolvimento no MVP, atendendo aos requisitos RNF-05 (Backend Único), RNF-06 (Modularidade) e RNF-07 (Manutenibilidade).

## Decisão Considerada
Adotar uma **Arquitetura Monolítica Modular em Camadas (Layered Monolith)** centralizada em FastAPI (Python 3.12+), expondo uma API REST versão 1 (`/api/v1`).

### Estrutura de Camadas:
1. **Apresentação (Transport):** Controllers/Routers FastAPI + Schemas Pydantic (validação de DTOs).
2. **Aplicação (Use Cases):** Orquestração de fluxos, transações de banco e permissões.
3. **Domínio (Core):** Entidades, regras de negócio e motores de cálculo puros em POO/Python, totalmente ISOLADOS de ORM e Web frameworks.
4. **Infraestrutura (Data/Adapters):** Repositórios SQLAlchemy, Migrations Alembic, PostgreSQL e Clientes de APIs externas.

## Alternativas Consideradas
* **Arquitetura de Microsserviços:** Descartada devido ao alto custo operacional de infraestrutura, complexidade de distribuição de dados e sobrecarga para o escopo do MVP e tamanho da equipe.
* **Monólito com Server-Side Rendering (Fullstack Django/Jinja):** Poderia expor API para mobile, mas não foi a opção escolhida pelo grupo; a decisão atual mantém clientes separados e FastAPI.

## Consequências
### Positivas:
* Ponto único de verdade para as regras financeiras e validação de DTOs.
* Facilidade de testes e deploy inicial simplificado (Docker / Railway / Render).
* Baixa latência de comunicação interna entre módulos.

### Negativas:
* Requer disciplina no código para evitar acoplamento entre os módulos da aplicação.
