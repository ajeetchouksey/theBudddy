# ADR 0011: Reads via native Google connectors in each tool

- **Status:** Accepted, verify in spike
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

All three tools already offer Google connectors. Building our own integration would need broad scopes and a server.

## Decision

Reads of Drive, Gmail (by sender list) and Calendar use each tool's native Google connector. We build no Gmail, Calendar or Drive integration.

## Consequences

- No extra scopes for our script; no server.
- Read quality depends on each vendor's connector (spike tests 8, 9, 21).
- Fallbacks: `status` and `handover` links, or the student pastes content.
