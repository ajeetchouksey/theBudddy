# Security policy

The Germany Student Companion holds no personal data on project infrastructure. Student data lives only in each student's own Google account. Most security issues will therefore be about the release pipeline, the action-link script, prompt-injection bypasses or wrong content.

## Reporting a vulnerability

Please **do not open a public issue.** Use GitHub private vulnerability reporting:
**Security → Report a vulnerability** on this repository.

Include what you found, how to reproduce it, and the release or commit. Never send real student data; invented examples are enough.

## What to expect

- **Acknowledgement within 72 hours.**
- Triage in a private security advisory with a severity:

| Severity | Example | Fix released |
| --- | --- | --- |
| S1 Critical | Release leaks tokens, script writes wrongly, maintainer account taken over | 24 h |
| S2 High | Wrong deadline or fee that could cost money or status | 48 h |
| S3 Medium | Injection bypass found in evals; minor wrong fact | Next release |
| S4 Low | Hardening gap, typo in a source | Next release |

- Students are told through the `critical` notice in `latest.json` and the pilot group when they need to act (for example, rotate their link key).
- **Credit** for reporters in the advisory and release notes, unless you prefer to stay anonymous.

## Scope

In scope: this repository, its GitHub Actions, released skill packages, the Apps Script template, `latest.json` and the public packs folder.

Out of scope: the AI apps themselves (Gemini, Claude, Copilot) and Google services. Report those to their vendors.

Full plan: `docs/security-plan.md`.
