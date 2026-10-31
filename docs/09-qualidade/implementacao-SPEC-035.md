# SPEC-035 — Central de educação e ajuda contextual

## Recorte implementado

Um único catálogo versionado em `backend/app/domain/education.py` é responsável tanto pelos resultados da busca quanto pelas explicações de ajuda. `get_article` fornece exatamente o verbete que aparece na central: nenhuma cópia de explicação é mantida em tooltip. O catálogo inicial tem oito conceitos em português e inglês: CDI, taxa de juros, juros compostos, diversificação, liquidez, volatilidade, Sharpe e patrimônio líquido.

**Política técnica provisória OPEN-30:** os textos são educativos, não operam investimentos nem representam aconselhamento. O catálogo está versionado no código (`education-v1`) para permitir revisão editorial por PR. É somente um conjunto inicial, e não substitui a aprovação formal de autoria, cobertura do acervo, revisão de traduções ou pipeline de publicação.

A busca trata maiúsculas e acentos de forma indiferente, limite de 100 caracteres. A consulta vazia lista o catálogo em ordem adaptada ao perfil da SPEC-003: conservador (prioridade introdutória), moderado (intermediária), arrojado (técnica). Perfil ainda não definido recebe prioridade introdutória, **sem forjar um perfil**. Nas buscas, relevância do termo precede priorização. A falta de correspondência devolve lista vazia; chave inexistente responde 404, sem retornar artigo diferente.

Cada verbete possui PT e EN aprovados para o recorte técnico; a API informa `language` e `fallback=false` para evitar ocultar tradução ausente. Caso o acervo cresça e inclua verbetes sem tradução, a política de fallback precisa ser aprovada em OPEN-30 em vez de inventar tradução.

## API e interface

Rotas de leitura protegidas por sessão autenticada; sem dados pessoais nos verbetes:

- `GET /api/v1/education/articles?q=CDI&lang=pt`
- `GET /api/v1/education/articles/cdi?lang=pt`

A resposta inclui `key`, `title`, `body`, `language`, `fallback` e `version`. Não existe gravação nem mutação financeira.

Na interface web o titular encontra a central com busca e resultados, além dos botões **?** vinculados aos conceitos de taxa anual nos objetivos nomeados e diversificação no comparador de alocação. Os botões são acessíveis por teclado, clique e toque, abrem explicação na própria tela, possuem `aria-expanded`, texto e comando de fechar. Quando a consulta falha, a função financeira permanece utilizável.

## Testes e limitações

`backend/tests/test_spec035_education.py`: sessão obrigatória, equivalência literal da central/ajuda para CDI, PT/EN, chave desconhecida, termo sem resultado, idioma inválido e conteúdo sem dados de outro titular.

Pendências: aceitação editorial formal (OPEN-30), cobertura Expo/mobile dedicada e auditoria externa de acessibilidade WCAG AA. CI exige Ruff, testes de backend com PostgreSQL, build/lint TypeScript e testes de navegador; aprovação não deve ser afirmada antes dos workflows finalizarem. Sem merge na `main` sem autorização.
