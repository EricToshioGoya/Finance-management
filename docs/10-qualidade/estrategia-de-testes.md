# Estratégia de Testes e Qualidade — FinNova

- **Status:** rascunho
- **Última atualização:** 2026-11-07
- **Modelo de qualidade:** `docs/10-qualidade/modelo-de-qualidade.md` (características ISO, métricas e custo do defeito)

---

## 1. Objetivos

1. Demonstrar que o código implementa a spec: toda cláusula `SHALL` tem ao menos um teste (`CLAUDE.md` C-02).
2. Garantir a acurácia dos cálculos financeiros, com cobertura mínima de 80% nas regras de cálculo (RNF-07).
3. Impedir o merge de código que quebre testes ou lint (RNF-16).
4. Encontrar defeitos o mais cedo possível: um defeito em produção custa até 100x mais que no design (modelo de qualidade, seção 2).

## 2. Pirâmide de testes

A maior parte dos testes fica na base, onde são rápidos e baratos; quanto mais alto o nível, menos testes e mais lentos.

| Nível | Proporção | Alvo | Ferramenta | Quando roda |
|---|---|---|---|---|
| Unitário (base) | Maioria dos testes | Domínio puro: entidades, regras de negócio e motores de cálculo | pytest + pytest-cov, sem banco (`backend/tests/unit`) | Todo commit e PR; gate de cobertura ≥ 80% do domínio |
| Integração | Menos que unitários | API + banco: endpoints, persistência, autenticação, autorização, posse dos dados, idempotência e fuso | pytest + cliente HTTP do FastAPI + PostgreSQL em Docker | Todo PR |
| Frontend | Por fluxo de interface | Navegação, formulários, acessibilidade (axe WCAG AA) e layout responsivo | Playwright + @axe-core/playwright | Local com API HTTPS; CI executa lint e build |
| Ponta a ponta (topo) | Poucos, só o fluxo principal | Cadastro → login → sessão → logout e fluxos de interface das Specs | Playwright contra API HTTPS e PostgreSQL (job `e2e`) | Todo PR |
| Desempenho | Cenários do RNF-04 | P95 < 3s em simulações e dashboards | `scripts/carga.py` | Antes da entrega final e quando o fluxo central mudar |
| Recuperação | RNF-14 | Backup restaurado em banco isolado com as mesmas linhas da origem | `scripts/backup.sh` e `scripts/verificar-restauracao.sh` | Antes da entrega final e quando houver migration |

**Distribuição atual (2026-11-07):** 196 casos unitários (36%) e 352 de integração no backend, 12 testes Playwright e 9 testes do mobile. Antes desta revisão eram 118 unitários (26%). A integração ainda é maioria porque grande parte das regras está na camada de aplicação (`application/auth.py`); mover regras para `app/domain` é o caminho para inverter a proporção (ver seção 11).

**Anti-padrão evitado — "casquinha de sorvete":** muitos testes manuais ou de interface e poucos unitários. Uma regra de negócio é testada no nível unitário; os testes de ponta a ponta só confirmam que as partes se conectam.

## 3. Rastreabilidade cláusula → teste

- Cada teste cita no nome ou na docstring o ID da cláusula que verifica. Exemplo:

```python
def test_spec002_r02_converte_taxa_anual_por_equivalencia_composta():
    """SPEC-002-R02 — Cenário 1."""
```

- A coluna "Teste previsto" da seção 5 de cada spec indica o nível de teste esperado.
- No PR, a pergunta de revisão é: "cada cláusula alterada tem teste e o teste passa?".
- `python scripts/verificar-c02.py` lista as cláusulas `SHALL` sem teste que cite o ID (nome `test_SPEC_NNN_Rxx`, docstring `Cláusulas: SPEC-NNN-Rxx` ou comentário em teste Playwright). Na CI (job `documentacao`) roda com `--estrito` e falha se houver pendência.
- Situação em 2026-11-01: 398 de 398 cláusulas citadas. Cláusulas de interface (ex.: SPEC-012-R04/R11/R12 e SPEC-030) são verificadas no navegador com Playwright, simulando apenas as respostas necessárias.

## 4. Suítes obrigatórias de risco

Aprendizados de falhas reais aplicados ao FinNova:

| Suíte | Risco que evita | O que verifica | Origem |
|---|---|---|---|
| Isolamento entre usuários | Usuário ver dados de outra conta | Para cada endpoint com dado financeiro, o usuário B tenta ler, alterar e excluir um recurso do usuário A e recebe "não encontrado", sem dado algum | DA-06, ADR-005, RNF-02 |
| Autorização por papel | Usuário comum acessar rota administrativa | Toda rota `/api/v1/admin/*` recusa um usuário sem papel de administrador | DA-05, RNF-21 |
| Idempotência | Lançamento duplicado por clique duplo ou reenvio | Duas criações com a mesma chave, em sequência e em paralelo (barreira de threads), geram um único lançamento e a mesma resposta | DA-10, RNF-24 |
| Fuso e virada de período | Despesa no mês errado; bloqueio liberado antes da hora | Relógio congelado em 31/10 às 23h30 (horário de Brasília), que já é 1/11 em UTC: a despesa conta em outubro; bloqueio e expiração respeitam a janela em UTC | DA-11, RNF-25, ADR-006 |
| Fonte externa indisponível | Simulação com taxa zerada ou erro | Com a fonte simulada fora do ar, a simulação usa o último valor com aviso | RF-23, ADR-003 |

## 5. Dublês de integrações externas

Nenhum teste automatizado chama serviço externo real (`CLAUDE.md` C-17).

| Integração | Dublê nos testes |
|---|---|
| API SGS (Banco Central) e Tesouro Transparente | Transporte injetável falso (`FakeTransport`) com respostas no formato das fontes e erros simulados |
| Dados Abertos da CVM | Arquivos CSV de exemplo versionados em `tests/` |
| Push (FCM) e e-mail transacional | Implementação falsa que registra as mensagens, verificada pelo teste |
| Relógio | Relógio injetado e congelado no teste (ADR-006) |

## 6. Dados de teste

- Valores monetários e taxas sempre em `Decimal` (SPEC-002 INV-02).
- Resultados financeiros conferidos contra cálculo de referência independente (ex.: planilha ou calculadora do Banco Central), registrado no próprio teste.
- Nenhum dado pessoal real em fixtures.

## 7. Gates de qualidade no CI (RNF-16)

| Gate | Critério |
|---|---|
| Lint | Sem erros: `ruff check` e `ruff format --check` no backend; `tsc --noEmit` e ESLint no frontend (CI) |
| Testes | 100% passando, incluindo as suítes da seção 4 |
| Cobertura | ≥ 80% de `app/domain` só com testes unitários sem banco (RNF-07) e ≥ 90% do backend com a suíte completa |
| Segurança | Sem vulnerabilidade alta nas dependências (`docs/09-seguranca/seguranca-ssdlc.md`) |

## 8. Definição de pronto

Uma issue só é concluída quando:

- [ ] A spec está atualizada no mesmo PR.
- [ ] Cada cláusula `SHALL` implementada tem teste passando.
- [ ] As suítes de risco afetadas pela mudança (seção 4) foram atualizadas.
- [ ] Os gates da seção 7 passaram.
- [ ] O PR foi revisado conforme `docs/combinados.md` e declara o uso de agente de IA.

## 9. Revisão de código gerado por agente

O código gerado por agente segue as mesmas regras, com atenção redobrada a:

- Regras de negócio inventadas, que não constam da spec.
- Uso de `float` ou de conversão de taxa por divisão simples.
- Testes que só confirmam a própria implementação, sem valor de referência independente.
- Leitura direta do relógio do sistema ou chamada a serviço externo real.

## 10. Refatoração

- Toda refatoração é feita em PR próprio, com justificativa (duplicação, acoplamento ou complexidade) e sem mudança de comportamento: os testes existentes devem continuar passando sem alteração.

## 11. Questões em aberto

- **Carga do teste de desempenho:** o RNF-04 define o P95, mas não o número de usuários simultâneos a simular.
- **Proporção da pirâmide:** `application/auth.py` (cerca de 3.000 linhas) concentra regras testáveis só com banco. A extração para `app/domain` exige PRs de refatoração próprios (seção 10) e ainda não foi planejada.
- **`npm audit` do mobile:** continua não bloqueante; as vulnerabilidades altas e críticas estão no ferramental do Expo SDK.

## Situação atual (2026-10-31)

- Backend: `pytest` com PostgreSQL temporário por sessão de teste; cobertura mínima de 90% exigida na CI (atual: 92%). Testes das Specs implementadas em 2026-10-31 seguem o padrão `test_SPEC_NNN_Rxx_...`.
- Dublês: canais externos (SPEC-061), entrega de e-mail (SPEC-015) e fontes de mercado usam dublês em memória; nenhum teste chama serviço externo real (C-17).
- CI: `.github/workflows/ci.yml` executa backend, frontend, mobile, segurança (Bandit, `pip-audit`, `npm audit`), E2E Playwright com API HTTPS e PostgreSQL, e verificador documental em cada PR.
- Carga (RNF-04): `scripts/carga.py` mede o P95 de simulação e dashboard; evidência em [`docs/09-qualidade/evidencias/rnf04-carga-2026-10-31.md`](../09-qualidade/evidencias/rnf04-carga-2026-10-31.md) (P95 ≤ 0,57 s).
- Pendente: restauração de backup (RNF-14) e medição em ambiente de produção (OPEN-32).

## Situação atual (2026-11-07)

Revisão contra o material de Qualidade de Software (ISO/IEC 9126/25010, custo do defeito, pirâmide de testes e casos reais):

- **Concorrência (caso de checkout duplicado):** novo teste com dois envios simultâneos da mesma `Idempotency-Key` revelou que a despesa respondia 503 no segundo envio; corrigido para devolver o registro gravado (SPEC-059).
- **Observabilidade:** cabeçalho `X-Request-ID`, log JSON por requisição e 500 genérico com pilha registrada, sem senha, token ou e-mail (SPEC-060-R07 a R09).
- **Recuperação:** procedimento de backup e restauração verificado localmente ([evidência](../09-qualidade/evidencias/rnf14-restauracao-2026-11-07.md)).
- **Pirâmide:** testes unitários para `cartao`, `market_metrics`, `foreign_currency`, `education`, `identity` e `expansion`; gate de cobertura unitária do domínio na CI.
- **Processo:** template de PR (checklist e declaração de IA, C-13) e template de defeito com a fase em que foi encontrado.
