from pathlib import Path


def skill_directory(root: Path) -> Path:
    """Cursor discovers skills here and reads root AGENTS.md."""
    return root / ".agents/skills"
