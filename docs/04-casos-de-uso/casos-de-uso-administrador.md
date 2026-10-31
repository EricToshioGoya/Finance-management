# FinNova — Casos de Uso do Administrador

## Visão geral

Este documento descreve os casos de uso relacionados à administração da plataforma FinNova, incluindo o painel administrativo de acesso restrito e as rotinas automáticas de manutenção e sincronização de dados.


## Diagrama

![Diagrama de casos de uso do administrador](casos-de-uso-administrador.png)

## Atores

- **Administrador**: acessa o painel administrativo para consultar usuários, permissões, uso do sistema e trilhas de auditoria.
- **Usuário**: pode solicitar a exclusão dos próprios dados de uso junto com a conta.
- Rotinas de sincronização e agendamento são internas ao FinNova; fontes de dados continuam atores externos. Se um agendador externo for adotado, essa fronteira deve ser revista.
- **API Banco Central (SGS) e Tesouro Transparente**: fornece indicadores oficiais para sincronização.
- **Portal de Dados Abertos da CVM**: fornece documentos e indicadores públicos da CVM.

## Casos de uso

### Painel Administrativo (acesso restrito)

| Caso de uso | Requisito relacionado | Descrição |
| --- | --- | --- |
| Acessar painel administrativo | RF-54 | Permite ao administrador entrar no painel, após validação do papel administrativo. |
| Validar papel de administrador (RBAC) | RB-21, RNF-21 | Valida no backend se o usuário possui o papel necessário para acessar cada rota administrativa. |
| Listar e buscar usuários | RF-55 | Permite consultar e localizar usuários cadastrados. |
| Consultar distribuição de perfil de investidor | RF-56 | Exibe a distribuição dos perfis de investidor dos usuários. |
| Consultar uso por módulo/aba | RF-57 | Exibe métricas agregadas de utilização por módulo ou aba. |
| Consultar engajamento e usuários recorrentes | RF-58 | Permite acompanhar o engajamento e identificar usuários recorrentes. |
| Consultar trilha de auditoria | RNF-18 | Permite consultar os registros imutáveis de ações administrativas e eventos de uso. |
| Criar/promover administrador | OPEN-13 | Decisão pendente; RF-54 protege acesso e não especifica promoção. Esta funcionalidade não é considerada definida. |

### Rotinas automáticas do sistema

| Caso de uso | Requisito relacionado | Ator ou integração | Descrição |
| --- | --- | --- | --- |
| Sincronizar documentos e indicadores da CVM | RF-30, RF-32 | Rotina interna; Portal de Dados Abertos da CVM | Obtém e atualiza documentos e indicadores disponibilizados pela CVM. |
| Sincronizar indicadores oficiais em cache | RF-23 | Rotina interna; API Banco Central e Tesouro Transparente | Consulta indicadores oficiais e mantém os dados disponíveis em cache. |
| Expurgar dados sincronizados (12 meses) | RF-33, RNF-10 | Rotina interna | Remove dados sincronizados com mais de 12 meses, sem ação manual. |
| Registrar evento de uso | RF-59 | Rotina interna | Registra o usuário, o módulo, a ação e o timestamp, sem armazenar conteúdo financeiro. |
| Registrar log de auditoria imutável | RNF-18, RB-19 | Sistema | Registra acessos e ações administrativas sem permitir alteração ou exclusão. |
| Excluir dados de uso junto com a conta | RF-05, RF-59 | Usuário | Exclui os dados de uso agregados quando o usuário solicita a exclusão da conta. |

## Relações entre os casos de uso

- **Acessar painel administrativo** inclui **Validar papel de administrador (RBAC)**.
- As consultas exigem sessão administrativa como pré-condição; não representam novo login/acesso ao painel a cada consulta.
- **Acessar painel administrativo**, **Listar e buscar usuários**, **Consultar uso por módulo/aba**, **Consultar distribuição de perfil de investidor**, **Consultar engajamento e usuários recorrentes** e **Consultar trilha de auditoria** registram auditoria conforme RNF-18; a condição é detalhada pelo comportamento. Não usar include para um passo condicional.
- **Registrar evento de uso** é utilizado pelas rotinas do sistema e pelas ações que precisam gerar métricas de uso.
- Exclusão de conta trata eventos de uso conforme OPEN-05; não inclui recriar o evento que se pretende excluir. A ação sensível registra auditoria conforme política de retenção, sem conservar dados identificáveis indefinidamente.
- **Sincronizar documentos e indicadores da CVM** e **Sincronizar indicadores oficiais em cache** podem ser executados pelo **Rotina interna** e dependem das respectivas fontes externas.

## Regras de negócio e requisitos não funcionais

- **RB-21 / RNF-21 — Validar papel:** o acesso a qualquer rota administrativa é validado no backend por papel. A interface não é considerada mecanismo de segurança; toda rota `/api/v1/admin/*` exige verificação de papel.
- **RB-22 — Listar usuários e consultar uso:** o painel não exibe dados financeiros individuais. São permitidos apenas metadados de conta e métricas agregadas de uso.
- **RB-23 — Registrar evento de uso:** o evento armazena somente usuário, módulo, ação e timestamp; não armazena conteúdo financeiro.
- **RB-19 / RNF-18 — Log de auditoria:** o registro não aceita edição/exclusão operacional; retenção e anonimização dependem da política OPEN-05. Todo acesso ao painel administrativo deve ser registrado.
- **OPEN-13 — Administração:** definir criação inicial/promoção se adotada; nunca conceder papel administrativo pelo cadastro público (RB-27).
- **RNF-04 — Registrar evento de uso:** a coleta é assíncrona e não deve impactar a performance percebida pelo usuário.
- **RNF-10 / RB-12 — Expurgar dados:** metadados e indicadores sincronizados são removidos 12 meses após a sincronização, sem ação manual.
- **LGPD:** a política de privacidade informa a coleta de dados de uso agregados. O usuário pode solicitar a exclusão desses dados junto com a exclusão da conta, conforme o **RF-05**.

## Generalização

O **Administrador** é uma especialização do **Usuário**. Portanto, além dos casos de uso administrativos descritos neste documento, o administrador também pode executar os casos de uso disponíveis para um usuário comum.


## Identificadores administrativos

| ID | Caso | Origem |
|---|---|---|
| UC-17 | Acessar painel administrativo | RF-54, RB-21, RNF-21 |
| UC-18 | Listar e buscar usuários | RF-55, RB-22 |
| UC-19 | Consultar métricas administrativas | RF-56, RF-57, RF-58 |
| UC-20 | Sincronizar dados externos | RF-23, RF-30, RF-32 |
| UC-21 | Expurgar dados sincronizados | RF-33, RNF-10 |
| UC-22 | Registrar evento de uso/auditoria | RF-59, RNF-18 |

Fonte editável da vista: [DOT](casos-de-uso-administrador.dot); [SVG](casos-de-uso-administrador.svg). A imagem apresenta o recorte administrativo, sem inventar requisito de promoção.


## Fronteira com a manutenção de conta

RF-68 a RF-74 são operações do titular, não autorização para um administrador consultar senhas, tokens ou finanças individuais. RF-54/RNF-21 exigem autorização no servidor; listar usuários não substitui esse controle. O papel existente no banco não representa painel administrativo implementado. Promoção inicial de administrador permanece em OPEN-13.
