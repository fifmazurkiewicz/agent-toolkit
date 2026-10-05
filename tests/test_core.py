import json
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


def test_python_service_architecture_skill_is_opt_in():
    from agent_toolkit.core import data_file

    root = Path(__file__).resolve().parents[1]
    source = root / "skills/python-service-architecture/SKILL.md"
    packaged = data_file("skills", "python-service-architecture", "SKILL.md")
    assert source.read_bytes() == packaged.read_bytes()
    for profile in ("web", "backend"):
        skills = yaml.safe_load((root / "profiles" / f"{profile}.yaml").read_text())["skills"]
        assert "python-service-architecture" not in skills


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


def test_product_workflow_skills_are_selected_and_installed_by_profiles(tmp_path: Path):
    for profile in ("web", "backend"):
        root = tmp_path / profile
        init(root, profile)
        config = yaml.safe_load((root / ".agent/manifest.yaml").read_text())
        skills = config["skills"]
        workflow = [
            "project-context-lifecycle",
            "problem-framing",
            "technical-research",
            "production-product-requirements",
            "writing-plans",
            "plan-review",
            "implementation",
            "tdd",
            "implementation-review",
            "goal-implement",
        ]
        assert all(name in skills for name in workflow)
        assert [skills.index(name) for name in workflow] == sorted(skills.index(name) for name in workflow)
        assert skills.index("brainstorming") < skills.index("idea-validation")
        assert skills.index("idea-validation") < skills.index("production-product-requirements")
        assert skills.index("production-product-requirements") < skills.index("writing-plans")
        install(root)
        for directory in (".agents/skills", ".claude/skills"):
            assert (root / directory / "idea-validation/SKILL.md").is_file()
            assert (root / directory / "production-product-requirements/SKILL.md").is_file()


def test_project_context_skills_define_graft_backed_lifecycle():
    root = Path(__file__).resolve().parents[1]
    lifecycle = (root / "skills/project-context-lifecycle/SKILL.md").read_text()
    goal = (root / "skills/goal-implement/SKILL.md").read_text()
    assert ".agent/context/changes/<change-id>/" in lifecycle
    assert "progress.md" in lifecycle
    assert "Graft" in lifecycle
    assert "lessons.md" in lifecycle
    assert "two repair attempts" in goal
    assert "manual" in goal
    assert "STOP" in goal


def test_project_context_workflow_installs_for_all_selected_clients(tmp_path: Path):
    init(tmp_path, "backend")
    install(tmp_path)
    names = (
        "project-context-lifecycle",
        "problem-framing",
        "technical-research",
        "plan-review",
        "implementation",
        "tdd",
        "implementation-review",
        "goal-implement",
    )
    for name in names:
        for base in (".agents/skills", ".claude/skills"):
            assert (tmp_path / base / name / "SKILL.md").is_file()
    assert not check(tmp_path)


def test_install_generates_graft_for_all_clients_and_preserves_json_servers(tmp_path: Path):
    cursor = tmp_path / ".cursor/mcp.json"
    cursor.parent.mkdir()
    cursor.write_text(json.dumps({"mcpServers": {"local": {"command": "local-mcp"}}}), encoding="utf-8")
    init(tmp_path)
    install(tmp_path)
    cursor_servers = json.loads(cursor.read_text())["mcpServers"]
    claude_servers = json.loads((tmp_path / ".mcp.json").read_text())["mcpServers"]
    codex = (tmp_path / ".codex/config.toml").read_text()
    assert cursor_servers["local"] == {"command": "local-mcp"}
    assert cursor_servers["graft"]["args"] == ["-y", "@nanonets/graft", "mcp"]
    assert claude_servers["graft"] == cursor_servers["graft"]
    assert "agent-toolkit:graft start" in codex
    assert yaml.safe_load((tmp_path / ".agent/lock.yaml").read_text())["mcp_servers"] == ["graft"]
    assert not check(tmp_path)


def test_check_detects_graft_drift_without_writing(tmp_path: Path):
    init(tmp_path, "backend")
    install(tmp_path)
    cursor = tmp_path / ".cursor/mcp.json"
    value = json.loads(cursor.read_text())
    value["mcpServers"]["graft"]["command"] = "wrong"
    cursor.write_text(json.dumps(value), encoding="utf-8")
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert any("Graft MCP configuration" in error for error in check(tmp_path))
    after = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
