from pathlib import Path

import yaml

from agent_toolkit.core import check, init, install, update
from agent_toolkit.cli import main


def test_packaged_content_matches_authoring_files():
    from agent_toolkit.core import data_file

    root = Path(__file__).resolve().parents[1]
    assert (root / "AGENT_STANDARD.md").read_bytes() == data_file("AGENT_STANDARD.md").read_bytes()
    for parent in ("profiles", "skills"):
        for source in (root / parent).rglob("*"):
            if source.is_file():
                assert source.read_bytes() == data_file(parent, *source.relative_to(root / parent).parts).read_bytes()


def test_install_is_idempotent_and_preserves_user_text(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# My project\n\nKeep this.\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Claude local\n", encoding="utf-8")
    init(tmp_path)
    install(tmp_path)
    first = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    install(tmp_path)
    second = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert first == second
    assert (tmp_path / "AGENTS.md").read_text().startswith("# My project\n\nKeep this.\n")
    assert (tmp_path / "CLAUDE.md").read_text().startswith("# Claude local\n")
    assert not check(tmp_path)


def test_check_detects_skill_hash_and_lock_drift_without_writing(tmp_path: Path):
    init(tmp_path, "backend")
    install(tmp_path)
    target = tmp_path / ".agents/skills/brainstorming/SKILL.md"
    target.write_text(target.read_text() + "\nchanged\n")
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert any("canonical skill drift" in e for e in check(tmp_path))
    after = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
    update(tmp_path)
    assert not check(tmp_path)
    lock = yaml.safe_load((tmp_path / ".agent/lock.yaml").read_text())
    assert len(lock["skills"]["brainstorming"]["SKILL.md"]) == 64


def test_check_detects_standard_manifest_and_claude_drift(tmp_path: Path):
    init(tmp_path)
    install(tmp_path)
    agent = tmp_path / "AGENTS.md"
    agent.write_text(agent.read_text().replace("Scale planning", "Ignore planning"))
    assert any("standard block" in e for e in check(tmp_path))
    update(tmp_path)
    claude_skill = tmp_path / ".claude/skills/brainstorming/SKILL.md"
    claude_skill.write_text("wrong")
    assert any("claude skill drift" in e for e in check(tmp_path))
    update(tmp_path)
    manifest = tmp_path / ".agent/manifest.yaml"
    value = yaml.safe_load(manifest.read_text())
    value["skills"].remove("accessibility")
    manifest.write_text(yaml.safe_dump(value))
    assert any("Manifest/lock metadata differs" in e for e in check(tmp_path))


def test_skill_hash_covers_supporting_files(tmp_path: Path):
    init(tmp_path)
    install(tmp_path)
    extra = tmp_path / ".agents/skills/brainstorming/reference.md"
    extra.write_text("local extra")
    assert any("canonical skill drift" in e for e in check(tmp_path))


def test_update_removes_deselected_managed_skill_and_claude_adapter(tmp_path: Path):
    init(tmp_path)
    install(tmp_path)
    path = tmp_path / ".agent/manifest.yaml"
    value = yaml.safe_load(path.read_text())
    value["skills"].remove("accessibility")
    value["clients"].remove("claude")
    path.write_text(yaml.safe_dump(value))
    assert check(tmp_path)
    update(tmp_path)
    assert not (tmp_path / ".agents/skills/accessibility").exists()
    assert not (tmp_path / ".claude/skills/brainstorming").exists()
    assert "agent-toolkit:claude" not in (tmp_path / "CLAUDE.md").read_text()
    assert not check(tmp_path)


def test_cli_check_exit_status(tmp_path: Path):
    assert main(["--project", str(tmp_path), "check"]) == 1
    assert main(["--project", str(tmp_path), "init", "--profile", "backend"]) == 0
    assert main(["--project", str(tmp_path), "install"]) == 0
    assert main(["--project", str(tmp_path), "check"]) == 0


def test_archify_is_vendored_for_all_clients(tmp_path: Path):
    init(tmp_path, "backend")
    install(tmp_path)
    config = yaml.safe_load((tmp_path / ".agent/manifest.yaml").read_text())
    assert "archify" in config["skills"]
    for folder in (".agents/skills", ".claude/skills"):
        assert (tmp_path / folder / "archify/SKILL.md").is_file()
        assert (tmp_path / folder / "archify/bin/archify.mjs").is_file()
        assert (tmp_path / folder / "archify/LICENSE").is_file()
    assert not check(tmp_path)
