# Product Workflow Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use native execution task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the agreed product-discovery-to-delivery workflow to both default profiles without changing the installer architecture.

**Architecture:** Skill documents remain ordinary vendored directories. Existing profile manifests select them and the installer copies and hashes them for every supported client. A focused standard rule requires context gathering through project documentation and Graft before significant work.

**Tech Stack:** Python 3, PyYAML, pytest, Markdown, YAML.

**Spec:** `docs/superpowers/specs/2026-10-03-product-workflow-skills.md`

## Global Constraints

- Keep authoring and packaged skill trees byte-identical.
- Add no dependency, manifest schema, or installer change.
- Add both product workflow skills to `web` and `backend` after `brainstorming` and before `writing-plans`.
- PRD guidance must not become file-by-file implementation planning.
- Use existing docs and Graft for significant project context; use focused `rg` only when Graft is unavailable.

## Review Focus

- Fresh web and backend projects select both new skills in the required order.
- Installation copies new skills to canonical and Claude directories.
- Packaged and authoring skills remain byte-identical.
- The PRD skill hands technical planning to `writing-plans` rather than prescribing files.
- The happy path does not force validation for already-decided maintenance work.

---

### Task 1: Add profile contract coverage

**Files:** Modify `tests/test_core.py`.

**Interfaces:** Consumes `init`, `install`, and YAML manifests; produces regression coverage for ordering and installation.

- [ ] Write a failing test that initializes both profiles and asserts: `brainstorming < idea-validation < production-product-requirements < writing-plans`.
- [ ] In the same test, install each project and assert both new `SKILL.md` files exist under `.agents/skills` and `.claude/skills`.
- [ ] Run `pytest tests/test_core.py::test_product_workflow_skills_are_selected_and_installed_by_profiles -v`; expect failure before profile changes.

### Task 2: Author and package workflow skills

**Files:** Create paired `SKILL.md` files for `idea-validation` and `production-product-requirements` in `skills/` and `src/agent_toolkit/data/skills/`; modify paired `brainstorming/SKILL.md` files.

**Interfaces:** Consumes decisions from the preceding workflow stage; produces validation findings, solution-shaping decisions, or a production-ready PRD for the next named skill.

- [ ] Write `idea-validation`: problem, target user, alternatives, evidence, assumptions, risks, cheapest validation; prohibit unilateral go/no-go.
- [ ] Write `production-product-requirements`: problem/context, goals/non-goals, users/flows, functional requirements, edge/error states, constraints, acceptance criteria, risks/open questions; hand technical planning to `writing-plans` and never name files, classes, or migrations.
- [ ] Update `brainstorming` to reuse validation output and shape business flow, user flow, solution alternatives, architecture/integrations, constraints, scope/non-scope, and delivery risks without repeating market evidence or validation experiments.
- [ ] Verify each authoring/package pair with `cmp`.
- [ ] Re-run the focused profile test; expect pass.

### Task 3: Apply standard, profiles, and README

**Files:** Modify `AGENT_STANDARD.md`, its packaged copy, both profile YAML files, and `README.md`.

**Interfaces:** Consumes the installed standard block and profile lists; produces context-aware rules, new fresh-manifest defaults, and documentation.

- [ ] Add a standard rule for significant changes: establish relevant stack, architecture, deployment model, domain/business boundaries, and local patterns from existing docs and Graft; use focused `rg` only when Graft is unavailable and do not reconstruct context.
- [ ] Insert `idea-validation` and `production-product-requirements` in both profiles between `brainstorming` and `writing-plans`.
- [ ] Document the conditional happy path: `idea-validation → brainstorming → production-product-requirements → writing-plans → implementation/review`; start at the earliest missing stage, and do not require every stage for already-decided maintenance work.
- [ ] Run `pytest -q`, `python -m build`, and `pytest tests/test_core.py::test_packaged_content_matches_authoring_files -v`; all must pass.

### Task 4: Publish verified changes

**Files:** No source files expected.

**Interfaces:** Consumes verified commits on `main`; produces committed changes on remote `main`.

- [ ] Inspect branch, remote, and worktree status.
- [ ] Commit the complete verified change set with a conventional feature message.
- [ ] Push `main` to the configured remote. If credentials or branch protection reject it, preserve commits and report the exact blocker.
