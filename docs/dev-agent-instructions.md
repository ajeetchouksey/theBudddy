# Germany Student Companion — Dev Agent Instructions

Oct 10, 2026 · @Ajeet Chouksey

## How to use this

Agents only know what is in the repo, so the design docs go into the repo first; then each task is one prompt, one branch, one PR.

**Before the first agent task**

1. Export the project docs to Markdown into `docs/`: brief, MVP 1 plan, technical architecture, requirements, security plan, AI guardrails, developer skills, student skill, tech stack, release management, DevOps system. Keep their names stable; prompts refer to them by path.
2. Commit `AGENTS.md` (section 2) at the repo root, and `CLAUDE.md` containing one line: `See AGENTS.md.`
3. Create the labels, board and branch protection from the DevOps doc by hand; agents may not change them.

**Order of tasks** (mostly sequential; P6 and P12 start in week 1 alongside P1–P4)

| # | Prompt | Week |
| --- | --- | --- |
| P1 | Repo scaffold | 1 |
| P2 | Schemas and validators | 1 |
| P3 | Build scripts and CI | 1 |
| P4 | Knowledge packs (one run per layer) | 1–2 |
| P5 | Letter packs | 2 |
| P6 | Adapters from spike evidence | 1–2 |
| P7 | Sheet templates and formulas | 3 |
| P8 | Action-link Apps Script | 3 |
| P9 | Student skill: SKILL.md, intents, cards | 3–4 |
| P10 | Eval harness and cases | 2–4 |
| P11 | Release workflow | 4 |
| P12 | Security hardening | 1, then each release |
| P13 | MCP server on Cloudflare Workers | Phase 2 |

**Handing a task to an agent:** open an issue, paste the prompt with its placeholders filled, assign the agent, and review the PR against the prompt's "Done when". Run P4 and P10 several times with different scopes; never combine two prompts in one run.

## AGENTS.md

Commit this file at the repo root as is; it is the standing brief every agent reads before any task.

```markdown
# AGENTS.md — Germany Student Companion

## What this project is
An open, privacy-first AI companion that helps international students settle into life and study in Germany. It ships as a skill for Gemini, Claude and Microsoft Copilot (free plans are the floor). First audience: students from India at CAU Kiel. Pilot: 10 students, 9–22 November 2026.

## Read before any task
- docs/brief.md — decisions; treat as settled
- docs/technical-architecture.md — components, action-link API, capability model
- docs/requirements.md — FR and NFR IDs; link every change to one
- docs/ai-guardrails.md and docs/security-plan.md — rules you must not break
- docs/devops-system.md — branches, commits, PRs, gates
- The docs folder for the area you touch (student-skill.md, developer-skills.md, release-management.md)

## Non-negotiable rules
1. No personal data on project infrastructure. Student data lives only in the student's Google account.
2. Numbers from sheet formulas, facts from packs. The model explains; it never invents figures.
3. Every pack entry has source_url (official source only), last_verified, reviewer. Never add an unsourced fact. Never set reviewer yourself.
4. SKILL.md and intent files contain no city, university or AI tool names.
5. Apps Script uses only the drive.file scope. No external libraries. No new services.
6. Writes happen only through action links (token + nonce + Log). Never add a write path that skips them.
7. Every adapter capability has a fallback. The floor (chat, bundled packs, text cards, action links) must work on every tool and plan.
8. Data contracts: minor versions only add fields. Renames or removals need a major version, a migration and an ADR.
9. Student-facing text: plain English, B1 level, short sentences, German terms explained the first time.
10. Legal topics are general information with a disclaimer and a referral.

## How you work
- One task per branch: agent/<skill-or-prompt>/<issue-number>. One PR per task.
- Conventional Commits with scopes: feat(skill), fix(script), packs(kiel), ci, docs, chore.
- Small PRs (under ~400 changed lines). Split if larger.
- Write or update tests and evals for every change.
- Run before opening a PR: make validate && make test (and make evals-smoke if you touched skill/).
- PR body: what and why, linked issue and requirement IDs, facts changed with sources, commands run with results, what you could not do. Add the ai-generated label.

## You may not
- Push to main, merge, tag, release, or approve PRs.
- Change .github/ permissions, branch protection, CODEOWNERS or secrets.
- Use blogs, forums, agencies or AI answers as sources.
- Mark an adapter capability yes without recorded spike evidence.
- Put real personal data in tests, fixtures, examples or logs.

## When stuck
Stop. In the PR or issue, write what you tried, what is missing (source, decision, credential, access) and the options you see. Do not guess past it.

## Commands
- make validate — yamllint, schema checks, content and skill rules, link check on changed files
- make test — pytest and Apps Script unit tests
- make build — packs, bundled snapshot, per-tool skill packages, latest.json (local)
- make evals-smoke — 10 quick eval cases on the local build
```

## Task prompt template

Every prompt below follows this shape; use it for new tasks too. The sections that make agent output good are "Read first", "Constraints" and "Done when": skip none of them.

```markdown
# Task {P#}: {title}
Issue: #{number} · Requirements: {FR/NFR IDs} · Branch: agent/{prompt}/{number}

## Goal
{One or two sentences: the outcome, not the steps.}

## Read first
- AGENTS.md
- {the 2–4 docs or files that define this task}

## Do
1. {ordered steps, each a verifiable action}

## Constraints
- {rules from AGENTS.md that matter most here, restated}
- {scope limits: what not to touch}

## Done when
- [ ] {testable criterion}
- [ ] make validate && make test pass

## Hand back
PR with: summary, files changed, commands run with output, open questions, anything you could not do and why.
```

## Foundation prompts

These three set up the repo so every later task has rails to run on.

### P1 · Repo scaffold

```markdown
# Task P1: Repo scaffold
Issue: #{n} · Requirements: NFR-POR.2, NFR-MAI.2 · Branch: agent/p1/{n}

## Goal
A repo skeleton that matches the agreed layout, with tooling config, so later tasks only add content.

## Read first
- AGENTS.md
- docs/brief.md (section 6, repo layout)
- docs/devops-system.md (repository conventions, quality gates)
- docs/tech-stack-development.md (languages and formats)

## Do
1. Create folders: knowledge/{national,national/letters,states,cities,universities,_schema}, skill/{reference/{intents,adapters,packs}}, templates/, apps-script/, build/, scripts/, evals/{cases,results}, site/, docs/adr/, .claude/skills/, .github/{workflows,ISSUE_TEMPLATE}.
2. Add README.md (what, why, how to contribute, links to docs/), CONTRIBUTING.md (from the DevOps doc), SECURITY.md (from the security plan, disclosure section), LICENSE placeholders for code and content with a TODO naming the proposed licences.
3. Add .github/pull_request_template.md and issue templates: feature, facts, bug, pilot-feedback, spike-result (fields from the DevOps doc).
4. Add .editorconfig, .yamllint, ruff config, package.json for JS tooling (Prettier, test runner), and a Makefile with targets validate, test, build, evals-smoke that call placeholder scripts printing "not implemented" and exiting 0.
5. Add docs/adr/0001…0011 as one file each from the Decision log in docs/technical-architecture.md, status as listed.

## Constraints
- No real facts, no personal data, no secrets.
- Do not create workflows yet (P3 does).
- Do not edit CODEOWNERS or branch protection; leave a TODO in the README listing them for a maintainer.

## Done when
- [ ] Tree matches the layout; every folder has a short README.md stating its purpose.
- [ ] make validate, make test, make build run and exit 0.
- [ ] 11 ADR files exist with title, status, context, decision, consequences.

## Hand back
PR with the tree, the Makefile targets and the list of TODOs for maintainers.
```

### P2 · Schemas and validators

```markdown
# Task P2: Schemas and validators
Issue: #{n} · Requirements: FR-3.2, NFR-ACC.1, NFR-ACC.2, NFR-POR.2, NFR-REL.2 · Branch: agent/p2/{n}

## Goal
Machine-checkable contracts for packs, adapters, eval cases and latest.json, plus rule checks CI can block on.

## Read first
- AGENTS.md
- docs/technical-architecture.md (capability model, knowledge pipeline)
- docs/ai-guardrails.md (evaluation section, case format)

## Do
1. Write JSON Schemas (draft 2020-12) in knowledge/_schema/: fact.json, letter.json, adapter.json, eval-case.json, latest.json. Fields exactly as in the architecture doc; additionalProperties false; id patterns enforced (<scope>.<topic>.<slug>).
2. Write scripts/check_content.py: every fact has source_url (https, domain in an allowlist file knowledge/_schema/official-domains.txt), last_verified (ISO date, not in the future), expires (default last_verified + 6 months); reviewer may be empty only on non-main branches; fail on expired entries.
3. Write scripts/lint_skill.py: fail if skill/SKILL.md or skill/reference/intents/* contain any name from a deny list (cities, universities, AI tools; list file in scripts/), if the guardrail block heading is missing, or if line budgets (SKILL.md 400, intents 150) are exceeded.
4. Write scripts/check_adapters.py: every capability has a fallback; plans inherit only from free; last_verified within 90 days on main.
5. Wire all of it into make validate. Add pytest tests with good and bad fixtures for each rule.

## Constraints
- Python standard library + pyyaml + jsonschema only.
- Fixtures use invented, obviously fake data (e.g. scope "testcity").
- Clear error messages: file, entry id, rule, how to fix.

## Done when
- [ ] Each rule has at least one passing and one failing fixture test.
- [ ] make validate fails on each bad fixture with a readable message.
- [ ] ≥ 80% line coverage on scripts/.

## Hand back
PR with schema summaries and a table of rules → script → test.
```

### P3 · Build scripts and CI

```markdown
# Task P3: Build scripts and CI
Issue: #{n} · Requirements: NFR-POR.3, NFR-SEC.4, NFR-MAI.1 · Branch: agent/p3/{n}

## Goal
A reproducible build of packs, snapshot and per-tool skill packages, and the CI workflows that guard every PR.

## Read first
- AGENTS.md
- docs/technical-architecture.md (knowledge pipeline, versioning)
- docs/devops-system.md (quality gates, testing strategy)
- docs/release-management.md (channels, what ships)
- docs/tech-stack-development.md (CI/CD workflows)

## Do
1. scripts/build.py: resolve packs per layer into build/packs/*.json; generate skill/reference/packs/ snapshot (Markdown, version-stamped); assemble build/skill-<tool>.zip for gemini, claude, copilot (Copilot: one flattened instruction file + packs file); write build/latest.json. Deterministic output (sorted keys, fixed timestamps from the tag or commit).
2. Workflows: validate.yml (every PR), freshness.yml (weekly, opens or updates one issue per layer), build-next.yml (push to main, uploads artefacts; publishing step left as a TODO for maintainers). Release workflow is P11.
3. Pin every third-party action to a full commit SHA; set permissions: read-all at the top and least privilege per job.
4. Add a fact-diff step that comments old → new values on PRs touching knowledge/.

## Constraints
- No secrets in these workflows. No publishing to Drive, Pages or Cloudflare.
- Do not change repository settings.

## Done when
- [ ] make build produces identical output twice in a row.
- [ ] validate.yml fails on a PR with a bad fixture (show the run).
- [ ] Every action pinned; workflow permissions minimal.

## Hand back
PR with build output tree, workflow summaries and the TODOs for maintainers.
```

## Product prompts

Seven prompts build what students actually use. P4 and P10 run once per scope.

### P4 · Knowledge packs

```markdown
# Task P4: Knowledge packs — {layer}/{scope}, phases {phases}, topics {topics}
Issue: #{n} · Requirements: FR-2.1, FR-3.1, FR-3.2, FR-3.5, NFR-ACC.1 · Branch: agent/p4/{n}

## Goal
Sourced, reviewable pack entries for {scope} covering {topics}, ready for a human reviewer.

## Read first
- AGENTS.md
- .claude/skills/pack-author/SKILL.md (follow it step by step)
- knowledge/_schema/fact.json and official-domains.txt
- Existing entries for these topics in all layers

## Do
1. List the facts a student needs for each topic in phases {phases} (what, where, when, cost, documents, deadline).
2. For each fact, find an official source. Write one entry per fact in the most specific layer the source covers.
3. Add a checklist task entry for each action a student must take (task_id, phase, why, depends_on, source_url).
4. Run make validate.

## Constraints
- Official sources only; if none, list the fact under "Could not source" and do not write it.
- No fees or dates from memory. Quote under 15 words per source in the PR body.
- Plain English B1; explain German terms the first time.
- Leave reviewer empty.

## Done when
- [ ] Every entry validates and has an official source.
- [ ] PR body lists each entry with source and quote, plus "Could not source".
- [ ] Layer CODEOWNER requested as reviewer.

## Hand back
PR + count of entries by topic + unsourced list.
```

### P5 · Letter packs

```markdown
# Task P5: Letter pack — {letter type}
Issue: #{n} · Requirements: FR-4.1, FR-4.2, FR-4.3 · Branch: agent/p5/{n}

## Goal
A letter-type entry that lets the companion explain this letter, its deadline and next step, plus eval cases.

## Read first
- AGENTS.md
- .claude/skills/letter-pack/SKILL.md
- knowledge/_schema/letter.json
- docs/ai-guardrails.md (untrusted input, scam handling)
- Redacted sample: {path or pasted text}

## Do
1. Write knowledge/national/letters/{type}.yaml: sender list (official domains and names), what it means, usual deadline rule, next step, cost of missing it, referral, scam signs.
2. Write 3 eval cases: a real-looking letter, an email version, and a scam variant.

## Constraints
- Remove every personal detail from the sample; never commit the original.
- Deadlines as rules ("within N days of the letter date") with source, never as fixed dates.

## Done when
- [ ] Letter entry and 3 cases validate; scam case has must_not: action link.

## Hand back
PR + sources + anything the official page did not state.
```

### P6 · Adapters from spike evidence

```markdown
# Task P6: Adapter — {tool}, plans {plans}
Issue: #{n} · Requirements: NFR-POR.1, NFR-REL.2, NFR-MAI.1 · Branch: agent/p6/{n}

## Goal
skill/reference/adapters/{tool}.yaml with flags set only from recorded spike results.

## Read first
- AGENTS.md
- docs/technical-architecture.md (capability model)
- docs/spike-results.md (section for {tool})
- knowledge/_schema/adapter.json

## Do
1. For each capability and plan, set yes, no or unknown from the spike evidence; link the evidence in notes.
2. Set fallbacks for every capability; set last_verified and verified_by from the spike record.
3. Update docs/spike-results.md summary table.

## Constraints
- No evidence → unknown. Never yes from documentation alone.

## Done when
- [ ] make validate passes; every yes has an evidence link.

## Hand back
PR + table of flags with evidence.
```

### P7 · Sheet templates and formulas

```markdown
# Task P7: Sheet templates
Issue: #{n} · Requirements: FR-2.1, FR-2.3, FR-5.1, FR-5.2, FR-8.3, NFR-REL.3 · Branch: agent/p7/{n}

## Goal
Template specs and formulas for Checklist, Budget, Dashboard and Log, which the setup script creates.

## Read first
- AGENTS.md
- docs/technical-architecture.md (data contracts, action links API)
- docs/student-skill.md (card templates: the numbers they need)

## Do
1. templates/checklist.md, budget.md: columns, types, validation lists, protected ranges.
2. Dashboard formulas: done/total per phase, overdue days, monthly totals, runway months, over-budget date. Use only built-in Sheets functions.
3. templates/index.md and profile.md with every field from the contracts; profile has no ID fields.
4. A formula test: known input rows → expected Dashboard values (as a script P8 can run against a test sheet).

## Constraints
- Data tabs and formula tabs separated so "Update template" never touches data.
- Template version recorded in index.md.

## Done when
- [ ] Every number a card shows has a named cell or range.
- [ ] Formula test cases cover empty, normal and over-budget months.

## Hand back
PR + list of named ranges.
```

### P8 · Action-link Apps Script

```markdown
# Task P8: Action-link web app and setup
Issue: #{n} · Requirements: FR-1.3, FR-1.4, FR-5.1, FR-8.1–8.5, FR-9.2, NFR-SEC.1–3, NFR-PRI.2, NFR-PER.1–2 · Branch: agent/p8/{n}

## Goal
The Apps Script project students deploy: setup, every action, Log, undo, token rotation and template update.

## Read first
- AGENTS.md
- docs/technical-architecture.md (action links API — follow exactly)
- docs/security-plan.md (controls C-A1 to C-A6, C-U1, C-U2)
- templates/ from P7

## Do
1. apps-script/: appsscript.json (V8, scopes: drive.file only; webapp executeAs USER_DEPLOYING, access MYSELF).
2. Setup: create Journey folder and files from templates; random 128-bit token; write index.md; load tasks for the student's phases.
3. doGet router: v, a, k, n, src, params; whitelist; constant-time token compare; nonce idempotency via Log; LockService; HTML-escaped result page with Undo; fmt=text for status.
4. Actions: done, undo, add_task, expense, study, phase, ics, status, handover, revert. Sheet menu: Rotate link key, Update template.
5. Unit tests with an Apps Script mock: happy path, replay, bad token, missing and malformed params, oversized input, escaping, concurrent same nonce.

## Constraints
- No other scopes, libraries, URL fetches or triggers.
- No personal data in logs (console) — only action names and outcomes.
- status and handover output never include ID numbers.

## Done when
- [ ] All tests pass; manifest check passes.
- [ ] Setup completes in under 60 s on the test account (record the time).

## Hand back
PR + test report + deployment notes for maintainers.
```

### P9 · Student skill

```markdown
# Task P9: Student skill — SKILL.md, intents, cards
Issue: #{n} · Requirements: F1–F12 Musts in docs/requirements.md · Branch: agent/p9/{n}

## Goal
The germany-companion skill: core routing, ten intent files, card templates and action-link instructions.

## Read first
- AGENTS.md
- docs/student-skill.md (layout, intents, specs, cards, skeleton — follow it)
- docs/ai-guardrails.md (paste the guardrail block verbatim)
- docs/technical-architecture.md (capability model, action links)

## Do
1. skill/SKILL.md from the skeleton, with the guardrail block at the top.
2. skill/reference/intents/*.md: one per intent, each with reads, does, shows, fallback, and 2 example exchanges.
3. skill/reference/cards.md (8 templates), action-links.md, data-contracts.md.
4. Run make validate and make evals-smoke.

## Constraints
- No city, university or tool names anywhere in skill/ (lint enforces it).
- Size budgets: SKILL.md ≤ 400 lines; intents ≤ 150 lines each.
- Examples use invented students and places like "Example City".

## Done when
- [ ] Lint passes; smoke evals pass on the local build.
- [ ] Every Must FR maps to an intent section (table in the PR).

## Hand back
PR + FR → intent mapping table.
```

### P10 · Eval harness and cases

```markdown
# Task P10: Evals — {set}
Issue: #{n} · Requirements: NFR-ACC.3 and the rules in {set} · Branch: agent/p10/{n}

## Goal
Eval cases for {set} and (first run only) the harness that runs and scores them per tool.

## Read first
- AGENTS.md
- docs/ai-guardrails.md (evaluation and red-team set)
- knowledge/_schema/eval-case.json
- .claude/skills/eval-writer/SKILL.md

## Do
1. First run: scripts/run_evals.py — loads a per-tool build, runs cases through an API where configured, otherwise writes a manual checklist; scores must/must_not; writes evals/results/<release>/<tool>.md; exits non-zero on any zero-tolerance failure.
2. Write {count} cases for {set}, each tagged with rule or FR IDs.

## Constraints
- Expected behaviour comes from the docs, never from a model's output.
- No API keys in the repo; read from environment variables.

## Done when
- [ ] Cases validate; harness runs end to end on the local build.

## Hand back
PR + case count by rule + a sample results file.
```

## Release, security and phase 2 prompts

These touch publishing and credentials, so agents prepare and maintainers switch things on.

### P11 · Release workflow

```markdown
# Task P11: Release workflow
Issue: #{n} · Requirements: NFR-SEC.4, NFR-ACC.2 · Branch: agent/p11/{n}

## Goal
A release workflow that builds from a signed tag and publishes to all channels only after maintainer approval.

## Read first
- AGENTS.md
- docs/release-management.md (all of it)
- docs/security-plan.md (C-R3, C-R8)
- .github/workflows/ from P3

## Do
1. release.yml on tags v*: verify tag signature; rebuild from the tag; run validate and fail on expired entries; attach artefacts with SHA-256 checksums and build provenance; publish packs to the Drive folder and latest.json to Pages in a job bound to the production environment.
2. scripts/changelog.py: Conventional Commits → CHANGELOG.md sections incl. Facts with entry IDs.
3. A dry-run mode that does everything except publish.
4. docs/runbooks/release.md and hotfix.md from the release doc.

## Constraints
- Use only the secret names listed in the doc; never print them; least-privilege job permissions.
- critical in latest.json requires a workflow input set by a maintainer.

## Done when
- [ ] Dry run on a test tag succeeds and shows what would publish.

## Hand back
PR + dry-run log + secrets and environment settings a maintainer must create.
```

### P12 · Security hardening

```markdown
# Task P12: Security hardening review
Issue: #{n} · Requirements: NFR-SEC.1–4, NFR-PRI.1–4 · Branch: agent/p12/{n}

## Goal
Check the repo against every control in the security plan and fix what an agent may fix.

## Read first
- AGENTS.md
- docs/security-plan.md
- docs/ai-guardrails.md (untrusted input)

## Do
1. For each control C-S1…C-R8, record: implemented where (file/line or setting), missing, or not agent-fixable.
2. Fix agent-fixable gaps (e.g. unpinned actions, missing tests, scope checks, escaping).
3. Add 15 prompt-injection eval cases if fewer exist.

## Constraints
- Do not change settings, secrets or CODEOWNERS; list them for maintainers.

## Done when
- [ ] Control table complete; fixes have tests.

## Hand back
PR + control table + maintainer action list.
```

### P13 · MCP server on Cloudflare Workers (phase 2)

```markdown
# Task P13: Read-only MCP server for packs
Issue: #{n} · Requirements: phase 2 · Branch: agent/p13/{n}

## Goal
A stateless remote MCP server on Cloudflare Workers that serves public pack data to MCP-capable tools.

## Read first
- AGENTS.md
- docs/tech-stack-development.md (phase 2 stack)
- docs/technical-architecture.md (knowledge pipeline, versioning)
- build/packs/ output format

## Do
1. mcp/: TypeScript Worker using the MCP TypeScript SDK (or Cloudflare's Agents SDK), Streamable HTTP transport.
2. Tools: search_packs(query, scope), get_entry(id), get_versions(), get_letter(type). Every response includes source_url and last_verified.
3. Pack JSON bundled as static assets at build; no database, no writes, no auth needed.
4. Rate limiting binding; logs without request bodies.
5. Contract tests with vitest and the Workers runtime; wrangler.toml; Terraform for route, custom domain and WAF rules (plan only).

## Constraints
- No personal data, no cookies, no analytics beyond Workers defaults.
- Do not deploy; a maintainer runs the first deploy.

## Done when
- [ ] Tests pass locally; p95 under 300 ms in a local load test.
- [ ] adapter flag mcp stays unknown until verified per tool.

## Hand back
PR + test report + deploy steps for a maintainer.
```

## Reviewer agent prompt

Run this on every agent PR before a maintainer looks at it; use a different agent session from the one that wrote the PR, so the work isn't grading itself.

```markdown
# Review: PR #{number}

You are reviewing a pull request for the Germany Student Companion. You did not write it. Be specific and strict; approve nothing (you can't), only report.

## Read first
- AGENTS.md
- The task prompt in the linked issue
- The docs it lists under "Read first"
- The full diff and the CI results

## Check, in this order
1. Scope: does the PR do exactly the task, nothing more? List anything out of scope.
2. Non-negotiable rules in AGENTS.md: list each one the diff touches and whether it holds.
3. Facts: for each changed pack entry, open the source_url and confirm the fact. Mark confirmed, wrong (with the correct text and quote) or unverifiable.
4. Contracts: any field renamed or removed in packs, adapters, templates, index.md, profile.md or the action-link API? If yes, is there a major version, migration and ADR?
5. Security and privacy: scopes, secrets, personal data in fixtures or logs, unescaped output, links built from content, missing token or nonce checks.
6. Tests: does each behaviour change have a test or eval that would fail without it?
7. Student text: plain English B1, German terms explained, disclaimer and referral where needed, no tool or place names in skill/.
8. Done when: tick each criterion from the task prompt with evidence.

## Report format
- Verdict: ready for maintainer / changes needed / blocked
- Must fix (with file:line and suggested change)
- Should fix
- Facts table: entry id · status · note
- Done-when checklist with evidence
```
