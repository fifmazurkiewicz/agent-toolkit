---
name: writing-plans
description: Use when an agreed design needs a multi-step implementation plan with dependencies, file changes, and verification.
---

# Writing plans

Turn the agreed design into ordered, testable steps. Name the files and interfaces each step changes, plus dependencies between steps. Each step should leave a working, reviewable increment.

For each behavior, specify a concrete check that would fail if the behavior regressed. Include migration, rollback, or compatibility checks only where the design actually needs them. Keep the plan proportional to the work, avoid speculative scaffolding, and update it when implementation reveals a real dependency or risk.
