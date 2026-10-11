# Germany Student Companion — Developer Skills

Oct 10, 2026 · @Ajeet Chouksey

## Purpose

Developer skills are the repeatable jobs we hand to an AI agent while building the companion: writing pack entries, reviewing them, testing tools, running evals, releasing. Each one turns a project rule (sourced facts, no tool names, fallbacks for every capability) into steps the agent follows the same way every time.

- **Where they live:** `.claude/skills/<name>/SKILL.md` in the repo, with helper scripts beside them. Claude Code picks them up automatically; the same files work as instructions for any agent.
- **Who uses them:** maintainers and pack contributors, in VS Code with Claude Code.
- **What they never do:** merge, release or publish on their own. Every skill ends in a pull request or a report that a person approves.
- **Separate from the student skill:** nothing in `.claude/skills/` ships to students; the student skill lives in `skill/` and has its own doc.

## Skill catalogue

Ten skills cover the whole build loop; three are needed in week 1.

| Skill | Job | Trigger | Output | Needed from |
| --- | --- | --- | --- | --- |
| `pack-author` | Draft pack entries from official sources | "Add Kiel Anmeldung facts" | PR with YAML entries + source notes | Week 1 |
| `pack-reviewer` | Check each entry against its source | PR touching `knowledge/` | Review comment: confirmed, changed, or unclear per entry | Week 1 |
| `letter-pack` | Build a letter-type entry from a redacted sample | "Add the Rundfunkbeitrag letter" | Letter YAML + eval cases | Week 2 |
| `adapter-verifier` | Run spike tests on a tool and plan, record flags | "Verify Claude free" | Updated adapter YAML + `spike-results.md` section | Week 1 |
| `eval-writer` | Write factual and guardrail eval cases | New pack entries or rules | `evals/` YAML cases | Week 2 |
| `eval-runner` | Run evals per tool and plan, score them | Before G3, every release | `evals/results/<release>/<tool>.md` | Week 4 |
| `skill-builder` | Lint `SKILL.md`, build per-tool packages, check size limits | "Build release" | Skill zips + lint report | Week 4 |
| `apps-script-dev` | Implement and test action-link actions | "Add the handover action" | Code + unit tests + scope check | Week 3 |
| `release-manager` | Versions, changelog, `latest.json`, `critical` notices | Release tag | Release PR for maintainer approval | Week 4 |
| `freshness-triage` | Work through expiring-entry issues | Weekly freshness issue | PRs re-verifying or retiring entries | Week 2 |

## Skill specs

Each spec lists what the skill needs, what it does, what it hands back, and the rule it must never break.

### pack-author

- **Needs:** topic, layer, scope (e.g. `city`, `kiel`), phase; official URLs if known.
- **Steps:** read `_schema/fact.json` and existing entries for the topic → fetch official pages (city, state, university, federal sites first) → draft one entry per fact in plain B1 English → set `last_verified` to today, `reviewer` empty → open a PR with a source note per entry (quoted line under 15 words, page section).
- **Hands back:** PR + list of facts it could not source.
- **Never:** add a fact without an official `source_url`; use blogs or forums as a source.

### pack-reviewer

- **Needs:** a PR touching `knowledge/`.
- **Steps:** for each changed entry, open the source, compare fact by fact, check layer and scope, check plain English and German-term explanation → mark confirmed, changed (with fix) or unclear.
- **Hands back:** PR review; sets `reviewer` only when a human approves.
- **Never:** approve its own author's PR or self-assign as reviewer.

### letter-pack

- **Needs:** a redacted sample letter (no names, numbers, addresses) and the sender's official page.
- **Steps:** identify sender and type → write letter entry (sender list, what it means, usual deadline, next step, cost of missing it, referral) → write 3 eval cases incl. one scam variant.
- **Never:** keep any personal detail from the sample in the repo.

### adapter-verifier

- **Needs:** tool, plan, test account, the spike checklist.
- **Steps:** walk each test (import, links, Drive read, Gmail by sender, Calendar, URL fetch, charts, file limits, switching) with the person at the device → record yes/no/notes with evidence (screenshot name) → update the adapter YAML and `last_verified`.
- **Hands back:** adapter PR + `docs/spike-results.md` section.
- **Never:** mark `yes` without a recorded successful run.

### eval-writer

- **Needs:** new pack entries, letter types or guardrail rules.
- **Steps:** per entry, one direct and one tricky question with `must` and `must_not`; per rule, cases in the guardrail sets; tag each case with rule IDs.
- **Never:** copy expected answers from the model under test.

### eval-runner

- **Needs:** release candidate, tool, plan.
- **Steps:** load the per-tool build → run cases (API where possible, else produce a manual checklist) → score against `must`/`must_not` → flag zero-tolerance failures.
- **Hands back:** results file + pass/fail summary for the gate.

### skill-builder

- **Needs:** `skill/`, adapters, packs.
- **Steps:** lint `SKILL.md` (no city, university or tool names; guardrail block present) → generate bundled snapshot → build one package per tool → check size against each adapter's limits.
- **Never:** hand-edit generated files.

### apps-script-dev

- **Needs:** action spec from the architecture doc.
- **Steps:** write the handler with whitelist, token, nonce, lock and Log → unit tests (replay, malformed input, escaping) → `clasp push` to a test project → manifest scope check.
- **Never:** add a scope beyond `drive.file`.

### release-manager

- **Needs:** merged changes since the last tag.
- **Steps:** bump versions by the rules → changelog in plain words → `latest.json` draft; `critical` only with a linked incident → open release PR.
- **Never:** tag or publish; a maintainer does that.

### freshness-triage

- **Needs:** the weekly freshness issue.
- **Steps:** for each expiring entry, recheck the source → if unchanged, bump `last_verified` in a PR for review → if changed, hand to `pack-author` → if gone, propose retiring the entry.
- **Never:** bump a date without opening the source.

## Toolchain

The skills call ordinary, scriptable tools so the same checks run locally and in CI. Versions get pinned when the repo is created.

| Tool | Used by | Role |
| --- | --- | --- |
| Claude Code in VS Code | All skills | Runs the skills; web fetch for sources |
| GitHub CLI (`gh`) | pack-author, release-manager, freshness-triage | PRs, reviews, issues |
| JSON Schema validator (e.g. `ajv-cli`) | pack-author, skill-builder, CI | Packs, adapters, eval cases |
| `yamllint` | All pack skills, CI | YAML style |
| Link checker (e.g. `lychee`) | pack-reviewer, freshness-triage, CI | `source_url` health |
| `scripts/lint_skill.py` | skill-builder, CI | No place or tool names; guardrail block present |
| `scripts/build.py` | skill-builder, CI | Snapshot, per-tool zips, `latest.json` |
| `scripts/run_evals.py` | eval-runner | API runs where available; manual checklist otherwise |
| `clasp` + a test runner for Apps Script | apps-script-dev | Push, deploy to a test project, unit tests |
| GitHub Actions | CI | Validate, freshness job, evals, release |

The three `scripts/` files are ours to write in week 1–2; everything else is off-the-shelf.

## Example: pack-author SKILL.md

The first skill to write, ready to commit as `.claude/skills/pack-author/SKILL.md`; the others follow the same shape.

```markdown
---
name: pack-author
description: Draft sourced knowledge-pack entries for the Germany Student Companion. Use when asked to add or update facts for a topic, layer (national, state, city, university) or letter type.
---

# Pack author

## Before you start
1. Read knowledge/_schema/fact.json and every existing entry for the topic in all layers.
2. Confirm topic, layer, scope and phase with the requester if any is missing.

## Sources
- Use official sources only: federal, state, city and university sites, the AStA, the Studierendenwerk.
- Never use blogs, forums, agencies or AI answers as a source_url.
- If no official source states the fact, do not write the entry. List it under "Could not source".

## Writing entries
- One fact per entry. id = <scope>.<topic>.<slug>.
- Plain English at B1. Short sentences. Explain German terms the first time.
- No personal data, no example names or numbers from real people.
- Set last_verified to today. Leave reviewer empty.
- Set expires to 6 months ahead, or sooner if the source says the rule changes.
- Use the most specific layer that the source covers. Don't copy a national fact into a city file.

## Checks before the PR
- Run: ajv validate -s knowledge/_schema/fact.json -d <changed files>
- Run: yamllint knowledge/
- Run: lychee <changed files>

## Pull request
- Title: "packs(<scope>): <topic>"
- Body: one line per entry with its source_url and a quote under 15 words showing the fact.
- Section "Could not source" with each missing fact and where you looked.
- Request review from the CODEOWNERS for that layer. Never approve or merge.
```

## Build order

Each skill is written just before the week that first needs it, and tested on one real task before it is trusted.

| Week | Write these skills | First real task |
| --- | --- | --- |
| 1 (12–18 Oct) | `pack-author`, `pack-reviewer`, `adapter-verifier` | National Anmeldung entries; Gemini free spike run |
| 2 (19–25 Oct) | `letter-pack`, `eval-writer`, `freshness-triage` | Rundfunkbeitrag letter; first 20 eval cases |
| 3 (26 Oct–1 Nov) | `apps-script-dev` | `expense` and `handover` actions with tests |
| 4 (2–8 Nov) | `skill-builder`, `eval-runner`, `release-manager` | Release candidate for G3 |

After the pilot, the useful ones get proposed to the shared skills library so other city teams can reuse them.
