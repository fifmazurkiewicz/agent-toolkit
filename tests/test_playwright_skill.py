"""An optional browser skill must vendor completely without changing defaults."""

import hashlib
import json
from pathlib import Path

import yaml

from agent_toolkit.core import check, init, install, data_file


def test_playwright_skill_is_opt_in_and_installs_for_every_client(tmp_path: Path):
    for profile in ("web", "backend"):
        root = tmp_path / profile
        init(root, profile)
        manifest_path = root / ".agent/manifest.yaml"
        config = yaml.safe_load(manifest_path.read_text())
        assert "playwright-cli" not in config["skills"]
        config["skills"].append("playwright-cli")
        manifest_path.write_text(yaml.safe_dump(config, sort_keys=False))
        install(root)
        for location in (".agents/skills", ".claude/skills"):
            skill = root / location / "playwright-cli"
            assert (skill / "SKILL.md").is_file()
            assert (skill / "references/playwright-tests.md").is_file()
            assert (skill / "references/storage-state.md").is_file()
            assert (skill / "LICENSE").is_file()
            provenance = json.loads((skill / "SOURCE.json").read_text())
            assert provenance["tag"] == "v0.1.23"
            assert provenance["repository"] == "https://github.com/microsoft/playwright-cli"
            for relative, expected_blob in provenance["files"].items():
                content = (skill / relative).read_bytes()
                actual_blob = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
                assert actual_blob == expected_blob, relative
            assert (skill / "SKILL.md").read_bytes() == data_file("skills", "playwright-cli", "SKILL.md").read_bytes()
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
        assert check(root) == []
        assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
