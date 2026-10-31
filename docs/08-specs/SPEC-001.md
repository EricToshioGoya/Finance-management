# SPEC-001: Cadastro de Usuário e Autenticação de Sessão

**Estado:** implementação funcional web complementada em 2026-10-23, incluindo CA-011/INV-007 e regressão. A implementação inicial foi autorizada pelo pedido explícito do usuário nesta sessão, em 2026-10-15, na branch `correcoes-reorganizacao-docs`. Decisões técnicas adotadas em ADR-007; aprovação formal do mapa/grupo permanece pendente e não é inferida desta autorização. Evidências e limites no [registro de implementação](../09-qualidade/implementacao-SPEC-001.md).

## 1. Identificação

- **ID:** SPEC-001
- **Nome:** Cadastro de Usuário e Autenticação de Sessão
- **Objetivo:** permitir cadastro seguro e autenticação por e-mail e senha.
- **Valor entregue:** permitir ao usuário obter uma identidade e uma sessão para acessar suas funcionalidades pessoais.

## 2. Rastreabilidade

- **RF:** RF-01, RF-02 e RF-74 (sessão já entregue, gestão ampliada na SPEC-017), em [requisitos](../03-requisitos/requisitos.md).
- **RB:** RB-27 (credenciais e cadastro público; política atual em ADR-007, histórico de aprovação em OPEN-16), RB-29 (titularidade).
- **RNF:** RNF-01, RNF-05, RNF-11, RNF-13, RNF-15, RNF-16, RNF-17, RNF-20; verificações na seção 10.
- **Fluxos:** UC-01 e UC-02, no [catálogo](../04-casos-de-uso/casos-de-uso-usuario.md).
- **Domínio:** Usuario, no [modelo conceitual](../05-modelo-de-dominio/modelo-de-dominio.md).
- **Arquitetura:** DA-05, ADR-001 e [ADR-007](../07-arquitetura/adrs/ADR-007-autenticacao-spec001.md), em [arquitetura](../07-arquitetura/arquitetura.md); JWT consta da [visão](../01-visao/visao.md) e RF-02.

## 3. Escopo

**Incluído:** formulário de cadastro e login web responsivo, conforme recorte inicial de ADR-007/OPEN-08, validação no servidor, unicidade de e-mail, proteção da senha com hash e salt, criação de usuário comum, emissão e validação da sessão JWT, expiração/logout conforme RF-02 e OPEN-01, limitação de tentativas conforme RNF-13.

**Fora do escopo:** recuperação de senha, login social, quiz (SPEC-003), promoção administrativa e demais operações pessoais. As rotas dessas operações aplicam autorização em suas próprias Specs; esta entrega fornece a validação de sessão reutilizável.

## 4. Dependências

Não depende de outra Spec funcional. Segue ADR-001 e as escolhas técnicas de ADR-007 para OPEN-01, OPEN-02, OPEN-08, OPEN-15 e OPEN-16. O pedido do usuário autoriza esta implementação; não comprova a sequência histórica de aprovação do mapa. Revisão formal do grupo e expansão mobile continuam pendentes. A validação consulta sessão persistida para aplicar expiração/logout, em vez de somente verificar assinatura JWT.

## 5. Comportamento esperado

**Pré-condições:** cadastro e login são públicos, sem sessão prévia. Política de credenciais, unicidade, sessão e limite de tentativas documentada em ADR-007.

**Cadastro:** cliente coleta nome, e-mail e senha; servidor valida entradas e unicidade; protege a senha; persiste Usuario com papel comum; devolve confirmação e dados públicos, sem senha/hash.

**Login:** cliente envia e-mail e senha; servidor verifica limite de tentativas e credenciais; em caso de sucesso emite sessão JWT conforme política de ADR-007. Validação de sessão e logout respeitam OPEN-01.

**Alternativas/exceções:** entrada inválida ou e-mail duplicado rejeita cadastro sem novo usuário; cadastros concorrentes respeitam unicidade; e-mail inexistente e senha incorreta produzem a mesma falha genérica, sem sessão; excesso de pedidos é limitado sem autenticar; token inválido, expirado ou invalidado segundo a política é recusado. Falha de persistência não deve produzir confirmação falsa; detalhes do erro pertencem a OPEN-15.

**Pós-condições:** cadastro bem-sucedido cria uma identidade comum; login válido disponibiliza sessão; rejeições não criam usuário nem sessão indevidos e não revelam credenciais.

### Cláusulas EARS rastreáveis desta revisão

| Cláusula | Comportamento normativo | Critério | Teste planejado |
|---|---|---|---|
| SPEC-001-R01 | WHEN cadastrar sob a condição de cadastro válido e e-mail livre THE SYSTEM SHALL criar exatamente um usuário comum e confirmar sem senha/hash. | CA-001 | T-R01 |
| SPEC-001-R02 | WHEN cadastrar novamente sob a condição de e-mail já existente segundo OPEN-16 THE SYSTEM SHALL rejeitar sem novo registro, inclusive em concorrência. | CA-002 | T-R02 |
| SPEC-001-R03 | WHEN autenticar com credenciais corretas sob a condição de usuário cadastrado THE SYSTEM SHALL obter sessão JWT válida pela política de ADR-007. | CA-003 | T-R03 |
| SPEC-001-R04 | WHEN autenticar sob a condição de e-mail inexistente ou senha incorreta THE SYSTEM SHALL retornar falha genérica equivalente, sem sessão. | CA-004 | T-R04 |
| SPEC-001-R05 | WHEN cadastrar sob a condição de nome ausente, e-mail inválido ou senha fora da política de ADR-007 THE SYSTEM SHALL rejeitar sem persistir usuário. | CA-005 | T-R05 |
| SPEC-001-R06 | WHEN processar sob a condição de cadastro com tentativa de escolher papel administrador THE SYSTEM SHALL não conceder esse papel. | CA-006 | T-R06 |
| SPEC-001-R07 | WHEN ultrapassar 100 requisições/minuto no endpoint sensível sob a condição de cliente no limite aprovado THE SYSTEM SHALL limitar o pedido conforme OPEN-02, sem autenticar o pedido excedente. | CA-007 | T-R07 |
| SPEC-001-R08 | WHEN validar acesso sob a condição de sessão inválida, expirada ou encerrada segundo OPEN-01 THE SYSTEM SHALL recusar sem dados pessoais; sessão válida identifica somente seu titular. | CA-008 | T-R08 |
| SPEC-001-R09 | WHEN inspecionar respostas, logs e armazenamento sob a condição de cadastro/login realizado THE SYSTEM SHALL observar INV-001 e tráfego sensível protegido por HTTPS. | CA-009 | T-R09 |
| SPEC-001-R10 | WHEN consultar operações desta entrega sob a condição de contrato publicado THE SYSTEM SHALL todas estão sob `/api/v1` e login preserva a rota de RF-02. | CA-010 | T-R10 |
| SPEC-001-R11 | WHEN tentar novamente antes de quinze minutos sob a condição de cinco falhas consecutivas de login da mesma conta THE SYSTEM SHALL recusar autenticação, inclusive com senha correta durante o bloqueio; após o bloqueio aplicar a política aprovada e após sucesso zerar o contador. Testar sem revelar existência de conta (OPEN-18). | CA-011 | T-R11 |

## 6. Regras e invariantes

- **INV-001:** senha em claro nunca é persistida ou registrada em logs; senha/hash não aparecem nas respostas.
- **INV-002:** no máximo um Usuario existe para cada e-mail segundo a equivalência documentada em ADR-007 para OPEN-16, inclusive sob concorrência.
- **INV-003:** falha por e-mail inexistente e por senha incorreta não revela qual credencial falhou.
- **INV-004:** entrada pública não concede papel administrativo.
- **INV-005:** validação de sessão recusa tokens inválidos ou expirados e aplica a política de logout/revogação de ADR-007.
- **INV-006:** cada cliente fica limitado a no máximo 100 requisições/minuto por endpoint sensível, com identificação/janela de ADR-007 para OPEN-02.

- **INV-007:** cinco falhas de login consecutivas para a mesma conta bloqueiam novas tentativas por quinze minutos; sucesso zera o contador; limite por cliente continua separado (RF-02).

## 7. Modelo de domínio envolvido

Usuario: identidade, nome, e-mail, credencial protegida e papel usuário/administrador. E-mail é único pela política de ADR-007; cadastro público cria papel comum. A identidade liga o titular aos dados pessoais, mas esta Spec não cria contas ou simulações. Sessão/JWT é um contrato de autenticação, não uma nova entidade conceitual persistente imposta por esta Spec. Não define tabelas, índices físicos ou migrations.

## 8. Impacto arquitetural

Cliente web/mobile coleta dados, apresenta confirmação e erros e utiliza a sessão conforme política; não decide papel ou autorização. Backend compartilhado valida credenciais e sessão. Camada de apresentação traduz contratos; aplicação coordena cadastro/login; infraestrutura protege credenciais e persiste Usuario. Domínio não importa FastAPI/ORM. ADR-001 restringe a separação. Não exige integração externa nem envio de e-mail nesta entrega. Persistência e proteção da unicidade são responsabilidades do backend.

## 9. Contratos necessários

| Operação | Entrada conceitual | Saída | Erros conceituais |
|---|---|---|---|
| Cadastrar | Nome, e-mail e senha | Confirmação e identidade pública | Entrada inválida, duplicidade, limite ou falha de persistência |
| Autenticar | E-mail e senha | Sessão JWT válida | Credenciais inválidas de modo genérico, limite excedido |
| Validar/encerrar sessão | Credencial de sessão | Identidade autenticada ou confirmação de encerramento | Sessão inválida/expirada/inutilizável pela política |

RF-02 estabelece `POST /api/v1/auth/login`; ADR-001 estabelece `/api/v1`, ambos preservados. [ADR-007](../07-arquitetura/adrs/ADR-007-autenticacao-spec001.md) registra rotas de cadastro, renovação, consulta do titular e logout, códigos de sucesso/erro, campos de resposta, claims JWT e persistência técnica. Contratos executáveis são publicados em `/api/v1/openapi.json`, com Swagger em `/api/v1/docs`. OPEN-15 permanece aberto somente para contratos de outras Specs e revisão formal; não falta contrato técnico para a autenticação implementada.

## 10. Requisitos não funcionais aplicáveis

| RNF | Verificação planejada | Evidência exigida |
|---|---|---|
| RNF-01 | Inspecionar criptografia de dados sensíveis em repouso e senha com hash e salt; capturar respostas e logs sem senha/hash; verificar HTTPS no ambiente de integração, inclusive rejeição de transmissão sensível sem proteção | Testes e inspeção de configuração sem expor credenciais |
| RNF-13 | Executar limite e tentativa excedente por cliente/endpoint na janela aprovada; validar comportamento nas fronteiras da janela e bloqueio | Relatório dos testes com parâmetros de OPEN-02 |
| RNF-05 | Exercitar o mesmo contrato de autenticação nos clientes web e mobile, conforme fase definida em OPEN-08 | Testes de contrato compartilhado e integração de cada cliente; não declarar compatibilidade integral sem ambos |
| RNF-11 | Verificar WCAG 2.1 AA nos formulários: teclado, leitor de tela e contraste | Relatório de acessibilidade com falhas corrigidas |
| RNF-15 | Comparar contrato implementado com OpenAPI/Swagger gerado | Teste de contrato e documentação sincronizada |
| RNF-16 | Executar testes/lint no PR e comprovar bloqueio de merge em caso de falha | Resultado da CI e evidência da proteção configurada; workflow sozinho não comprova bloqueio |
| RNF-20 | Exercitar cadastro/login em português e inglês, inclusive erros, com textos externalizados | Testes de interface e revisão dos recursos de tradução |
| RNF-17 | Conferir contrato publicado e operações desta entrega sob `/api/v1` | Teste de contrato e documentação da API |

Referência complementar: QT-01, QT-02 e QT-03 do [plano de qualidade](../09-qualidade/plano-qualidade.md). Resultados executados e limites de verificação estão no [registro de implementação](../09-qualidade/implementacao-SPEC-001.md); plano e execução são distinguidos, inclusive revisão manual de acessibilidade e checks obrigatórios remotos.

## 11. Critérios de Aceitação

- **CA-001** — **Dado** cadastro válido e e-mail livre, **Quando** cadastrar, **Então** criar exatamente um usuário comum e confirmar sem senha/hash.
- **CA-002** — **Dado** e-mail já existente segundo OPEN-16, **Quando** cadastrar novamente, **Então** rejeitar sem novo registro, inclusive em concorrência.
- **CA-003** — **Dado** usuário cadastrado, **Quando** autenticar com credenciais corretas, **Então** obter sessão JWT válida pela política de ADR-007.
- **CA-004** — **Dado** e-mail inexistente ou senha incorreta, **Quando** autenticar, **Então** retornar falha genérica equivalente, sem sessão.
- **CA-005** — **Dado** nome ausente, e-mail inválido ou senha fora da política de ADR-007, **Quando** cadastrar, **Então** rejeitar sem persistir usuário.
- **CA-006** — **Dado** cadastro com tentativa de escolher papel administrador, **Quando** processar, **Então** não conceder esse papel.
- **CA-007** — **Dado** cliente no limite aprovado, **Quando** ultrapassar 100 requisições/minuto no endpoint sensível, **Então** limitar o pedido conforme OPEN-02, sem autenticar o pedido excedente.
- **CA-008** — **Dado** sessão inválida, expirada ou encerrada segundo OPEN-01, **Quando** validar acesso, **Então** recusar sem dados pessoais; sessão válida identifica somente seu titular.
- **CA-009** — **Dado** cadastro/login realizado, **Quando** inspecionar respostas, logs e armazenamento, **Então** observar INV-001 e tráfego sensível protegido por HTTPS.
- **CA-010** — **Dado** contrato publicado, **Quando** consultar operações desta entrega, **Então** todas estão sob `/api/v1` e login preserva a rota de RF-02.

- **CA-011** — **Dado** cinco falhas consecutivas de login da mesma conta, **Quando** tentar novamente antes de quinze minutos, **Então** recusar autenticação, inclusive com senha correta durante o bloqueio; após o bloqueio aplicar a política aprovada e após sucesso zerar o contador. Testar sem revelar existência de conta (OPEN-18).

## 12. Casos de teste derivados

| Teste | Critérios / invariantes | Execução mínima planejada |
|---|---|---|
| T-001 | CA-001, CA-005; INV-001, INV-004 | Cadastro válido; ausência de cada campo; e-mail inválido; senha no limite e abaixo da política de ADR-007 |
| T-002 | CA-002; INV-002 | Duplicidade sequencial e concorrente; equivalência de e-mail conforme OPEN-16 |
| T-003 | CA-003, CA-004; INV-003 | Login válido, senha incorreta e e-mail ausente; comparar falhas e ausência de sessão |
| T-004 | CA-006; INV-004 | Tentar injetar papel administrativo no cadastro e conferir papel resultante |
| T-005 | CA-007; INV-006 | Limite, excedente, janela e isolamento entre clientes/endpoints conforme OPEN-02 |
| T-006 | CA-008; INV-005 | JWT válido, adulterado, expirado e encerrado; refresh/revogação segundo OPEN-01 |
| T-007 | CA-009; INV-001 | Inspecionar proteção da senha, respostas/logs e transporte HTTPS |
| T-008 | CA-010; RNF-05, RNF-15 | Validar contrato/prefixo, documentação e consumo pelo mesmo backend nos clientes, após OPEN-08 e OPEN-15 |
| T-009 | RNF-11, RNF-20 | Percorrer formulários e erros por teclado/leitor de tela; medir contraste e conferir português/inglês |
| T-010 | RNF-16 | Conferir testes/lint no PR e bloqueio de merge com check obrigatório falhando |
| T-011 | CA-011; INV-007 | Relógio injetado: quinta falha, instante anterior/exato ao fim de 15min, reset após sucesso, concorrência e rate limit independente; comportamento de inexistente em OPEN-18 |

Os testes desta entrega estão em `backend/tests/test_auth.py` e `frontend/tests/auth.spec.ts`, com smoke HTTPS em `scripts/smoke-auth.py`. O registro de implementação associa as evidências às linhas T desta tabela. Revisão manual com leitor de tela e proteção obrigatória de branch não foram presumidas.

| T-R01 | SPEC-001-R01; CA-001 | Executar cenário de CA-001 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R02 | SPEC-001-R02; CA-002 | Executar cenário de CA-002 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R03 | SPEC-001-R03; CA-003 | Executar cenário de CA-003 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R04 | SPEC-001-R04; CA-004 | Executar cenário de CA-004 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R05 | SPEC-001-R05; CA-005 | Executar cenário de CA-005 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R06 | SPEC-001-R06; CA-006 | Executar cenário de CA-006 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R07 | SPEC-001-R07; CA-007 | Executar cenário de CA-007 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R08 | SPEC-001-R08; CA-008 | Executar cenário de CA-008 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R09 | SPEC-001-R09; CA-009 | Executar cenário de CA-009 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R10 | SPEC-001-R10; CA-010 | Executar cenário de CA-010 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |
| T-R11 | SPEC-001-R11; CA-011 | Executar cenário de CA-011 com as entradas explícitas da seção 11 e comparar o resultado observável; preservar testes originais |

## 13. Questões em Aberto

- OPEN-01 e OPEN-02 — decisões técnicas de sessão/hash/limite adotadas em ADR-007; revisão formal do grupo pendente.
- OPEN-08 — esta entrega seleciona web responsiva; aplicação Expo e recorte final do MVP continuam pendentes.
- OPEN-15 — contratos de autenticação definidos por ADR-007 e OpenAPI; contratos do motor continuam pendentes, fora desta Spec.
- OPEN-16 — manter mínimo de 8 caracteres da baseline e equivalência de e-mail de ADR-007; não inventar evidência da aprovação histórica ausente.

O [registro central](questoes-abertas.md) distingue decisões adotadas tecnicamente das aprovações formais pendentes. Revisão manual WCAG com leitor de tela, validação em app nativo e configuração de checks obrigatórios no GitHub continuam limitações explicitadas, sem bloquear o uso local da entrega web.

- OPEN-18 — solução técnica implementada em 2026-10-23: bloqueio por e-mail normalizado, concorrência serializada no PostgreSQL, respostas genéricas e Retry-After. Ver ADR-007 e registro de execução.

## 14. Definition of Done da Spec

- [ ] Mapa revisado e aprovado pelo grupo, com responsável, data e evidência reais.
- [ ] Questões OPEN que afetam esta entrega resolvidas e refletidas na baseline antes da aprovação desta Spec.
- [ ] Spec revisada e aprovada individualmente, após o mapa.
- [x] Critérios funcionais da entrega web implementados, incluindo bloqueio RF-02/CA-011; ver registro de execução de 2026-10-23. Os RNFs e aprovações formais têm itens separados abaixo.
- [x] Suíte automatizada da entrega web executada e aprovada, com evidência ligada ao commit no registro; verificações manuais/operacionais dos RNFs continuam separadas.
- [ ] Todos os RNFs aplicáveis verificados pelos métodos da seção 10.
- [ ] Nenhuma divergência conhecida entre implementação e Spec; divergências da baseline explicitamente analisadas.

Esta lista distingue código validado de conclusão formal: itens sem marcação continuam pendentes, mesmo com implementação e testes funcionais executados. Se surgir conflito, registrar a divergência e corrigir a implementação para respeitar a baseline ou propor alteração da baseline para aprovação humana. Não alterar comportamento silenciosamente.

## Complemento de integração — 2026-10-22

RF-74 explicita renovação/logout já cobertos por esta implementação. RF-68 a RF-73 entram em unidades futuras do mapa; não fazem parte do código entregue. O RF-02 da main exige bloqueio de cinco falhas consecutivas por conta durante quinze minutos e reset após sucesso: esse comportamento ainda não estava implementado na consolidação de 2026-10-22 e foi concluído no complemento de 2026-10-23, com T-011. Evidências antigas não comprovam atendimento à baseline integrada. Fluxos futuros de confirmação/recuperação são públicos por token; autenticar-se não exige sessão prévia.

### Limite após consolidação de 2026-10-22

O checklist funcional acima se refere ao recorte original. RF-02 consolidado também exige bloqueio por conta após 5 falhas durante 15 minutos. Essa lacuna de 2026-10-22 foi resolvida no complemento de 2026-10-23 abaixo. Não considerar CA-007 suficiente para esse bloqueio. Sessões/logout entregues são rastreados também em RF-74; RF-68 a RF-72 serão refinados em SPEC-014 a SPEC-016 no mapa. Recuperação permanece fora desta implementação, mas integra o produto planejado. Validar formato não confirma posse de e-mail. Nenhuma nova API de conta é declarada implementada.

### Revisão documental do lote

Revisão em 2026-10-22 autorizada para documentação. Mantidos conteúdo original, IDs CA/INV/T e limites de implementação; adicionada rastreabilidade por cláusulas. Esta revisão não executa código nem substitui aprovação individual do grupo. [Cobertura completa](cobertura-requisitos.md).


### Complemento funcional desta entrega

CA-011/INV-007 recebem implementação de bloqueio por e-mail normalizado, compartilhado no banco; cinco falhas/quinze minutos, sucesso zera contador e expiração inicia nova sequência. Sessões já abertas continuam válidas. Contrato adicional: 429 login_temporarily_unavailable e Retry-After em segundos no quinto erro e durante o bloqueio; respostas são idênticas para endereço inexistente. Detalhes e risco de bloqueio abusivo constam no ADR-007. Os trechos históricos acima se referem ao estado anterior; resultados atuais constam no [registro desta entrega](../09-qualidade/implementacao-SPEC-001.md).

Novos testes em backend/tests/test_login_lock.py cobrem fronteiras temporais, concorrência, reset, inexistente, normalização, IPs/instâncias, limpeza e preservação de sessão. Frontend testa mensagem traduzida/contagem e demonstração fictícia sem rede. O relógio do demo não altera o servidor. Aprovação formal e verificações operacionais seguem separadas de código implementado.
