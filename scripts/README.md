# scripts/

Python 3 tools used locally and in CI. Standard library + `pyyaml` + `jsonschema` only.

| Script | Purpose |
| --- | --- |
| `validate.py` | Runs every check below (`make validate`) |
| `check_schemas.py` | Validates YAML/JSON against `knowledge/_schema/` |
| `check_content.py` | Pack rules: sources, dates, reviewer, expiry |
| `lint_skill.py` | Skill rules: no names, guardrail block, size budget |
| `check_adapters.py` | Adapter rules: fallbacks, inheritance, freshness |
| `build.py` | Packs, snapshot, skill zips, `latest.json` (task P3) |
| `run_evals.py` | Eval runner (task P10) |
