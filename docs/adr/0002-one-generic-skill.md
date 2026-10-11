# ADR 0002: One generic SKILL.md, no place or tool names

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

The companion must scale to new cities, universities and AI tools without forking the skill. Hard-coded names would make every new place or tool a code change.

## Decision

There is one `SKILL.md` source with no city, university or AI tool names. Place-specific knowledge comes from packs; tool-specific behaviour comes from adapters.

## Consequences

- A new city or university needs only pack files (NFR-POR.4).
- `scripts/lint_skill.py` blocks any PR that adds a deny-listed name to `SKILL.md` or intents (NFR-POR.2).
- Examples in the skill must use generic wording, which can make them slightly less concrete.
