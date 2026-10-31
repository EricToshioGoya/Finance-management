"""Relatório de rastreabilidade C-02: cláusulas SHALL das specs sem teste que cite o ID.

Uso: python scripts/verificar-c02.py [--estrito]
Considera citação o nome `test_SPEC_NNN_Rxx[_Ryy...]` ou o texto `SPEC-NNN-Rxx` em testes de
backend, frontend (Playwright) e mobile. Sem --estrito, apenas informa (código de saída 0).
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PADROES = ("backend/tests/**/test_*.py", "frontend/tests/**/*.ts", "mobile/src/**/*.test.ts*")


def citadas() -> set[str]:
    ids: set[str] = set()
    for padrao in PADROES:
        for arquivo in RAIZ.glob(padrao):
            if "node_modules" in arquivo.parts:
                continue
            texto = arquivo.read_text(encoding="utf-8")
            for spec, grupo in re.findall(r"test_SPEC_(\d{3})_((?:R\d{2}_?)+)", texto):
                ids.update(f"SPEC-{spec}-{r}" for r in re.findall(r"R\d{2}", grupo))
            ids.update(f"SPEC-{a}-{b}" for a, b in re.findall(r"SPEC[-_](\d{3})[-_](R\d{2})", texto))
    return ids


def main() -> int:
    cobertas = citadas()
    total = faltantes = 0
    for spec in sorted((RAIZ / "docs/08-specs").glob("SPEC-*.md")):
        clausulas = sorted(set(re.findall(r"\| (SPEC-\d{3}-R\d{2}) \|", spec.read_text("utf-8"))))
        sem_teste = [c for c in clausulas if c not in cobertas]
        total += len(clausulas)
        faltantes += len(sem_teste)
        if sem_teste:
            print(f"{spec.stem}: {len(sem_teste)}/{len(clausulas)} sem teste nomeado -> "
                  + ", ".join(c[-3:] for c in sem_teste))
    print(f"C-02: {total - faltantes}/{total} cláusulas citadas por teste ({faltantes} pendentes).")
    return 1 if faltantes and "--estrito" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
