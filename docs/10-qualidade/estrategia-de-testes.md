# Estratégia de Testes e Qualidade — FinNova

- **Status:** rascunho
- **Última atualização:** 2026-10-18

---

## 1. Objetivos

1. Demonstrar que o código implementa a spec: toda cláusula `SHALL` tem ao menos um teste (`CLAUDE.md` C-02).
2. Garantir a acurácia dos cálculos financeiros, com cobertura mínima de 80% nas regras de cálculo (RNF-07).
3. Impedir o merge de código que quebre testes ou lint (RNF-16).

## 2. Níveis de teste

| Nível | Alvo | Ferramenta | Quando roda |
|---|---|---|---|
| Unitário | Domínio puro: entidades, regras de negócio e motores de cálculo | pytest + pytest-cov | Todo commit e PR |
| Integração | API + banco: endpoints, persistência, autenticação e autorização | pytest + cliente HTTP do FastAPI + PostgreSQL em Docker | Todo PR |
| Frontend | Componentes e regras de interface | Vitest/Jest | Todo PR (Fase 4) |
| Ponta a ponta | Fluxo principal: cadastro → login → despesa → simulação | A definir | Antes da entrega final |

## 3. Rastreabilidade cláusula → teste

- Cada teste cita no nome ou na docstring o ID da cláusula que verifica. Exemplo:

```python
def test_spec002_r02_converte_taxa_anual_por_equivalencia_composta():
    """SPEC-002-R02 — Cenário 1."""
```

- A coluna "Teste previsto" da seção 5 de cada spec indica o nível de teste esperado.
- No PR, a pergunta de revisão é: "cada cláusula alterada tem teste e o teste passa?".

## 4. Dados de teste

- Valores monetários e taxas sempre em `Decimal` (SPEC-002 INV-02).
- Resultados financeiros conferidos contra cálculo de referência independente (ex.: planilha ou calculadora do Banco Central), registrado no próprio teste.
- Nenhum dado pessoal real em fixtures.

## 5. Gates de qualidade no CI (RNF-16)

| Gate | Critério |
|---|---|
| Lint | Sem erros (ferramenta a confirmar na Fase 4; proposta: ruff e ESLint) |
| Testes | 100% passando |
| Cobertura | ≥ 80% no pacote de domínio de cálculo financeiro (RNF-07) |
| Segurança | Sem vulnerabilidade alta nas dependências (`docs/09-seguranca/seguranca-ssdlc.md`) |

## 6. Definição de pronto

Uma issue só é concluída quando:

- [ ] A spec está atualizada no mesmo PR.
- [ ] Cada cláusula `SHALL` implementada tem teste passando.
- [ ] Os gates da seção 5 passaram.
- [ ] O PR foi revisado conforme `docs/combinados.md` e declara o uso de agente de IA.

## 7. Revisão de código gerado por agente

O código gerado por agente segue as mesmas regras, com atenção redobrada a:

- Regras de negócio inventadas, que não constam da spec.
- Uso de `float` ou de conversão de taxa por divisão simples.
- Testes que só confirmam a própria implementação, sem valor de referência independente.

## 8. Refatoração

- Toda refatoração é feita em PR próprio, com justificativa (duplicação, acoplamento ou complexidade) e sem mudança de comportamento: os testes existentes devem continuar passando sem alteração.
