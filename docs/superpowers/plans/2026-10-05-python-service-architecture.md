# Python Service Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use native execution task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in Python service architecture skill and adopt its concise, project-specific boundary rule in every in-scope Python repository.

**Architecture:** The toolkit gains one independent skill, selected explicitly by Python service manifests and propagated by the existing installer. Each project receives only a local boundary statement at its backend/package scope; existing source files are not moved. Trady makes `AGENTS.md` canonical for its safety rules.

**Tech Stack:** Python 3, YAML manifests, Markdown agent instructions, pytest, existing `agent-toolkit` installer.

**Spec:** `docs/superpowers/specs/2026-10-05-python-service-architecture-design.md`

## Global Constraints

- Do not modify nonstandard files already dirty in any worktree.
- Do not add dependencies or refactor source code.
- Do not add the skill to the general `backend` profile.
- Generate managed skill copies and locks with the existing toolkit installer.
- Commit only the exact files owned by this change, on each repository's `main` branch.

## Review Focus

- A non-Python backend profile must not select the new skill by default.
- Every selected project must receive identical canonical and Claude skill copies and an updated lock hash.
- Architecture language must permit the existing app/package layout rather than imply a source migration.
- Trady's `AGENTS.md` must contain every hard risk rule previously visible only to Claude.
- Installer checks must remain read-only and report no drift after regeneration.

---

### Task 1: Add and package the opt-in toolkit skill

**Files:**
- Create: `skills/python-service-architecture/SKILL.md`
- Create: `src/agent_toolkit/data/skills/python-service-architecture/SKILL.md`
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: manifest `skills` list validated by `agent_toolkit.core.manifest()`.
- Produces: a selectable skill folder copied by `install()` to `.agents/skills/` and `.claude/skills/`.

- [ ] **Step 1: Add a failing packaging test**

Add a test asserting that the source skill and packaged data skill have identical bytes, and that both profiles omit `python-service-architecture`.

- [ ] **Step 2: Run the focused test to verify failure**

Run: `pytest tests/test_core.py -k python_service_architecture -v`

Expected: FAIL because neither skill copy exists.

- [ ] **Step 3: Add the compact skill in both source locations**

Write equivalent `SKILL.md` files with frontmatter that selects the skill for Python service structure and with only these behaviors: prefer `src` layout for new installable packages, enforce inward dependency direction, use `main.py` as composition root, separate unit from integration tests, and avoid empty layers or speculative abstractions.

- [ ] **Step 4: Re-run the focused test**

Run: `pytest tests/test_core.py -k python_service_architecture -v`

Expected: PASS.

- [ ] **Step 5: Run toolkit verification**

Run: `pytest`

Expected: PASS, including existing source/package synchronization tests.

- [ ] **Step 6: Commit the toolkit change**

Run:

```bash
git add skills/python-service-architecture/SKILL.md \
  src/agent_toolkit/data/skills/python-service-architecture/SKILL.md \
  tests/test_core.py
git commit -m "feat: add Python service architecture skill"
```

### Task 2: Select and install the skill in managed Python projects

**Files:**
- Modify: `.agent/manifest.yaml`, `.agent/lock.yaml`, `.agents/skills/python-service-architecture/SKILL.md`, `.claude/skills/python-service-architecture/SKILL.md` in Aide, Langy, POZZ, Reelcut, TeacherHelper, goat, Trady, and Linksifty.

**Interfaces:**
- Consumes: the new packaged skill and each existing manifest.
- Produces: matching managed copies and locks that pass `agent-toolkit check`.

- [ ] **Step 1: Add the skill selection to each manifest**

Append `python-service-architecture` after `ponytail-review` in each listed manifest, retaining profile, clients, and all existing selections.

- [ ] **Step 2: Install with the toolkit from its checkout**

Run the following commands from the toolkit checkout:

```bash
python -m agent_toolkit --project /Users/Filip/dev/Aide install
python -m agent_toolkit --project /Users/Filip/dev/Langy install
python -m agent_toolkit --project /Users/Filip/dev/POZZ install
python -m agent_toolkit --project /Users/Filip/dev/Reelcut install
python -m agent_toolkit --project /Users/Filip/dev/TeacherHelper install
python -m agent_toolkit --project /Users/Filip/dev/goat install
python -m agent_toolkit --project /Users/Filip/dev/Trady install
python -m agent_toolkit --project /Users/Filip/dev/linksifty install
```

Expected: only the selected manifest's lock and generated new skill directories change, plus any managed blocks already expected by the installer.

- [ ] **Step 3: Check generated state**

Run the following commands from the toolkit checkout:

```bash
python -m agent_toolkit --project /Users/Filip/dev/Aide check
python -m agent_toolkit --project /Users/Filip/dev/Langy check
python -m agent_toolkit --project /Users/Filip/dev/POZZ check
python -m agent_toolkit --project /Users/Filip/dev/Reelcut check
python -m agent_toolkit --project /Users/Filip/dev/TeacherHelper check
python -m agent_toolkit --project /Users/Filip/dev/goat check
python -m agent_toolkit --project /Users/Filip/dev/Trady check
python -m agent_toolkit --project /Users/Filip/dev/linksifty check
```

Expected: exit 0 and no filesystem writes.

- [ ] **Step 4: Commit each managed-project update**

For each repository, stage only its manifest, lock, and two generated skill files, then commit with `chore: add Python architecture skill`.

### Task 3: Add narrowly scoped local boundary rules

**Files:**
- Create: `Aide/backend/AGENTS.md`
- Modify: `Langy/backend/AGENTS.md`, `POZZ/backend/AGENTS.md`, `Reelcut/backend/AGENTS.md`, `TeacherHelper/AGENTS.md`, `goat/backend/AGENTS.md`, `linksift/AGENTS.md`, `linksifty/AGENTS.md`

**Interfaces:**
- Consumes: the selected skill and each project's current layout.
- Produces: project-local exceptions and placement rules without duplicating framework guidance.

- [ ] **Step 1: Add one concise boundary paragraph per project**

State the actual package root and project-specific exception from the approved spec. Use `backend/app/` for Aide, Langy, POZZ, and goat; `backend/src/reelcut/` for Reelcut; `backend/teacher_helper/` for TeacherHelper; `src/linksift/` for LinkSift; and Linksifty's package only when it is introduced or expanded.

- [ ] **Step 2: Preserve existing instructions**

Do not repeat FastAPI, Pydantic, lint, command, or generic Clean Code advice already covered elsewhere. Do not change unrelated product requirements.

- [ ] **Step 3: Verify instruction diffs**

Run these commands in the named repositories:

```bash
git -C /Users/Filip/dev/Aide diff --check -- backend/AGENTS.md
git -C /Users/Filip/dev/Langy diff --check -- backend/AGENTS.md
git -C /Users/Filip/dev/POZZ diff --check -- backend/AGENTS.md
git -C /Users/Filip/dev/Reelcut diff --check -- backend/AGENTS.md
git -C /Users/Filip/dev/TeacherHelper diff --check -- AGENTS.md
git -C /Users/Filip/dev/goat diff --check -- backend/AGENTS.md
git -C /Users/Filip/dev/linksift diff --check -- AGENTS.md
git -C /Users/Filip/dev/linksifty diff --check -- AGENTS.md
```

Expected: no whitespace errors and no source code files changed.

- [ ] **Step 4: Commit local rules repository by repository**

For each repository, stage only its designated `AGENTS.md` files and commit with `docs: define Python service boundaries`.

### Task 4: Make Trady's AGENTS.md canonical for risk and architecture rules

**Files:**
- Modify: `Trady/AGENTS.md`, `Trady/CLAUDE.md`

**Interfaces:**
- Consumes: the existing hard rules from `CLAUDE.md`.
- Produces: a single canonical rule source for Codex and a Claude wrapper importing it.

- [ ] **Step 1: Copy all safety-critical rules into AGENTS.md**

Preserve the existing constraints on risk-limit changes, `dry_run`, credentials, deterministic pricing/sizing, and risk-code tests. Add the narrow application scope: service boundaries apply to `sidecar/`, `mcp_server/`, and future risk-gate code, not Freqtrade strategies.

- [ ] **Step 2: Reduce CLAUDE.md to product context plus the existing managed AGENTS import**

Retain the product description and execution-environment facts that are Claude-specific only if they are not safety rules. Ensure the managed `@AGENTS.md` import remains present.

- [ ] **Step 3: Verify rule availability**

Run: `rg -n "dry_run|risk limits|leverage caps|API keys" AGENTS.md`

Expected: all hard-risk topics are present in `AGENTS.md`.

- [ ] **Step 4: Commit the Trady instruction change**

Run:

```bash
git add AGENTS.md CLAUDE.md
git commit -m "docs: make Trady risk rules canonical"
```

### Task 5: Final cross-repository verification and report

**Files:**
- Modify: none.

**Interfaces:**
- Consumes: all commits from Tasks 1–4.
- Produces: verified clean commits with unrelated local work preserved.

- [ ] **Step 1: Verify toolkit source integrity**

Run: `pytest` in `agent-toolkit`.

Expected: PASS.

- [ ] **Step 2: Verify every managed project**

Run:

```bash
python -m agent_toolkit --project /Users/Filip/dev/Aide check
python -m agent_toolkit --project /Users/Filip/dev/Langy check
python -m agent_toolkit --project /Users/Filip/dev/POZZ check
python -m agent_toolkit --project /Users/Filip/dev/Reelcut check
python -m agent_toolkit --project /Users/Filip/dev/TeacherHelper check
python -m agent_toolkit --project /Users/Filip/dev/goat check
python -m agent_toolkit --project /Users/Filip/dev/Trady check
python -m agent_toolkit --project /Users/Filip/dev/linksifty check
```

Expected: every check exits 0.

- [ ] **Step 3: Inspect repository status**

Run `git status --short` in every repository and compare it with the pre-change dirty-file inventory.

Expected: no unrelated tracked or untracked file is staged or committed.

- [ ] **Step 4: Report commits and verification**

Provide the commit SHA for the toolkit and every changed project, identify any intentionally retained pre-existing dirty files, and state whether remote push was performed or requires separate authority.
