# Plano de qualidade — FinNova

Plano original de 2026-10-09, atualizado em 2026-10-15. Estratégia ligada à baseline; SPEC-001 agora tem aplicação e testes executáveis, com resultados no registro de implementação. A tabela abaixo é estratégia: resultados não são presumidos para as demais Specs. O material de qualidade orienta atributos e prevenção; não foi presumido um checklist específico além do material fornecido.

| Caso | Risco / atributo | Origem | Verificação planejada | Resultado esperado |
|---|---|---|---|---|
| QT-01 | Cadastro duplicado / confiabilidade | RF-01, RB-27, SPEC-001 | Integração: duplicidade e concorrência | No máximo um usuário por e-mail segundo a equivalência aprovada em OPEN-16 |
| QT-02 | Credencial exposta / segurança | RNF-01, SPEC-001 | Respostas, persistência e logs | Senha/hash não aparecem em resposta/log; senha não é armazenada em claro |
| QT-03 | Acesso a dados alheios / segurança | RB-29, RNF-21 | Integração: usuário A tenta ler/alterar B; usuário comum chama admin | Negar sem expor nem alterar dados |
| QT-04 | Cálculo incorreto / adequação | RF-22, RB-10, RB-28, SPEC-002 | Unitário: equivalência, aportes, zero e erro | Resultados da matriz abaixo; política numérica em OPEN-03 |
| QT-05 | Duplicidade de saldo / confiabilidade | RB-03, RF-11 | Integração: incluir, editar, excluir e repetir operação | Totais coerentes com dados persistidos, sem efeito duplicado |
| QT-06 | Cache inválido / resiliência | RB-11, RNF-09, ADR-003 | Integração com fonte simulada: cache válido/vencido/ausente | Dado válido com referência; vencido/ausente não vira taxa atual |
| QT-07 | Lentidão / eficiência | RNF-04 | Carga no ambiente definido em OPEN-06 | P95 < 3s no perfil registrado |
| QT-08 | Interface inacessível / usabilidade | RNF-03, RNF-11 | Teclado, leitor de tela, contraste e etapas de navegação | Fluxo acessível e registro em até 3 etapas; registrar critérios e evidência |
| QT-09 | Perda de dados / recuperabilidade | RNF-14 | Restauração em ambiente separado | RPO 24h e RTO 4h medidos; não reintroduzir dados excluídos sem política |
| QT-10 | Regressão / manutenibilidade | RNF-07, RNF-16 | CI com testes e lint a cada PR | Falha impede merge quando proteção estiver configurada; cobertura de linhas >= 80% nas regras financeiras |

## Rastreabilidade dos testes das Specs

As listas mínimas por Spec estão na seção 12 de [SPEC-001](../08-specs/SPEC-001.md) e [SPEC-002](../08-specs/SPEC-002.md); cada uma liga testes a critérios CA e invariantes INV locais. Este plano complementa essas listas, não as substitui.

- QT-01 e QT-02: SPEC-001, T-001/T-002/T-004/T-007.
- QT-03: validação de sessão em SPEC-001, T-006; autorização por objeto/papel exige também testes das Specs consumidoras.
- QT-04: SPEC-002, T-001 a T-007; incluir conversão mensal → anual e equivalência de prazos.
- QT-07 e QT-10: SPEC-002, T-008; CI de autenticação em SPEC-001, T-010.
- QT-08: formulários de SPEC-001 em T-009; limite de três passos de RNF-03 se refere a lançamento financeiro e deve ser conferido na SPEC-006, não no motor.

Testes de produto da SPEC-001 foram executados e estão no [registro de implementação](implementacao-SPEC-001.md). Testes de motor/cálculos das demais Specs continuam somente planejados. A verificação documental não substitui esta matriz nem a aprovação humana.

## Referências numéricas para o motor

Taxas percentuais são normalizadas: 12 representa 12% e 0,12 é sua fração; aportes ocorrem no fim do mês.

| Inicial | Aporte mensal | Taxa | Prazo | Montante bruto esperado |
|---|---|---|---|---|
| 1000 | 0 | 12% anual | 12 meses | 1120,00 exibido; mensal aproximadamente 0,9488792935% |
| 0 | 100 | 1% mensal | 2 meses | 201,00 |
| 1000 | 0 | 12% anual | 1 ano | 1120,00 exibido; equivalente a 12 meses |
| 100 | 10 | 0% mensal | 2 meses | 120,00 |
| 0 | 0 | 0% mensal | 1 mês | 0,00 |
| negativo | qualquer | qualquer | positivo | Erro de parâmetro, sem resultado |
| não negativo | não negativo | negativa | positivo | Erro de parâmetro |
| não negativo | não negativo | não negativa | zero ou fracionário | Erro de parâmetro |

Conversão inversa: 1% mensal equivale aproximadamente a 12,6825030132% anual, não a 12% anual.

A raiz de equivalência não é decimal finita; a implementação deverá comparar pela tolerância e arredondamento aprovados em OPEN-03, sem igualdade literal de uma aproximação.

## Registro de execução

Para cada teste real: registrar ID QT/Spec, versão/commit, ambiente, entradas, resultado, responsável, data e link à evidência. A documentação nesta revisão foi conferida quanto a IDs, links, exemplos matemáticos e imagens. Isso não substitui execução de produto, medição de carga ou teste de segurança.


## Verificação do ciclo de conta — RF-68 a RF-74

Cobrir acesso cruzado a perfil/preferências/sessões, confirmação e troca de e-mail, unicidade concorrente, recuperação com resposta genérica, tokens inválidos/expirados/reutilizados, intervalo de reenvio, senha atual incorreta, revogação global e rejeição financeira de conta não verificada. Validar rate limit e, separadamente, cinco falhas por conta/15 minutos de RF-02. Não incluir senhas, tokens brutos nem links de recuperação nos logs/auditoria.

RF-05/RF-50 exigem testes de exportação/exclusão por titular; RNF-14 exige backup e restauração isolada com evidência de RPO/RTO e exclusões reaplicadas. RF-54/RNF-21 exigem testes de autorização administrativa no servidor. Testes das novas capacidades são planejados; resultados históricos da SPEC-001 não comprovam sua execução. Workflow configurado também não comprova checks obrigatórios remotos, operação de backups ou monitoramento em produção.

## Verificação do ciclo de conta — planejamento de 2026-10-22

A [matriz de cobertura](../09-qualidade/cobertura-funcional.md) é a referência de situação: documentado não significa implementado. Testar RF-68 a RF-73 com titular A/B, validação no servidor, senha atual incorreta, token expirado/adulterado/usado, finalidade diferente, reenvio, falha de e-mail, unicidade concorrente e rollback. Validar revogação de todas as sessões após troca/recuperação/exclusão e logout imediato da sessão atual.

RF-02 exige teste de 5 falhas/15 minutos e reset após sucesso, distinto de RNF-13 (100 pedidos/minuto por IP/endpoint); a primeira proteção ainda falta no código. Exportação/exclusão precisam de testes de isolamento, reautenticação, expiração de arquivo, retenção e restauração sem ressuscitar dados excluídos (OPEN-05). Nunca registrar tokens, senhas, links secretos ou conteúdo financeiro em auditoria/logs. Proteger segredos de e-mail fora do Git; decidir provedor e política em OPEN-17.

Migrations futuras devem preservar usuários existentes, aplicar restrições e ter verificação em banco de teste. Para módulos financeiros, validar integridade e isolamento por titular, além de cálculo puro e invariantes do patrimônio. Esses testes são planejados; o registro de implementação de SPEC-001 contém apenas evidências históricas do recorte entregue.
