"""Machine-local steps: the Graft index build and one-time client approvals.

These touch only the current machine (the git-ignored index and per-user
client settings), never the managed project files that `check` compares.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from .core import ToolkitError, manifest

GRAFT = ["npx", "-y", "@nanonets/graft"]
CLAUDE_LOCAL = ".claude/settings.local.json"


def build_graft(root: Path) -> str:
    """Build the structural Graft index; a missing Node runtime is reported, not fatal."""
    if shutil.which("npx") is None:
        return "Graft index not built: npx is unavailable; run `npx -y @nanonets/graft build` once Node is installed"
    result = subprocess.run([*GRAFT, "build", str(root)], capture_output=True, text=True)
    if result.returncode != 0:
        return f"Graft index build failed (exit {result.returncode}); run `npx -y @nanonets/graft build` to see why"
    return "Graft index built"


def trust_codex(root: Path, home: Path) -> str:
    config = home / ".codex/config.toml"
    header = f'[projects."{root}"]'
    text = config.read_text(encoding="utf-8") if config.exists() else ""
    if header in text:
        return "Codex: project already trusted"
    config.parent.mkdir(parents=True, exist_ok=True)
    separator = "" if not text or text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    config.write_text(f'{text}{separator}{header}\ntrust_level = "trusted"\n', encoding="utf-8")
    return "Codex: project trusted"


def approve_cursor(root: Path) -> str:
    binary = shutil.which("cursor-agent") or shutil.which("agent")
    if binary is None:
        return "Cursor: CLI not found; run `agent mcp enable graft` in the project"
    result = subprocess.run([binary, "mcp", "enable", "graft"], cwd=root, capture_output=True, text=True)
    return "Cursor: graft enabled" if result.returncode == 0 else "Cursor: `agent mcp enable graft` failed; run it in the project"


def approve_claude(root: Path) -> str:
    path = root / CLAUDE_LOCAL
    try:
        settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError as exc:
        raise ToolkitError(f"Invalid JSON in {CLAUDE_LOCAL}: {exc.msg}") from exc
    if not isinstance(settings, dict):
        raise ToolkitError(f"{CLAUDE_LOCAL} must be an object")
    servers = settings.setdefault("enabledMcpjsonServers", [])
    if not isinstance(servers, list):
        raise ToolkitError(f"enabledMcpjsonServers in {CLAUDE_LOCAL} must be a list")
    if "graft" in servers:
        return "Claude Code: graft already approved"
    servers.append("graft")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    exclude = root / ".git/info/exclude"
    if exclude.parent.is_dir():
        lines = exclude.read_text(encoding="utf-8").splitlines() if exclude.exists() else []
        if f"/{CLAUDE_LOCAL}" not in lines:
            exclude.write_text("\n".join([*lines, f"/{CLAUDE_LOCAL}"]) + "\n", encoding="utf-8")
    return "Claude Code: graft approved"


def setup(root: Path, home: Path | None = None) -> list[str]:
    """Approve the project's Graft MCP server for each selected client on this machine."""
    clients = manifest(root)["clients"]
    home = home or Path(os.path.expanduser("~"))
    steps = []
    if "codex" in clients:
        steps.append(trust_codex(root, home))
    if "cursor" in clients:
        steps.append(approve_cursor(root))
    if "claude" in clients:
        steps.append(approve_claude(root))
    return steps
