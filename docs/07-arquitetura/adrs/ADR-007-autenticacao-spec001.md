# ADR-007: Contratos e segurança da autenticação da SPEC-001

**Estado:** adotado tecnicamente na implementação solicitada pelo usuário nesta sessão; revisão formal do grupo pendente. **Data:** 2026-10-15. Não constitui ata de aprovação do mapa inteiro nem evidência de aprovação retroativa.

## Contexto e autorização

A SPEC-001 tinha decisões pendentes de sessão, proteção de senha, contratos e política de cadastro. Após a revisão documental, o usuário pediu explicitamente implementar a primeira Spec e enviá-la à mesma branch `correcoes-reorganizacao-docs`. Essa instrução autoriza esta implementação e as escolhas técnicas documentadas abaixo; não é registrada como aprovação humana de decisões históricas ausentes. Preservam-se os comportamentos de RF-01, RF-02, RB-27, RB-29 e RNF-13 e a arquitetura de ADR-001.

## Decisões adotadas nesta entrega

| Pendência | Escolha técnica implementada |
|---|---|
| OPEN-01 | JWT HS256, chave aleatória de pelo menos 32 bytes, expiração padrão de 15 minutos, issuer/audience/type obrigatórios e verificação de sessão no PostgreSQL em toda validação. Renovação por token opaco de 48 bytes aleatórios em cookie Secure/HttpOnly/SameSite=Strict, com sessão absoluta de 7 dias. Cada uso rotaciona a renovação; replay revoga a família. Logout revoga a sessão atual imediatamente, sem encerrar outros dispositivos. Sem segredo de produção padrão |
| OPEN-02 | Argon2id com salt aleatório por senha, 64 MiB, 3 iterações e paralelismo 4; verificar necessidade de rehash no login. Falhas de e-mail/senha usam resposta genérica e verificação dummy. Limite de 100 pedidos por minuto fixo UTC, por IP da conexão e endpoint sensível, compartilhado no PostgreSQL. Excedente recebe 429 e Retry-After até a próxima janela; bloqueio por conta de cinco falhas/quinze minutos adicionado no complemento de 2026-10-23 abaixo |
| OPEN-08 | Entrega inicial web responsiva em React/TypeScript/Vite, consumindo backend compartilhado. App nativo Expo e recorte completo do MVP permanecem pendentes; testes com cliente mobile simulado não são testes de um aplicativo nativo |
| OPEN-15 | Contratos HTTP de autenticação abaixo; a representação do motor financeiro continua em aberto. Camada de apresentação traduz códigos para mensagens em português/inglês no cliente |
| OPEN-16 | Aplicar o mínimo de 8 caracteres já escrito em RB-27, com máximo operacional de 128. Nome não vazio, até 100 caracteres; e-mail validado, até 254 caracteres, aparado e comparado sem distinção de caixa no endereço completo. Não remover pontos ou sufixos de provedores. Unicidade garantida no banco por índice do HMAC do e-mail normalizado. O histórico de aprovação anterior do grupo continua não comprovado |

## Contratos HTTP

Todas as operações usam HTTPS e prefixo `/api/v1/auth`. Entradas JSON rejeitam campos extras, incluindo papel administrativo. Dados de validação nunca são devolvidos em erros.

| Operação | Entrada | Sucesso | Erros previstos |
|---|---|---|---|
| POST `/register` | name, email, password | 201: id, name, email, role=usuario | 409 email_exists; 422 invalid_input |
| POST `/login` | email, password | 200: access_token, token_type=bearer, expires_in; cookie de renovação | 401 invalid_credentials; 422 invalid_input; 429 login_temporarily_unavailable com Retry-After |
| POST `/refresh` | Cookie de renovação, sem corpo obrigatório | 200: novo access_token, token_type, expires_in e cookie rotacionado | 401 invalid_session, inclusive replay |
| GET `/me` | Authorization: Bearer com JWT | 200: dados públicos do próprio titular | 401 invalid_session |
| POST `/logout` | JWT e/ou cookie; sem corpo obrigatório | 204 e remoção do cookie; sem sessão é idempotente | 401 se credenciais apresentadas forem inválidas sem cookie reconhecido, ou se JWT válido e cookie pertencerem a sessões distintas |
| GET /sessions | Bearer JWT válido | 200: sessões ativas do titular, sem tokens | 401 invalid_session |
| POST /sessions/{id}/revoke | Bearer JWT válido e UUID | 204; idempotente para sessão própria; remove cookie se atual | 401 invalid_session; 404 session_not_found para ID alheio/inexistente |
| POST /sessions/revoke-all | Bearer JWT válido | 200: revoked_sessions e remoção de cookie; inclui sessão atual | 401 invalid_session |

Erros têm formato `{"detail":"codigo"}`. Operações sensíveis também podem produzir 429 rate_limited, 403 invalid_origin ou 503 service_unavailable; requisição HTTP é recusada com 400 https_required. Requisições de navegador com Origin diferente da origem configurada ou Sec-Fetch-Site cross-site são recusadas. Cliente nativo sem Origin pode consumir a API por HTTPS. Não se habilita CORS irrestrito.

JWT contém sub, sid, jti, iat, exp, iss, aud e type. Token de acesso fica somente em memória no navegador; não vai ao localStorage. Renovação ocorre antes da expiração e ao recarregar a página. Tokens opacos são guardados no banco somente como SHA-256; metadados expirados de sessão e respectivas renovações são removidos em login subsequente. Nomes/e-mails usam Fernet autenticado em repouso, com chave externa à base; chave de lookup é derivada com separação de finalidade. Senha tem hash, nunca criptografia reversível.

## Fronteiras e persistência

Domínio contém identidade/normalização sem FastAPI ou ORM. Aplicação orquestra cadastro e sessão; adaptadores SQLAlchemy/PostgreSQL e criptografia ficam em infraestrutura; transporte FastAPI/Pydantic valida contratos. Migration Alembic cria usuários, sessões técnicas, digests de renovação e contadores compartilhados. Essas tabelas de infraestrutura não transformam sessão em entidade de negócio do modelo conceitual.

## Alternativas e consequências

- JWT sem estado foi descartado porque não oferece logout/revogação imediatos. A consulta da sessão aumenta a dependência do banco, mas preserva RF-02.
- Token em localStorage foi descartado para reduzir exposição persistente a scripts. Cookie seguro exige HTTPS, inclusive no desenvolvimento; certificado local não é certificado de produção.
- Contador em memória foi descartado por não limitar múltiplos workers. IP direto evita confiar em X-Forwarded-For fornecido por cliente; atrás de proxy é preciso configurar explicitamente proxies confiáveis antes de mudar essa política. Janela fixa pode permitir rajadas na fronteira de dois minutos distintos, sem exceder 100 em cada janela definida.
- Fernet protege dados pessoais em repouso, mas exige preservar/rotacionar chaves e backups com cuidado; perder a chave impede recuperar esses campos. Produção requer TLS até o banco remoto, controle de acesso e gestão externa de chaves.

## Verificação e limites

Critérios e invariantes da SPEC-001 são exercitados por integração com PostgreSQL real, teste HTTPS com certificado/hostname verificados e testes de navegador. Resultados ficam no registro de implementação. WCAG AA completo requer também revisão manual com leitor de tela. CI configurada não prova proteção de branch; o projeto precisa tornar seus checks obrigatórios no GitHub. Não se declara deploy de produção, aprovação formal do grupo ou implementação do app Expo.


## Integração com a main — 2026-10-22

Este ADR governa a implementação atual de sessão e substitui a proposta sem estado do documento histórico ADR-005. A opção histórica de não bloquear por conta não satisfaz o RF-02 mais recente da main: o bloqueio de cinco falhas por quinze minutos deve ser implementado em complemento ao rate limit, sem alegar conformidade atual. IDs de drivers seguem o catálogo da arquitetura consolidada.

## Consolidação em 2026-10-22

Este documento foi renumerado de ADR-005 para ADR-007 para preservar o ADR-005 adicionado na main. Substitui a alternativa sem estado somente quanto à sessão implementada; não elimina o bloqueio por conta exigido por RF-02. Naquela consolidação o código não satisfazia esse bloqueio; o complemento de 2026-10-23 abaixo o implementa. RF-68 a RF-73 acrescentam o ciclo completo de conta como planejamento; contratos novos dependem de refinamento e OPEN-17, sem rotas implementadas nesta alteração.


## Complemento SPEC-001 autorizado nesta entrega

O pedido de concluir SPEC-001 autoriza a adequação de RF-02/CA-011. Além do rate limit por IP/endpoint, a autenticação mantém contador por e-mail normalizado no PostgreSQL, com chave HMAC separada de lookup de usuário e sem e-mail em claro. Endereços inexistentes recebem contador e comportamento idênticos. Não há FK para usuário nem retorno que confirme existência.

As primeiras quatro falhas recebem 401 invalid_credentials. A quinta inicia bloqueio de quinze minutos e recebe 429 login_temporarily_unavailable com Retry-After: 900; tentativas durante o bloqueio, inclusive senha correta, recebem o mesmo erro e prazo restante arredondado para cima. Tentativas bloqueadas não prorrogam o prazo. No instante exato de expiração, começa nova sequência; sucesso zera contador. Reset de bloqueio não depende de IP, worker ou aba. Verificação de hash ocorre também para inexistente/bloqueado.

Insert-on-conflict e bloqueio de linha serializam a verificação e a atualização, evitando perda de incrementos em concorrência. Sessões já abertas não são revogadas por novas falhas de login. Contadores inativos por mais de 24h são removidos no login subsequente; bloqueios ativos são preservados. Relógio UTC é injetável para testar a fronteira de quinze minutos sem esperar. O bloqueio por conta pode ser provocado por terceiros; rate limit por IP/endpoint continua mitigação adicional, sem alegação de eliminar esse risco.

Migration 002_login_attempts é aditiva e preserva usuários/sessões. A interface traduz o novo erro em PT/EN e mostra prazo de nova tentativa; somente o servidor decide bloqueio. A demonstração standalone usa contas fictícias em memória e relógio local acelerável; não é prova de PostgreSQL, hash ou tokens reais. O modo normal continua usando a API HTTPS e não aceita o relógio de demonstração.

OPEN-18 passa a ter solução técnica implementada, com testes de regressão próprios; resultados executados constam no [registro de implementação](../../09-qualidade/implementacao-SPEC-001.md). Isso não inventa aprovação formal do grupo, certificação WCAG ou operação de produção.

## Complemento SPEC-017 — 2026-10-24

A gestão de sessões preserva a sessão persistida como fronteira de revogação. created_at é registrado em UTC pela migration 004; a listagem filtra titular, expiração e revogação, sem consultar refresh_tokens para resposta. Revogação individual consulta o par user_id/id e não distingue publicamente sessão alheia de inexistente. A revogação global inclui a sessão atual, remove o cookie e invalida acesso/refresh por causa da verificação de sessão já existente. Não adiciona identificação de dispositivo, geolocalização ou serviço externo.

## Complemento SPEC-014 — 2026-10-24

Perfil é sempre consultado pelo titular derivado do JWT, sem identificador de usuário em rota. A migration 005 grava preferências por titular e mantém e-mail pendente cifrado até a confirmação. Trocar e-mail exige a senha atual e gera token opaco de finalidade email_change; o endereço ativo só é substituído em transação com o consumo do token. Os endpoints PATCH de perfil e preferências seguem a mesma proteção de origem, HTTPS e limite de requisições sensíveis de autenticação.

## Complemento SPEC-016 — 2026-10-25

Recuperação usa token opaco, enviado apenas pelo adaptador de e-mail, persistido somente como digest e válido por 30 minutos. A solicitação pública sempre responde sem revelar se o e-mail existe; reenvio do mesmo titular é limitado e invalida o token anterior somente após entrega aceita. O consumo do token ou a troca autenticada pela senha atual altera o hash e revoga todas as sessões do titular na mesma transação. Os contratos publicados são `POST /password-recovery`, `POST /password-recovery/confirm` e `PATCH /password` sob `/api/v1/auth`.

## Complemento SPEC-055 — 2026-10-25

Categorias são obtidas a partir do titular do JWT, sem IDs de usuário em rota. O catálogo padrão é imutável e a visibilidade é persistida por titular; categorias pessoais usam nome cifrado e chave de busca HMAC para que duplicidade seja verificada no servidor sem guardar o nome em claro. Escritas exigem e-mail confirmado e preservam a mesma proteção HTTPS, origem e limite de requisições sensíveis.
