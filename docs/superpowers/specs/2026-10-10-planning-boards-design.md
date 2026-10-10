# Planning Boards Design

## Purpose

Make a product roadmap and the active change plan visible as maintained Kanban
boards, without creating a second source of truth. The boards help a human
owner see what is next, active, blocked, or complete; they do not authorize
work outside an approved plan.

## Scope

The toolkit adds a first-party `planning-boards` skill and selects it in the
web and backend profiles. It defines two board levels:

| Level | Canonical records | Generated visual |
| --- | --- | --- |
| Product | `docs/roadmap.md` | `docs/roadmap-kanban.html` |
| Active change | `plan.md`, `progress.md` | `.agent/context/changes/<change-id>/plan-kanban.html` |

`roadmap.md`, `plan.md`, and `progress.md` remain authoritative. The board is
a rendered, synchronized view and must never be the only place a status,
decision, dependency, or blocker is recorded.

## Board model

Both boards use the same status vocabulary: **Planned**, **Ready**, **In
progress**, **Blocked**, and **Done**. A roadmap card represents a milestone;
a change board card represents an independently verifiable plan task.

Each card includes a concise outcome, status, dependencies or blockers when
present, and a reference to its canonical record. Boards must include only
current work and completed work useful for context; archived change boards
remain in the archived change record.

## Workflow

1. During product framing or roadmap work, create or update `docs/roadmap.md`
   and its board when the project has more than one milestone.
2. During planning, derive the active change board from the approved plan and
   initialize all tasks as Planned or Ready.
3. During implementation, change the canonical execution record first, then
   synchronize the affected board after a task starts, completes, blocks, or
   is materially replanned.
4. A material scope, architecture, or acceptance-criterion mismatch stops
   implementation. The owner updates the plan and, where relevant, roadmap;
   plan review occurs again before execution resumes.
5. Implementation review verifies board-to-record consistency before archive.

## Rendering and quality

Boards are self-contained HTML diagrams with inline SVG, produced using the
existing `diagram-design` Kanban guidance. They favor a compact readable view
over a project-management application: no editing controls, live sync, or
new runtime dependency. The board must label its generation date and name the
canonical source files.

The standard style-guide gate applies when a project has not selected a
diagram profile or explicitly kept the default style. Board generation must
not overwrite unrelated documentation.

## Safety and acceptance criteria

- A new product with multiple milestones has a Markdown roadmap and a matching
  roadmap board.
- A meaningful active change has a matching change board alongside its plan.
- Status changes update `progress.md` before the visual board.
- A board never silently adds scope or marks manual work complete.
- A material mismatch requires plan/roadmap revision and plan review; it is
  not treated as ordinary progress.
- Both authoring and packaged copies of all changed first-party skills and
  profile files remain byte-for-byte synchronized.
