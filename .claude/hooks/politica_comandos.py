"""Camada 2 — hook PreToolUse do Claude Code (docs/09-seguranca/governanca-agentes.md).

Lê a chamada de ferramenta em JSON pela entrada padrão e devolve a decisão:
- deny: acesso a .env ou mcp.env, DROP/TRUNCATE, git push forçado e rm recursivo forçado;
- ask: instalação de dependência (pip, npm), git push e migração de banco (alembic);
- sem saída: a decisão segue as permissões de .claude/settings.json.

Teste manual: echo '{"tool_name":"Bash","tool_input":{"command":"git push"}}' | python3 .claude/hooks/politica_comandos.py
"""

import json
import re
import sys
from pathlib import PurePath

INICIO = r"(?:^|[\s;&|(`$])"

ARQUIVO_SEGREDO = re.compile(r"(?<![\w.-])(?:[\w./~-]*/)?(mcp\.env|\.env(?:\.[\w-]+)?)(?![\w.-])")

NEGAR = [
    (re.compile(r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE)\b", re.IGNORECASE),
     "Comando destrutivo de banco (DROP/TRUNCATE) é proibido ao agente."),
    (re.compile(INICIO + r"git(\s+-C\s+\S+)?\s+push\b[^;&|]*(\s--force(-with-lease)?\b|\s-f\b|\s\+\S)"),
     "git push forçado é proibido ao agente."),
    (re.compile(INICIO + r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-r\s+-f|-f\s+-r|--recursive\s+--force|--force\s+--recursive)\b"),
     "rm recursivo forçado é proibido ao agente."),
]

PERGUNTAR = [
    (re.compile(INICIO + r"(pip3?|python3?\s+-m\s+pip|uv\s+pip)\s+install\b"),
     "Instalação de dependência Python exige confirmação humana."),
    (re.compile(INICIO + r"npm\s+(install|i|ci|add)\b"),
     "Instalação de dependência npm exige confirmação humana."),
    (re.compile(INICIO + r"git(\s+-C\s+\S+)?\s+push\b"),
     "git push exige confirmação humana."),
    (re.compile(INICIO + r"alembic\s+(upgrade|downgrade|stamp)\b"),
     "Migração de banco exige confirmação humana."),
]


def cita_arquivo_segredo(texto: str) -> bool:
    return any(nome != ".env.example" for nome in ARQUIVO_SEGREDO.findall(texto))


def decidir(chamada: dict) -> tuple[str, str] | None:
    ferramenta = chamada.get("tool_name", "")
    entrada = chamada.get("tool_input") or {}

    if ferramenta in {"Read", "Edit", "Write", "Grep"}:
        caminho = entrada.get("file_path") or entrada.get("path") or ""
        if caminho and cita_arquivo_segredo(PurePath(caminho).name):
            return "deny", "Acesso a .env ou mcp.env é proibido ao agente (CLAUDE.md C-10)."
        return None

    if ferramenta != "Bash":
        return None

    comando = entrada.get("command", "")
    if cita_arquivo_segredo(comando):
        return "deny", "Acesso a .env ou mcp.env é proibido ao agente (CLAUDE.md C-10)."
    for padrao, motivo in NEGAR:
        if padrao.search(comando):
            return "deny", motivo
    for padrao, motivo in PERGUNTAR:
        if padrao.search(comando):
            return "ask", motivo
    return None


def main() -> int:
    try:
        chamada = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    decisao = decidir(chamada)
    if decisao:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decisao[0],
                "permissionDecisionReason": decisao[1],
            }
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
