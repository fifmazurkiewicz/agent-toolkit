"""Managed, credential-free Graft MCP configuration."""

from __future__ import annotations

import json
import re
from pathlib import Path


SERVER = {"command": "npx", "args": ["-y", "@nanonets/graft", "mcp"]}
CODEX_START = "# agent-toolkit:graft start"
CODEX_END = "# agent-toolkit:graft end"


class GraftConfigError(ValueError):
    pass


def cursor_path(root: Path) -> Path:
    return root / ".cursor/mcp.json"


def claude_path(root: Path) -> Path:
    return root / ".mcp.json"


def codex_path(root: Path) -> Path:
    return root / ".codex/config.toml"


def json_with_graft(content: str) -> str:
    try:
        value = json.loads(content) if content.strip() else {}
    except json.JSONDecodeError as exc:
        raise GraftConfigError(f"Invalid MCP JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise GraftConfigError("MCP JSON must be an object")
    servers = value.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise GraftConfigError("mcpServers must be an object")
    existing = servers.get("graft")
    if existing is not None and existing != SERVER:
        raise GraftConfigError("Existing Graft MCP configuration conflicts with agent-toolkit")
    servers["graft"] = SERVER
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def codex_with_graft(content: str) -> str:
    opening = content.count(CODEX_START)
    closing = content.count(CODEX_END)
    if opening != closing or opening > 1:
        raise GraftConfigError("Malformed managed Graft block in .codex/config.toml")
    body = f'{CODEX_START}\n[mcp_servers.graft]\ncommand = "npx"\nargs = ["-y", "@nanonets/graft", "mcp"]\n{CODEX_END}'
    if opening:
        left, rest = content.split(CODEX_START, 1)
        _, right = rest.split(CODEX_END, 1)
        return left + body + right
    if re.search(r"^\\[mcp_servers\\.graft\\]\\s*$", content, re.MULTILINE):
        raise GraftConfigError("Existing unmarked Graft MCP configuration conflicts with agent-toolkit")
    separator = "" if not content else ("\n" if content.endswith("\n") else "\n\n")
    return content + separator + body + "\n"
