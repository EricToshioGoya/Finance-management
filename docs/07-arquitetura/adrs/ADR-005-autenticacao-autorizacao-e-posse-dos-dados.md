# ADR-005: Autenticação por JWT, Autorização por Papel e Posse dos Dados por Usuário

* **Status:** parcialmente substituído na integração de 2026-10-22 pelo ADR-007-autenticacao-spec001.md (sessão, renovação e logout); autorização por papel e titularidade permanecem requisitos
* **Data:** 2026-10-18
* **Decisores:** Equipe de Arquitetura FinNova
* **Drivers atendidos:** DA-05, DA-06

## Contexto e Problema
O FinNova guarda dados financeiros pessoais e atende clientes web e mobile pela mesma API (RNF-05). É preciso autenticar o usuário (RF-01, RF-02), proteger as credenciais (RNF-01), resistir a força bruta (RF-02: bloqueio após 5 tentativas; RNF-13), restringir as rotas administrativas por papel (RNF-21) e garantir que cada usuário acesse apenas os próprios dados (RNF-02, LGPD; DOM-01, DOM-03 e DOM-08 do modelo de domínio). Um erro em qualquer desses pontos expõe dados de todos os usuários.

## Decisão
1. **Autenticação:** token JWT assinado, sem estado no servidor, com identificador do usuário e expiração; senha armazenada com hash e salt (Bcrypt ou Argon2).
2. **Força bruta:** bloqueio das tentativas de login para o e-mail por 15 minutos após 5 falhas consecutivas, com mensagem genérica exista ou não a conta, e rate limit de 100 requisições por minuto por cliente nos endpoints de autenticação.
3. **Autorização por papel:** o papel (`usuario` ou `administrador`) é verificado no backend, na camada de aplicação, antes de executar o caso de uso; toda rota `/api/v1/admin/*` exige o papel de administrador.
4. **Posse dos dados (negar por padrão):** toda leitura e alteração de dado financeiro é filtrada pelo `usuario_id` do token dentro da própria consulta do repositório. Categorias padrão, que não têm dono, são somente leitura para todos.

## Alternativas Consideradas
* **Sessão no servidor com cookie:** descartada, porque mantém estado no backend e complica o uso pelo cliente mobile.
* **Provedor de identidade externo (OAuth2/OIDC):** descartado no MVP pelo custo de integração; o login social está fora do escopo da SPEC-001.
* **Verificar a posse depois de carregar o registro:** descartada, porque basta esquecer a verificação em uma rota para vazar dados; o filtro na consulta garante o isolamento por construção.

## Consequências
### Positivas:
* O mesmo mecanismo atende web e mobile, sem estado de sessão no servidor.
* O isolamento entre usuários é garantido pela forma da consulta, e não pela lembrança de cada desenvolvedor.
* Autorização e posse são testáveis em testes de integração dedicados.

### Negativas:
* Revogar um token antes da expiração exige expiração curta ou refresh token, ainda em aberto (SPEC-001, OPEN-01 e OPEN-03).
* Todo repositório de dados financeiros precisa receber o usuário autenticado como parâmetro obrigatório.


## Reconciliação

JWT sem estado e refresh pendente descrevem a proposta anterior. A implementação usa sessão persistida e revogável conforme `ADR-007-autenticacao-spec001.md`. O bloqueio por conta após cinco falhas foi implementado no complemento de 2026-10-23 do ADR-007, além do rate limit já entregue.

## Reconciliação em 2026-10-22

A alternativa de JWT sem estado está **substituída pelo ADR-007** para a sessão implementada. Este arquivo preserva a decisão histórica; autorização e isolamento por titular continuam requisitos. Bloqueio por conta de 5 falhas/15 minutos permanece pendente de implementação conforme RF-02. Não interpretar o estado histórico “Aceito” como comprovação de código ou testes dessas capacidades.
