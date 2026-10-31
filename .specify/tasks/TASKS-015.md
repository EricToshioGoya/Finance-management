# Tarefas — SPEC-015

- [x] Criar migration aditiva para estado de verificação e digests de confirmação.
- [x] Implementar emissão, limite de reenvio, invalidação, expiração e consumo com bloqueio de linha.
- [x] Adicionar adaptador HTTPS configurável e falha segura sem provedor.
- [x] Publicar contratos `POST /api/v1/auth/email-confirmation` e `/confirm`.
- [x] Expor estado pendente/verificado no perfil e ação de reenvio no cliente web.
- [x] Cobrir token único, expiração/adulteração, digest/finalidade/TTL, reenvio, falha de envio e concorrência.
- [x] Atualizar Spec, requisitos, arquitetura, modelo, mapa e evidência de implementação.
- [ ] Configurar provedor/remetente/domínio e testar entrega operacional (OPEN-17).
