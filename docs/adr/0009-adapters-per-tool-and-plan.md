# ADR 0009: Adapters per tool × plan with inheritance; plan detected by use

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Features vary by tool and plan and change over time. Asking students which plan they have adds setup friction.

## Decision

Each tool has an adapter YAML with `free`, `paid` and `education` profiles; paid and education inherit from free and list only differences. The skill resolves each capability per tool and plan, tries `unknown` once and records the result in `profile.md` (`ai_plans`).

## Consequences

- Setup stays at 3 actions; no plan question.
- A flag is `yes` only with recorded spike evidence; CI requires a fallback for every capability and `last_verified` within 90 days.
- Adapters must be re-verified each release (NFR-MAI.1).
