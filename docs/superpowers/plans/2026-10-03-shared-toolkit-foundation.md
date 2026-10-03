# Shared Toolkit Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add shared rules, vendored general skills, and required Graft setup to agent-toolkit.

**Architecture:** Package data remains the source used by the installer. Client adapters expose only each client's Graft location and renderer; core merges JSON MCP files, writes a marked Codex TOML block, and compares expected configuration during `check`.

**Tech Stack:** Python 3.11+, PyYAML, standard-library JSON and pathlib.

**Spec:** `docs/superpowers/specs/2026-10-03-shared-toolkit-foundation.md`

## Global Constraints

- Graft is the only managed MCP and is required for selected clients.
- No credentials, secrets, project runtime choices, or client hooks are copied.
- `check` remains read-only.
- Skills are copied, never symlinked.

## Review Focus

- Existing JSON MCP servers survive installation unchanged.
- A malformed JSON MCP file is rejected before changes are made.
- An unmarked existing Codex Graft table is not duplicated.
- Deselecting a client does not erase user-owned MCP configuration.
- A changed Graft command is detected without modifying the project.

### Task 1: Package the common foundation

**Files:**
- Modify: `AGENT_STANDARD.md`, `README.md`, `THIRD_PARTY_NOTICES.md`, `profiles/*.yaml`, `pyproject.toml`
- Create: additional `skills/*/SKILL.md` and matching package data

- [ ] Add concise common rules and document the Graft contract.
- [ ] Vendor the general shared skill library and expose appropriate profile defaults.
- [ ] Synchronize authoring files with package data and package all skill files.

### Task 2: Generate and validate Graft configuration

**Files:**
- Create: `src/agent_toolkit/adapters/graft.py`
- Modify: `src/agent_toolkit/core.py`, client adapters

- [ ] Add failing tests for generated Cursor, Claude, and Codex Graft configuration.
- [ ] Add the smallest safe JSON merge and marked TOML block implementation.
- [ ] Extend the lock metadata and read-only drift checks.

### Task 3: Verify and publish

**Files:**
- Modify: `tests/test_core.py`, documentation and version metadata

- [ ] Run the focused tests and CLI smoke checks.
- [ ] Commit the updated repository and publish the commit to `main`.
