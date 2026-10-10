# theBudddy — Germany Student Companion

An open, privacy-first AI companion that helps international students settle into life and study in Germany — starting with students from India at **CAU Kiel**.

The companion is a **skill** that runs inside the student's own AI app (Gemini, Claude or Microsoft Copilot, free plans included). Everything personal lives in the student's own Google account. The project hosts no runtime and stores no personal data.

> **Status:** scaffold and validators in place (tasks P1–P2). Knowledge packs, adapters, Apps Script and the skill land from 12 October 2026. Pilot with 10 CAU Kiel students runs **9–22 November 2026**.

---

## How it works

```
 Project (public)              Student's AI app               Student's Google account
 ─────────────────             ─────────────────              ─────────────────────────
 SKILL.md + adapters   ──▶     Runs the skill        ◀──▶     Drive: Germany Journey folder
 Knowledge packs (YAML)        Reads via its own              (Checklist, Budget, Log,
 latest.json                   Google connector               index.md, profile.md)
                               Proposes action links  ──▶     Apps Script web app writes
                                                              the change (drive.file scope)
```

1. **Add the skill** to Gemini, Claude or Copilot.
2. **First chat:** three questions (country, university, semester start).
3. **Tap "Set up my Drive":** the student's own Apps Script creates a private *Germany Journey* folder.

After that, the AI answers from sourced knowledge packs, reads Drive, Gmail and Calendar through the app's own Google connector, and proposes changes as one-tap **action links**. The student taps; their script writes and logs the change, with undo. Students can switch AI apps at any time without losing progress.

## Design rules

1. **No personal data on project servers.** State lives only in the student's Google account.
2. **Numbers from formulas, facts from packs.** The AI explains and acts; it never invents a figure or a rule.
3. **Generic skill, layered knowledge.** No city, university or tool names in `SKILL.md`. Facts resolve university → city → state → national.
4. **Every fact carries `source_url`, `last_verified` and `reviewer`.** CI rejects anything unsourced.
5. **Lean setup.** Three student actions. Apps Script uses only the `drive.file` scope.
6. **Writes go through action links** — token-checked, idempotent (nonce), logged and undoable.
7. **Free plans are the floor.** Chat, bundled packs, text cards and action links work everywhere; extras (charts, Canvas dashboards, Sheets canvas) switch on only where an adapter says so, and every extra has a fallback.
8. **Legal content is general information, not legal advice.** Answers point to AStA, Mieterverein or a lawyer.

## Documentation

| Document | What it covers |
| --- | --- |
| [Brief](docs/brief.md) | Decisions so far — treat as settled |
| [What You Need](docs/what-you-need.md) | Student-facing guide: accounts, choosing an AI app, connecting Google, privacy, common problems |
| [MVP 1 Plan](docs/mvp-1-plan.md) | Scope, tool × plan capability matrix, weekly plan, gates G1–G4, spike tests, pilot metrics, open decisions |
| [Requirements (MVP 1)](docs/requirements.md) | Feature catalogue, functional and non-functional requirements, out of scope |
| [Technical Architecture](docs/technical-architecture.md) | Components, capability model and adapter schema, action-links API, knowledge pipeline, key flows, ADR log |
| [Student Skill](docs/student-skill.md) | Skill package layout, intents, card templates, `SKILL.md` skeleton |
| [AI Guardrails](docs/ai-guardrails.md) | Grounding, sensitive topics, prompt-injection defence, tone, guardrail block and red-team set |
| [Security Plan (MVP 1)](docs/security-plan.md) | Assets, threat model, controls by layer, supply chain, testing, incident response, GDPR position |
| [Tech Stack (Development)](docs/tech-stack-development.md) | Stack at a glance, languages, environments, CI/CD workflows, phase 2 MCP server |
| [DevOps and Engineering System](docs/devops-system.md) | Branching, commits, PRs, labels, CODEOWNERS, quality gates, testing, metrics |
| [Release Management](docs/release-management.md) | Release model, process, approvals, hotfix and rollback, release calendar |
| [Developer Skills](docs/developer-skills.md) | Claude skills for maintainers (e.g. pack author), toolchain, build order |
| [Dev Agent Instructions](docs/dev-agent-instructions.md) | `AGENTS.md`, task prompt template, prompts P1–P13, reviewer agent prompt |
| [ADRs](docs/adr/) | 11 architecture decision records |

## Repository layout

```
AGENTS.md                   standing brief for AI agents (CLAUDE.md points here)
knowledge/                  YAML packs: national/ (+ letters/), states/, cities/, universities/
  _schema/                  JSON Schemas + official-domains.txt (source allowlist)
skill/                      SKILL.md and reference/ (intents, adapters, bundled packs)
templates/                  Journey folder templates (data contracts v1)
apps-script/                action-link web app and Drive setup (clasp)
scripts/                    validate, schema/content/skill/adapter checks, build, evals
tests/                      pytest suite with invented fixture data
evals/                      eval cases and results
site/                       GitHub Pages: latest.json, setup page
docs/                       design docs and docs/adr/
.claude/skills/             developer skills (pack-author, ...)
.github/                    PR and issue templates (workflows arrive with P3)
build/                      generated, not committed
```

Every folder has a `README.md` stating its purpose.

## Quick start

```sh
python3 -m pip install -r requirements-dev.txt
npm install
make validate   # yamllint, schemas, content, skill and adapter rules
make test       # pytest with coverage (>= 80%), Apps Script tests
make build      # packs, snapshot, skill zips, latest.json (task P3)
```

`make validate ROOT=tests/fixtures/good` runs the checks against another tree.

## Maintainer to-dos

Agents may not do these; a maintainer sets them up by hand (see `docs/devops-system.md`):

- [ ] Add `CODEOWNERS` with the reviewers per layer (national, state, Kiel, CAU, Apps Script, `.github/`)
- [ ] Branch protection on `main`: PRs only, CODEOWNER review, required `validate` check, signed tags
- [ ] Create the labels: `type:*`, `area:*`, `layer:*`, `tool:*`, `priority:*`, `ai-generated`, `needs-source`, `pilot-feedback`
- [ ] Create the GitHub Project board (Inbox → Ready → In progress → In review → Done) and milestones
- [ ] Turn on private vulnerability reporting, secret scanning, Dependabot and CodeQL
- [ ] Confirm the licences and replace `LICENSE` and `LICENSE-CONTENT`
- [ ] Review `knowledge/_schema/official-domains.txt` before the first pack PR

## Tech stack

| Layer | Technology |
| --- | --- |
| Knowledge | YAML packs + JSON Schema |
| Build and CI | GitHub Actions, Python 3 |
| Distribution | GitHub Releases, GitHub Pages (`latest.json`, setup page), public Google Drive folder |
| Student runtime | Skill inside Gemini, Claude or Copilot |
| Student state | Google Drive, Sheets (formulas), Gmail, Calendar, Tasks |
| Writes | Google Apps Script web app (V8), `clasp` |
| Phase 2 | Read-only MCP server for public packs on Cloudflare Workers, Terraform |

## Roadmap

| Gate | Date | Passes when |
| --- | --- | --- |
| G1 · Spike | 18 Oct 2026 | 21 capability tests recorded; adapter flags set per tool and plan |
| G2 · Setup | 1 Nov 2026 | A new user finishes setup alone in under 10 minutes on each tool |
| G3 · Quality | 8 Nov 2026 | ≥ 45/50 evals pass on Gemini; floor flows pass on Claude and Copilot free; no unsourced facts |
| Pilot | 9–22 Nov 2026 | 10 CAU Kiel students across all three tools |
| G4 · Review | 23 Nov 2026 | Pilot results checked against targets |

**MVP 1 covers:** settling-in phases 1–3 and the top 10 official letters, for national, Schleswig-Holstein, Kiel and CAU layers.
**Not yet:** MCP server, PWA, ChatGPT, other cities, phases 4–7, study quizzes.

## Contributing

Contributions open once the scaffold is pushed. In short:

- Branches: `feat/<issue>-<slug>`, `packs/<scope>-<topic>`, `fix/<issue>-<slug>`; agent branches use `agent/<skill>/<issue>`.
- Commits: Conventional Commits (`feat(skill)`, `fix(script)`, `packs(kiel)`, `ci`, `docs`).
- Fact changes need a source, date and reviewer, and are reviewed by the layer's CODEOWNER.

See [DevOps and Engineering System](docs/devops-system.md) for the full conventions.

## Licence

To be decided by 25 October 2026. Proposed: **MIT** for code, **CC BY-SA** for knowledge content.

## Disclaimer

The companion gives general information about life and study in Germany. It is not legal, tax or immigration advice. Always check the linked official source, and contact AStA, a Mieterverein or a lawyer for your specific case. In an emergency, call 112.
