# ADR 0006: Writes through action links, not native edits, by default

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

AI tools differ in whether and how they can edit Sheets, and model-driven edits are hard to audit or undo.

## Decision

Every write is a one-tap HTTPS action link to the student's own Apps Script web app, carrying version, token, nonce and source tool. The student taps; the script validates, writes, logs and offers Undo. Native edits are used only where an adapter says `sheets_edit: yes`.

## Consequences

- Writes behave the same on every tool and plan.
- Every change is logged with before/after and can be reverted.
- One extra tap per change for the student.
