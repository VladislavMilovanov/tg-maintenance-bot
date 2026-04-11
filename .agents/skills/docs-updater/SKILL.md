---
name: docs-updater
description: Detect code changes that affect API or onboarding docs, then update docs/tech/api-contracts.md and related onboarding sections to keep repository documentation in sync.
---

# Docs Updater

Use this subagent when code changes alter documented backend behavior, API contracts, integration flows, setup steps, operational checks, or onboarding guidance.

## Triggers

- backend endpoint, schema, request/response DTO, auth flow, or error contract changed
- `backend/docs/openapi.yaml` changed or runtime OpenAPI behavior changed
- new env vars, startup steps, dependencies, ports, or quality gates affect onboarding
- docs drift is visible between implementation and:
  - `docs/tech/api-contracts.md`
  - `docs/onboarding.md`
  - related architecture or integration docs linked from onboarding

## Primary Responsibilities

1. Inspect the code diff and identify whether the documentation impact is real.
2. Update `docs/tech/api-contracts.md` as the repository-level entry point for API contract changes.
3. Update `docs/onboarding.md` when developer setup, smoke checks, entrypoints, or source-of-truth links changed.
4. Update closely related docs only when required for consistency, keeping edits minimal and factual.

## Source Of Truth

- Implementation and tests in `backend/`
- OpenAPI spec in `backend/docs/openapi.yaml`
- Detailed backend API notes in `backend/docs/api-contracts.md`
- Repo-level API overview in `docs/tech/api-contracts.md`
- Developer onboarding in `docs/onboarding.md`

## Working Rules

- Do not invent behavior that is not implemented in code or spec.
- Prefer small synchronization edits over broad rewrites.
- Preserve existing document structure unless it is actively misleading.
- When backend API details changed, verify links between repo docs and backend docs still point to the right source of truth.
- When onboarding is touched, keep setup commands, URLs, env vars, and smoke checks concrete.
- If code changed but no documentation update is needed, say that explicitly and explain why.

## Expected Output

- Updated markdown files with only the necessary sync changes
- A concise summary of:
  - what code change triggered the docs update
  - which docs were updated
  - whether onboarding was affected
