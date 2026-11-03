# Varredura de QA pré-comercialização — 2026-11-03

Execução local (contêiner Linux, 4 vCPU, PostgreSQL 16, API em um processo `uvicorn` com HTTPS) da esteira oficial e de testes exploratórios funcionais, de segurança, banco, carga e confiabilidade. Nenhum teste chamou serviço externo real (C-17). Plano em `.specify/plans/PLAN-064-correcoes-qa.md`.

## Esteira oficial

| Verificação | Antes | Depois |
|---|---|---|
| Backend: `ruff check` e `ruff format --check` | limpos | limpos |
| Backend: `alembic check` (modelos × migrations) | divergente | sem divergência (incluído na CI) |
| Backend: `pytest` com cobertura | 458 aprovados, 91,8% | 479 aprovados, 93,3% (com a `main` integrada) |
| Web: lint, build e Playwright (fluxos, WCAG AA, layout) | 12/12 | 12/12 |
| Mobile: typecheck, testes e export Android | aprovados | aprovados |
| Bandit (média ou maior) e pip-audit | sem achados | sem achados |
| `npm audit` web (produção) | 0 | 0 |
| `npm audit` mobile (produção), alta + crítica | 5 + 1 | 3 + 1 (ferramental do Expo SDK 52) |
| Verificador documental e C-02 estrito | aprovados | aprovados |

## Achados e correções

| # | Área | Achado (evidência antes) | Correção | Evidência depois |
|---|---|---|---|---|
| 1 | Cálculo | Patrimônio descontava despesa recorrente uma única vez: R$ 63.000 contra R$ 43.000 pela soma dos resumos mensais | Desconto por competência iniciada, regra do resumo mensal (SPEC-028) | Patrimônio R$ 43.000 = saldo inicial + soma das variações |
| 2 | Capacidade | Com 75 simultâneos: P50 de 30 s e 33% de 503; com 150, 100% de falha e 31 s para voltar | Controle de admissão (30 em execução, fila de até 10 s), pool 20+20 com espera de 10 s | 0% de erro com 100, 200 e 300 simultâneos; retorno imediato após o pico |
| 3 | Segurança | Webhook seguia redirecionamento 302 para serviço interno HTTP (SSRF) | Sem redirecionamento e com IP validado fixado (SPEC-042) | 3xx registrado como falha; serviço interno não recebe requisição |
| 4 | Disponibilidade | Dashboard sem limite de período: 1900–2026 em 3,8 s; 0001–9999 estimado em minutos por pedido | Máximo de 120 competências entre 1900 e 2100 (SPEC-022) | 0001–9999 recusado com 400 em menos de 10 ms |
| 5 | Segurança | Rate limit por IP da conexão: atrás de proxy, todos os clientes dividiriam o mesmo limite | `FINNOVA_TRUSTED_PROXIES` e `X-Forwarded-For` só de proxy confiável (SPEC-001) | Testes de identidade do cliente |
| 6 | Robustez | Erro 500 com parcelas após 9999-12 e exportação com `year` 0, -5 ou 10000 | Datas entre 1900 e 2100 e validação de período (SPEC-059, SPEC-019) | 422/400 com código de erro |
| 7 | Idempotência | 20 envios simultâneos com a mesma chave: 1 resposta 503 | Conflito de unicidade devolve o lançamento gravado (RNF-24) | 20 respostas 201 e um único registro |
| 8 | Segurança | `PUT` fora do rate limit: 110 `PUT` seguidos aceitos | Limite em toda escrita sob `/api/v1` (RNF-13) | 101ª requisição recebe 429 |
| 9 | Segurança | Bloqueio por conta permite bloqueio direcionado por terceiros | Mantido (exigido por SPEC-001-R11) | Registrado em OPEN-34 |
| 10 | Observabilidade | Sem log estruturado nem registro de erro 500 | Log JSON por requisição (sem query string) e por erro não tratado, com `X-Request-ID` (RNF-12) | Teste de erro sem dado pessoal no log |
| 11 | Operação | API encerrava ao iniciar com o banco fora do ar | Novas tentativas configuráveis antes de atender (fail-closed preservado) | API aguardou e subiu quando o banco voltou |
| 12 | Validação | Descrição de despesa só com espaços aceita | Recusada na criação e edição (SPEC-059) | 422 |
| 13 | Contrato | Código de indicador inexistente devolvia 503 | 404 `indicator_not_found` (SPEC-007) | 404; 503 só para código conhecido sem cache |
| 14 | Segurança | Cadastro revela e-mail existente (`email_exists`) | Mantido (contrato de SPEC-001) | Registrado em OPEN-35 |
| 15 | Banco | `alembic check` divergente; um autogenerate removeria as restrições de idempotência | Restrições declaradas nos modelos | Sem divergência; verificação na CI |
| 16 | Cobertura | `app/jobs` 0%, `email_delivery` 42%, `channel_delivery` 54% | Testes com dublês | 92–100% |

## Testes exploratórios (mesmo roteiro antes e depois)

- Roteiro automatizado de 126 verificações: autorização entre usuários (IDOR), JWT adulterado, rotação e reuso de refresh, força bruta, SQL injection, XSS, CSV injection, cabeçalhos de segurança, validação de entrada, idempotência, concorrência, LGPD e logs. Antes: 4 falhas (descrição em branco aceita, erro 500 com parcelas após 9999, 503 em reenvio concorrente e `PUT` sem rate limit). Depois, com verificações de regressão acrescentadas: 111 aprovadas e 0 falhas, com 15 itens informativos.
- Fuzzing pelo contrato OpenAPI (Schemathesis): cerca de 13,8 mil casos depois das correções, sem nenhuma resposta 500. As respostas 503 restantes são o comportamento previsto quando o cache de indicadores ou de cotações está vazio ou vencido (C-08).
- Banco: backup com `pg_dump` e restauração em base nova; ao subir a API sobre o backup, a conta excluída depois do backup foi removida de novo. Sem registros órfãos e todas as chaves estrangeiras validadas.
- Confiabilidade: com o PostgreSQL parado, a API responde 503 em menos de 10 ms e volta sozinha quando o banco retorna.

## Carga de leitura depois das correções (um processo)

| Simultâneos | Req/s | P50 | P95 | Erros |
|---|---|---|---|---|
| 10 | 48 | 127 ms | 610 ms | 0% |
| 50 | 53 | 858 ms | 1.947 ms | 0% |
| 100 | 56 | 1.847 ms | 2.940 ms | 0% |
| 200 | 60 | 3.931 ms | 5.072 ms | 0% |
| 300 (pico) | 66 | 5.892 ms | 7.349 ms | 0% |

O RNF-04 (P95 abaixo de 3 s) se mantém até cerca de 100 usuários simultâneos por processo. Acima disso a fila evita falhas, mas a latência cresce; capacidade maior exige escala horizontal (OPEN-32).

## Limites desta verificação

- Firefox e Safari, aparelhos Android e iOS reais, usabilidade com pessoas e carga prolongada por horas não foram executados.
- Monitoramento externo, alertas, backup automático agendado e artefatos de implantação em produção continuam pendentes (OPEN-32).
- OPEN-34 e OPEN-35 dependem de decisão de produto.
