"""Módulo simulador do domínio: interface pública do motor de juros compostos (SPEC-002)."""

from finnova.domain.simulador.juros_compostos import (
    EvolucaoMensal,
    ResultadoEvolucao,
    TipoPeriodo,
    TipoTaxa,
    calcular_evolucao,
    converter_taxa_anual_para_mensal,
)

__all__ = [
    "EvolucaoMensal",
    "ResultadoEvolucao",
    "TipoPeriodo",
    "TipoTaxa",
    "calcular_evolucao",
    "converter_taxa_anual_para_mensal",
]
