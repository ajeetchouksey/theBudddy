# ADR 0008: Free plans are the floor on Gemini, Claude and Copilot

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Most students do not pay for an AI plan.

## Decision

All core flows (chat with skill, bundled packs, text cards, action links) must work on the free plans of Gemini, Claude and Copilot. Paid features are extras with fallbacks.

## Consequences

- The skill never asks a student to upgrade.
- Every release is tested on free plans first.
- Richer visuals (charts, Canvas, Sheets canvas) reach only some students.
