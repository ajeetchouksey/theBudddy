# scripts/

Python 3 tools used locally and in CI. Standard library + `pyyaml` + `jsonschema` only.

| Script | Purpose |
| --- | --- |
| `validate.py` | Runs every check below (`make validate`) |
| `check_schemas.py` | Validates YAML/JSON against `knowledge/_schema/` |
| `check_content.py` | Pack rules: sources, dates, reviewer, expiry |
| `lint_skill.py` | Skill rules: no names, guardrail block, size budget |
| `check_adapters.py` | Adapter rules: fallbacks, inheritance, freshness |
| `build.py` | Packs, resolved views, snapshot, skill zips, `latest.json` |
| `fact_diff.py` | Old → new values of changed facts (PR comment) |
| `check_links.py` | Checks `source_url` of changed facts |
| `freshness.py` | Entries expiring soon, per layer (weekly issues) |
| `money_plan.py` | Reference model for the Money plan sheet formulas (F13) |
| `run_evals.py` | Eval runner (task P10) |
