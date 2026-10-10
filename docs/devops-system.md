# Germany Student Companion — DevOps and Engineering System

Oct 10, 2026 · @Ajeet Chouksey

## Principles

A small team plus AI agents can ship safely only if the repo itself enforces the rules; people review intent, machines check everything else.

1. **Trunk-based, small changes.** Short-lived branches, PRs under about 400 changed lines, merged within two days.
2. **Everything as code.** Packs, adapters, templates, evals, CI, repo settings and Cloudflare config live in Git.
3. **Gates, not heroics.** If a rule matters (sources, scopes, no tool names, fallbacks), CI enforces it.
4. **Agents draft, humans decide.** Agents open PRs; only maintainers merge, tag and publish.
5. **Facts are code.** A fact change gets the same review, tests and changelog as a code change.
6. **Measure the student outcome.** Pilot feedback and eval results drive the backlog, not feature ideas.
7. **Write it down.** Decisions as ADRs, how-tos in `docs/`, everything linked from the README.

## Repository conventions

One repo, one `main`, everything else is a short-lived branch.

**Branches**

| Pattern | Used for | Who |
| --- | --- | --- |
| `feat/<issue>-<slug>` | Features and code changes | People and agents |
| `packs/<scope>-<topic>` | Fact changes | People and agents |
| `fix/<issue>-<slug>` | Bug fixes | People and agents |
| `agent/<skill>/<issue>` | Any agent-created branch (prefix wins over the above) | Agents only |
| `hotfix/<issue>` | From the last stable tag | Maintainers |

**Commits:** Conventional Commits with scopes: `feat(skill)`, `fix(script)`, `packs(kiel)`, `ci`, `docs`, `chore`. Breaking changes use `!` and need an ADR link.

**Pull requests:** template with What and why · Linked issue · Facts changed (IDs + sources) · Data contracts touched (yes/no) · Tests and evals run · Screenshots for cards or setup pages · AI-generated (yes/no, which skill).

**Labels:** `type:*` (feature, bug, facts, docs, chore) · `area:*` (packs, skill, script, templates, ci, mcp) · `layer:*` (national, state, city, university) · `tool:*` (gemini, claude, copilot) · `priority:*` (must, should, could) · `ai-generated` · `needs-source` · `pilot-feedback`.

**CODEOWNERS**

```
/knowledge/national/      @ajeetchouksey @<national-reviewer>
/knowledge/states/        @<state-reviewer>
/knowledge/cities/kiel*   @<kiel-verifier>
/knowledge/universities/  @<cau-verifier>
/skill/                   @ajeetchouksey
/skill/reference/adapters @ajeetchouksey
/apps-script/             @ajeetchouksey @<second-maintainer>
/.github/                 @ajeetchouksey @<second-maintainer>
```

## Work management

GitHub Issues and one GitHub Project board; milestones match the weekly release train.

**Board columns:** Inbox → Ready → In progress → In review → Done. Milestones: `v0.1.0` … `v1.0.2`.

**Issue types (templates)**

| Type | Template asks for | Default labels |
| --- | --- | --- |
| Feature | Requirement IDs (FR/NFR), acceptance criteria, tools affected | `type:feature` |
| Facts | Topic, layer, scope, official source URL | `type:facts`, `needs-source` until a source is attached |
| Bug | Tool and plan, steps, expected vs actual, Log row if relevant (no personal data) | `type:bug` |
| Pilot feedback | Student code (P01–P10), what happened, quote in their words | `pilot-feedback` |
| Spike result | Test number, tool, plan, result, evidence | `area:skill` |

**Definition of ready**

- Linked to a requirement ID or pilot feedback.
- Acceptance criteria are testable.
- For facts: an official source is attached.
- For agents: the task prompt is written (see the Dev Agent Instructions doc).

**Definition of done**

- PR merged with all gates green and the right CODEOWNER approval.
- Tests or evals added for the change.
- Docs, changelog entry and, where needed, an ADR updated.
- For facts: `reviewer` set by a human.
- Works on the floor of all three tools, or the adapter fallback is set.

## Quality gates

Every check below is automated and blocking unless marked review; the release gates add the evals and smoke tests from Release Management.

| Gate | Checks | Applies to | Blocking |
| --- | --- | --- | --- |
| Format | `yamllint`, `ruff`, Prettier for JS and HTML | All PRs | Yes |
| Schema | Packs, adapters, eval cases, `latest.json` | All PRs | Yes |
| Content rules | `source_url`, `last_verified`, `reviewer` set on merge; no expired entries; official-domain allowlist for sources | `knowledge/` | Yes |
| Skill rules | No city, university or tool names in `SKILL.md`; guardrail block present; file size budget | `skill/` | Yes |
| Adapter rules | Every capability has a fallback; `last_verified` within 90 days | Adapters | Yes |
| Script rules | Unit tests pass; manifest scopes = `drive.file` only; no external libraries | `apps-script/` | Yes |
| Security | Secret scanning, CodeQL on JS and Python, Dependabot alerts, Actions pinned to SHAs | All PRs | Yes for high/critical |
| Links | `lychee` on changed files | All PRs | Yes for `source_url`; warning elsewhere |
| Fact diff | Comment listing old → new values per entry | `knowledge/` | Review |
| Human review | CODEOWNER approval | All PRs | Yes |
| Release | Evals per tool, smoke script, compatibility check with previous minor | Release PR | Yes |

## Testing strategy

The model can't be unit-tested, so we test everything around it hard and test the model's behaviour with evals.

| Layer | Test type | Tool | When | Target |
| --- | --- | --- | --- | --- |
| Packs | Schema, rules, links | `ajv`, `yamllint`, `lychee` | Every PR | 100% pass |
| Build scripts | Unit tests | `pytest` | Every PR | ≥ 80% line coverage |
| Action-link script | Unit tests with an Apps Script mock (Drive, Sheets, Lock, Properties) | `jest` or `vitest` | Every PR | Every action: happy path, replay, bad token, malformed params, escaping |
| Sheet templates | Formula tests: known inputs → known Dashboard values | Script against a test sheet | Before each release | Runway and totals exact |
| Skill behaviour | Factual evals (50) + guardrail evals (80) | `run_evals.py`, manual checklist | Release candidates | ≥ 45/50; zero-tolerance sets pass |
| End to end | Smoke script per tool: setup → done → expense → undo → status → handover → switch | Manual, 15 min per tool | Release candidates | All steps pass |
| Compatibility | New skill against previous template and script | Test Journey from the last release | Release candidates | No errors, no data loss |
| Phase 2 MCP | Contract tests per tool name; load test | `vitest` + Workers local runtime | Before deploy | p95 < 300 ms at edge |

## Feedback loop and metrics

We have no telemetry by design, so feedback comes from people and from the pipeline. Everything flows into GitHub issues.

**Inputs**

- Pilot weekly chats → `pilot-feedback` issues (pseudonymised P01–P10).
- Questions the companion couldn't answer: students say "send this to the team", the companion offers a prefilled issue link with the question text only (no profile data).
- "This looks wrong" reports → `type:facts` bug with the entry ID.
- Eval and freshness runs → issues opened by CI.

**Engineering metrics (reviewed every Friday at the release cut)**

| Metric | Target during the pilot |
| --- | --- |
| Lead time, merged PR → stable release | ≤ 7 days; facts ≤ 48 h |
| Change failure rate (releases needing a hotfix) | ≤ 1 in 3 |
| Time to fix a reported wrong fact | ≤ 48 h |
| Eval pass rate, factual / guardrail | ≥ 90% / 100% zero-tolerance |
| Open `needs-source` issues | Falling week on week |
| Entries within 30 days of expiry | 0 untriaged |

## Working agreement for AI agents

Agents are welcome contributors with a narrower lane than people. These rules go into `AGENTS.md` and are enforced by branch protection and CODEOWNERS.

| Agents may | Agents may not |
| --- | --- |
| Create `agent/*` branches and open PRs | Push to `main`, merge, tag, publish or approve PRs |
| Run local tests, linters, schema checks, evals | Change branch protection, CODEOWNERS, workflows' permissions or secrets |
| Fetch official web pages for sources | Use unofficial sources, or invent a source URL |
| Draft facts, code, tests, docs, ADR drafts | Set `reviewer` on a pack entry |
| Propose adapter flags from recorded spike evidence | Mark a capability `yes` without evidence |
| Comment on issues and PRs | Add OAuth scopes, external libraries to the script, or new services |

**Every agent PR** carries the `ai-generated` label, names the skill or prompt used, lists the commands it ran with results, and states anything it could not do. One task per PR.

**When stuck:** stop, write what was tried and what is missing in the PR or issue, and ask; never guess past a missing source, credential or decision.
