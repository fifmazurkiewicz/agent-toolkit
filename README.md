# agent-toolkit v1.8

Small, versioned standards and vendored skills for Cursor, Codex and Claude Code. A project's `.agent/manifest.yaml` declares desired state; `.agent/lock.yaml` records the installed toolkit version and SHA-256 of each vendored skill file. Both profiles include [Archify](https://github.com/tt-a1i/archify) for validated interactive architecture diagrams.

## Start a project

```sh
python -m pip install -e /path/to/agent-toolkit
cd /path/to/my-project
agent-toolkit init --profile web
agent-toolkit install
agent-toolkit check
```

Use `--profile backend` for backend projects. Edit `.agent/manifest.yaml` to select clients or skills, then run `agent-toolkit install`. `agent-toolkit update` refreshes the vendored files and lock using the currently installed toolkit version. Commit the manifest, lock, `AGENTS.md`, generated MCP configuration, `CLAUDE.md` when generated, and skill directories. `check` exits 1 on drift and never writes files; invalid input exits 2.

Use `agent-toolkit --project /path/to/my-project <command>` when outside the project directory. For development, `python -m pip install -e '.[test]'` and `pytest` run the focused suite. The repository can be initialized with `git init` as is.

## Architecture diagrams

The toolkit includes an [editable Archify source](docs/architecture/agent-toolkit.architecture.json) and its [rendered HTML](docs/architecture/agent-toolkit.html). The diagram shows how the manifest, installer, runtime files and drift check fit together. Archify is vendored at v3.0.1 with its license in `src/agent_toolkit/data/skills/archify/`; rendering needs Node.js 18+ but ordinary `init/install/check/update` do not. Set `ARCHIFY_UPDATE_CHECK_DISABLED=1` when rendering offline or when you do not want Archify's optional update check.

When an agent initializes documentation for another project, ask it to use the installed `archify` skill to inspect that project's actual code and create `docs/architecture/overview.architecture.json` plus `docs/architecture/overview.html`. Commit both: the JSON is editable, while the HTML is a self-contained viewer. The Python installer only copies the skill; it cannot infer a project's architecture from its manifest.

## Project layout

```text
my-project/
  AGENTS.md                 # shared instructions; managed block only
  CLAUDE.md                 # generated @AGENTS.md import if Claude selected
  .mcp.json                 # generated Graft entry for Claude Code
  .agent/manifest.yaml      # desired state, edit this
  .agent/lock.yaml          # generated version and file hashes
  .agent/context/           # project-owned change context when lifecycle is used
  .agents/skills/           # canonical vendored runtime skills for Cursor and Codex
  .cursor/mcp.json          # generated Graft entry for Cursor
  .codex/config.toml        # managed Graft block for Codex
  .claude/skills/           # generated vendored copies for Claude Code
```

`install` changes the standard only between `<!-- agent-toolkit:standard v1 start -->` and `<!-- agent-toolkit:standard end -->`. It preserves text outside that block, including project rules. Claude's `CLAUDE.md` similarly gets a managed `@AGENTS.md` import while retaining local text. Skills are ordinary files, not symlinks. The package owns the selected skill directories; keep project-specific skills outside those names. When you deselect a previously locked skill or Claude, `install` removes its managed runtime copies.

## Shared rules, skills, and MCP

The toolkit is the source for general rules and reusable skills, not product decisions. It includes workflow, simplification, FastAPI, UI quality, accessibility, performance, SEO, diagram, and architecture skills. Profiles choose sensible defaults, while the manifest remains the desired state for an individual project.

For a meaningful change, use the happy path: `idea-validation → brainstorming → project-context-lifecycle → problem-framing → technical-research → decisions → production-product-requirements → writing-plans → plan-review → implementation/TDD → evidence → implementation-review → review-decisions → archive`. Start at the earliest stage whose output is missing: `idea-validation` tests the problem and evidence, `brainstorming` shapes the solution, and `production-product-requirements` creates the production-ready product contract. Small, already-decided maintenance work can begin later in the sequence.

`project-context-lifecycle` defines project-owned `.agent/context/changes/<change-id>/` records for the active change, including `frame.md`, `research.md`, `decisions.md`, `plan.md`, `progress.md`, `evidence.md`, a derived `plan-kanban.html`, and review reports. `progress.md` is the canonical execution state. Every non-informational review finding receives a canonical `reviews/review-decisions.md` entry and a derived `reviews/review-decisions-kanban.html` card. The supported decisions are Fix now, Fix differently, Skip, and Record as lesson; Skip needs documented human-owner acceptance and a re-evaluation trigger. For products with multiple milestones, `docs/roadmap.md` is the canonical roadmap and `docs/roadmap-kanban.html` its derived Kanban view. Canonical records change before a board; material replanning returns the plan to review. Finished change folders move to `.agent/context/archive/` after implementation review. Graft is the durable knowledge layer: query it before research, planning, implementation, and review; add only reusable, evidence-backed knowledge after archive. If Graft is unavailable, use focused `rg` and state the limitation. Do not create `lessons.md` as a competing knowledge store.

`goal-implement` is opt-in, non-interactive execution of an approved plan. The plan must identify automated versus manual steps, allowed file scope, network and secret boundaries, and verification gates. It commits only after green verification, returns manual work as a checklist, makes no more than two repair attempts for one failed gate, and stops on structural drift instead of expanding scope.

`implementation-review` is a self-contained AI code-review skill: it uses the current session and existing repository tools, with no additional account, CLI, service, or installation. A fresh reviewer agent inspects changes independently when subagents are available; otherwise the agent performs an explicit second pass and discloses that limitation. Findings cover bugs, regressions, security/privacy, failure paths, and missing tests, and flow through the existing review-decision workflow. Upgrade to v1.3.1, then run `agent-toolkit update` in existing projects to receive these instructions. This replaces the external CodeRabbit requirement introduced in v1.3.0.

The standard sets test depth from a risk map. Before writing tests for a meaningful change, the agent rates each main failure scenario high, medium, or low for impact and likelihood and records the map with the plan. High impact, or medium impact with high likelihood, requires behavioral tests of the failure, error, and edge cases at the level that exercises them; medium/medium or low impact with high likelihood requires a focused test of the main path and known failure; other scenarios may rely on stated existing coverage or a smoke check. Upgrade to v1.4.0, then run `agent-toolkit update` in existing projects to receive this rule.

`test-strategy` keeps a project-owned `docs/testing-strategy.md`: the confirmed risk map with its sources, the existing test profile, the QA phases and test types that address each risk, how agent work raises quality, and a cookbook for extending existing tests. Before use it checks that risks are realistic, sourced, described in user and business terms, and include an abuse scenario when the project has authentication, payments, or secrets; the human owner confirms the ratings. `writing-plans`, `tdd`, and `implementation-review` read the document instead of re-deriving risks. Upgrade to v1.5.0 and run `agent-toolkit update`; the toolkit installs the skill but does not write the strategy document.

Graft is the only mandatory shared MCP. `install` configures it for every selected client with `npx -y @nanonets/graft mcp`, without credentials or runtime installation. Existing JSON MCP servers are preserved. Codex receives only a marked managed block; an unmarked, conflicting Graft table is rejected rather than overwritten. Graft serves no tools until the project has an index, so the standard requires `graft check` at the start of work and `graft build` when the index is missing or stale; the structural build is local, needs no LLM or key, and keeps `graft/` git-ignored, while `--deep` requires approval because it calls a paid LLM. Each client also needs a one-time local approval of the project MCP server: folder trust in Codex, `agent mcp enable graft` in Cursor, and the project-server prompt in Claude Code. The standard requires a focused `rg` fallback when Graft cannot run. Upgrade to v1.6.0 and run `agent-toolkit update` to receive the build rule.

Since v1.7.0, `install` and `update` also build the local Graft index after writing managed files; pass `--no-graft-build` to skip it, and a missing Node runtime is reported without failing. Run `agent-toolkit setup` once per machine and project to approve the Graft MCP server for each selected client: it trusts the project in `~/.codex/config.toml`, runs `agent mcp enable graft` for Cursor, and adds `graft` to `enabledMcpjsonServers` in the git-excluded `.claude/settings.local.json`. `check` still never writes. The standard also carries the shared defaults that projects previously copied by hand: the default web stack, secret and personal-data handling, UI baseline, diagram review in the handoff, and leaving deployment configuration alone unless the task requires it. Remove any hand-copied copy of these defaults from a project and keep only its documented exceptions.

`behavioral-tests` (v1.8.0) is the starting point for writing tests, including tests for existing code that `tdd` does not cover. It establishes expected behavior from the test stack and requirements before reading the implementation, lists the behaviors first, and stops to ask when the sources do not settle the correct behavior. Tests assert observable outcomes, compute expected values independently, add risk-driven edge cases, and each catch a different regression; the summary table names the regression and code change each test detects and marks uncertain rows for the user. `tdd`, `test-strategy`, and `implementation-review` reference it. Upgrade to v1.8.0, add `behavioral-tests` to existing manifests, and run `agent-toolkit update`.

## Discovery contract

As checked on 2026-10-03, [Codex loads repo `.agents/skills/`](https://learn.chatgpt.com/docs/build-skills), [Cursor loads `.agents/skills/` and root `AGENTS.md`](https://prod.cursor.com/docs/skills), and [Claude Code loads `.claude/skills/`](https://code.claude.com/docs/en/skills) with [imports in `CLAUDE.md`](https://code.claude.com/docs/en/memory). The same source skill is copied to each required runtime location. `name` and `description` in `SKILL.md` drive selection; there is no custom routing engine. Client behavior can change, so the fixtures in `evals/web-routing/` are for live compatibility checks on your installed clients.

## Upgrade policy

Install a newer `agent-toolkit` package, run `agent-toolkit update`, inspect the diff, then run `agent-toolkit check`. `update` overwrites selected managed skill directories. The lock detects edits, missing files, added files, and mismatch with the installed package. Unrelated skill names remain user-owned.
