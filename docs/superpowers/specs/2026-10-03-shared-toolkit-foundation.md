# Shared toolkit foundation

## Goal

Make `agent-toolkit` the versioned source for general agent practices, reusable skills, and the required Graft MCP configuration. Product architecture, commands, provider setup, user preferences, and product safety rules remain in each consuming repository.

## Scope

- Extend the managed `AGENT_STANDARD.md` with the common rules repeated across the local projects: instruction discovery, selective skill use, durable documentation, Graft-first exploration with a safe `rg` fallback, smallest coherent change, secret and personal-data protection, deliberate external actions, UI quality, and proportionate verification.
- Vendor the general skills already available in the local shared skill library. Profiles remain selective: the web profile enables web and UI skills; the backend profile enables workflow, architecture, FastAPI, safety, and simplicity skills.
- Generate Graft configuration for every selected client: `.cursor/mcp.json`, root `.mcp.json`, and a managed block in `.codex/config.toml`.
- Keep Graft mandatory in the toolkit, but allow an environment without `npx` or Graft to fall back to focused `rg` exploration; `install` must never install software or add credentials.
- Extend `check` to detect missing or altered selected-client Graft configuration without writing files.

## Non-goals

- No project migration in this change.
- No project-specific commands, hosting, runtime stack, policy, design dials, hooks, secrets, or MCPs.
- No custom MCP router, runtime installer, or portability metadata.

## Data flow

`agent-toolkit init` writes the selected profile to `.agent/manifest.yaml`. `install` copies selected skills, inserts the managed standard, generates the selected clients' Graft files, and writes a lock that records the mandatory MCP. `check` recomputes each expected artifact and reports drift read-only.

## Compatibility and safety

JSON MCP files preserve unrelated server definitions. Codex configuration is limited to an explicit managed marker block, avoiding a TOML dependency and preserving unrelated settings. A pre-existing unmarked Codex `graft` table is reported as a conflict rather than overwritten. Graft uses `npx -y @nanonets/graft mcp`; no secrets are included.
