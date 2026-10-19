"""Verifica se os links relativos dos arquivos Markdown apontam para arquivos existentes.

Uso: python3 scripts/verificar_links.py [raiz]
Retorna código 1 quando encontra ao menos um link quebrado (gate do CI).
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IGNORADOS = {".git", "node_modules", ".venv", "venv"}
EXTERNOS = ("http://", "https://", "mailto:", "#")


def arquivos_markdown(raiz: Path):
    for caminho in sorted(raiz.rglob("*.md")):
        if not IGNORADOS.intersection(caminho.relative_to(raiz).parts):
            yield caminho


def links_quebrados(arquivo: Path):
    em_bloco_de_codigo = False
    for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
        if linha.lstrip().startswith("```"):
            em_bloco_de_codigo = not em_bloco_de_codigo
            continue
        if em_bloco_de_codigo:
            continue
        for alvo in LINK.findall(linha):
            if alvo.startswith(EXTERNOS):
                continue
            caminho = unquote(alvo.split("#", 1)[0])
            if caminho and not (arquivo.parent / caminho).exists():
                yield numero, alvo


def main() -> int:
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    total = 0
    for arquivo in arquivos_markdown(raiz):
        for numero, alvo in links_quebrados(arquivo):
            print(f"{arquivo.relative_to(raiz)}:{numero}: link quebrado -> {alvo}")
            total += 1
    print(f"{total} link(s) quebrado(s).")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
