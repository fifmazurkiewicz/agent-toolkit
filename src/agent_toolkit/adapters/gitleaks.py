"""Managed Gitleaks allowlist for the toolkit's own lock file.

The lock records SHA-256 hashes next to file names, which Gitleaks'
generic-api-key rule reports as secrets. The managed block allowlists only
that path and leaves any project rules in the same file untouched.
"""

from __future__ import annotations

from pathlib import Path

START = "# agent-toolkit:gitleaks start"
END = "# agent-toolkit:gitleaks end"
BODY = f"""{START}
[[allowlists]]
description = "agent-toolkit lock: SHA-256 hashes of vendored skill files, not secrets"
paths = ['''^\\.agent/lock\\.yaml$''']
{END}"""
NEW_FILE = f"""[extend]
useDefault = true

{BODY}
"""


class GitleaksConfigError(ValueError):
    pass


def path(root: Path) -> Path:
    return root / ".gitleaks.toml"


def with_allowlist(content: str) -> str:
    """Return the config with the managed block added or refreshed."""
    if not content.strip():
        return NEW_FILE
    opening, closing = content.count(START), content.count(END)
    if opening != closing or opening > 1:
        raise GitleaksConfigError("Malformed managed block in .gitleaks.toml")
    if opening:
        left, rest = content.split(START, 1)
        _, right = rest.split(END, 1)
        return left + BODY + right
    return content.rstrip("\n") + "\n\n" + BODY + "\n"
