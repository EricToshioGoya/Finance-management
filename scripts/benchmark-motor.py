"""Perfil sequencial de SPEC-002/OPEN-06; não mede o P95 da aplicação."""

import argparse
import json
import os
import platform
import sys
from decimal import Decimal
from pathlib import Path
from time import perf_counter_ns

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.domain.juros_compostos import MotorJurosCompostos  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--amostras", type=int, default=100)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    if args.amostras < 20:
        parser.error("--amostras deve ser >=20 para este perfil de P95")
    resultados = []
    for meses in (12, 120, 360, 600):
        tempos = []
        for indice in range(5 + args.amostras):
            inicio = perf_counter_ns()
            MotorJurosCompostos.calcular(
                valor_inicial=Decimal("1000"),
                aporte_mensal=Decimal("100"),
                taxa_percentual=Decimal("12"),
                periodicidade_taxa="anual",
                prazo=meses,
                unidade_prazo="meses",
            )
            duracao = perf_counter_ns() - inicio
            if indice >= 5:
                tempos.append(duracao)
        tempos.sort()
        p50 = tempos[(len(tempos) * 50 + 99) // 100 - 1]
        p95 = tempos[(len(tempos) * 95 + 99) // 100 - 1]
        resultados.append({"meses": meses, "amostras": len(tempos), "p50_ns": p50, "p95_ns": p95})
    relatorio = {
        "perfil": "SPEC-002: sequencial, 5 aquecimentos; inicial=1000, aporte=100, taxa anual=12%",
        "quantil": "posto mais proximo: ceil(p*n), sem interpolacao",
        "ambiente": {
            "python": platform.python_version(),
            "plataforma": platform.platform(),
            "arquitetura": platform.machine(),
            "cpus_logicas": os.cpu_count(),
        },
        "orcamento_motor_p95_ns": 3_000_000_000,
        "resultados": resultados,
        "dentro_orcamento": all(r["p95_ns"] < 3_000_000_000 for r in resultados),
        "limite": "Nao mede API, banco, concorrencia, dashboards ou disponibilidade.",
    }
    texto = json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n"
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto, encoding="utf-8")
    print(texto, end="")
    if not relatorio["dentro_orcamento"]:
        raise SystemExit("P95 do motor excedeu o orcamento neste perfil.")


if __name__ == "__main__":
    main()
