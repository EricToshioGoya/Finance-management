# Modelo de Domínio — FinNova

> Ciclo completo: (1) termos de domínio extraídos dos RF/RB, (2) classes candidatas e responsabilidades, (3) diagrama de classes do domínio V1, (4) rastreabilidade RF/RB → classes (replicada nas Issues).
>
> Referência completa dos requisitos: `/docs/03-requisitos/requisitos.md`. Este documento cobre o **modelo de domínio (conceitual/OO)** — não deve ser confundido com o modelo de dados relacional da seção 4 de `requisitos.md`, que é o modelo de persistência (tabelas). Aqui, `Renda`, `Meta` e `PatrimonioItem` aparecem como hierarquias (generalização/especialização) para expressar comportamento comum entre subtipos — uma decisão de modelagem OO que a tabela relacional não precisa refletir 1:1.

---

## 1. Termos de domínio extraídos das stories/RF

Revisão de `requisitos.md` (RF-01 a RF-67) destacando os substantivos que representam conceitos do negócio:

| Módulo | Termos de domínio identificados |
|---|---|
| Conta e Acesso | Usuário, Perfil de investidor, Papel (usuário/administrador) |
| Administração Financeira | Conta, Cartão, Categoria, Renda fixa, Renda variável, Bônus/PLR, Despesa, Meta geral, Meta por categoria |
| Simulador de Investimentos | Simulação, Meta financeira, Indicador oficial (Selic/CDI/IPCA), Cotação |
| Relatórios de Empresas | Empresa aberta, Documento CVM, Indicador financeiro, Watchlist |
| Patrimônio | Ativo, Passivo, Patrimônio líquido, Meta nomeada |
| Score de Saúde Financeira | Score de saúde, Fator de ponderação, Benchmark |
| Conteúdo Educacional | Conteúdo educacional, Termo |
| Compras Financiadas | Compra financiada, Parcela, Amortização |
| Recursos transversais | Notificação, Exportação, Webhook, Evento de uso, Log de auditoria |
| Painel Administrativo | Administrador, Dashboard de uso |
| Contas Compartilhadas | Conta compartilhada, Despesa compartilhada, Acerto de contas |
| Aposentadoria/Previdência/Impostos | Simulação de aposentadoria, PGBL, VGBL, Estimativa de IR, Informe de rendimentos |
| Gamificação | Badge/Conquista |

---

## 2. Classes candidatas e responsabilidades

| Classe | Responsabilidade principal | RF/RB de origem |
|---|---|---|
| `Usuario` | Autenticar-se, manter preferências (idioma, tema, perfil de investidor) e ser o agregador raiz de todos os dados financeiros pessoais | RF-01, RF-02, RF-03 |
| `Conta` | Representar uma conta bancária/carteira e expor o saldo atual | RF-12 |
| `Cartao` | Controlar limite e ciclo de fatura; calcular limite disponível (RB-04) | RF-12, RF-13 |
| `Categoria` | Classificar despesas em áreas de gasto (padrão ou personalizada) | RF-10 |
| `Renda` (abstrata) | Generalizar o comportamento comum de qualquer entrada de renda; calcular contribuição mensal | RF-06, RF-07, RF-08 |
| `RendaFixa` / `RendaVariavel` / `BonusPLR` | Especializações de `Renda`, cada uma com sua regra de cálculo (RB-05, RB-06) | RF-06, RF-07, RF-08 |
| `Despesa` | Representar um gasto, opcionalmente recorrente ou compartilhado | RF-09, RF-11 |
| `Meta` (abstrata) | Generalizar metas do usuário; calcular progresso | RF-14, RF-15 |
| `MetaGeral` / `MetaCategoria` / `MetaFinanceira` / `MetaNomeada` | Especializações de `Meta` por escopo (renda/gasto geral, categoria, projeção de investimento, objetivo nomeado vinculado a um ativo) | RF-14, RF-15, RF-26, RF-40 |
| `Simulacao` | Executar um cálculo financeiro (motor de juros compostos, RB-10) e armazenar parâmetros/resultado — reaproveitada por renda fixa, variável, aposentadoria, IR e stress test | RF-20 a RF-28, RF-39, RF-62 a RF-64 |
| `EmpresaAberta` | Representar uma companhia listada em bolsa | RF-29 |
| `DocumentoCVM` | Guardar metadados de um documento oficial e o link externo (nunca o binário) | RF-30, RF-31, RB-12 |
| `IndicadorFinanceiro` | Guardar um indicador estruturado extraído dos dados abertos da CVM | RF-32 |
| `Watchlist` | Vincular um usuário a empresas de interesse | RF-34 |
| `PatrimonioItem` (abstrata) | Generalizar itens que compõem o patrimônio, com valor e origem (automática/manual) | RF-35 |
| `Ativo` / `Passivo` | Especializações de `PatrimonioItem`; calculam a cor do mapa de calor patrimonial (RB-14) | RF-35, RF-37 |
| `ScoreSaude` | Calcular e manter a nota de saúde financeira do usuário | RF-41, RF-42 |
| `CompraFinanciada` | Simular um financiamento e, ao ser confirmada, gerar um `Passivo` (RB-16) | RF-45 a RF-47 |
| `Notificacao` | Representar e enviar um alerta ao usuário pelo canal habilitado | RF-48, RF-49 |
| `WebhookSubscription` | Configurar e assinar (HMAC) o payload enviado a sistemas externos | RF-53, RNF-23 |
| `AuditLog` | Registrar de forma imutável ações sensíveis do usuário/administrador | RF-54, RNF-18 |
| `EventoUso` | Registrar eventos de uso agregáveis para os dashboards administrativos | RF-59, RB-22, RB-23 |
| `ConteudoEducacional` | Fornecer verbetes explicativos e ajuda contextual | RF-43, RF-44 |
| `ContaCompartilhada` | Vincular dois usuários e controlar o ciclo de vida do vínculo | RF-60 |
| `DespesaCompartilhada` | Registrar a divisão de uma `Despesa` entre os dois usuários vinculados | RF-61, RB-24 |
| `AcertoConta` | Registrar um pagamento entre os dois usuários que reduz o saldo pendente | RF-61, RB-24 |
| `Badge` | Representar uma conquista obtida pelo usuário | RF-67 |

> **Nota de design:** `Simulacao` concentra vários tipos de cálculo (renda fixa, variável, aposentadoria, IR, stress test); no refinamento para V2, é candidata a adotar o padrão **Strategy** (uma `EstrategiaDeSimulacao` por tipo), evitando um único método `executar()` com múltiplos `if/switch` por `tipo`.

---

## 3. Diagrama de classes do domínio (V1)

![Diagrama de classes do domínio — FinNova](diagrama-de-dominio.png)

Fonte editável (Mermaid): `diagrama_dominio.mmd`. Para regenerar a imagem após editar o `.mmd`:

```bash
mmdc -i diagrama_dominio.mmd -o diagrama-de-dominio.png -b white -w 2200 -H 2400 --scale 2
```

### Principais relações do diagrama

- `Usuario` é o agregador raiz: possui contas, cartões, categorias, rendas, despesas, metas, simulações, itens de patrimônio, score, compras financiadas, notificações, webhooks, logs de auditoria, eventos de uso e badges.
- `Renda`, `Meta` e `PatrimonioItem` são classes abstratas com especializações (generalização/herança), reduzindo duplicação de regra entre subtipos.
- `Despesa` pode ser debitada de uma `Conta` ou de um `Cartao`, pertence a uma `Categoria`, e pode ser referenciada por uma `DespesaCompartilhada`.
- `ContaCompartilhada` vincula exatamente 2 `Usuario`, agrupa `DespesaCompartilhada` e registra `AcertoConta` (RF-60/61).
- `CompraFinanciada`, ao ser confirmada como real, gera um `Passivo` (RB-16).
- `EmpresaAberta` publica `DocumentoCVM` e reporta `IndicadorFinanceiro`; `Watchlist` liga `Usuario` a `EmpresaAberta`.

---

## 4. Rastreabilidade RF/RB → Classes do domínio

| Classe | RFs relacionados | RBs relacionadas |
|---|---|---|
| Usuario | RF-01, RF-02, RF-03, RF-04, RF-05 | RB-09 |
| Conta / Cartao | RF-12, RF-13 | RB-04 |
| Categoria | RF-10 | RB-02 |
| Renda / RendaFixa / RendaVariavel / BonusPLR | RF-06, RF-07, RF-08 | RB-01, RB-05, RB-06 |
| Despesa | RF-09, RF-11 | RB-01, RB-02 |
| Meta / MetaGeral / MetaCategoria / MetaFinanceira / MetaNomeada | RF-14, RF-15, RF-19, RF-26, RF-40 | RB-18 |
| Simulacao | RF-20 a RF-28, RF-39, RF-62, RF-63, RF-64 | RB-07, RB-08, RB-10, RB-17, RB-25 |
| EmpresaAberta / DocumentoCVM / IndicadorFinanceiro / Watchlist | RF-29 a RF-34 | RB-12 |
| PatrimonioItem / Ativo / Passivo | RF-35, RF-36, RF-37, RF-38 | RB-13, RB-14 |
| ScoreSaude | RF-41, RF-42, RF-66 | RB-15, RB-26 |
| CompraFinanciada | RF-45, RF-46, RF-47 | RB-16 |
| Notificacao | RF-48, RF-49 | — |
| WebhookSubscription | RF-52, RF-53 | — (RNF-23) |
| AuditLog | RF-54 | — (RNF-18, RNF-21) |
| EventoUso | RF-55 a RF-59 | RB-22, RB-23 |
| ConteudoEducacional | RF-43, RF-44 | — |
| ContaCompartilhada / DespesaCompartilhada / AcertoConta | RF-60, RF-61 | RB-24 |
| Badge | RF-67 | — |
