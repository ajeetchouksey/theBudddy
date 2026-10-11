# ADR 0012: Students use the vendors' own apps; AI CLIs are maintainer tooling only

- **Status:** Accepted
- **Date:** 2026-10-11

## Context

We asked whether students could chat with the companion through the vendors' command-line
tools (Claude Code, Gemini/Antigravity CLI, GitHub Copilot CLI), wrapped in our own tooling,
instead of opening Gemini, Claude or Copilot.

Findings (checked 11 Oct 2026):

- **Claude Code** needs a Pro, Max, Team, Enterprise or Console account; the free Claude plan
  does not include it. Anthropic does not permit third-party products to offer Claude.ai login
  or to route requests through a user's Free, Pro or Max credentials; products built on Claude
  use API keys. ([setup](https://code.claude.com/docs/en/setup),
  [legal and compliance](https://code.claude.com/docs/en/legal-and-compliance))
- **Gemini CLI** stopped serving free and individual accounts on 18 June 2026; Google moved
  them to Antigravity CLI. Official free-tier limits for Antigravity CLI were not published
  where we looked. ([discussion #28017](https://github.com/google-gemini/gemini-cli/discussions/28017),
  [discussion #27274](https://github.com/google-gemini/gemini-cli/discussions/27274))
- **Copilot:** only GitHub Copilot has a CLI and SDK (available on Copilot Free with a GitHub
  account). The consumer Microsoft Copilot that students use has no CLI.
  ([GitHub changelog](https://github.blog/changelog/2026-06-02-copilot-sdk-is-now-generally-available/))
- All CLIs run on desktops with a terminal. Students mostly use phones.

## Decision

Students use the companion inside the vendors' own apps (web and mobile), as designed. We do
not build, host or distribute a CLI-based chat for students.

Maintainers may use the CLIs in project tooling, first for automated eval runs
(`scripts/run_evals.py`, task P10), on their own accounts.

## Consequences

- Rules kept: free plans are the floor (ADR 0008), three-action setup, no personal data on
  project servers (ADR 0001), reads through native connectors (ADR 0011).
- Evals can run headless per tool, which cuts manual work before each release. CLI runs test
  the skill's content and guardrails, not the consumer app: the floor smoke test per tool stays
  manual.
- Revisit if a vendor offers a free, phone-friendly, officially supported way for third-party
  tools to use a student's own consumer account.
