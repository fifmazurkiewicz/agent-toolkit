# Python Service Architecture Design

## Goal

Provide an opt-in `python-service-architecture` skill for Python projects that
need durable boundaries without imposing a framework or refactoring existing
code solely to match a template.

## Scope

The change affects the `agent-toolkit` source and the Python repositories in
`/Users/Filip/dev`: Aide, Langy, POZZ, Reelcut, TeacherHelper, goat, Trady,
LinkSift, and Linksifty. DocReader and template-project are out of scope.

## Design

### Toolkit capability

Add a first-party, opt-in skill named `python-service-architecture`. Its
compact instruction establishes these defaults for new or materially rewritten
Python service code:

1. Prefer `src/<package_name>/` for installable packages.
2. Keep delivery adapters (`api/`, CLI, workers) separate from application
   orchestration; keep business rules independent of FastAPI, ORM, HTTP
   clients, and environment configuration.
3. Wire concrete infrastructure (database, provider clients, storage) only in
   the composition root such as `main.py`.
4. Keep unit tests independent of delivery and external infrastructure; put
   boundary or end-to-end checks under integration tests.
5. Add a directory or abstraction only when the project has a real second
   concern or implementation. Do not create empty Clean Architecture layers.

The skill does not choose FastAPI, an ORM, dependency-injection library,
repository pattern, or a universal package name. It complements the existing
FastAPI skill; it does not modify it.

The skill is not added to the `backend` profile because that profile is also
used by non-Python projects. Projects opt in through their manifests where
they use the toolkit.

### Repository adaptation

Each target receives a concise project-local rule rather than a directory
migration. The rule identifies the applicable package root and any exception:

| Repository | Applicable root | Constraint |
| --- | --- | --- |
| Aide | `backend/app/` | New backend behavior follows the boundary rule; mobile app is unchanged. |
| Langy | `backend/app/` | Existing FastAPI delivery code remains the outer layer. |
| POZZ | `backend/app/` | The legacy Streamlit prototype remains outside the new production boundary. |
| Reelcut | `backend/src/reelcut/` | Pipeline is the domain/application core; the legacy FastAPI layer stays an outer adapter. |
| TeacherHelper | `backend/teacher_helper/` | Existing FastAPI service becomes the outer delivery layer. |
| goat | `backend/app/` | Do not migrate unrelated frontend or Supabase migration code. |
| Trady | `sidecar/`, `mcp_server/`, and future risk gate | Never impose service layers on Freqtrade strategy files. |
| LinkSift | `src/linksift/` | Keep the existing `src` layout and pending target layout as the source of truth. |
| Linksifty | project package | Apply only when the package root is introduced or expanded. |

Toolkit-managed repositories also add the selected skill to
`.agent/manifest.yaml` and regenerate managed skill copies and locks through
the toolkit. LinkSift has no toolkit manifest, so it receives only its local
rule.

### Trady instruction ownership

Move the safety-critical risk rules from `CLAUDE.md` into `AGENTS.md`.
`CLAUDE.md` becomes a thin Claude-specific wrapper that imports the canonical
`AGENTS.md`. The risk limits, `dry_run`, credentials, deterministic sizing,
and required risk tests stay unchanged.

## Non-goals

- No source-code relocation or broad refactor.
- No new dependency, ORM, DI container, repository base class, or generic
  service layer.
- No automatic inclusion in all backend projects.
- No changes to unrelated dirty worktree files.

## Verification

1. Confirm the toolkit source and packaged skill copies match.
2. Run the toolkit's drift/check and relevant tests without staging unrelated
   files.
3. Confirm each opted-in manifest and generated lock is consistent.
4. Review each repository diff and commit only the designated files on `main`.
