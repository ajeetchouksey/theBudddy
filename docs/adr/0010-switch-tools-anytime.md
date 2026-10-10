# ADR 0010: Students can switch tools any time; state only in Drive; nonce idempotency

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Students change AI tools, or use two at once. Progress must not be lost or doubled.

## Decision

All state lives in the Journey folder in Drive. Every tool runs the same release. Action links carry the student's token, not a tool ID, and a unique nonce; a repeated nonce returns the first result and writes nothing.

## Consequences

- Switching needs only adding the skill and connecting Google on the new tool.
- `handover.md` covers tools that cannot read Drive.
- The Log records the proposing tool (`src`) for each change.
