# Germany Student Companion — Tech Stack (Development)

Oct 10, 2026 · @Ajeet Chouksey

## Stack at a glance

MVP 1 runs with no servers of our own: everything is files, CI and the student's Google account. The only infrastructure we would operate arrives in phase 2.

| Layer | Technology | Runs where | Cost model |
| --- | --- | --- | --- |
| Knowledge | YAML packs + JSON Schema | GitHub repo | Free |
| Build and CI | GitHub Actions, Python 3 scripts | GitHub-hosted runners | Free tier for public repos |
| Distribution | GitHub Releases, GitHub Pages (`latest.json`, setup page), public Google Drive folder (packs) | GitHub, Google | Free |
| Student runtime | Skill package inside Gemini, Claude or Copilot | The student's AI app | Student's own plan |
| Student state | Google Drive, Sheets (formulas), Gmail, Calendar, Tasks | The student's Google account | Student's own account |
| Writes | Google Apps Script web app (V8), `clasp` | The student's Google account | Free quotas |
| Visuals | Markdown cards; `dashboard.html` (plain HTML, CSS, vanilla JS) for Canvas | The AI app | Free |
| Dev tooling | VS Code, Claude Code, developer skills, `gh`, `clasp`, `wrangler` | Maintainers' machines | Existing tools |
| Phase 2 | MCP server on Cloudflare Workers, Terraform | Cloudflare | Workers free tier, paid plan only if traffic needs it; public data only |

## Languages and formats

Six formats, kept deliberately boring so contributors from any background can help.

| Format | Used for | Conventions |
| --- | --- | --- |
| YAML | Packs, adapters, eval cases | 2-space indent, `yamllint` default rules, one fact per entry |
| JSON Schema (draft 2020-12) | Validating packs, adapters, eval cases, `latest.json` | Files in `knowledge/_schema/`; versioned with `schema:` field |
| Markdown | `SKILL.md`, intent and reference files, cards, templates, docs, ADRs | Plain English B1; no HTML in student-facing files |
| Python 3 | `lint_skill.py`, `build.py`, `run_evals.py` | Standard library + `pyyaml`, `jsonschema`; `ruff` for lint; `pytest` |
| Apps Script (V8 JavaScript) | Action-link web app and setup | Pushed with `clasp`; no external libraries; tests run locally with a small Apps Script mock |
| HTML + CSS + vanilla JS | `dashboard.html` Canvas template | Single file, no CDN calls, reads data passed in the chat |

## Environments and accounts

Three environments, separated by Google account and release channel rather than by servers.

| Environment | Packs and `latest.json` | Apps Script | Who uses it |
| --- | --- | --- | --- |
| Dev | Local build from a branch | Personal test project via `clasp` | Maintainers |
| Test | `next` channel: test Drive folder, `latest-next.json` | Test deployment in a test Google account | Spike, evals, G2/G3 dry runs |
| Production | Release channel: public Drive folder, `latest.json` | Each student's own deployment from a released template | Pilot students |

**Accounts to set up in week 1**

| Account | Purpose | Protection |
| --- | --- | --- |
| GitHub org or repo under `ajeetchouksey` | Code, packs, CI, releases, Pages | 2 maintainers, security keys, branch protection |
| Project Google account | Owns the public packs folder and the test folder | Security key; no personal use |
| Test Google accounts (personal, free) | Spike and evals on Gemini, Claude, Copilot | One per tester; no real personal data |
| CAU login (from a volunteer student) | Education-plan test (spike test 18) | Volunteer runs it; we observe |
| One paid plan per tool (optional) | Paid-plan flags (test 19) | Monthly, cancelled after testing |

CI holds one secret in MVP 1: a Drive upload credential limited to the packs folders, stored as an encrypted Actions secret in a `production` environment that needs maintainer approval. Everything else uses the repo's built-in token.

## CI/CD workflows

Five GitHub Actions workflows; only `release` publishes to production, and only after a maintainer approves the `production` environment.

| Workflow | Trigger | Steps | Blocks merge or release when |
| --- | --- | --- | --- |
| `validate` | Every PR | `yamllint` → schema checks → `lint_skill.py` → link check on changed `source_url` → fact diff report as PR comment → `pytest` and Apps Script tests | Any check fails |
| `freshness` | Weekly (Monday) | Find entries within 30 days of `expires` → open or update one issue per layer | Never blocks; expired entries are caught by `release` |
| `evals` | Manual, and on release candidates | `run_evals.py` per tool and plan → results to `evals/results/` | Zero-tolerance guardrail failure, or under 45/50 factual on Gemini |
| `build-next` | Push to `main` | Build packs, snapshot, per-tool zips → publish to the `next` channel | Validation fails |
| `release` | Signed tag `v*` | Rebuild from tag → checksums and provenance → GitHub release → packs to public Drive folder → `latest.json` to Pages | Expired entries, failed evals, missing approval |

All Actions pinned to commit SHAs; Dependabot keeps them current.

## Phase 2 stack: MCP server

After the pilot, an MCP server on Cloudflare Workers serves the public packs to tools that support remote MCP. It is read-only and never sees personal data, so it stays a small, stateless edge service with no servers to run.

| Concern | Choice |
| --- | --- |
| Runtime | Cloudflare Workers; remote MCP over Streamable HTTP |
| Service | TypeScript with the MCP TypeScript SDK (or Cloudflare's Agents SDK); tools such as `search_packs`, `get_entry`, `get_versions`, `get_letter` |
| Data | Pack JSON bundled as Workers static assets at release; R2 only if packs outgrow the asset limits; no database |
| Build | `wrangler` in GitHub Actions; Worker bundle checksummed with the release |
| CI credential | Cloudflare API token scoped to this one Worker and account, stored in the approval-gated `production` environment |
| IaC | Terraform with the Cloudflare provider for the Worker route, custom domain and WAF rules; `wrangler` deploys the code |
| Edge | Custom domain on Cloudflare; Workers rate limiting and WAF rate rules; anonymous read-only access |
| Observability | Workers analytics and error logs only; no request bodies logged |
| Cost guard | Free-plan request limits as the ceiling; usage notifications on the account |

The skill keeps the bundled snapshot as its floor, so the MCP server is an extra flag (`mcp: yes`) in each adapter, never a dependency.

## Choices and alternatives

Each choice below favours zero hosting and the student owning their data over convenience for us.

| Need | Chosen | Considered | Why not |
| --- | --- | --- | --- |
| Student writes | Apps Script web app in the student's account | Our own API; Google Forms only | Our API would hold personal data; Forms can't undo or validate well (kept as fallback) |
| Student state | Google Sheets with formulas | Firestore; local app storage | Not in the student's account; not readable by AI connectors |
| Knowledge store | YAML in Git | Headless CMS; Notion | Weaker review trail, harder CI rules, extra accounts |
| Pack delivery | Bundled snapshot + public Drive folder | MCP server only | Free plans may not reach it; MCP comes in phase 2 as an extra |
| Visuals | Markdown cards first | A PWA dashboard | Extra app to install; PWA only if the pilot asks for it |
| Build scripts | Python | Node.js | Either works; Python is quicker for YAML and schema tooling |
| Phase 2 hosting | Cloudflare Workers | Azure Container Apps; Google Cloud Run | Workers need no containers or regions to manage, have a generous free tier and first-class remote MCP support |
