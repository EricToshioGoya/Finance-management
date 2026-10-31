# Modelo de Qualidade — FinNova

- **Status:** rascunho
- **Última atualização:** 2026-10-19
- **Referência:** ISO/IEC 9126, substituída pela ISO/IEC 25010 (norma de referência, não de certificação)

Mapeia as características de qualidade da norma para os requisitos do FinNova e para a forma de verificação. Serve para mostrar o que já está coberto, o que é lacuna aceita e como cada característica será medida. A execução dos testes está em `estrategia-de-testes.md`.

---

## 1. Características, requisitos e verificação

| Característica | Subcaracterística | Requisitos do FinNova | Como verificar |
|---|---|---|---|
| **Funcionalidade** | Adequação | RFs *Must have* e cláusulas EARS das specs | Um teste por cláusula `SHALL` (`CLAUDE.md` C-02) |
| | Acurácia | RF-22, RB-10, SPEC-002, `CLAUDE.md` C-03 (`Decimal`) | Testes unitários contra cálculo de referência independente |
| | Interoperabilidade | RF-23 (SGS e Tesouro), RF-30 e RF-32 (CVM), RNF-15 (OpenAPI) | Testes de integração com dublês das fontes externas (estratégia, seção 5) |
| | Segurança de acesso | RNF-01, RNF-13, RNF-21, ADR-005 (DA-05, DA-06) | Suíte de isolamento entre usuários e de autorização por papel; análise estática de segurança |
| | Conformidade | RNF-02 (LGPD), RB-12 (CVM) | Testes de exportação e exclusão (RF-05, RF-50); checklist de segurança no PR |
| **Confiabilidade** | Maturidade | Sem requisito no MVP | Acompanhar erros não tratados em produção (RNF-12) a partir da implantação |
| | Tolerância a falhas | RF-23 (último valor com aviso), ADR-003, RNF-24 (idempotência), RNF-22 (offline) | Testes com fonte externa indisponível e com reenvio do mesmo lançamento |
| | Recuperabilidade | RNF-14 (backup com RPO de 24h e RTO de 4h) | Teste de restauração do backup antes da entrega |
| | Consistência temporal | RNF-25, ADR-006 (UTC e America/Sao_Paulo) | Testes com relógio congelado em virada de mês e de dia |
| **Usabilidade** | Inteligibilidade | RF-43, RF-44 (conteúdo e ajuda contextual) | Revisão com as personas (`docs/02-personas/personas.md`) |
| | Apreensibilidade | RF-04 (onboarding) | Revisão com as personas |
| | Operacionalidade | RNF-03 (lançamento em até 3 passos) | Teste ponta a ponta do registro de despesa |
| | Atratividade | RNF-19 (tema claro e escuro) | Revisão visual |
| | Conformidade | RNF-11 (WCAG 2.1 AA), RNF-20 (i18n) | Verificação automática de acessibilidade no frontend (ferramenta a definir) |
| **Eficiência** | Comportamento em relação ao tempo | RNF-04 (P95 < 3s), RNF-09 (defasagem de 24h) | Teste de desempenho (estratégia, seção 2) |
| | Utilização de recursos | Sem requisito no MVP | Avaliar com dados de monitoramento quando houver ambiente de produção |
| **Manutenibilidade** | Analisabilidade | RNF-12 (logs estruturados), ADRs | Revisão de PR e logs com identificação da requisição |
| | Modificabilidade | RNF-06, ADR-001 (módulos por aba) | Regra de dependência entre camadas verificada na revisão |
| | Estabilidade | RNF-16 (CI bloqueia merge) | Suíte de regressão completa em todo PR |
| | Testabilidade | RNF-07, ADR-002 (domínio puro) | Cobertura ≥ 80% no domínio de cálculo; testes unitários sem banco |
| **Portabilidade** | Adaptabilidade | RNF-05 (mesmo backend para web e mobile) | Testes de integração da API, independentes do cliente |
| | Capacidade de instalação | Stack com Docker (`arquitetura.md`, seção 5) | Subir o ambiente do zero a partir do README |
| | Coexistência e capacidade de substituir | Sem requisito no MVP | Não se aplica |

> A ISO/IEC 25010 separa **Segurança** e **Compatibilidade** como características próprias. Aqui elas aparecem como subcaracterísticas da 9126 (Segurança de acesso e Interoperabilidade/Coexistência), seguindo o material da disciplina.

### Lacunas registradas

- **Maturidade** e **Utilização de recursos** não têm requisito mensurável no MVP; serão avaliadas com dados reais após a implantação.
- **Coexistência** e **Capacidade de substituir** não se aplicam ao escopo atual.

---

## 2. Por que testar cedo

O custo de corrigir um defeito cresce com a fase em que ele é encontrado (iSixSigma, com dados NIST/IBM):

| Fase em que o defeito é encontrado | Custo relativo |
|---|---|
| Design | 1x |
| Implementação | 6,5x |
| Testes | 15x |
| Manutenção (produção) | 100x |

Por isso o FinNova concentra a prevenção nas primeiras fases: requisitos em EARS e specs antes do código (`CLAUDE.md`, seção 2), revisão do modelo e das decisões, e testes automáticos bloqueando o merge.

---

## 3. Métricas de qualidade

| Métrica | Meta | Fonte | Origem |
|---|---|---|---|
| Testes passando | 100% em todo PR | CI | RNF-16 |
| Cobertura do domínio de cálculo | ≥ 80% | pytest-cov | RNF-07 |
| Cláusulas `SHALL` com teste | 100% das cláusulas implementadas | Revisão do PR | `CLAUDE.md` C-02 |
| Tempo de resposta de simulações e dashboards | P95 < 3s | Teste de desempenho | RNF-04 |
| Defeitos por fase | Registrar a fase em que cada defeito foi encontrado | Issues com o rótulo `bug` e a fase | Custo do defeito (seção 2) |
| Disponibilidade | ≥ 99,5% no mês | Monitoramento após a implantação | RNF-08 |
