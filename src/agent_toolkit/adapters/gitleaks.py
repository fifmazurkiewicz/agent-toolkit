"""Managed Gitleaks allowlist for the toolkit's own lock file.

The lock records SHA-256 hashes next to file names, which Gitleaks'
generic-api-key rule reports as secrets. The managed block allowlists only
SHA-256 values for that path and leaves project rules untouched, except
that a legacy `[allowlist]` table becomes `[[allowlists]]`: Gitleaks 8.25+
refuses to load a config that mixes the two forms.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

START = "# agent-toolkit:gitleaks start"
END = "# agent-toolkit:gitleaks end"
BODY = f"""{START}
[[rules]]
id = "generic-api-key"

[[rules.allowlists]]
description = "agent-toolkit lock: SHA-256 hashes of vendored skill files, not secrets"
condition = "AND"
regexTarget = "secret"
regexes = ['''^[a-f0-9]{{64}}$''']
paths = ['''^\\.agent/lock\\.yaml$''']
{END}"""
NEW_FILE = f"""[extend]
useDefault = true

{BODY}
"""
LEGACY = re.compile(r"^\[allowlist\][ \t]*$", re.MULTILINE)


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
    unmanaged = content
    if opening:
        left, rest = content.split(START, 1)
        _, right = rest.split(END, 1)
        unmanaged = left + right
    if any(rule.get("id") == "generic-api-key" for rule in tomllib.loads(unmanaged).get("rules", [])):
        raise GitleaksConfigError(
            "Project overrides generic-api-key outside the managed block; "
            "merge its settings with the managed rule before updating."
        )
    content = LEGACY.sub("[[allowlists]]", content)
    if opening:
        left, rest = content.split(START, 1)
        _, right = rest.split(END, 1)
        return left + BODY + right
    return content.rstrip("\n") + "\n\n" + BODY + "\n"
