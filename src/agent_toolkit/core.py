"""Desired state, installation, and read-only drift checks."""

from __future__ import annotations

import hashlib
import re
import shutil
from importlib import resources
from pathlib import Path

import yaml

from . import __version__
from .adapters import claude, codex, cursor, graft

START = "<!-- agent-toolkit:standard v1 start -->"
END = "<!-- agent-toolkit:standard end -->"
MANAGED = ".agent/manifest.yaml"
LOCK = ".agent/lock.yaml"
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CLIENTS = {"codex", "cursor", "claude"}


class ToolkitError(ValueError):
    pass


def data_file(*parts: str) -> Path:
    return Path(str(resources.files("agent_toolkit").joinpath("data", *parts)))


def load_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ToolkitError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ToolkitError(f"Expected YAML mapping in {path}")
    return value


def names(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not SKILL_NAME.fullmatch(x) for x in value):
        raise ToolkitError(f"{label} must be a nonempty list of skill names")
    if len(value) != len(set(value)):
        raise ToolkitError(f"{label} contains duplicates")
    return value


def manifest(root: Path) -> dict:
    value = load_yaml(root / MANAGED)
    if set(value) != {"profile", "clients", "skills"}:
        raise ToolkitError("Manifest must contain exactly profile, clients, skills")
    if not isinstance(value["profile"], str) or value["profile"] not in {"web", "backend"}:
        raise ToolkitError("Unknown profile")
    if not isinstance(value["clients"], list) or not value["clients"] or any(not isinstance(x, str) for x in value["clients"]) or len(set(value["clients"])) != len(value["clients"]) or set(value["clients"]) - CLIENTS:
        raise ToolkitError("clients must be a nonempty subset of codex, cursor, claude")
    names(value["skills"], "skills")
    available = {p.name for p in data_file("skills").iterdir() if p.is_dir()}
    if set(value["skills"]) - available:
        raise ToolkitError("Unknown skill: " + ", ".join(sorted(set(value["skills"]) - available)))
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_files(base: Path, skill: str) -> list[Path]:
    folder = base / skill
    if not (folder / "SKILL.md").is_file():
        raise ToolkitError(f"Missing SKILL.md: {folder}")
    entries = sorted(folder.rglob("*"))
    if any(p.is_symlink() for p in entries) or folder.is_symlink():
        raise ToolkitError(f"Symlink in skill: {folder}")
    files = [p for p in entries if p.is_file()]
    return files


def expected_lock(root: Path, config: dict) -> dict:
    result = {
        "toolkit_version": __version__,
        "profile": config["profile"],
        "clients": config["clients"],
        "mcp_servers": ["graft"],
        "skills": {},
    }
    for skill in config["skills"]:
        result["skills"][skill] = {
            str(p.relative_to(root / ".agents/skills" / skill)): digest(p)
            for p in skill_files(root / ".agents/skills", skill)
        }
    return result


def block(content: str, start: str, end: str, body: str) -> str:
    opening = content.count(start)
    closing = content.count(end)
    if opening != closing or opening > 1:
        raise ToolkitError("Malformed managed block markers")
    rendered = f"{start}\n{body.rstrip()}\n{end}"
    if opening:
        left, rest = content.split(start, 1)
        _, right = rest.split(end, 1)
        return left + rendered + right
    separator = "" if not content else ("\n" if content.endswith("\n") else "\n\n")
    return content + separator + rendered + "\n"


def remove_block(content: str, start: str, end: str) -> str:
    opening = content.count(start)
    closing = content.count(end)
    if opening != closing or opening > 1:
        raise ToolkitError("Malformed managed block markers")
    if not opening:
        return content
    left, rest = content.split(start, 1)
    _, right = rest.split(end, 1)
    return left + right.lstrip("\n")


def standard_block(root: Path) -> str:
    current = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").exists() else ""
    return block(current, START, END, data_file("AGENT_STANDARD.md").read_text(encoding="utf-8"))


def mcp_text(path: Path, renderer) -> str:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    try:
        return renderer(current)
    except graft.GraftConfigError as exc:
        raise ToolkitError(f"{path}: {exc}") from exc


def expected_mcp_files(root: Path, clients: list[str]) -> dict[Path, str]:
    result: dict[Path, str] = {}
    if "cursor" in clients:
        path = graft.cursor_path(root)
        result[path] = mcp_text(path, graft.json_with_graft)
    if "claude" in clients:
        path = graft.claude_path(root)
        result[path] = mcp_text(path, graft.json_with_graft)
    if "codex" in clients:
        path = graft.codex_path(root)
        result[path] = mcp_text(path, graft.codex_with_graft)
    return result


def init(root: Path, profile: str = "web") -> None:
    if profile not in {"web", "backend"}:
        raise ToolkitError("Profile must be web or backend")
    destination = root / MANAGED
    if destination.exists():
        raise ToolkitError(f"Manifest already exists: {destination}")
    selected = load_yaml(data_file("profiles", profile + ".yaml"))
    config = {"profile": profile, "clients": ["cursor", "codex", "claude"], "skills": names(selected.get("skills"), "profile skills")}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def install(root: Path) -> None:
    config = manifest(root)
    # Validate all managed blocks before writing anything.
    agent_text = standard_block(root)
    mcp_files = expected_mcp_files(root, config["clients"])
    claude_path = root / "CLAUDE.md"
    claude_text = None
    if "claude" in config["clients"]:
        old = claude_path.read_text(encoding="utf-8") if claude_path.exists() else ""
        claude_text = block(old, claude.CLAUDE_START, claude.CLAUDE_END, claude.CLAUDE_BODY)
    elif claude_path.exists():
        claude_text = remove_block(claude_path.read_text(encoding="utf-8"), claude.CLAUDE_START, claude.CLAUDE_END)
    previous = {}
    if (root / LOCK).exists():
        previous = load_yaml(root / LOCK).get("skills", {})
        if not isinstance(previous, dict) or any(not isinstance(name, str) or not SKILL_NAME.fullmatch(name) for name in previous):
            raise ToolkitError("Malformed previous lock skills mapping")
    source = data_file("skills")
    canonical = codex.skill_directory(root)
    assert canonical == cursor.skill_directory(root)
    for old_skill in set(previous) - set(config["skills"]):
        for base in (canonical, claude.skill_directory(root)):
            old = base / old_skill
            if old.is_symlink():
                raise ToolkitError(f"Refusing symlink target: {old}")
            if old.is_dir():
                shutil.rmtree(old)
    for skill in config["skills"]:
        skill_files(source, skill)
        target = canonical / skill
        if target.is_symlink():
            raise ToolkitError(f"Refusing symlink target: {target}")
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        for original in skill_files(source, skill):
            dest = target / original.relative_to(source / skill)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, dest)
    (root / "AGENTS.md").write_text(agent_text, encoding="utf-8")
    for path, text in mcp_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    if claude_text is not None and ("claude" in config["clients"] or claude_path.exists()):
        claude_path.write_text(claude_text, encoding="utf-8")
    if "claude" in config["clients"]:
        for skill in config["skills"]:
            target = claude.skill_directory(root) / skill
            if target.is_symlink():
                raise ToolkitError(f"Refusing symlink target: {target}")
            if target.exists():
                shutil.rmtree(target)
            target.mkdir(parents=True, exist_ok=True)
            for original in skill_files(canonical, skill):
                dest = target / original.relative_to(canonical / skill)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, dest)
    else:
        for skill in config["skills"]:
            old = claude.skill_directory(root) / skill
            if old.is_symlink():
                raise ToolkitError(f"Refusing symlink target: {old}")
            if old.is_dir():
                shutil.rmtree(old)
    lock = expected_lock(root, config)
    lock_path = root / LOCK
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(yaml.safe_dump(lock, sort_keys=False), encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        config = manifest(root)
    except ToolkitError as exc:
        return [str(exc)]
    try:
        actual_agent = (root / "AGENTS.md").read_text(encoding="utf-8")
        if actual_agent != standard_block(root):
            errors.append("AGENTS.md standard block differs")
    except (OSError, ToolkitError) as exc:
        errors.append(f"AGENTS.md: {exc}")
    if "claude" in config["clients"]:
        try:
            actual = (root / "CLAUDE.md").read_text(encoding="utf-8")
            expected = block(actual, claude.CLAUDE_START, claude.CLAUDE_END, claude.CLAUDE_BODY)
            if actual != expected:
                errors.append("CLAUDE.md import block differs")
        except (OSError, ToolkitError) as exc:
            errors.append(f"CLAUDE.md: {exc}")
    elif (root / "CLAUDE.md").exists() and claude.CLAUDE_START in (root / "CLAUDE.md").read_text(encoding="utf-8"):
        errors.append("Obsolete Claude import block")
    if "claude" not in config["clients"]:
        for skill in config["skills"]:
            if (claude.skill_directory(root) / skill).exists():
                errors.append(f"Obsolete Claude skill: {skill}")
    try:
        actual_lock = load_yaml(root / LOCK)
    except ToolkitError as exc:
        return errors + [str(exc)]
    locked_skills = actual_lock.get("skills")
    if not isinstance(locked_skills, dict):
        return errors + ["Malformed lock skills mapping"]
    if actual_lock.get("toolkit_version") != __version__ or actual_lock.get("profile") != config["profile"] or actual_lock.get("clients") != config["clients"] or actual_lock.get("mcp_servers") != ["graft"] or set(locked_skills) != set(config["skills"]):
        errors.append("Manifest/lock metadata differs")
    try:
        mcp_files = expected_mcp_files(root, config["clients"])
    except ToolkitError as exc:
        errors.append(f"Graft MCP configuration: {exc}")
        mcp_files = {}
    for path, expected in mcp_files.items():
        try:
            actual = path.read_text(encoding="utf-8")
            if actual != expected:
                errors.append(f"Graft MCP configuration differs: {path.relative_to(root)}")
        except (OSError, ToolkitError) as exc:
            errors.append(f"Graft MCP configuration: {exc}")
    for old_skill in set(locked_skills) - set(config["skills"]):
        errors.append(f"Obsolete managed skill: {old_skill}")
    for skill in config["skills"]:
        recorded = locked_skills.get(skill, {})
        source = data_file("skills") / skill
        for base, label in ((codex.skill_directory(root), "canonical"), *(([(claude.skill_directory(root), "claude")] if "claude" in config["clients"] else []))):
            try:
                files = skill_files(base, skill)
                found = {str(p.relative_to(base / skill)): digest(p) for p in files}
                if found != recorded:
                    errors.append(f"{label} skill drift: {skill}")
                if label == "canonical":
                    packaged = {str(p.relative_to(source)): digest(p) for p in skill_files(data_file("skills"), skill)}
                    if found != packaged:
                        errors.append(f"Toolkit skill update available: {skill}")
            except (OSError, ToolkitError) as exc:
                errors.append(f"{label} skill {skill}: {exc}")
    return errors


def update(root: Path) -> None:
    install(root)
