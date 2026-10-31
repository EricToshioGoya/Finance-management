# Plano — SPEC-015: confirmar posse do e-mail

## Decisões de implementação

- PostgreSQL recebe `email_verified_at` no usuário e uma tabela de tokens temporários com digest SHA-256, finalidade fixa, emissão, expiração, consumo e invalidação.
- O token bruto é gerado com `secrets.token_urlsafe(48)`, entregue somente ao adaptador e nunca persistido, retornado ou registrado.
- Solicitação exige sessão do próprio titular; confirmação é pública, atômica e responde somente estado verificado ou erro genérico do token.
- Reenvio é serializado pelo usuário: intervalo de 60 s, invalida o token ativo anterior somente depois de aceite do adaptador; falha de entrega preserva o anterior.
- O adaptador padrão falha fechado se não houver `FINNOVA_EMAIL_WEBHOOK_URL` HTTPS. O endpoint configurado recebe comando neutro de e-mail; seleção/credencial do provedor continua em OPEN-17.

## Fora do recorte

Alteração de e-mail, recuperação/troca de senha, fila/outbox e módulos financeiros pertencem às Specs próprias. Login e cadastro continuam possíveis para conta pendente, conforme RF-69.
