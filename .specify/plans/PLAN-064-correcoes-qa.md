# Plano — Correções da varredura de QA pré-comercialização (2026-11-03)

Origem: varredura funcional, de segurança, carga, banco e confiabilidade registrada em [evidências](../../docs/09-qualidade/evidencias/qa-pre-comercializacao-2026-11-03.md). O responsável solicitou corrigir todos os achados. As correções seguem as Specs existentes (seção 13 de SPEC-001, 007, 019, 022, 028, 042 e 059); não há Spec nova, pois os itens transversais pertencem a RNF (OPEN-32 veda Spec isolada por RNF).

## Camadas e arquivos

- Domínio: `backend/app/domain/periodo.py` (intervalo de datas suportado, parsing de competência, máximo de 120 competências).
- Aplicação: `backend/app/application/auth.py` (despesa recorrente no saldo da conta, idempotência concorrente em despesas, indicador fora do catálogo, agregação por categoria em uma leitura); `backend/app/application/webhooks.py` (entrega sem redirecionamento e com IP fixado).
- Infraestrutura: `backend/app/infrastructure/runtime.py` (identidade do cliente atrás de proxy confiável, controle de admissão e logs JSON); `backend/app/infrastructure/models.py` (restrições alinhadas às migrations).
- Apresentação: `backend/app/main.py` (rate limit em todas as escritas, limites de período, handler de erro 500, pool configurável e novas tentativas na inicialização); `backend/app/presentation/schemas.py` (datas limitadas e descrição obrigatória).
- Configuração: `backend/app/config.py` e `backend/.env.example` (`FINNOVA_TRUSTED_PROXIES`, `FINNOVA_MAX_CONCURRENT_REQUESTS`, `FINNOVA_QUEUE_TIMEOUT_SECONDS`, `FINNOVA_DB_POOL_*`, `FINNOVA_STARTUP_*`).
- Web: mensagens para `invalid_period`, `period_too_long`, `server_busy` e `internal_error` em `frontend/src/i18n.ts`.
- Mobile: `overrides` de `postcss` e `@xmldom/xmldom` (correções sem quebra).
- CI: `alembic check` após as migrations.
- Testes: `backend/tests/test_qa_2026_11_correcoes.py` e `backend/tests/test_qa_2026_11_adaptadores.py`.

## Riscos e limites

- Escritas antes livres de limite (compartilhamento, webhooks, integrações, perfil de investidor e telemetria) passam a contar no limite de 100 pedidos por minuto por cliente e grupo.
- O controle de admissão troca travamento por fila: acima de cerca de 100 simultâneos o P95 passa de 3 s em um único processo; capacidade maior exige escala horizontal com rotinas agendadas em um só processo (OPEN-32).
- Vulnerabilidades restantes do mobile (`tar`, `cacache`, `image-size`, `@expo/cli`) estão no ferramental de build do Expo SDK 52 e exigem atualização de versão maior do Expo.
- OPEN-34 (bloqueio direcionado) e OPEN-35 (revelação de e-mail no cadastro) dependem de decisão de produto; o comportamento exigido por SPEC-001 foi mantido.
