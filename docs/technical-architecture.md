# Germany Student Companion — Technical Architecture

Oct 10, 2026 · @Ajeet Chouksey

## Context

The companion is a skill that runs inside the student's own AI tool and stores everything personal in the student's own Google account. We host no runtime: the project ships files (skill, packs, version) and a script template the student deploys in their account.

**Drivers**

- Students use Gemini, Claude or Microsoft Copilot, often on free plans, and may switch at any time.
- Germany-specific facts change often and must be traceable to a source.
- Run by a small open-source team with no budget for hosting personal data or for GDPR processor duties.

**Constraints**

| Constraint | Consequence |
| --- | --- |
| No personal data on project servers | No backend in MVP; state in Drive; MCP server (phase 2) serves public packs only |
| Free plans are the floor | Core flows use only chat, text, links and bundled files |
| Tool features vary and change | Capability flags per tool × plan, verified by the spike and re-tested per release |
| Setup in 3 student actions | One Apps Script deploy does all Drive setup; Google connectors switched on from the first chat |
| Apps Script scope `drive.file` only | Script touches only files it created; no Gmail or Calendar scopes |

**Quality goals, in priority order**

1. Privacy: personal data never leaves the student's account except to the AI tool they authorised.
2. Correctness: every fact sourced, dated and reviewed; numbers from formulas, never from the model.
3. Portability: the same release behaves the same on every tool; state survives a tool switch.
4. Resilience to tool change: every extra has a fallback; the floor needs none.
5. Low operating cost: static hosting only (GitHub, GitHub Pages, a public Drive folder).

## Overview

The project publishes files; the AI tool runs the skill; the student's Google account holds all state and the only code that writes it.

&#91;embedded content: architecture overview · 3 zones\]

The AI tool reads Drive, Gmail and Calendar through its own Google connector and proposes changes as links; the student taps a link and their own Apps Script writes the change. Live packs are an extra: every skill build carries a bundled snapshot.

## Components

Nine components across three zones; only the student zone holds personal data.

| Component | Zone | Responsibility | Tech |
| --- | --- | --- | --- |
| `SKILL.md` | Project → AI tool | Behaviour: read adapter and `index.md`, answer from packs, propose action links, fall back quietly | Markdown skill; imported per tool |
| Adapters | Project → AI tool | Capability flags per tool × plan, fallback chain | YAML in `skill/reference/adapters/` |
| Bundled pack snapshot | Project → AI tool | Floor knowledge when URL or Drive reads fail | Generated Markdown in `skill/reference/packs/`, version-stamped |
| Knowledge packs | Project | Source of truth for facts, layered national → state → city → university | YAML + JSON Schema in `knowledge/` |
| Build and CI | Project | Validate, freshness check, evals, build per-tool skill zips, packs, `latest.json` | GitHub Actions |
| Public packs folder + `latest.json` | Project | Live packs and version notices for tools that can fetch | Public Drive folder; GitHub Pages |
| Journey folder | Student | State: Checklist, Budget, Log, `index.md`, `profile.md`, Letters, Documents | Google Drive and Sheets, formulas for all numbers |
| Action-link web app | Student | Setup and every write; token check, idempotency, undo, Log | Apps Script web app in the student's account, `drive.file` scope, deployed from our clasp project |
| Native Google connectors | AI tool ↔ Student | Reads of Drive, Gmail by sender, Calendar; native writes only where flagged | Built into Gemini; connectors in Claude and Copilot |

The AI tool is a component we do not control: it is treated as an untrusted, swappable runtime that only sees what the student shares with it.

## Capability model

The skill never assumes a feature: it resolves each capability from the adapter for the current tool and plan, and walks a fallback chain until something works. The floor (chat, bundled packs, text cards, action links) needs no flag.

**Resolution order at runtime**

1. Identify the tool from the adapter bundled in this tool's skill build.
2. Read `profile.md` (if Drive works) for `ai_plans.<tool>`; otherwise assume `free`.
3. Resolve the plan profile: `free`, then the plan's own flags over it (`inherits`).
4. Per capability: `yes` → use · `no` → fallback · `unknown` → try once, record result in `profile.md` (`ai_plans`) on success, else fallback.
5. Never claim a feature to the student unless the call succeeded this session.

**Adapter schema (v1)**

```yaml
# skill/reference/adapters/<tool>.yaml
tool: gemini | claude | copilot
schema: 1
plans:
  free:      { <capability>: yes | no | unknown, ... }
  paid:      { inherits: free, ... }
  education: { inherits: free, ... }
fallbacks:   { <capability>: <capability | floor_action> }
notes:       { <capability>: short note for maintainers }
last_verified: YYYY-MM-DD
verified_by: <github handle>
```

**Capabilities and fallback chain**

| Capability | Used for | Falls back to |
| --- | --- | --- |
| `drive_read` | `index.md`, `profile.md`, sheets | `status` link → `handover.md` upload → ask the student |
| `fetch_url` | `latest.json`, live packs | bundled snapshot |
| `gmail_search` | letters from known senders | student pastes or forwards |
| `calendar_write` | deadlines | `.ics` action link |
| `tasks_write` | Google Tasks | Checklist row via `add_task` |
| `sheets_edit` | direct edits | action links |
| `charts_inline` → `canvas_html` → `sheets_canvas` | visuals | text cards |

CI validates every adapter against the schema and fails a release if any capability lacks a fallback.

## Action links API

Every write is a one-tap HTTPS link to the student's own Apps Script web app, so writes behave the same on every tool. The web app runs as the student and is deployed with access **Only myself**: a link works only in a browser signed in to that Google account.

**Request shape**

```
GET https://script.google.com/macros/s/<deployment-id>/exec
    ?v=1&a=<action>&k=<token>&n=<nonce>&<params>
```

- `v` API version · `a` action · `k` per-student token from `index.md` · `n` nonce the skill generates per proposed change (UUID v4).
- Response: a small HTML page with the result in plain words and an Undo button; `fmt=text` returns plain text for `status`.

| Action | Params | Effect | Log entry |
| --- | --- | --- | --- |
| `done` / `undo` | `task` | Checklist status change | Yes |
| `add_task` | `title`, `due`, `phase?` | New Checklist row | Yes |
| `expense` | `amount`, `category`, `note` | New Budget row | Yes |
| `study` | `module`, `minutes` | Revision log row | Yes |
| `phase` | `n` | Adds that phase's tasks from packs | Yes |
| `ics` | `title`, `date`, `time?` | Returns an `.ics` file; no Drive write | No |
| `status` | `fmt?` | Read-only summary: phase, next 3 tasks, runway | No |
| `handover` | — | Writes `handover.md` (no ID numbers) | Yes |
| `revert` | `ref` (a nonce) | Reverses that Log entry | Yes |

**Guarantees**

- **Auth:** Only-myself access + token. Link-preview bots are not signed in, so prefetches cannot write; the token stops crafted links from third parties.
- **Idempotency:** the nonce is stored in Log; a repeated nonce returns the original result and writes nothing. This is what makes the same link safe to tap from two tools.
- **Concurrency:** `LockService.getUserLock()` around every write.
- **Audit and undo:** Log columns `ts, nonce, action, params, before, after, tool, result`; `revert` restores `before`.
- **Validation:** whitelist of actions and params, length and type checks, amounts as decimals in EUR, dates ISO 8601.
- **Token rotation:** a sheet menu item rotates the token and rewrites `index.md`; old links then fail with a clear message.
- **Tool attribution:** the skill adds `src=<tool>` so the Log records which tool proposed each change.

## Knowledge pipeline

Facts live as YAML in the repo and reach students only through a CI release; nothing is edited in Drive or in a skill by hand.

**Pack entry (schema v1)**

```yaml
id: kiel.anmeldung.office
layer: city            # national | state | city | university
scope: kiel
topic: anmeldung
phase: 2
text: >-
  Register your address within 14 days of moving in ...
source_url: https://...
last_verified: 2026-10-20
reviewer: <github handle>
expires: 2027-04-20    # optional; defaults to last_verified + 6 months
```

**Resolution:** university → city → state → national. A more specific layer overrides an entry with the same `topic` key; the skill always shows the `source_url` of the entry it used.

**CI stages** (GitHub Actions, on every pull request and on release tags)

1. Schema check on packs and adapters (JSON Schema).
2. Rules: no entry without `source_url`, `last_verified`, `reviewer`; no city or tool names in `SKILL.md`; every capability has a fallback.
3. Link check on `source_url`; weekly freshness job opens an issue for entries past `expires`.
4. Evals: 50 questions with required facts, run per tool where an API is available, otherwise by a manual checklist.
5. Build: per-tool skill zip (SKILL.md + that tool's adapter + bundled snapshot), public packs, `latest.json`.
6. Release: GitHub release, packs to the public Drive folder, `latest.json` to GitHub Pages.

**Versioning**

| Artefact | Scheme | Breaking change means |
| --- | --- | --- |
| Skill | SemVer | Behaviour or data-contract change |
| Packs | Date per layer (`2026-11-02`) | Never breaking; entries only added, edited or expired |
| Templates / data contracts | Major.minor | Rename or removal → major + migration in Apps Script |
| Adapters | `schema` + `last_verified` | New schema → skill major |

`latest.json` carries the current versions, a `critical` flag for urgent fact fixes, and a one-line note. Tools that cannot fetch it learn about updates from the bundled snapshot's version stamp and the `status` page.

## Key flows

Three flows carry the MVP: setup once, write by tap, and switch tools with nothing lost.

**Write (expense, task done, new task)**

&#91;embedded content: write flow · 4 participants, 7 messages\]

The AI never writes on its own; it proposes a link with a fresh nonce, and the student's script checks token and nonce before it writes and logs. Totals come back from sheet formulas on the next read.

**Setup (3 student actions)**

1. Add the skill to their AI tool (import on Gemini and Claude; agent or starter prompt on Copilot).
2. First chat: three questions (country, university, semester start); the skill asks the student to switch on the Google connector if it is off.
3. Tap "Set up my Drive": the student deploys the web app from our template, which creates the Journey folder, sheets, `index.md` with token and URL, `profile.md`, and the packs shortcut.

**Switch tools**

1. Student adds the skill on the new tool and switches on its Google connector.
2. First chat finds the Journey folder (or asks for `handover.md` if Drive is not readable) and skips onboarding.
3. The skill reads `index.md` for the action-link URL and token; the same links and Log carry on.
4. `profile.md` records the new `ai_tool` and its plan under `ai_plans`.

## Security and privacy

The project is never a data processor: personal data stays in the student's Google account and flows only to the AI tool the student chose and connected.

**Data map**

| Data | Stored in | Seen by | Never contains |
| --- | --- | --- | --- |
| Profile, phase, goals | `profile.md` in Drive | Student, their AI tool | Passport, visa, tax or bank numbers |
| Tasks, budget, Log | Sheets in Drive | Student, their AI tool, their Apps Script | Card or account numbers |
| Letters, documents | Drive folders | Student, their AI tool when shared | — |
| Mail | Gmail | AI tool via native connector, by sender list | — |
| Action-link token | `index.md` | Student, their AI tool | — |
| Packs, adapters, versions | GitHub, public Drive, Pages | Everyone | Any personal data |

**Scopes:** the Apps Script asks only for `drive.file` (files it created) plus the web-app runtime; no Gmail, Calendar or full-Drive scopes. Gmail and Calendar access is granted by the student to their AI tool, not to us.

**Threats and mitigations**

| Threat | Mitigation |
| --- | --- |
| Token leaks via chat history or provider logs | Only-myself access means a token alone cannot write; rotation from the sheet menu |
| Link preview or prefetch triggers a write | Previewers are not signed in as the student; nonce idempotency |
| Prompt injection from a letter or email | Skill treats mail and documents as data; writes only via links the student taps; no auto-send |
| Wrong or stale fact causes harm | Source, date, reviewer on every entry; freshness CI; `critical` flag; legal content as general information with referral |
| Malicious pack pull request | CODEOWNERS review per layer; CI rules; signed release tags |
| Unverified-app warning scares students | `drive.file` only; spike test 6; Google Form fallback |
| Student deletes or breaks a sheet | Log-based undo; setup can rebuild templates and keep data tabs |

**GDPR position:** each student is the controller of their own data and their AI provider is their processor; the project publishes only non-personal content. To confirm with a legal reviewer before public launch.

## Decision log

Twelve decisions shape the MVP; each becomes an ADR file in `docs/adr/` when the repo exists. Newest first.

| ADR | Decision | Why | Status |
| --- | --- | --- | --- |
| 012 | Students use the vendors' own apps; AI CLIs only as maintainer tooling (evals) | CLIs need paid plans or desktops, and consumer logins may not be routed through third-party tools | Accepted |
| 011 | Reads via native Google connectors in each tool; we build no Gmail, Calendar or Drive integration | All three tools already connect to Google | Accepted, verify in spike |
| 010 | Students can switch tools any time; state only in Drive; nonce idempotency | Students change tools; no lost or doubled changes | Accepted |
| 009 | Adapters per tool × plan with inheritance; plan detected by use | Features vary by plan; keep setup at 3 actions | Accepted |
| 008 | Free plans are the floor on Gemini, Claude and Copilot | Students rarely pay | Accepted |
| 007 | Action-link web app deployed with Only-myself access + token | Blocks prefetch and crafted-link writes | Proposed |
| 006 | Writes through action links, not native edits, by default | Only write path that behaves the same everywhere | Accepted |
| 005 | Bundled pack snapshot in every skill build | Floor must work without URL fetch or Drive | Accepted |
| 004 | Apps Script with `drive.file` scope only | Avoid verification and unverified-app warnings | Accepted, verify in spike |
| 003 | Knowledge as layered YAML packs with schema and CI | Traceable, reviewable facts; scale by pull request | Accepted |
| 002 | One generic `SKILL.md`, no place or tool names | One skill for every city and tool | Accepted |
| 001 | No personal data on project servers | Privacy; no processor duties | Accepted |

## Open questions

Six architecture questions need an answer by G1 on 18 October; the first two can change the API.

- [ ] Only-myself access blocks AI tools from fetching `status` server-side. Accept that (Drive connectors cover reads), or add a second read-only deployment with Anyone access and a read token?
- [ ] Does the web app's first run trigger the unverified-app screen with `drive.file` only? If yes, is the Google Form fallback enough for the pilot?
- [ ] Can each tool's Drive connector read Sheets cell values, or only text exports? This decides whether the skill reads the Dashboard tab or calls `status`.
- [ ] How large can the bundled snapshot be per tool (reference file count and size)? This sets how many layers ship in the floor.
- [ ] Write `handover.md` automatically after each write, or only on tap?
- [ ] Copilot packaging on free plans: custom agent, saved instructions, or a starter prompt plus file upload?
