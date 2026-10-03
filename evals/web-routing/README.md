# Web routing evals

These are prompt fixtures for manual runs in Cursor, Codex, and Claude Code after `agent-toolkit install` with the web profile. Ask each prompt without naming a skill, record the skills selected, and compare with `cases.yaml`. This tests actual model routing; the CLI deliberately has no router engine.

For a regression pass, run each case in a fresh chat with the same project and model settings. A pass selects every `expected` skill and none of the `excluded` skills. Inspect the response as well: selection alone does not prove the skill was followed.
