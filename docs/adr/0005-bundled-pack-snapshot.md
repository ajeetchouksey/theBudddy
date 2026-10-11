# ADR 0005: Bundled pack snapshot in every skill build

- **Status:** Accepted
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Not every tool or plan can fetch a URL or read Drive. The floor experience must still answer from sourced facts.

## Decision

Every per-tool skill build includes a generated, version-stamped Markdown snapshot of the packs in `skill/reference/packs/`. Live packs via URL or Drive are an extra.

## Consequences

- The floor works without `fetch_url` or `drive_read`.
- Snapshot size is limited by each tool's reference-file limits (spike test 14).
- Students on tools without fetch see facts only as fresh as their last skill import; time-sensitive answers state the snapshot date when it is over 90 days old (FR-10.3).
