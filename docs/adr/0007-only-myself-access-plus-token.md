# ADR 0007: Action-link web app deployed with Only-myself access + token

- **Status:** Proposed
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Action links appear in chat history and may be fetched by link-preview bots or shared by mistake.

## Decision

The web app is deployed with access *Only myself*, so a link works only in a browser signed in to the student's Google account. Each request also carries a per-student token from `index.md`, rotatable from the sheet menu.

## Consequences

- Prefetch bots cannot write; crafted links from third parties fail the token check.
- AI tools cannot call `status` server-side; reads must use the Drive connector or the student pastes the result. Open question for G1.
- Token rotation invalidates old links with a clear message.
