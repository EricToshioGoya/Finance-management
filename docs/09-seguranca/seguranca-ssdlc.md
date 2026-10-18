# Segurança e SSDLC — FinNova

- **Status:** rascunho
- **Última atualização:** 2026-10-18
- **Drivers arquiteturais:** DA-05 e DA-06 (`docs/07-arquitetura/arquitetura.md`); decisão registrada no ADR-005

Descreve como a segurança é tratada em cada etapa do ciclo de vida (Secure Software Development Life Cycle). As ferramentas citadas são propostas e serão confirmadas na Fase 4.

Os controles sobre o agente de codificação (permissões, hooks, Git hook local e CI) estão em `docs/09-seguranca/governanca-agentes.md`.

---

## 1. Ativos a proteger

| Ativo | Sensibilidade |
|---|---|
| Credenciais (senha, token JWT) | Alta |
| Dados financeiros pessoais (renda, despesas, patrimônio) | Alta (LGPD) |
| Segredos de integração (HMAC de webhooks, chaves de API) | Alta |
| Registros de auditoria | Média (integridade) |
| Eventos de uso | Baixa (sem conteúdo financeiro, RB-23) |

## 2. Requisitos de segurança e privacidade

| Requisito | Resumo |
|---|---|
| RNF-01 | HTTPS em todo o tráfego; dados sensíveis criptografados; senhas com hash e salt |
| RNF-02 | Usuário pode exportar e excluir seus dados (RF-05, RF-50) |
| RNF-13 | Rate limiting de 100 requisições por minuto em endpoints sensíveis |
| RNF-18 | Auditoria imutável de ações sensíveis |
| RNF-21 | Papel de administrador verificado no backend em toda rota administrativa |
| RNF-23 | Payload de webhook assinado com HMAC |
| RB-22, RB-23, RB-26 | Minimização: painel administrativo e benchmark sem dados financeiros individuais |
| SPEC-001 INV-01 a INV-03 | Sem senha em texto plano; e-mail único; erros de autenticação genéricos |

## 3. Modelagem de ameaças (STRIDE)

| Ameaça | Exemplo no FinNova | Mitigação | Requisito |
|---|---|---|---|
| **S**poofing (falsificação de identidade) | Força bruta no login | Rate limiting, bloqueio de 15 minutos após 5 tentativas inválidas, mensagens genéricas | RNF-13, RF-02, SPEC-001 |
| **T**ampering (adulteração) | Alteração de registros de auditoria | Tabela somente inserção | RNF-18 |
| **R**epudiation (repúdio) | Usuário nega exclusão ou exportação de dados | Auditoria com usuário, ação e data/hora | RNF-18 |
| **I**nformation disclosure (vazamento) | Usuário comum acessa rota administrativa; usuário lê lançamentos de outro usuário trocando o identificador na requisição; webhook expõe dados | RBAC no backend; filtro de posse por usuário dentro da consulta (ADR-005); HMAC e escopo mínimo no payload | RNF-21, RNF-02, RNF-23 |
| **D**enial of service (negação de serviço) | Excesso de requisições à API; indisponibilidade da API do BCB | Rate limiting; cache local de indicadores | RNF-13, ADR-003 |
| **E**levation of privilege (elevação de privilégio) | Cadastro público cria administrador | Promoção somente por outro administrador ou configuração inicial | RF-54 |

## 4. Práticas por etapa do ciclo de vida

| Etapa | Prática |
|---|---|
| Requisitos | Requisitos de segurança e privacidade com ID e enunciado EARS testável (seção 2) |
| Design | Modelagem de ameaças (seção 3) revista a cada novo módulo; decisões relevantes registradas em ADR |
| Implementação | Validação de entrada com Pydantic; consultas parametrizadas via SQLAlchemy; segredos apenas em variáveis de ambiente (`CLAUDE.md` C-10); CORS restrito às origens dos clientes |
| Verificação | Testes automatizados de RBAC e de autenticação; análise estática de segurança (proposta: Bandit); auditoria de dependências (proposta: `pip-audit`, `npm audit` e Dependabot); secret scanning do GitHub |
| Implantação | HTTPS obrigatório; configuração por ambiente; nenhum segredo em imagem Docker |
| Operação | Monitoramento de erros (RNF-12); backup diário com RPO de 24h e RTO de 4h (RNF-14); revisão periódica dos logs de auditoria |

## 5. LGPD

- Coleta mínima: o sistema não usa Open Finance nem dados bancários automáticos no MVP.
- Direitos do titular: exportação (RF-50) e exclusão de conta e dados (RF-05), inclusive dos dados de uso.
- Transparência: a política de privacidade informa a coleta de dados de uso agregados.

## 6. Checklist de segurança no PR

- [ ] Nenhum segredo ou dado pessoal real foi versionado.
- [ ] Entradas novas são validadas por schema.
- [ ] Rotas novas exigem autenticação; rotas administrativas verificam o papel.
- [ ] Logs não registram senha, token nem dado financeiro.
- [ ] Dependências novas foram justificadas e não têm vulnerabilidade conhecida.
