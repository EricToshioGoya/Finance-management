# Benchmark — FinNova

- **Status:** rascunho
- **Data da pesquisa:** 2026-10-18
- **Objetivo:** comparar soluções existentes com a proposta do FinNova e evidenciar a lacuna que o projeto ocupa (ver `visao.md`, seção 1).

---

## 1. Soluções analisadas

| Solução | Foco principal | Público |
|---|---|---|
| **Mobills** | Controle financeiro pessoal (gastos, cartões, orçamento) | Pessoa física |
| **Organizze** | Controle financeiro pessoal e de pequenas empresas | Pessoa física e jurídica |
| **Kinvo** | Consolidação e acompanhamento de carteira de investimentos | Investidor pessoa física |
| **Gorila** | Consolidação e análise de investimentos (GorilaVIEW) | Investidor pessoa física e profissionais de investimento |

## 2. Comparativo de funcionalidades

Legenda: ✅ oferece · ⚠️ parcial ou limitado · ❌ não identificado nas fontes consultadas.

| Funcionalidade | Mobills | Organizze | Kinvo | Gorila | FinNova (proposta) |
|---|---|---|---|---|---|
| Registro de gastos por categoria | ✅ | ✅ | ❌ | ❌ | ✅ RF-09, RF-10 |
| Controle de cartão e fatura | ✅ | ✅ | ❌ | ❌ | ✅ RF-12, RF-13 |
| Orçamento e metas de gasto | ✅ | ✅ | ⚠️ metas de investimento | ❌ | ✅ RF-14, RF-15 |
| Sincronização bancária automática | ✅ | ✅ Open Finance | ⚠️ falhas em algumas integrações | ✅ via B3 | ❌ fora do escopo do MVP |
| Consolidação de carteira de investimentos | ❌ | ❌ | ✅ | ✅ | ⚠️ manual, via Patrimônio (RF-35) |
| Rentabilidade comparada a CDI, IPCA e Ibovespa | ❌ | ❌ | ✅ | ⚠️ rentabilidade por produto | ⚠️ comparação entre cenários (RF-25) |
| Simulação de renda fixa com taxas oficiais (SGS/Tesouro) | ❌ | ❌ | ❌ | ❌ | ✅ RF-20, RF-23 |
| Conexão entre sobra do orçamento e simulação de investimento | ❌ | ❌ | ❌ | ❌ | ✅ RF-26 |
| Experiência adaptada ao perfil de investidor | ❌ | ❌ | ❌ | ❌ | ✅ RF-03, RB-09 |
| Relatórios de empresas com dados abertos da CVM | ❌ | ❌ | ❌ | ❌ | ✅ RF-29 a RF-33 |
| Conteúdo educacional contextual | ❌ | ❌ | ❌ | ❌ | ✅ RF-43, RF-44 |
| Web e mobile | ✅ | ✅ | ✅ | ✅ | ✅ RNF-05 |
| Plano gratuito | ⚠️ limitado | ⚠️ limitado | ⚠️ até 10 ativos | ✅ com limites | ✅ projeto acadêmico |

## 3. Conclusões

1. **Mobills e Organizze** resolvem o controle de gastos, mas não ajudam a decidir o que fazer com a sobra do orçamento.
2. **Kinvo e Gorila** consolidam quem já investe, mas não tratam orçamento nem atendem bem quem ainda não investe.
3. **Lacuna ocupada pelo FinNova:** ligar "quanto sobra" a "quanto isso pode render", com taxas oficiais e linguagem adaptada ao nível do usuário.
4. **Diferencial a não perseguir no MVP:** sincronização bancária automática (Open Finance), já oferecida pelos concorrentes e fora do escopo do FinNova.

## 4. Limitações

- Os sites oficiais não puderam ser acessados no momento da pesquisa; as informações vêm da App Store, de artigos especializados e de páginas de terceiros listadas abaixo.
- Preços não foram comparados porque as fontes trazem valores divergentes e possivelmente desatualizados.

## 5. Fontes

- [Mobills — App Store](https://apps.apple.com/BR/app/id921838244)
- [Canaltech — Organizze ou Mobills: qual aplicativo é melhor para controlar gastos](https://canaltech.com.br/apps/organizze-ou-mobills-qual-aplicativo-melhor-para-controlar-gastos/)
- [Organizze — App Store](https://apps.apple.com/BR/app/id677699286)
- [Canaltech — Como usar o Organizze](https://canaltech.com.br/apps/como-usar-organizze/)
- [B3 Bora Investir — 4 apps que consolidam sua carteira](https://borainvestir.b3.com.br/objetivos-financeiros/investir-melhor/organize-seus-investimentos-4-apps-que-consolidam-sua-carteira/)
- [Investidor10 — Ferramentas para acompanhar investimentos](https://investidor10.com.br/amp/conteudo/ferramentas-controle-de-investimento/)
- [Reclame Aqui — Kinvo Premium: problemas de integração](https://www.reclameaqui.com.br/kinvo/kinvo-premium-problemas-de-integracao-e-falta-de-suporte-na-plataforma_mFUNgx4XsG8hJO1_/)
- [Quero Bolsa — Gorila Invest](https://querobolsa.com.br/revista/gorila-invest)
- [InfoMoney — IA do Gorila analisa carteiras](https://www.infomoney.com.br/advisor/essa-ia-le-sua-carteira-e-aponta-falhas-como-warren-buffett-faria/)
