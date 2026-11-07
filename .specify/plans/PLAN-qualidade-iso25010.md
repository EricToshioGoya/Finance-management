# Plano — Revisão de qualidade contra o material ISO/IEC 9126/25010

Plano aprovado pelo responsável em 2026-11-07, após a comparação do material da disciplina (Qualidade de Software e de Código) com o repositório. Não cria Spec isolada por RNF (OPEN-32): a observabilidade entra na SPEC-060 e a recuperação fica como procedimento operacional com evidência.

| # | Lacuna (característica ISO) | Mudança | Arquivos |
|---|---|---|---|
| 1 | Processo: declaração de IA (C-13) e métrica "defeitos por fase" sem instrumento | Templates de PR e de defeito | `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/bug.md` |
| 2 | Testabilidade: pirâmide invertida, 6 módulos de domínio sem teste unitário | Testes unitários com referência independente | `backend/tests/unit/test_spec0*.py` |
| 3 | Testabilidade: cobertura do domínio sem gate próprio (RNF-07) | Gate ≥ 80% de `app/domain` só com unitários, sem banco | `.github/workflows/ci.yml` |
| 4 | Tolerância a falhas: sem teste de envio simultâneo (RNF-24) | Teste com barreira; correção da despesa | `backend/tests/test_rnf24_concorrencia_idempotencia.py`, `application/auth.py`, SPEC-059 |
| 5 | Analisabilidade e maturidade: sem log estruturado (RNF-12) | Request id, log JSON e 500 genérico registrado | `infrastructure/observabilidade.py`, `main.py`, SPEC-060-R07 a R09 |
| 6 | Recuperabilidade: sem backup nem restauração (RNF-14) | Scripts e evidência local | `scripts/backup.sh`, `scripts/verificar-restauracao.sh`, `docs/09-qualidade/evidencias/` |
| 7 | Segurança de acesso: logout sem limpeza local em falha | Avaliado e mantido: o cookie de refresh é `httpOnly` e só o servidor o revoga; limpar só o estado local simularia uma saída que não ocorreu | — |
| 8 | Testabilidade do mobile: um único arquivo de teste | Transporte HTTP puro testado com fetch falso | `mobile/src/http.ts`, `mobile/src/http.test.ts` |
| 9 | Documentação desatualizada | Modelo de qualidade e estratégia de testes com a situação real | `docs/10-qualidade/*.md` |

## Riscos

- A mudança em `main.py` envolve todas as requisições: o middleware de observabilidade é o mais externo e não altera status nem corpo, exceto para erro não tratado (antes 500 em texto do servidor, agora 500 JSON genérico).
- O backup depende de `pg_dump`/`pg_restore` na mesma versão principal do servidor.

## Fora do escopo

- Refatoração de `application/auth.py` e `main.py` (PR próprio, seção 10 da estratégia de testes).
- Serviço de monitoramento externo e alertas (exige ADR e ambiente de produção; OPEN-32).
- Tornar bloqueante o `npm audit` do mobile (vulnerabilidades no ferramental do Expo SDK).
