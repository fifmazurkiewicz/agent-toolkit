# Project Context Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a vendorable, Graft-backed project-context lifecycle and its seven workflow skills in both toolkit profiles.

**Architecture:** The feature is declarative: skill directories define behavior and existing profile, installer, package-data, and lock mechanisms distribute and hash them without a new CLI or schema. `project-context-lifecycle` owns the project-local context layout; stage skills own their individual entry, output, and gate contracts.

**Tech Stack:** Python 3.11+, PyYAML, setuptools package data, pytest, Markdown/YAML.

**Spec:** `docs/superpowers/specs/2026-10-03-project-context-lifecycle-design.md`

## Global Constraints

- Keep `AGENT_STANDARD.md`, `profiles/`, and `skills/` byte-identical to their copies under `src/agent_toolkit/data/`.
- Do not add dependencies, manifest fields, lock fields, CLI commands, client-adapter changes, or a `lessons.md` fallback.
- Use Graft as the preferred durable knowledge layer; use focused `rg` only when Graft is unavailable.
- Add lifecycle skills to both profiles in deterministic workflow order.
- `goal-implement` may execute only approved, explicitly automated work within declared file, network, and secret limits; stop after two failed repairs of one gate.
- `check` must stay read-only.

## Review Focus

- A profile omits one lifecycle stage or orders it after an action that depends on its artifact; assert every required name and relative ordering.
- A package copy differs by one byte from the authoring copy; retain the recursive parity test over all skills and profiles.
- A generated project lacks one lifecycle runtime directory for a selected client; install a profile and assert all names for canonical and Claude destinations.
- Graft cannot run; each lifecycle stage must direct a focused `rg` fallback and not create `lessons.md`.
- `goal-implement` sees a manual step, structural drift, or a third failed repair; its contract must return a human checklist or STOP rather than proceeding.

---

### Task 1: Define the lifecycle and stage-skill contracts

**Files:**
- Create: `skills/project-context-lifecycle/SKILL.md`
- Create: `skills/problem-framing/SKILL.md`
- Create: `skills/technical-research/SKILL.md`
- Create: `skills/plan-review/SKILL.md`
- Create: `skills/implementation/SKILL.md`
- Create: `skills/tdd/SKILL.md`
- Create: `skills/implementation-review/SKILL.md`
- Create: `skills/goal-implement/SKILL.md`
- Create matching eight files below `src/agent_toolkit/data/skills/`

**Interfaces:**
- Consumes: an existing project's `.agent/context/` directory, an active `<change-id>`, existing project instructions, Graft when available, and the artifacts produced by preceding stages.
- Produces: the fixed context layout and change-local artifacts specified in the design: `frame.md`, `research.md`, `decisions.md`, `plan.md`, `progress.md`, `evidence.md`, and review reports under `reviews/`.

- [ ] **Step 1: Write the content assertions before authoring the skills**

Add a test that loads the authoring files and asserts the lifecycle names,
the `.agent/context/changes/<change-id>/` location, `progress.md`, Graft, and
the no-`lessons.md` boundary. Assert `goal-implement` contains the phrases
`two repair attempts`, `manual`, and `STOP`.

```python
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
```

- [ ] **Step 2: Run the focused test and verify failure**

Run: `pytest tests/test_core.py::test_project_context_skills_define_graft_backed_lifecycle -q`

Expected: FAIL because the lifecycle and goal skill files do not exist.

- [ ] **Step 3: Author the minimum skill contracts and package copies**

Use a YAML frontmatter `name` equal to each directory name and a precise
selection description. The lifecycle skill creates no files automatically;
it specifies the layout, order, active-change rule, archive condition, Graft
query/write boundary, and focused `rg` fallback. Each stage states inputs,
artifact output, non-goals, and handoff. The TDD skill requires a failing
test before behavior changes and a deliberately broken protected behavior
before declaring test evidence. The goal skill restricts autonomy to approved
automated plan work, records boundaries and gates, limits a single gate to two
repairs, and emits STOP or manual items instead of improvising.

Copy every authoring file byte-for-byte to its package-data counterpart.

- [ ] **Step 4: Run the focused test and verify success**

Run: `pytest tests/test_core.py::test_project_context_skills_define_graft_backed_lifecycle -q`

Expected: PASS.

- [ ] **Step 5: Commit the skill contracts**

```bash
git add skills src/agent_toolkit/data/skills tests/test_core.py
git commit -m "feat: add project context workflow skills"
```

### Task 2: Select the workflow in profiles and shared guidance

**Files:**
- Modify: `profiles/backend.yaml`
- Modify: `profiles/web.yaml`
- Modify: `src/agent_toolkit/data/profiles/backend.yaml`
- Modify: `src/agent_toolkit/data/profiles/web.yaml`
- Modify: `AGENT_STANDARD.md`
- Modify: `src/agent_toolkit/data/AGENT_STANDARD.md`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: the eight skill names introduced in Task 1 and the existing profile list order.
- Produces: manifests initialized from either profile select every lifecycle skill in a usable order, and installed `AGENTS.md` names the project-context/Graft boundary.

- [ ] **Step 1: Extend the profile test with exact required ordering**

Replace the narrow product-workflow assertion with an ordered list that checks
the existing stages plus the new lifecycle sequence. Use an explicit helper
for relative order instead of relying on unrelated skill positions.

```python
workflow = [
    "project-context-lifecycle", "problem-framing", "technical-research",
    "production-product-requirements", "writing-plans", "plan-review",
    "implementation", "tdd", "implementation-review", "goal-implement",
]
assert all(name in skills for name in workflow)
assert [skills.index(name) for name in workflow] == sorted(skills.index(name) for name in workflow)
```

- [ ] **Step 2: Run the profile test and verify failure**

Run: `pytest tests/test_core.py::test_product_workflow_skills_are_selected_and_installed_by_profiles -q`

Expected: FAIL because profiles do not select the new names.

- [ ] **Step 3: Update profile and standard content**

Insert `project-context-lifecycle` before all context stages in both profiles.
Place `problem-framing` and `technical-research` after existing product
shaping, then `plan-review`, `implementation`, `tdd`,
`implementation-review`, and `goal-implement` after `writing-plans`.
Update the shared standard with one concise lifecycle rule: use the active
change context for change-local state, query Graft for durable knowledge, and
do not create a parallel `lessons.md` store. Copy all three edited files
byte-for-byte into package data.

- [ ] **Step 4: Run the profile and installation tests and verify success**

Run: `pytest tests/test_core.py::test_product_workflow_skills_are_selected_and_installed_by_profiles tests/test_core.py::test_packaged_content_matches_authoring_files -q`

Expected: PASS.

- [ ] **Step 5: Commit profile selection**

```bash
git add AGENT_STANDARD.md profiles src/agent_toolkit/data tests/test_core.py
git commit -m "feat: select context lifecycle in profiles"
```

### Task 3: Document the shipped workflow and validate distribution

**Files:**
- Modify: `README.md`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: documented skill contracts, profile ordering, and the existing install/lock behavior.
- Produces: user-facing setup guidance and an installation test proving every selected client receives the lifecycle skills and `check` remains clean.

- [ ] **Step 1: Add a failing client-installation test**

Create a profile, install it, assert that every new skill's `SKILL.md` exists
in `.agents/skills` and `.claude/skills`, then assert `check(root)` is empty.

```python
def test_project_context_workflow_installs_for_all_selected_clients(tmp_path: Path):
    init(tmp_path, "backend")
    install(tmp_path)
    for name in ("project-context-lifecycle", "problem-framing", "technical-research",
                 "plan-review", "implementation", "tdd", "implementation-review", "goal-implement"):
        for base in (".agents/skills", ".claude/skills"):
            assert (tmp_path / base / name / "SKILL.md").is_file()
    assert not check(tmp_path)
```

- [ ] **Step 2: Run the focused test and verify failure**

Run: `pytest tests/test_core.py::test_project_context_workflow_installs_for_all_selected_clients -q`

Expected: FAIL until the profile and skill work from Tasks 1–2 are present.

- [ ] **Step 3: Update README workflow guidance**

Replace the old linear happy path with the lifecycle sequence, state that
`project-context-lifecycle` manages `.agent/context/`, explain that Graft is
the durable knowledge layer with focused `rg` fallback, and document
`goal-implement` as opt-in approved-plan automation with explicit limits. Do
not claim CI review, AWS registry, or npm support.

- [ ] **Step 4: Run focused verification and full test suite**

Run:

```bash
pytest tests/test_core.py::test_project_context_workflow_installs_for_all_selected_clients -q
pytest
python -m build
```

Expected: every test passes and `python -m build` produces both source and
wheel distributions without adding tracked build artifacts.

- [ ] **Step 5: Verify clean formatting and package parity, then commit**

```bash
git diff --check
pytest tests/test_core.py::test_packaged_content_matches_authoring_files -q
git add README.md tests/test_core.py
git commit -m "docs: document project context lifecycle"
```

### Task 4: Final release verification and push

**Files:**
- Verify only: all modified files from Tasks 1–3.

**Interfaces:**
- Consumes: complete implementation and a clean `main` branch.
- Produces: evidence that the toolkit builds, tests, and detects no drift; a commit pushed to `origin/main`.

- [ ] **Step 1: Verify status and locked installation behavior**

Run:

```bash
git status --short --branch
pytest
python -m build
```

Expected: intended commits are present, tests pass, and package build succeeds.

- [ ] **Step 2: Exercise read-only drift check**

Run the existing `test_check_detects_skill_hash_and_lock_drift_without_writing`
test to prove the new skill hashes use the same non-mutating check path.

```bash
pytest tests/test_core.py::test_check_detects_skill_hash_and_lock_drift_without_writing -q
```

Expected: PASS.

- [ ] **Step 3: Push the committed main branch**

```bash
git push origin main
```

Expected: remote `main` accepts the new commits.
