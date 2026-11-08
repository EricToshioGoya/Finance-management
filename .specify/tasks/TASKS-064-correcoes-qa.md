# Tarefas — Correções da varredura de QA (2026-11-03)

1. [x] Descontar despesa recorrente em cada competência no saldo da conta (SPEC-028-R03, SPEC-006-R05).
2. [x] Entregar webhook sem seguir redirecionamentos e com IP validado fixado (SPEC-042-R02).
3. [x] Limitar datas a 1900–2100 e períodos a 120 competências (SPEC-019, SPEC-022, SPEC-059).
4. [x] Devolver o lançamento existente no reenvio concorrente; recusar descrição em branco; 404 para indicador fora do catálogo (SPEC-059, SPEC-007).
5. [x] Aplicar o rate limit a todas as escritas e identificar o cliente só por proxy confiável (SPEC-001-R07).
6. [x] Adicionar controle de admissão, pool configurável e novas tentativas na inicialização (RNF-04, RNF-08).
7. [x] Registrar log JSON por requisição e por erro não tratado, sem dados pessoais (RNF-12, SPEC-001-R09).
8. [x] Alinhar modelos às migrations e incluir `alembic check` na CI.
9. [x] Cobrir adaptadores de e-mail/canais e jobs manuais com dublês (C-17).
10. [x] Aplicar `overrides` sem quebra no mobile e validar typecheck, testes e export Android.
11. [x] Registrar OPEN-34/OPEN-35, decisões na seção 13 das Specs e evidências antes/depois.
12. [x] Repetir lint, testes, E2E, exploratórios, fuzzing, carga, auditorias e verificadores.
