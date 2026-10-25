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
    assert main(["--project", str(tmp_path), "install", "--no-graft-build"]) == 0
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
            "planning-boards",
            "problem-framing",
            "technical-research",
            "production-product-requirements",
            "test-strategy",
            "writing-plans",
            "plan-review",
            "implementation",
            "tdd",
            "behavioral-tests",
            "mutation-testing",
            "implementation-review",
            "review-decisions",
            "goal-implement",
        ]
        assert all(name in skills for name in workflow)
        assert [skills.index(name) for name in workflow] == sorted(skills.index(name) for name in workflow)
        assert skills.index("brainstorming") < skills.index("idea-validation")
        assert skills.index("idea-validation") < skills.index("production-product-requirements")
        assert skills.index("project-context-lifecycle") < skills.index("planning-boards")
        assert skills.index("production-product-requirements") < skills.index("writing-plans")
        install(root)
        for directory in (".agents/skills", ".claude/skills"):
            assert (root / directory / "idea-validation/SKILL.md").is_file()
            assert (root / directory / "production-product-requirements/SKILL.md").is_file()
            assert (root / directory / "planning-boards/SKILL.md").is_file()
            assert (root / directory / "review-decisions/SKILL.md").is_file()
            assert (root / directory / "test-strategy/SKILL.md").is_file()
            assert (root / directory / "behavioral-tests/SKILL.md").is_file()
            assert (root / directory / "mutation-testing/SKILL.md").is_file()


def test_project_context_skills_define_graft_backed_lifecycle():
    root = Path(__file__).resolve().parents[1]
    lifecycle = (root / "skills/project-context-lifecycle/SKILL.md").read_text()
    boards = (root / "skills/planning-boards/SKILL.md").read_text()
    goal = (root / "skills/goal-implement/SKILL.md").read_text()
    assert ".agent/context/changes/<change-id>/" in lifecycle
    assert "progress.md" in lifecycle
    assert "Graft" in lifecycle
    assert "lessons.md" in lifecycle
    assert "two repair attempts" in goal
    assert "manual" in goal
    assert "STOP" in goal
    assert "docs/roadmap.md" in boards
    assert "roadmap-kanban.html" in boards
    assert "plan-kanban.html" in boards
    assert "source of truth" in boards


def test_project_context_workflow_installs_for_all_selected_clients(tmp_path: Path):
    init(tmp_path, "backend")
    install(tmp_path)
    names = (
        "project-context-lifecycle",
        "planning-boards",
        "problem-framing",
        "technical-research",
        "plan-review",
        "implementation",
        "tdd",
        "implementation-review",
        "review-decisions",
        "goal-implement",
    )
    for name in names:
        for base in (".agents/skills", ".claude/skills"):
            assert (tmp_path / base / name / "SKILL.md").is_file()
    assert not check(tmp_path)


def test_review_decisions_are_selected_installed_and_canonical():
    root = Path(__file__).resolve().parents[1]
    review = (root / "skills/implementation-review/SKILL.md").read_text()
    decisions = (root / "skills/review-decisions/SKILL.md").read_text()
    lifecycle = (root / "skills/project-context-lifecycle/SKILL.md").read_text()
    boards = (root / "skills/planning-boards/SKILL.md").read_text()

    assert "reviews/review-decisions.md" in review
    assert "reviews/review-decisions.md" in decisions
    assert "reviews/review-decisions-kanban.html" in decisions
    assert "human owner" in decisions
    assert "reviews/review-decisions.md" in lifecycle
    assert "review-decisions-kanban.html" in boards

    for profile in ("web", "backend"):
        skills = yaml.safe_load((root / "profiles" / f"{profile}.yaml").read_text())["skills"]
        assert skills.index("implementation-review") < skills.index("review-decisions")
        assert skills.index("review-decisions") < skills.index("goal-implement")


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


def test_test_strategy_is_the_shared_source_for_test_risks():
    root = Path(__file__).resolve().parents[1]
    strategy = (root / "skills/test-strategy/SKILL.md").read_text()
    standard = (root / "AGENT_STANDARD.md").read_text()
    assert "docs/testing-strategy.md" in strategy
    for section in ("Key risks", "Evidence", "Existing test profile", "QA phases", "Useful test types", "Agent quality boosts", "Cookbook"):
        assert section in strategy
    assert "abuse scenario" in strategy
    assert "human owner" in strategy
    assert "draft" in strategy
    assert "docs/testing-strategy.md" in standard
    assert "abuse scenario" in standard
    assert "npx -y @nanonets/graft build" in standard
    assert "--deep" in standard
    for name in ("tdd", "writing-plans", "implementation-review"):
        assert "docs/testing-strategy.md" in (root / "skills" / name / "SKILL.md").read_text()


def test_standard_carries_shared_defaults():
    standard = (Path(__file__).resolve().parents[1] / "AGENT_STANDARD.md").read_text()
    for text in ("Vercel", "GDPR", "never request it in chat", "44px", "ask the user to review it", "do not change deployment or runtime configuration"):
        assert text in standard


def test_graft_build_reports_missing_node(tmp_path: Path, monkeypatch):
    from agent_toolkit import local

    monkeypatch.setattr(local.shutil, "which", lambda name: None)
    assert "npx is unavailable" in local.build_graft(tmp_path)


def test_setup_approves_graft_for_each_client_idempotently(tmp_path: Path, monkeypatch):
    from agent_toolkit import local

    project, home = tmp_path / "project", tmp_path / "home"
    init(project)
    (project / ".git/info").mkdir(parents=True)
    (home / ".codex").mkdir(parents=True)
    (home / ".codex/config.toml").write_text('model = "x"\n', encoding="utf-8")
    (project / ".claude").mkdir()
    (project / ".claude/settings.local.json").write_text('{"permissions": {"allow": []}}', encoding="utf-8")
    monkeypatch.setattr(local.shutil, "which", lambda name: None)
    before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file() and ".claude" not in p.parts and ".git" not in p.parts}

    steps = local.setup(project, home)
    assert steps == ["Codex: project trusted", "Cursor: CLI not found; run `agent mcp enable graft` in the project", "Claude Code: graft approved"]
    config = (home / ".codex/config.toml").read_text()
    assert config.startswith('model = "x"\n') and f'[projects."{project}"]\ntrust_level = "trusted"\n' in config
    claude = json.loads((project / ".claude/settings.local.json").read_text())
    assert claude == {"permissions": {"allow": []}, "enabledMcpjsonServers": ["graft"]}
    assert "/.claude/settings.local.json" in (project / ".git/info/exclude").read_text().splitlines()
    assert before == {p: p.read_bytes() for p in before}

    local.setup(project, home)
    assert (home / ".codex/config.toml").read_text() == config
    assert json.loads((project / ".claude/settings.local.json").read_text()) == claude
    assert (project / ".git/info/exclude").read_text().count("settings.local.json") == 1


def test_behavioral_tests_skill_defines_the_three_stages():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "skills/behavioral-tests/SKILL.md").read_text()
    for text in ("rather than what it currently does", "STOP and ask", "observable outcome", "never reuse the logic", "different regression", "mark the row uncertain"):
        assert text in skill
    for name in ("tdd", "test-strategy"):
        assert "behavioral-tests" in (root / "skills" / name / "SKILL.md").read_text()
    assert "duplicate one another" in (root / "skills/implementation-review/SKILL.md").read_text()
    assert "`behavioral-tests`" in (root / "AGENT_STANDARD.md").read_text()


def test_mutation_testing_is_consent_gated_and_language_aware():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "skills/mutation-testing/SKILL.md").read_text()
    for text in ("always ask before running", "Never run mutation testing or add its tooling without explicit approval", "mutmut", "StrykerJS", "Never install\nglobal tools", "Equivalent"):
        assert text in skill
    assert "`mutation-testing`" in (root / "skills/behavioral-tests/SKILL.md").read_text()


def test_install_manages_gitleaks_allowlist_and_preserves_project_rules(tmp_path: Path):
    project_rules = 'title = "x"\n\n[extend]\nuseDefault = true\n\n[allowlist]\npaths = [\'\'\'\\.env\\.example$\'\'\']\n'
    (tmp_path / ".gitleaks.toml").write_text(project_rules, encoding="utf-8")
    init(tmp_path)
    install(tmp_path)
    config = (tmp_path / ".gitleaks.toml").read_text()
    assert config.startswith(project_rules.rstrip("\n"))
    assert config.count("# agent-toolkit:gitleaks start") == 1
    assert "[[allowlists]]" in config and "agent/lock" in config
    install(tmp_path)
    assert (tmp_path / ".gitleaks.toml").read_text() == config
    assert not check(tmp_path)
    (tmp_path / ".gitleaks.toml").write_text(project_rules, encoding="utf-8")
    assert "Gitleaks allowlist differs: .gitleaks.toml" in check(tmp_path)


def test_new_gitleaks_config_extends_default_rules(tmp_path: Path):
    init(tmp_path)
    install(tmp_path)
    assert (tmp_path / ".gitleaks.toml").read_text().startswith("[extend]\nuseDefault = true\n")

