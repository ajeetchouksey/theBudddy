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
