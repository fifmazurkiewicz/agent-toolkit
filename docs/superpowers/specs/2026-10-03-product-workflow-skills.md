# Product Workflow Skills Design

## Intent

Give projects initialized with agent-toolkit a clear, reusable path from a
product idea to implementation without adding a new runtime, dependency, or
custom routing system. The workflow must work for web and backend profiles in
Cursor, Codex, and Claude Code.

## Workflow and boundaries

```text
idea-validation -> brainstorming -> production-product-requirements
-> writing-plans -> implementation/review
```

- `idea-validation` answers whether the problem is worth pursuing now. It
  records the target user, pain, alternatives, evidence, assumptions, risks,
  and the cheapest next validation. It does not choose an architecture or
  issue a unilateral go/no-go verdict.
- `brainstorming` assumes the idea is either validated or explicitly accepted
  as an assumption. It shapes the solution through business flow, user flow,
  solution alternatives, architecture/integrations, constraints,
  scope/non-scope, and delivery risks. It must not repeat market evidence or
  validation experiments.
- `production-product-requirements` turns approved shaping decisions into one
  production-ready PRD: problem/context, goals/non-goals, users/flows,
  functional requirements, edge/error states, constraints, acceptance
  criteria, risks, and open questions. It does not prescribe files, classes,
  migrations, or a step-by-step implementation plan.
- `writing-plans` remains the handoff from approved PRD to the technical,
  file-level implementation plan.

Each product skill provides a concise “what next?” happy path so an agent can
route a user who asks how to continue. The route is conditional: start at the
earliest stage whose output is missing; do not force validation for a narrowly
scoped, already-decided maintenance request.

## Project context rule

For a significant feature or change to behavior, API, deployment, or
architecture, the shared standard requires agents to understand the relevant
project context before deciding or implementing. That context is limited to:

- stack and runtime/toolchain;
- relevant architecture and integration boundaries;
- deployment model and operational constraints;
- domain and business boundaries; and
- established local patterns.

Agents use existing documentation and Graft for focused orientation/impact
analysis. If Graft is unavailable, they use targeted `rg` queries. This rule
does not require reconstructing undocumented history or broad source reading.

## Distribution

The toolkit keeps authoring copies in `skills/` and packaged copies in
`src/agent_toolkit/data/skills/`; both must be byte-identical. Add the two new
skills to the default `web` and `backend` profile lists between `brainstorming`
and `writing-plans`. No installer or manifest schema change is necessary:
profiles already select arbitrary available skill directories, and existing
drift checks hash every file.

## Documentation and verification

Update the README’s shared-skills description and document the workflow.
Extend Python tests to prove a fresh project initialized with either profile
selects the two new skills in the intended order and installs them for every
supported client. Existing packaged-content parity coverage remains the guard
against diverging source trees.

## Non-goals

- No copy of the 10x CLI, remote content delivery, or new profile types.
- No automatic product decision engine or forced go/no-go decision.
- No modification of the installer’s generic skill-copying mechanism.
- No file-by-file implementation guidance in the PRD skill.
