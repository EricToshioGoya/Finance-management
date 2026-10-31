# ADR-008 — Confirmação de e-mail por token opaco

- **Status:** adotado tecnicamente pela SPEC-015; configuração operacional do provedor pendente.
- **Contexto:** RF-69 exige confirmar o endereço sem guardar token bruto, aceitar um único uso e impedir reenvio acelerado.

## Decisão

Guardar no PostgreSQL somente o digest SHA-256, finalidade `email_confirmation`, emissão, validade de 24 h, consumo e invalidação. Gerar token com 48 bytes aleatórios codificados por URL. Reenvio autenticado é limitado a 60 s por titular e invalida token ativo anterior após o adaptador aceitar a entrega. A confirmação pública faz `SELECT ... FOR UPDATE`, recusa token expirado/inválido/consumido/inativado e marca usuário e token na mesma transação.

O adaptador padrão não envia sem `FINNOVA_EMAIL_WEBHOOK_URL` HTTPS; assim uma configuração ausente devolve erro sem invalidar token anterior nem marcar endereço. O web hook é uma fronteira de transporte, não uma escolha de provedor. OPEN-17 mantém credenciais, remetente, domínio, fila, retentativa e prova operacional.

## Consequências

Cadastro/login mantêm contas pendentes; `GET /me` expõe somente booleano `email_verified`, e futuras rotas financeiras devem negá-las enquanto falso. Token ou e-mail não aparecem em logs/respostas de erro. A entrega externa ainda não alcança semântica transacional exatamente uma vez; a próxima decisão de outbox/retry deverá preservar o consumo único.
