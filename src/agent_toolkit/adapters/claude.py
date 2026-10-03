from pathlib import Path


CLAUDE_START = "<!-- agent-toolkit:claude start -->"
CLAUDE_END = "<!-- agent-toolkit:claude end -->"
CLAUDE_BODY = "@AGENTS.md\n"


def skill_directory(root: Path) -> Path:
    """Claude Code's project skill location."""
    return root / ".claude/skills"
