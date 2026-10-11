# Contributing

Thanks for helping international students settle in Germany. This guide is the short version of `docs/devops-system.md`.

## Principles

- **Small changes.** Short-lived branches, PRs under about 400 changed lines, merged within two days.
- **Facts are code.** A fact change gets the same review, tests and changelog as a code change.
- **Gates, not heroics.** If a rule matters, CI checks it. Run `make validate && make test` before you push.
- **Agents draft, humans decide.** Agents open PRs; only maintainers merge, tag and publish. Agents read `AGENTS.md` first.

## Set up

```sh
python3 -m pip install -r requirements-dev.txt
npm install          # Prettier and the Apps Script test runner
make validate test
```

## Branches

| Pattern | Used for |
| --- | --- |
| `feat/<issue>-<slug>` | Features and code changes |
| `packs/<scope>-<topic>` | Fact changes |
| `fix/<issue>-<slug>` | Bug fixes |
| `agent/<skill>/<issue>` | Any agent-created branch |
| `hotfix/<issue>` | From the last stable tag (maintainers) |

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) with scopes: `feat(skill)`, `fix(script)`, `packs(kiel)`, `ci`, `docs`, `chore`. Breaking changes use `!` and need an ADR link.

## Adding or changing facts

1. Open a **Facts** issue with the official source.
2. Use the `pack-author` skill, or follow `.claude/skills/pack-author/SKILL.md` by hand.
3. Official sources only (federal, state, city and university sites, AStA, Studierendenwerk). Never blogs, forums, agencies or AI answers.
4. Leave `reviewer` empty. A human reviewer for that layer sets it. Until then the `ready-to-merge` check stays red; that is expected.

## Pull requests

Fill in the template: what and why, linked issue and requirement IDs, facts changed with sources, data contracts touched, tests and evals run, AI-generated or not.

### Definition of done

- All gates green and the right CODEOWNER approval.
- Tests or evals added for the change.
- Docs, changelog entry and, where needed, an ADR updated.
- For facts: `reviewer` set by a human.
- Works on the floor of all three tools, or the adapter fallback is set.

## Rules that never bend

1. No personal data in the repo: not in packs, tests, fixtures, examples or logs.
2. No city, university or AI tool names in `skill/SKILL.md` or intent files.
3. Apps Script uses only the `drive.file` scope and no external libraries.
4. Every write goes through an action link (token, nonce, Log).

## Labels

`type:*` (feature, bug, facts, docs, chore) · `area:*` (packs, skill, script, templates, ci, mcp) · `layer:*` (national, state, city, university) · `tool:*` (gemini, claude, copilot) · `priority:*` (must, should, could) · `ai-generated` · `needs-source` · `pilot-feedback`.
