# PLAN-002 — Motor puro de juros compostos

Origem: SPEC-002, ordem 2 do mapa; issue #13. Base: SPEC-001 concluída na feature/spec001-completa. Pedido atual autoriza aplicar a próxima Spec; não implica merge das anteriores ou aprovação formal do grupo.

1. Registrar política numérica/contrato em ADR-002 e OPEN-03/06/15; preservar RB-10/RB-28 e delimitar RF-22 parcial.
2. Implementar backend/app/domain/juros_compostos.py com biblioteca padrão, contexto Decimal isolado, objetos imutáveis, validação e erros por campo/código.
3. Testar cada SPEC-002-R01 a R08, referências independentes de maior precisão, equivalências, entrada inválida, contexto externo/concorrência e ausência de I/O.
4. Medir cobertura do motor >=80% e adicionar CI dedicada sem banco/segredos. Rodar regressão de autenticação existente na CI.
5. Medir perfil sequencial 12/120/360/600 meses no script externo ao domínio; registrar ambiente/P50/P95 e limite de evidência.
6. Atualizar Spec, mapa/situação, README e registro de implementação; commits/PR da issue #13, sem deploy/merge implícitos.

Contrato: calcular com Decimal e argumentos nomeados; converter_taxa preserva unidade percentual; arredondar_moeda aplica centavos HALF_UP somente no consumo. Riscos: erros de unidade, capitalização antecipada de aporte, contexto global, arredondamento precoce e precisão em raízes. Mitigar com testes numéricos independentes e contexto próprio de 50 dígitos. Prazo não tem novo teto funcional; memória O(n) deve ser tratada pelo futuro consumidor público.
