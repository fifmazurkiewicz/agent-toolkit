# Review Decision Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use native execution in this session. Steps use checkbox syntax for tracking.

**Goal:** Make every implementation-review finding receive a durable decision record and a derived, visible Kanban view.

**Architecture:** A new `review-decisions` skill owns the canonical
`reviews/review-decisions.md` contract and its derived
`review-decisions-kanban.html`. Existing lifecycle, review, implementation and
planning-board skills invoke it at their existing boundaries; no product code
or new runtime dependency is added.

**Tech Stack:** Markdown skills, static HTML/SVG through diagram-design,
Python pytest packaging and install tests.

**Spec:** `docs/superpowers/specs/2026-10-11-review-decision-workflow-design.md`

## Global Constraints

- `reviews/review-decisions.md` is canonical; its board is derived.
- Only a human owner may accept `Skip`; record the acceptance and a
  re-evaluation trigger.
- `Record as lesson` writes reusable, evidence-backed knowledge to Graft after
  archive; never create `lessons.md`.
- Keep source and `src/agent_toolkit/data/` package files byte-identical.
- Do not modify application source while rolling out the toolkit.

## Review Focus

- An information-only note must not create an empty decision card.
- A Skip without an explicit human acceptance or re-evaluation trigger must
  block an approve outcome.
- Fix differently must return to plan review when it changes a material plan
  criterion.
- Board text must not become the sole record of a finding decision.
- An archived lesson must not duplicate transient review details in Graft.

### Task 1: Define the review-decision skill and lifecycle contract

**Files:**
- Create: `skills/review-decisions/SKILL.md`
- Create: `src/agent_toolkit/data/skills/review-decisions/SKILL.md`
- Modify: `skills/implementation-review/SKILL.md`
- Modify: `skills/project-context-lifecycle/SKILL.md`
- Modify: `skills/implementation/SKILL.md`
- Modify: `skills/planning-boards/SKILL.md`
- Modify: packaged copies of each changed skill

**Interfaces:**
- Consumes: `reviews/implementation-review.md`, plan/progress/evidence records.
- Produces: `reviews/review-decisions.md` and
  `reviews/review-decisions-kanban.html`.

- [ ] Define the exact record fields and the four decision outcomes.
- [ ] Specify human-only Skip acceptance and material replan behavior.
- [ ] Specify board derivation and Graft lesson handoff.
- [ ] Copy each authoring skill exactly into its package location.

### Task 2: Select the workflow through profiles and standard documentation

**Files:**
- Modify: `profiles/web.yaml`, `profiles/backend.yaml`
- Modify: package profile copies
- Modify: `AGENT_STANDARD.md`, package copy, and `README.md`

**Interfaces:**
- Consumes: default profile skill sequence.
- Produces: `review-decisions` installed after `implementation-review`.

- [ ] Add the skill directly after implementation review in both profiles.
- [ ] Add the canonical-record rule to the shared standard and README.
- [ ] Copy the changed profiles and standard exactly into the package.

### Task 3: Test the selection, packaging, and contract

**Files:**
- Modify: `tests/test_core.py`

**Interfaces:**
- Consumes: profile lists and authoring/package directory trees.
- Produces: pytest assertions for installed skill and decision workflow text.

- [ ] Extend the default workflow ordering assertion.
- [ ] Assert both clients install the new skill.
- [ ] Assert lifecycle/review text names the record and board.
- [ ] Run `pytest -q` and fix any failure.

### Task 4: Roll out to managed projects

**Files:**
- Modify: each existing `/Users/Filip/dev/*/.agent/manifest.yaml` that uses
  agent-toolkit, plus generated managed skill files and locks.

**Interfaces:**
- Consumes: released local agent-toolkit package.
- Produces: a clean `agent-toolkit check` for every updated project.

- [ ] Insert `review-decisions` after `implementation-review` when absent.
- [ ] Run `agent-toolkit update` and `agent-toolkit check` per project.
- [ ] Preserve unrelated working-tree changes and report any project not
  managed by agent-toolkit.

### Task 5: Commit and publish the toolkit change

**Files:**
- Stage only review-decision workflow files; exclude pre-existing `uv.lock`.

- [ ] Review diff and test evidence.
- [ ] Commit with `feat: add review decision workflow`.
- [ ] Push the committed change to `origin/main` only after explicit user
  authorization for this remote mutation.
