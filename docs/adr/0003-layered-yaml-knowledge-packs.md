# ADR 0003: Knowledge as layered YAML packs with schema and CI

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Germany-specific facts (fees, deadlines, offices) change often and differ by state, city and university. Students act on them, so every fact must be traceable and reviewable.

## Decision

Facts live as YAML pack entries in `knowledge/`, layered national → state → city → university, validated by JSON Schema and CI rules. Each entry carries `source_url`, `last_verified`, `reviewer` and `expires`. The most specific layer wins.

## Consequences

- Facts change only through pull requests with CODEOWNER review per layer.
- CI enforces sources, official-domain allowlist, freshness and expiry.
- Contributors need basic YAML skills; the `pack-author` skill lowers the bar.
