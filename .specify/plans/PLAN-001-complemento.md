# Plano do complemento SPEC-001

Pedido: concluir a primeira Spec e tornar seu comportamento visualizável. Escopo: RF-02/CA-011, regressão do fluxo existente e demonstração isolada. Baseline: branch docs/specs-completas-sdd.

1. Persistir tentativas por HMAC do e-mail normalizado, inclusive inexistente, com migration aditiva.
2. Serializar por linha no PostgreSQL, manter bloqueio por quinze minutos após cinco falhas e reset por sucesso/expiração; preservar IP rate limit e sessões existentes.
3. Injetar relógio UTC e testar com PostgreSQL de desenvolvimento isolado; nenhum banco de produção.
4. Traduzir erro/Retry-After e mostrar prazo no cliente real.
5. Exportar demonstração fictícia sem rede com a mesma interface; relógio acelerado somente na demonstração.
6. Rodar verificações documentais, lint/build, suíte de API com cobertura e navegador/acessibilidade automática. Registrar limitações reais de ambiente.

Contrato concreto, antienumeração e risco de bloqueio abusivo no ADR-007. Não implementar confirmação de e-mail, recuperação ou edição de perfil nesta Spec. Não presumir revisão/assinatura do colega nem aprovação formal do grupo.
