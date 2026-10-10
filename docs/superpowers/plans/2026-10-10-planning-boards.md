# Planning Boards Implementation Plan

> **For agentic workers:** Execute tasks in order. Keep the authoring and packaged toolkit copies synchronized, and run the named tests before committing.

**Goal:** Add maintained Kanban visualizations for product roadmaps and active change plans.

**Architecture:** A compact `planning-boards` skill supplies the two-level board contract. Existing lifecycle, planning, implementation, and review skills invoke that contract at the point where their canonical Markdown records change. Static HTML/SVG boards remain derived views rather than a workflow database.

**Tech Stack:** Markdown skills, YAML profiles, pytest, existing `diagram-design` skill.

**Spec:** `docs/superpowers/specs/2026-10-10-planning-boards-design.md`

## Global Constraints

- Preserve `roadmap.md`, `plan.md`, and `progress.md` as the canonical records.
- Do not add a dashboard, external service, dependency, or live synchronization.
- Synchronize every edited first-party authoring file under `skills/` or `profiles/` with `src/agent_toolkit/data/`.
- Keep `planning-boards` selected by both bundled profiles.

## Review Focus

- Board status differs from `progress.md` after a task is marked complete.
- A material replan changes the board without a renewed plan review.
- The roadmap board becomes an unbounded archive of every finished task.
- A board is generated before its source records exist.
- Packaged and authoring copies drift.

### Task 1: Define and package the board contract

**Files:**
- Create: `skills/planning-boards/SKILL.md`
- Create: `src/agent_toolkit/data/skills/planning-boards/SKILL.md`
- Modify: `profiles/web.yaml`
- Modify: `profiles/backend.yaml`
- Modify: `src/agent_toolkit/data/profiles/web.yaml`
- Modify: `src/agent_toolkit/data/profiles/backend.yaml`
- Modify: `AGENT_STANDARD.md`
- Modify: `src/agent_toolkit/data/AGENT_STANDARD.md`

- [ ] Define source-of-truth, file locations, board columns, generation events, and material-drift stop condition.
- [ ] Add `planning-boards` after `project-context-lifecycle` in both profiles and packaged copies.
- [ ] Verify every authoring/profile change matches its packaged equivalent.

### Task 2: Connect the board contract to the lifecycle

**Files:**
- Modify: `skills/project-context-lifecycle/SKILL.md`
- Modify: `skills/writing-plans/SKILL.md`
- Modify: `skills/implementation/SKILL.md`
- Modify: `skills/implementation-review/SKILL.md`
- Modify: matching `src/agent_toolkit/data/skills/*/SKILL.md` files

- [ ] Require the lifecycle to create/synchronize a change board for meaningful changes and preserve it on archive.
- [ ] Require plans to initialize their board and to reconcile it after a replan.
- [ ] Require implementation to update canonical progress before the board.
- [ ] Require review to reject inconsistent board and canonical status.

### Task 3: Test profile selection and packaged parity

**Files:**
- Modify: `tests/test_core.py`

- [ ] Extend workflow-profile assertions to expect `planning-boards` in order and installed for `.agents` and `.claude`.
- [ ] Add assertions for board contract wording and source/package byte parity.
- [ ] Run `pytest` and `agent-toolkit check` against a temporary initialized project.

### Task 4: Document the public workflow

**Files:**
- Modify: `README.md`

- [ ] Describe the roadmap board, change board, source-of-truth rule, and replan behavior in the shared workflow section.
- [ ] Run the complete test suite.
