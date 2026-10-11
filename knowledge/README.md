# knowledge/

Knowledge packs: the source of truth for every fact the companion states.

Facts are YAML, one fact per entry, layered **national → state → city → university**. The most specific layer wins (FR-3.2). Every entry needs `source_url` (official source only), `last_verified` and `reviewer` (NFR-ACC.1).

Add or change facts with the `pack-author` skill (`.claude/skills/pack-author/`). Run `make validate` before a PR.
