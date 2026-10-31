# ADR-004: Indexação de Relatórios CVM por Metadados e Expurgo Automático

* **Status:** Aceito
* **Data:** 2026-10-08
* **Decisores:** Equipe de Arquitetura FinNova

## Contexto e Problema
O módulo de Relatórios de Empresas (RF-30, RF-31, RF-33) precisa disponibilizar demonstrativos financeiros (DFP, ITR, FRE). Armazenar arquivos PDF completos gera alto custo de storage, necessidade de verificar as condições de uso e lidar com desatualização. Além disso, a RB-12 e o RNF-10 impõem expurgo automático de dados sincronizados em 12 meses.

## Decisão Considerada
Adotar a **Arquitetura de Indexação por Metadados e Redirecionamento por Link Externo**.

1. O FinNova consome o Portal de Dados Abertos da CVM, grava no PostgreSQL **apenas metadados e tabelas numéricas estruturadas**.
2. O documento na íntegra (PDF) **nunca é armazenado**. O sistema salva e disponibiliza o link direto apontando para o ambiente RAD/ENET da CVM.
3. Uma rotina periódica expurga metadados com `idade do registro >= 12 meses desde sincronizado_em`.

## Alternativas Consideradas
* **Download e Storage dos PDFs no AWS S3 / Local:** Descartado devido aos custos computacionais, complexidade de gestão de armazenamento e riscos de desatualização legal.

## Consequências
### Positivas:
* Redução esperada de armazenamento por não guardar PDFs; percentual ainda não medido.
* Limitação da cópia de documentos e rastreio da fonte. Conformidade depende de verificar termos de uso e política de dados; não é garantida por guardar apenas links.

### Negativas:
* Dependência de que os links do portal RAD/ENET da CVM permaneçam válidos (exige rotina de validação periódica de links quebrados conforme RF-31).
