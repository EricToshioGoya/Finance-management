# Registro de implementação — SPEC-001

**Data:** 2026-10-15. **Branch:** `correcoes-reorganizacao-docs`. Implementação solicitada explicitamente pelo usuário na sessão, após a revisão documental de `22ed4e5`. Não representa aprovação formal do grupo ou deploy de produção.

## Entrega e decisões

API FastAPI com cadastro/login, identidade do titular, renovação rotativa e logout com revogação imediata da sessão; PostgreSQL/SQLAlchemy com migration Alembic e unicidade concorrente de e-mail; Argon2id para senhas, Fernet para dados pessoais, rate limit persistente e contratos OpenAPI/Swagger. Interface React/TypeScript/Vite responsiva, em português e inglês, com formulários acessíveis, sessão restaurável e token de acesso apenas em memória. Renovação é serializada entre abas por Web Locks quando disponível.

[ADR-007](../07-arquitetura/adrs/ADR-007-autenticacao-spec001.md) registra decisões técnicas de OPEN-01, OPEN-02, OPEN-08, OPEN-15 e OPEN-16. A autorização para implementar não é registrada como aprovação histórica das regras nem como aprovação do mapa completo. Outras Specs não foram implementadas.

## Evidências locais

Os comandos abaixo correspondem à entrega desta branch. Resultados finais registrados após execução; CI remota é distinta.

| Verificação | Resultado |
|---|---|
| Backend: `uv run --frozen pytest -q --cov=app --cov-fail-under=90` | 30 testes aprovados com PostgreSQL real; 95,68% de cobertura total de linhas em app |
| Backend: Ruff check e format check | Aprovados |
| Frontend: TypeScript/ESLint e build Vite | Aprovados |
| Navegador: `npm test` | 5 testes aprovados: fluxo/restauração e abas simultâneas, idiomas/erros, Axe/teclado, tamanhos 320/390/1440px e Swagger sem CDN |
| HTTPS: `python3 scripts/smoke-auth.py` | Aprovado com verificação de certificado/hostname; cadastro, duplicidade, login, titular, renovação, logout e recusa de sessão encerrada |
| Instalação/startup e migrations | Fluxo local executado; migrations reaplicadas sem duplicar esquema |
| Verificação documental e diff | 25 documentos com referências/estrutura válidas; `git diff --check` sem erros |

Testes de API usam base temporária isolada, criada/migrada e removida pelo fixture, sem truncar a base de desenvolvimento. Testes de navegador e smoke usam usuários sintéticos no banco local. O teste de API com cliente mobile simulado demonstra consumo do contrato compartilhado, sem alegar execução de app nativo. O runner emite um aviso de depreciação sobre o adaptador HTTPX de Starlette; os testes executaram e passaram.

### Rastreabilidade da matriz de testes

| Linha da SPEC-001 | Evidência executável / limite |
|---|---|
| T-001 | Cadastro válido, mínimo de senha, campos ausentes/invalidade e rejeição de campo administrativo em `backend/tests/test_auth.py` |
| T-002 | Duplicidade sequencial, e-mail com caixa diferente e dois cadastros concorrentes; índice único deixa um usuário |
| T-003 | Login válido e falhas de senha/e-mail com mesma resposta genérica |
| T-004 | Campo role=administrador é rejeitado com 422, sem persistir usuário |
| T-005 | Limite 100/excedente, fronteira da janela, cliente/endpoint distintos e estado compartilhado por duas instâncias de aplicação |
| T-006 | JWT expirado/adulterado/audience/tipo incorretos; sessão expirada, rotação, replay sequencial/concorrente, logout e isolamento entre sessões |
| T-007 | Hash Argon2id com salt distinto, campos pessoais cifrados, respostas/erros sem credenciais e smoke TLS com cadeia/hostname verificados |
| T-008 | Prefixo/contrato OpenAPI, dois consumidores do mesmo backend e Swagger local em navegador; app Expo não implementado |
| T-009 | Português/inglês, erro traduzido, teclado, Axe WCAG A/AA e responsividade em navegador; leitor de tela manual pendente |
| T-010 | Workflow de testes/lint/build configurado; execução remota e proteção de branch não inferidas da execução local |

## Limites e pendências

- Não houve implementação de motor financeiro, simuladores, quiz ou funcionalidades de outras Specs.
- Web responsiva foi o cliente inicial escolhido. Não há aplicativo Expo entregue nem validação em dispositivo nativo.
- Varredura automática Axe e navegação por teclado não certificam todo WCAG 2.1 AA; revisão manual com leitor de tela permanece pendente.
- Configuração de checks obrigatórios e comprovação de bloqueio de merge exigem configuração do GitHub; o workflow foi adicionado, sem presumir essa proteção ativa.
- Produção exige certificado confiável, gestão/rotação de chaves, TLS ao banco remoto, privilégios mínimos, backups e observabilidade. O certificado e o banco locais são de desenvolvimento.
- Revisão formal do grupo/mapa e comprovação de aprovação histórica continuam pendentes. A Definition of Done distingue essas pendências da implementação funcional testada.

O [README](../../README.md) contém os comandos de preparação, inicialização e testes. Arquivos `.env`, chaves, certificados, caches, builds e dados locais permanecem fora do Git.


## Correção da abertura de HTML

O usuário informou tela vazia ao abrir `index.html` diretamente. O arquivo de entrada dependia de TypeScript/Vite e deixava apenas uma raiz vazia se o módulo não carregasse. Foi adicionada mensagem de orientação no HTML de entrada e exportação automática de `.local/finnova-preview.html` com JavaScript, CSS e ícone incorporados.

A prévia visual não chama API, não cria contas fictícias e desativa o envio dos formulários. O fluxo real servido por HTTPS preserva a autenticação existente. Bloqueio de localStorage em visualizadores agora tem fallback para idioma em memória, sem impedir a renderização.

Validação: cinco cenários existentes de navegador aprovados após o novo build; teste adicional da prévia aprovado com HTTP bloqueado e localStorage indisponível. O Chromium gerenciado bloqueia navegação file:, então o teste carrega o conteúdo exato do HTML em um documento vazio, sem usar servidor. Foram conferidos renderização, troca de formulário/idioma, botões desativados e ausência de requests HTTP e erros JavaScript. TypeScript, ESLint, build, verificação documental e diff também aprovados. O HTML exportado é artefato local, não deploy nem aplicativo completo publicado.

## Limite da evidência após merge — 2026-10-22

Resultados acima pertencem à implementação original; não são execução desta consolidação. Código de autenticação foi preservado. Bloqueio por conta de RF-02 e funcionalidades novas RF-68 a RF-72 continuam pendentes. RF-73 rastreia sessão existente, sem implementar os gatilhos de troca/recuperação/exclusão ainda ausentes. A matriz de cobertura separa evidência histórica de planejamento.

## Complemento funcional — 2026-10-23

**Branch:** `feature/spec001-completa`, a partir de `docs/specs-completas-sdd`. **Código validado:** `05ae364c9bb28143a73084c08679a79d97655a1f`. **PR:** [#12](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/pull/12), para a branch de Specs. Este registro não declara merge na main, deploy nem aprovação formal do grupo.

A lacuna de RF-02/CA-011/INV-007 descrita no estado de 2026-10-22 foi implementada. O contador por endereço normalizado fica no PostgreSQL, inclusive para e-mail inexistente, com chave HMAC, bloqueio de linha e migration aditiva `002_login_attempts`. Cinco erros consecutivos bloqueiam por quinze minutos; sucesso zera contador; tentativas durante bloqueio não prorrogam prazo. No instante exato de expiração inicia nova sequência. Sessões já abertas permanecem válidas. O rate limit por IP/endpoint continua independente. Contrato e risco de bloqueio provocado por terceiros: ADR-007.

### Evidência executada nesta entrega

Execução em runner GitHub Actions com PostgreSQL 16 real e Chromium, sem serviços externos de autenticação. [Execução da CI do código](https://github.com/ArthurAlencarDeOliveiraSa/Projeto-Modelagem-de-Sistemas/actions/runs/39885876680).

| Verificação | Resultado |
|---|---|
| API/PostgreSQL: pytest e cobertura | 38 testes aprovados; 95,87% de cobertura total de linhas em `app`; mínimo exigido 90% |
| Ruff check/format | Aprovados |
| TypeScript, ESLint e build Vite | Aprovados |
| HTTPS smoke | Certificado/hostname verificados; cadastro, duplicidade, login, titular, renovação e logout aprovados |
| Chromium/Playwright | 8 cenários aprovados: fluxo de conta/restauração/abas, erros/idiomas, teclado/Axe, responsividade, Swagger, prévia estática isolada, bloqueio real e demonstração interativa isolada |
| Integridade documental | 97 documentos verificados, incluindo links e referências |

### Rastreabilidade adicional

| Critério / cláusula | Evidência |
|---|---|
| CA-011, INV-007, SPEC-001-R11, T-011 e T-R11 | Oito testes em `backend/tests/test_login_lock.py`: quinta falha; senha correta recusada; instante anterior/exato à expiração; prazo não prorrogado; reset no sucesso/expiração; inexistente com resposta igual; estado sem e-mail; normalização/IPs/instâncias; cinco erros concorrentes; sessões preservadas; limpeza seletiva |
| Mensagem de bloqueio e prazo no cliente | Cenário `SPEC-001-R11` em `frontend/tests/auth.spec.ts`, contra API real; PT/EN e varredura automática Axe no estado bloqueado |
| Visualização sem backend | Cenário `demonstração interativa sem API` em `frontend/tests/auth.spec.ts`: cadastro fictício, cinco falhas, avanço de quinze minutos, login e logout; HTTP bloqueado, sem requests nem erros JavaScript; larguras 320/1024px |
| Migração incremental | Pytest cria banco temporário e aplica a cadeia Alembic; smoke executa após `alembic upgrade head` |

A demonstração incorpora o mesmo cliente web e usa somente dados fictícios em memória. Seu botão de avanço de tempo não altera a API nem está presente no cliente normal. Os arquivos exportados `.local/finnova-demo.html` e `.local/finnova-preview.html` são gerados pelo build, sem necessidade de versionar builds ou credenciais reais. O workflow exporta apenas as capturas fictícias `demo-*.png` no artefato `spec001-demo`; o complemento de CI habilita a coleta desse padrão dentro de `.local`, sem incluir chaves ou `.env`.

Os resultados antigos acima são históricos. A entrega funcional web foi complementada e revalidada; app Expo, revisão manual completa WCAG, proteção obrigatória de branch e operação de produção mantêm os limites já descritos. Nenhuma assinatura ou revisão humana é preenchida por estes testes. A assistência de IA à implementação/revisão técnica automatizada está declarada no PR.
