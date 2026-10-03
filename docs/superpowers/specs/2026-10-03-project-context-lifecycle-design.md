# Project Context Lifecycle Design

## Problem and outcome

`agent-toolkit` currently supplies product-shaping skills and generic
implementation guidance, but it does not provide a consistent, persisted
context for a single change as it moves from problem definition through review.
Projects therefore have no shared contract for locating the active change,
recording decisions, retaining verification evidence, or closing work cleanly.

The toolkit will provide a small project-context lifecycle subsystem and six
workflow skills that make this progression explicit:

```text
problem-framing -> technical-research -> decisions -> plan -> plan-review
-> implementation / tdd -> evidence -> implementation-review -> archive
```

The outcome is a vendorable workflow that works for all supported clients and
is automatically selected by the existing `web` and `backend` profiles.

## Scope

### Included

- A `project-context-lifecycle` skill defining the `.agent/context/` layout,
  active-change selection, lifecycle transitions, and archiving rules.
- Separate skills for `problem-framing`, `technical-research`, `plan-review`,
  `implementation`, `tdd`, `implementation-review`, and `goal-implement`.
- A standard set of change-local artifacts: `frame.md`, `research.md`,
  `decisions.md`, `plan.md`, `progress.md`, `evidence.md`, and `reviews/`.
- Graft as the durable knowledge store for reusable project lessons and
  discoveries; workflow artifacts only contain change-specific context.
- Profile ordering, shared standard, README, packaged-data parity, and tests.

### Excluded

- New CLI commands, manifest fields, lock-file schema, or runtime
  dependencies.
- Automatic context creation, automatic Graft writes, or an append-only
  `lessons.md` file.
- Changing client adapters or the existing MCP configuration.
- CI review automation, npm packaging, AWS CodeArtifact, Terraform, and
  GitHub Actions publication pipelines.

## Architecture

The subsystem is documentation-only: its contract lives in vendored skills and
the existing installer copies it and hashes it like every other skill. This
avoids adding a second configuration or lifecycle engine. `.agent/context/`
belongs to each consumer project and is intentionally outside the toolkit's
managed runtime skill directories.

For a change named `<change-id>`, agents use:

```text
.agent/context/
  foundation/                 # optional stable, explicit repo contracts
  changes/<change-id>/
    frame.md
    research.md
    decisions.md
    plan.md
    progress.md
    evidence.md
    reviews/
  archive/<change-id>/
```

`progress.md` is the canonical in-progress state. The implementation and TDD
skills update it and link concrete verification evidence. Archiving moves the
completed change directory to `archive/` only after implementation review is
complete. A project may keep a minimal foundation directory when it has stable
contracts worth recording, but it is not a duplicate long-term lessons store.

## Graft knowledge boundary

Graft is the preferred persistent knowledge layer. Before research, planning,
implementation, and review, agents query Graft for relevant conventions and
past decisions. After a completed archive, an agent may record only reusable,
evidence-backed knowledge in Graft according to the project's Graft policy.
It must not upload credentials, personal data, transient work logs, or
unverified conclusions.

If Graft is unavailable, the existing focused `rg` fallback applies. No
`lessons.md` fallback is introduced: absence of Graft reduces retrieval
capability but does not create a second, divergent source of truth.

## Workflow skill contracts

- **problem-framing** creates `frame.md`: problem, affected users or systems,
  constraints, success criteria, and explicitly stated assumptions.
- **technical-research** creates `research.md`: verified repository facts,
  external facts with source/date where relevant, unknowns, and alternatives;
  it does not select the solution.
- **plan-review** reviews `plan.md` against `frame.md`, `research.md`, and
  `decisions.md`, recording findings in `reviews/plan-review.md` before work
  begins.
- **implementation** executes accepted plan criteria only, updates
  `progress.md`, and records changed surfaces and verification in `evidence.md`.
- **tdd** writes a focused failing test before behavioral implementation when a
  testable behavior is added or altered, then records the red/green evidence.
- **implementation-review** records review findings in
  `reviews/implementation-review.md`, requires evidence for accepted criteria,
  and permits archival only when blockers are resolved or explicitly accepted
  by the human owner.
- **goal-implement** is the non-interactive counterpart to `implementation`.
  It may execute only an approved plan whose automated and manual steps are
  identified. Before starting, it records the allowed file scope, network and
  secret boundaries, verification commands, and a maximum of two repair
  attempts per quality gate. It commits only after the gate passes, returns a
  human checklist for manual work, and stops conservatively on structural
  plan/repository drift or an exhausted repair limit.

All skills preserve the existing safety, approval, and proportionate
verification rules in `AGENT_STANDARD.md`. They do not override an
already-applicable project skill or instruction.

## Profile and packaging behavior

Both profiles will install the lifecycle skill before the workflow stages.
`problem-framing` and `technical-research` occur after the existing
idea-validation/brainstorming product-shaping work and before
production-product-requirements and writing-plans. `plan-review` follows
writing-plans; implementation, TDD, implementation review, and optional
goal-implement follow it. `goal-implement` does not replace interactive
implementation and never grants permissions that the current environment or
the approved plan does not grant.

The authoring files in `skills/`, `profiles/`, and `AGENT_STANDARD.md` are
copied byte-for-byte to `src/agent_toolkit/data/`. The existing manifest and
lock behavior discovers the directories and includes their hashes without
code changes.

## Verification

Tests will prove both profiles select the lifecycle and all seven stages in
order, and that installation copies the lifecycle plus every stage to the
canonical and Claude runtime directories. Existing parity, drift, and
read-only `check` tests remain the compatibility safety net. The complete
pytest suite and a package build will run before committing.
