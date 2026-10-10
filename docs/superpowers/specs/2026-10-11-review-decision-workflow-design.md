# Review Decision Workflow Design

## Purpose

Make every implementation-review finding traceable to an explicit, durable
decision. Reviewers retain their assessment role; they do not silently apply
fixes or decide that risk is acceptable on behalf of a human owner.

## Scope and success criteria

For each non-informational finding, a change record will contain a canonical
decision with an ID, severity, impact, owner, decision, rationale, status,
evidence link, and follow-up. The four supported decisions are:

- **Fix now** — return a concrete correction to implementation and keep the
  change in review until evidence is present.
- **Fix differently** — amend the plan/progress record, repeat plan review
  when the different solution is material, then implement and verify it.
- **Skip** — an explicit human-owner risk acceptance, with rationale and a
  re-evaluation trigger; it cannot be selected by the reviewing agent alone.
- **Record as lesson** — capture a reusable, evidence-backed insight in Graft
  after archive; it does not replace any corrective action required by risk.

The canonical record is `reviews/review-decisions.md`. It is paired with a
derived, self-contained `reviews/review-decisions-kanban.html` that shows one
card per finding in columns for the four decisions. The board is a view only:
all changes begin in the Markdown record, then the board is regenerated.

## Lifecycle integration

`implementation-review` creates `reviews/implementation-review.md` and calls
the new `review-decisions` workflow whenever it has findings. `review-decisions`
creates or updates the canonical decision record and the derived board. A
review may approve only when every finding has a valid terminal decision and
all Fix-now/Fix-differently work has verification evidence. Skip remains a
human-authorized exception, not a clean technical pass.

`progress.md` remains execution state, `decisions.md` remains design choices,
and `evidence.md` remains observed verification. The decision record links to
those files instead of duplicating them. On archive, only a Record-as-lesson
entry with reusable, evidence-backed knowledge is added to Graft; no parallel
`lessons.md` is created.

## Record contract

Each finding uses a stable heading such as `## REV-001` and includes the
following fields: finding reference, severity, impact, decision, owner,
rationale, status, canonical follow-up, evidence, and for Skip a human
acceptance plus re-evaluation trigger. Information-only notes may remain in
the review report and do not require a decision card.

## Rendering and compatibility

The board is static HTML with inline SVG, generated through `diagram-design`.
It displays source file, generation date, status, owner, severity and impact
on each card. It must be kept small and legible; split by review round if the
number of findings exceeds the diagram's Kanban budget. No external service,
live dashboard, dependency, or product runtime code is introduced.

## Rollout

Add `review-decisions` to both default profiles immediately after
`implementation-review`. Update the authoring files and exact packaged copies,
standard, README, lifecycle and planning-board contracts, and routing tests.
`agent-toolkit update` installs the managed skill into every selected client
without altering application source code. Existing reviews are not backfilled;
the workflow applies when a finding is created or revised.
