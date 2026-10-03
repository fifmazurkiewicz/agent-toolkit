---
name: best-practices
description: Use when reviewing or improving application code for security, compatibility, maintainability, or reliability.
---

# Best practices

Inspect the relevant code path and its callers before proposing changes. Prioritize concrete risks over generic checklists. Use platform and standard-library features where they fit.

At trust boundaries, validate input, enforce authorization, and avoid exposing secrets or sensitive data. Preserve the project's supported compatibility range. Prefer one coherent fix at the source of a problem over repeated guards at callers. Add focused checks for behavior that could regress and report evidence and remaining uncertainty.
