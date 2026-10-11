# ADR 0001: No personal data on project servers

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Students share sensitive details (address, finances, letters from offices). A small open-source team has no budget or appetite for GDPR processor duties, hosting, breach handling or data requests.

## Decision

The project stores and processes no personal data. All student state lives in the student's own Google account (Drive, Sheets, Gmail, Calendar, Tasks). Project infrastructure only serves public, non-personal content: packs, skill packages, `latest.json`.

## Consequences

- Each student is the controller of their own data; their AI provider is their processor (to confirm with a legal reviewer before public launch).
- No backend in MVP 1. Any phase 2 server (MCP) serves public packs only.
- No telemetry: feedback comes from people and CI, not usage data.
- Features that would need server-side state are out of scope or must be redesigned around the student's Drive.
