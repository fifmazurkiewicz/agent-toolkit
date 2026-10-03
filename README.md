# agent-toolkit v1.1

Small, versioned standards and vendored skills for Cursor, Codex and Claude Code. A project's `.agent/manifest.yaml` declares desired state; `.agent/lock.yaml` records the installed toolkit version and SHA-256 of each vendored skill file. Both profiles include [Archify](https://github.com/tt-a1i/archify) for validated interactive architecture diagrams.

## Start a project

```sh
python -m pip install -e /path/to/agent-toolkit
cd /path/to/my-project
agent-toolkit init --profile web
agent-toolkit install
agent-toolkit check
```

Use `--profile backend` for backend projects. Edit `.agent/manifest.yaml` to select clients or skills, then run `agent-toolkit install`. `agent-toolkit update` refreshes the vendored files and lock using the currently installed toolkit version. Commit the manifest, lock, `AGENTS.md`, `CLAUDE.md` when generated, and skill directories. `check` exits 1 on drift and never writes files; invalid input exits 2.

Use `agent-toolkit --project /path/to/my-project <command>` when outside the project directory. For development, `python -m pip install -e '.[test]'` and `pytest` run the focused suite. The repository can be initialized with `git init` as is.

## Architecture diagrams

The toolkit includes an [editable Archify source](docs/architecture/agent-toolkit.architecture.json) and its [rendered HTML](docs/architecture/agent-toolkit.html). The diagram shows how the manifest, installer, runtime files and drift check fit together. Archify is vendored at v3.0.1 with its license in `src/agent_toolkit/data/skills/archify/`; rendering needs Node.js 18+ but ordinary `init/install/check/update` do not. Set `ARCHIFY_UPDATE_CHECK_DISABLED=1` when rendering offline or when you do not want Archify's optional update check.

When an agent initializes documentation for another project, ask it to use the installed `archify` skill to inspect that project's actual code and create `docs/architecture/overview.architecture.json` plus `docs/architecture/overview.html`. Commit both: the JSON is editable, while the HTML is a self-contained viewer. The Python installer only copies the skill; it cannot infer a project's architecture from its manifest.

## Project layout

```text
my-project/
  AGENTS.md                 # shared instructions; managed block only
  CLAUDE.md                 # generated @AGENTS.md import if Claude selected
  .agent/manifest.yaml      # desired state, edit this
  .agent/lock.yaml          # generated version and file hashes
  .agents/skills/           # canonical vendored runtime skills for Cursor and Codex
  .claude/skills/           # generated vendored copies for Claude Code
```

`install` changes the standard only between `<!-- agent-toolkit:standard v1 start -->` and `<!-- agent-toolkit:standard end -->`. It preserves text outside that block, including project rules. Claude's `CLAUDE.md` similarly gets a managed `@AGENTS.md` import while retaining local text. Skills are ordinary files, not symlinks. The package owns the selected skill directories; keep project-specific skills outside those names. When you deselect a previously locked skill or Claude, `install` removes its managed runtime copies.

## Discovery contract

As checked on 2026-10-03, [Codex loads repo `.agents/skills/`](https://learn.chatgpt.com/docs/build-skills), [Cursor loads `.agents/skills/` and root `AGENTS.md`](https://prod.cursor.com/docs/skills), and [Claude Code loads `.claude/skills/`](https://code.claude.com/docs/en/skills) with [imports in `CLAUDE.md`](https://code.claude.com/docs/en/memory). The same source skill is copied to each required runtime location. `name` and `description` in `SKILL.md` drive selection; there is no custom routing engine. Client behavior can change, so the fixtures in `evals/web-routing/` are for live compatibility checks on your installed clients.

## Upgrade policy

Install a newer `agent-toolkit` package, run `agent-toolkit update`, inspect the diff, then run `agent-toolkit check`. `update` overwrites selected managed skill directories. The lock detects edits, missing files, added files, and mismatch with the installed package. Unrelated skill names remain user-owned.
