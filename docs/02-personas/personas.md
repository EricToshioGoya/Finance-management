# Personas — FinNova

## Atores

| Ator | Descrição |
|---|---|
| Usuário iniciante | Pouco ou nenhum conhecimento de investimentos; busca organização e primeiros passos |
| Usuário avançado | Já investe; busca centralização, comparação de cenários e planejamento de metas |
| Administrador | Papel autorizado a administrar metadados e métricas, sem acesso a finanças pessoais individuais |

Cálculos e rotinas internas são responsabilidades do sistema, não atores externos. Iniciante/avançado são perfis de experiência; administrador é papel de acesso.

## Personas

**Persona 1 — Iniciante.** Mariana Souza, 24 anos, analista júnior, primeiro emprego CLT há 8 meses. Começou a sobrar dinheiro no fim do mês, mas não sabe organizar nem investir — só conhece a poupança. Objetivo: entender para onde vai o dinheiro e dar os primeiros passos em investimentos sem medo de errar. Usa o celular para quase tudo e tem pouca paciência com telas complexas.

**Persona 2 — Avançado.** Rodrigo Almeida, 34 anos, analista de sistemas, investe há 6 anos em CDB, Tesouro Direto e algumas ações/FIIs, mas de forma dispersa entre corretora e planilhas. Objetivo: centralizar o controle financeiro, comparar cenários de investimento e simular metas de forma mais sofisticada. Usa notebook no trabalho e celular no restante do tempo.

## PERSONA 1: INVESTIDOR INICIANTE

### Função
Investidor Iniciante (Pessoa Física sem experiência prévia em investimentos).

### Perfil Geral
Usuário que está iniciando sua vida financeira ativa ou conseguindo poupar pela primeira vez. Possui pouca ou nenhuma familiaridade com conceitos financeiros avançados, taxas ou modalidades de aplicação além da poupança.

### Dificuldades e Dores
- Falta de clareza sobre para onde vai o dinheiro no final do mês.
- Medo e insegurança de investir e perder patrimônio por falta de conhecimento.
- Dificuldade em compreender termos técnicos e jargões do mercado financeiro.
- Frustração e pouca paciência com interfaces complexas, burocráticas ou poluídas.

### Intenções com o FinNova
- Organizar e visualizar seus gastos de forma simples, direta e intuitiva.
- Compreender e dar os primeiros passos em investimentos seguros com orientações claras.
- Realizar simulações financeiras básicas e visuais sem medo de errar.
- Acompanhar a evolução do seu patrimônio preferencialmente pelo smartphone.

## PERSONA 2: INVESTIDOR AVANÇADO

### Função
Investidor Avançado (Pessoa Física com carteira diversificada e experiência de mercado).

### Perfil Geral
Usuário experiente no mercado financeiro (CDB, Tesouro Direto, Ações, FIIs). Costuma utilizar múltiplas plataformas, corretoras e planilhas pessoais para gerenciar seus aportes e metas.

### Dificuldades e Dores
- Dispersão das informações financeiras em múltiplos aplicativos, corretoras e planilhas.
- Dificuldade para comparar cenários de investimentos e rentabilidade real líquida em um só lugar.
- Perda de tempo ao atualizar dados e acompanhar metas manualmente em ferramentas não integradas.
- Limitação de ferramentas simples que não oferecem simulações sofisticadas ou projeções detalhadas.

### Intenções com o FinNova
- Centralizar o controle financeiro e a consolidação de toda a sua carteira de investimentos.
- Comparar cenários de investimento sofisticados e simular projeções de rentabilidade e metas de longo prazo.
- Acessar dashboards detalhados, relatórios analíticos e métricas avançadas de rentabilidade.
- Utilizar a plataforma tanto no desktop (para análises aprofundadas) quanto no mobile (para consultas rápidas).

## PERSONA 3: ADMINISTRADOR DO SISTEMA

### Função
Administrador do Sistema (Gestor de Plataforma / Suporte Operacional).

### Perfil Geral
Profissional técnico/operacional responsável pelo gerenciamento, manutenção das regras de negócio, parametrização de índices econômicos e governança da plataforma FinNova.

### Dificuldades e Dores
- Necessidade de atualizar manualmente taxas, índices econômicos ou regras tributárias de forma descentralizada.
- Risco de incoerência ou falhas nos motores de cálculo que impactem o usuário final.
- Dificuldade de rastrear falhas, erros de integração ou comportamentos anômalos sem logs centralizados.
- Sobrecarga operacional caso não existam rotinas automatizadas e painéis administrativos eficientes.

### Intenções com o FinNova
- Parametrizar e atualizar centralizadamente as regras de negócio, tabelas tributárias e índices econômicos.
- Supervisionar a execução automatizada dos motores de cálculo, classificação de perfis e geração de dashboards.
- Monitorar a saúde da aplicação, acessos, logs de auditoria e a segurança dos dados dos usuários.
- Garantir a alta disponibilidade, conformidade com a LGPD e o funcionamento contínuo do sistema.


## Necessidades comuns de conta

Ambos os perfis precisam recuperar acesso sem suporte, confirmar seu e-mail, corrigir nome/endereço, alterar senha, escolher tema/idioma/canais e encerrar sessões em outro dispositivo. RF-68 a RF-74 atendem essas jornadas sem depender do resultado do quiz. O usuário com e-mail pendente deve receber instruções claras de confirmação e reenvio.

## Necessidades comuns de conta

Ambos os perfis precisam confirmar o e-mail, recuperar acesso, editar nome/endereço, trocar senha e salvar idioma/tema/notificações (RF-68 a RF-73). Devem compreender expiração/logout e poder solicitar exportação/exclusão dos próprios dados (RF-50 e RF-05). Fluxos e limites de implementação constam na matriz de cobertura da qualidade.
