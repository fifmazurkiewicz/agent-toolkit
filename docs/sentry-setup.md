# Sentry setup and acceptance gates

Application projects use the official Sentry SDK for their runtime. This is an
application integration, not a requirement to run another backend, install an
MCP server on the host, or grant a coding agent hosting-account access.

## Account and projects

Create one Sentry organization. Choose its data-storage region deliberately;
for these applications use EU unless the owner chooses otherwise. An existing
SaaS organization's storage location cannot simply be changed in place.
Start with the Developer plan and measure actual event use. Creating more
projects does not reserve separate free allowances; consult the current
[pricing](https://sentry.io/pricing/) before enabling paid usage.

Create a separate Sentry project for each independently released client or
backend. Do not share one DSN across unrelated applications. Development,
staging and production use the environment field; they do not require duplicate
Sentry projects. Local/test ingestion stays off unless deliberately testing it.

| Application | Project names | Runtime |
| --- | --- | --- |
| Langy | `langy-web`, `langy-api` | Next.js, Python/FastAPI |
| POZZ | `pozz-web`, `pozz-api` | Next.js, Python/FastAPI |
| TeacherHelper | `teacherhelper-web`, `teacherhelper-api` | React, Python/FastAPI |
| goat | `goat-web`, `goat-api` | React, Python/FastAPI |
| Linksifty | `linksifty-web`, `linksifty-api` | React, Python/FastAPI |
| Aide | `aide-mobile`, `aide-web`, `aide-api` | React Native/Expo, web client, Python/FastAPI |
| Reelcut | `reelcut-web`, `reelcut-backend` | Next.js, Python API/CLI |
| Trady | `trady-sidecar`, `trady-mcp` | Python processes |
| ModelFabric | `modelfabric-python` | Python batch/CLI |

These are the agreed application naming conventions, not evidence that remote
projects already exist. Native macOS DocReader requires an owner decision
before changing its current no-telemetry contract. Tooling-only repositories,
an empty template and a superseded prototype do not justify silently adding
network telemetry; record their applicability rather than sending events from
all repositories to a shared endpoint.

## Three separate credentials or connections

1. A **DSN** selects the ingestion project. Find it under the project's client
   keys/DSN settings. It is an ingestion identifier and may be public in a web
   bundle; it does not authorize reading events or managing the account.
2. A **CI upload token** authorizes release/debug-artifact uploads. Use the
   current organization-token flow and the `org:ci` scope where supported.
   Store it as `SENTRY_AUTH_TOKEN` in CI secrets, with the appropriate
   `SENTRY_ORG` and `SENTRY_PROJECT` identifiers. Never publish this token in a
   client bundle or commit it. Request broader rights only for a concrete API
   operation that requires them.
3. **Sentry MCP** uses a separate OAuth login to read and investigate existing
   Sentry data. It does not enable SDK collection. The hosted endpoint is
   `https://mcp.sentry.dev/mcp`; its URL can default to one organization or
   project. URL context does not replace account permissions.

No token belongs in a chat message. Configure secrets locally or through the
provider's secret settings; share only organization/project slugs and readiness
status with an agent. Prefer project client-key settings over copying credentials
from existing environment files.

## Application configuration contract

Use the conventions appropriate to the application; list its actual variable
names in `.env.example` and setup documentation:

| Runtime | DSN variable | Other configuration |
| --- | --- | --- |
| Python | `SENTRY_DSN` | Explicit enabled flag, environment, release |
| Next.js browser | `NEXT_PUBLIC_SENTRY_DSN` | Public enabled flag and release/environment values |
| Next.js server | `SENTRY_DSN` | Server enabled flag, environment, release |
| Vite/React | `VITE_SENTRY_DSN` | Build-time public enabled flag and release/environment values |
| Expo | `EXPO_PUBLIC_SENTRY_DSN` | Build-time public enabled flag and release/environment values |

These names are a contract for implementing integrations, not a claim that the
SDK has already been installed in every consumer. Missing or invalid monitoring
configuration must not prevent local application use. Production activation
requires the correct DSN and green privacy/integration checks; absent setup is
a visible readiness gap, not a completed deployment. Public build-time settings
require a new client build after changing them.

Initialize once at real process/client entrypoints. Keep SDK dependencies and
initialization outside domain rules. Explicitly report caught terminal job
failures that would otherwise become only a failed status. Avoid duplicate
reports for intermediate retries and expected product outcomes. SDK failure
must not turn a successful user operation into an application error.

## Privacy and verification

Approve technical fields such as release, environment, component, operation
code, exception type and sanitized code stack locations. Do not send user
content, conversations, transcripts, prompts, model outputs, recordings,
documents, source URLs, secrets, authentication/session data, local variables,
raw provider responses or absolute user-file paths. Remove sensitive data from
exception messages, breadcrumbs and nested contexts as well as obvious bodies.
Use restrictive SDK settings and an outbound-event allowlist, not only a PII
toggle. Keep replay, profiling, tracing, attachments and full log forwarding off
unless separately authorized and verified.

For every runtime, before live ingestion:

- Use a fake transport and synthetic sensitive sentinels; inspect the actual
  outgoing event/envelope and prove no sentinel survives any captured field.
- Prove no DSN/disabled configuration sends nothing and leaves application work
  usable. A malformed config or transport error must not break the application.
- Verify an unexpected exception is reported to the intended component and a
  terminal caught failure is reported once, while normal cancellation, a known
  budget limit or an expected approval gate is not an error flood.
- Keep existing access rules, budgets, scoring, approvals and retry behavior
  unchanged. Monitoring is not authorization or a safety control.
- Verify supported native crash paths separately. A JavaScript callback alone
  is not evidence that native crash reports, attachments or cached events have
  been sanitized.
- Upload source maps/debug artifacts privately from CI when needed, match them
  to the release, and verify a synthetic event has a readable code stack.
- Only after configuration and privacy gates are green, send one explicitly
  authorized synthetic staging event and confirm project, environment and
  release. Record unavailable manual/device checks honestly.

Keep health checks and existing heartbeats: no captured exceptions does not
prove that a stopped process or an unreachable service is healthy.

## References

- [Data storage location](https://docs.sentry.io/organization/data-storage-location/)
- [Authentication](https://docs.sentry.io/api/auth/)
- [Permissions and CI scope](https://docs.sentry.io/api/permissions/)
- [Python SDK](https://github.com/getsentry/sentry-python)
- [JavaScript SDKs](https://github.com/getsentry/sentry-javascript)
- [React Native SDK](https://github.com/getsentry/sentry-react-native)
- [Hosted MCP](https://mcp.sentry.dev/)
