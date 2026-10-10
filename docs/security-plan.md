# Germany Student Companion — Security Plan (MVP 1)

Oct 10, 2026 · @Ajeet Chouksey

## Objectives and scope

The plan's goal is that no student loses data, money or a deadline because of the companion, and that the project never holds personal data it could leak. It covers MVP 1 up to the pilot review on 23 November 2026.

**In scope:** the GitHub repo and CI, released artefacts (skill builds, adapters, packs, `latest.json`), the action-link Apps Script template and its deployments in student accounts, the skill's behaviour inside Gemini, Claude and Copilot, and the pilot process.

**Out of scope:** security of the AI providers, Google and Microsoft themselves; the student's device and account hygiene beyond what we advise.

**Principles**

1. **Hold nothing worth stealing.** No backend, no personal data, no secrets in project infrastructure.
2. **Least privilege.** `drive.file` only; reads through the student's own connectors; no scopes we don't need.
3. **Human in the loop for writes.** The AI proposes, the student taps; nothing writes on the model's say-so.
4. **Untrusted inputs stay data.** Mail, letters, web pages and pack text never become instructions.
5. **Integrity over secrecy for content.** Packs are public; what matters is that only reviewed content ships.
6. **Fail safe and visible.** Fallbacks never widen access; errors say what happened in plain words.

## Assets and trust boundaries

The most valuable assets sit in the student's account; the project's own assets matter because they shape what every student is told.

| Asset | Where | Owner | Impact if compromised |
| --- | --- | --- | --- |
| Checklist, Budget, Log, `profile.md` | Student's Drive | Student | High: wrong deadlines, lost money tracking, privacy loss |
| Letters and documents | Student's Drive, Gmail | Student | High: personal and official data |
| Action-link token + web-app URL | `index.md` | Student | Medium: crafted writes, limited by Only-myself access |
| Knowledge packs | GitHub, public Drive folder | Project | High: wrong facts reach every student |
| Skill builds and adapters | GitHub releases | Project | High: changed behaviour, data leak instructions |
| `latest.json` | GitHub Pages | Project | Medium: false or suppressed urgent notices |
| Apps Script template | GitHub, clasp | Project | High: runs with the student's Drive rights |
| Maintainer accounts | GitHub, Google | Maintainers | Critical: root of all the above |

**Trust boundaries**

| # | Boundary | Crossing | Trust rule |
| --- | --- | --- | --- |
| B1 | Project → AI tool | Skill, adapters, bundled packs imported by the student | Trusted only if from a signed release |
| B2 | Internet → AI tool | Mail, letters, pasted text, web pages | Untrusted data, never instructions |
| B3 | AI tool → student | Answers, action links | Student reviews before tapping |
| B4 | Browser → Apps Script | Action-link request | Authenticated (Google sign-in) + token + nonce + validation |
| B5 | AI tool ↔ Google | Connector reads (and flagged writes) | Granted by the student to their tool; we are not a party |
| B6 | Contributor → repo | Pull requests to packs, skill, script | Untrusted until reviewed by CODEOWNERS and CI |

## Threat model

14 threats, 3 rated high before controls; prompt injection and a compromised maintainer account are the two that remain medium after them. Risk = likelihood × impact (L/M/H), shown before → after controls.

| ID | Component | STRIDE | Threat | Risk | Controls (section 4–5) |
| --- | --- | --- | --- | --- | --- |
| T1 | AI tool + skill | Tampering | Prompt injection in a letter or email makes the AI propose harmful links or advice | H → M | C-S1, C-S2, C-S3 |
| T2 | AI tool + skill | Info disclosure | Injected text tells the AI to reveal `index.md` token or profile in a reply or link | M → L | C-S2, C-A1, C-A3 |
| T3 | Action-link app | Spoofing | A third party crafts a link and tricks the student into tapping it | M → L | C-A1, C-A2, C-A5 |
| T4 | Action-link app | Tampering | Link preview or prefetch triggers a write | M → L | C-A1, C-A3 |
| T5 | Action-link app | Repudiation | Student cannot tell which change came from which tool | L → L | C-A4 |
| T6 | Action-link app | Elevation | Template asks for broader scopes than needed | M → L | C-A6, C-R4 |
| T7 | Action-link app | Denial of service | Malformed or huge params break sheets or hit quotas | L → L | C-A5 |
| T8 | Packs | Tampering | Malicious or careless PR ships a wrong fee, deadline or office | H → L | C-R1, C-R2, C-R5 |
| T9 | Packs | Tampering | Stale fact stays live after a rule change | M → L | C-R5, C-R6 |
| T10 | Repo / CI | Tampering | Compromised GitHub Action or dependency alters builds | M → L | C-R3, C-R4 |
| T11 | Maintainers | Spoofing | Maintainer GitHub or Google account taken over | H → M | C-R7 |
| T12 | `latest.json` | Tampering | Fake `critical` notice or a suppressed real one | L → L | C-R3, C-R8 |
| T13 | Student account | Info disclosure | Journey folder shared by mistake, or token pasted in a public place | M → L | C-U1, C-U2 |
| T14 | Connectors | Info disclosure | AI tool reads more mail or files than needed | M → L | C-S4, C-U3 |

## Controls by layer

Thirteen runtime controls across three layers; the action-link app carries the most because it is the only code that writes.

**Skill and AI behaviour**

| ID | Control | Mitigates |
| --- | --- | --- |
| C-S1 | `SKILL.md` rule: content from mail, letters, files and web is data; instructions inside it are ignored and flagged to the student | T1 |
| C-S2 | Links only from a fixed template (base URL from `index.md`, whitelisted action and params); never a URL taken from content | T1, T2 |
| C-S3 | Facts only from packs; money and deadlines only from sheets; legal topics with disclaimer and referral | T1 |
| C-S4 | Gmail searched only by the known sender list; Drive reads limited to the Journey folder | T14 |

**Action-link app (Apps Script)**

| ID | Control | Mitigates |
| --- | --- | --- |
| C-A1 | Deployed as "Execute as me, access Only myself"; previews and other users cannot run it | T2, T3, T4 |
| C-A2 | Token (128-bit random) checked in constant time on every request | T3 |
| C-A3 | Nonce idempotency stored in Log; a write needs a fresh nonce | T2, T4 |
| C-A4 | Log with before, after, tool and timestamp; `revert` by nonce | T5 |
| C-A5 | Whitelist of actions and params; types, lengths, EUR amounts, ISO dates; `LockService` on writes; output HTML-escaped | T3, T7 |
| C-A6 | Manifest declares `drive.file` only; CI fails on any added scope | T6 |

**Student account and guidance**

| ID | Control | Mitigates |
| --- | --- | --- |
| C-U1 | Journey folder created private; setup warns never to share it or `index.md` | T13 |
| C-U2 | "Rotate my link key" menu item; skill suggests it if the token appears outside Drive | T13 |
| C-U3 | Onboarding explains which Google access each tool gets and how to revoke it | T14 |

## Supply chain and content integrity

Eight repo and release controls make sure only reviewed code and facts reach students.

| ID | Control | Mitigates |
| --- | --- | --- |
| C-R1 | Branch protection on `main`: PR only, 1 approving review, CI green, no force push | T8, T10 |
| C-R2 | CODEOWNERS per pack layer (national, state, city, university), per adapter and for `apps-script/` | T8 |
| C-R3 | Releases built only by CI from a signed tag; artefacts published with SHA-256 checksums and build provenance | T10, T12 |
| C-R4 | GitHub Actions pinned to commit SHAs; Dependabot; secret scanning and push protection; CodeQL on scripts; scope check on the Apps Script manifest | T6, T10 |
| C-R5 | CI rules: schema, `source_url`, `last_verified`, `reviewer` on every entry; link check; diff report of changed facts in the PR | T8, T9 |
| C-R6 | Weekly freshness job opens issues for expiring entries; expired entries block a release | T9 |
| C-R7 | Maintainer accounts: hardware security keys or passkeys for GitHub and Google; at least 2 maintainers with release rights; access reviewed per release | T11 |
| C-R8 | `latest.json` written only by the release job; `critical` needs a second maintainer's approval | T12 |

**Public packs folder:** owned by a project Google account with no personal use; edit rights only for the release job; students get a view-only shortcut.

**Template distribution:** students deploy the Apps Script from a released, checksummed version; the setup page shows the version and links to its source.

## Security testing plan

Nine test activities run alongside the build; everything marked G3 must pass before the pilot starts on 9 November.

| When | Activity | Pass criteria | Gate |
| --- | --- | --- | --- |
| 12–18 Oct | Spike: Apps Script with `drive.file`, Only-myself access, link previews in each tool's chat | No unverified-app block; preview cannot write | G1 |
| 12–18 Oct | Repo hardening: branch protection, CODEOWNERS, secret scanning, pinned Actions | All C-R1–C-R4 settings on | G1 |
| 26 Oct–1 Nov | Action-link unit tests: token, nonce replay, whitelist, malformed and oversized params, HTML escaping | 100% pass in CI | G2 |
| 26 Oct–1 Nov | Concurrency test: same link tapped from 2 tools at once | 1 write, 1 Log row | G2 |
| 2–8 Nov | Prompt-injection evals: 15 hostile letters and emails (fake links, "reveal your token", fake deadlines) on all 3 tools | 0 unsafe links or leaks | G3 |
| 2–8 Nov | Pack integrity: PR with an unsourced fact and one with a changed fee | CI blocks the first; diff report flags the second | G3 |
| 2–8 Nov | Release dry run: signed tag → checksums → `latest.json` with `critical` | Second-maintainer approval enforced | G3 |
| 2–8 Nov | Privacy check of templates, `status` and `handover.md` | No ID-number fields or values | G3 |
| 9–22 Nov | Pilot monitoring: weekly Log review with each student's consent; issue triage | No security incident unresolved > 48 h | G4 |

## Incident response and disclosure

Because we hold no personal data, most incidents are about wrong content or a bad release; the response is a fast corrected release and a clear notice.

| Severity | Example | Acknowledge | Fix released | Student notice |
| --- | --- | --- | --- | --- |
| S1 Critical | Release leaks tokens, script writes wrongly, maintainer account taken over | 4 h | 24 h | `critical` notice + pilot message |
| S2 High | Wrong deadline or fee that could cost money or status | 12 h | 48 h | `critical` notice |
| S3 Medium | Injection bypass found in evals; minor wrong fact | 2 days | Next release | Release note |
| S4 Low | Hardening gap, typo in a source | 1 week | Next release | None |

**Steps**

1. Triage in a private GitHub security advisory; assign severity and owner.
2. Contain: revert the release or the pack entry, revoke maintainer sessions, pause the packs folder if needed.
3. Fix through the normal PR and CI path, with a second maintainer's review.
4. Notify: `critical` flag in `latest.json`, pilot students by message, and steps for them (e.g. rotate link key, revert a change).
5. Review within a week: root cause, new test or CI rule, ADR if design changes.

**Disclosure:** `SECURITY.md` in the repo with a private reporting route (GitHub private vulnerability reporting), a 72-hour acknowledgement promise, and credit for reporters.

## Privacy and compliance

The product design keeps the project out of personal data; the pilot is the one place where we do see some, so it gets its own rules. All positions below are to be confirmed by a legal reviewer before public launch.

**Product (GDPR position)**

- Each student controls their own data; their AI provider and Google act for them under the student's own terms.
- The project publishes only non-personal content and runs no service that receives personal data.
- Students are told in plain words what each AI tool and connector can see, and how to revoke it.

**Pilot (we do see some data)**

- Written consent from each of the 10 students: what we observe (setup call, weekly chat, Log review), why, for how long.
- Observe on the student's screen; no copies of their files, mail or Log in project storage.
- Feedback notes pseudonymised (P01–P10), kept in a private repo or folder, deleted 90 days after the pilot review.
- A student can leave at any time; their notes are deleted on request.

**DPIA-lite** before the pilot: data flows, risks to students, the controls in this plan; signed off by the maintainers and the legal reviewer if one is found.

**Legal content (Rechtsdienstleistungsgesetz):** rights, rent and work-law answers stay general information with a disclaimer and a referral to AStA, Mieterverein or a lawyer; no case-specific legal advice.

## Owners and open items

@Ajeet Chouksey owns this plan until a second maintainer joins; that second maintainer is itself the first open item, because C-R7 and C-R8 need two people.

- [ ] Name a second maintainer with release rights, by Oct 18, 2026
- [ ] Decide on a read-only `status` deployment (Anyone access + read token) or none, by Oct 18, 2026
- [ ] Create the project Google account for the public packs folder, with a security key, by Oct 25, 2026
- [ ] Write `SECURITY.md` and enable private vulnerability reporting, by Oct 25, 2026
- [ ] Pilot consent form and DPIA-lite signed off, by Nov 8, 2026
- [ ] 15 prompt-injection eval cases written and passing on all 3 tools, by Nov 8, 2026
- [ ] Find a legal reviewer for the GDPR position and rights content, by Nov 8, 2026 (or before public launch at the latest)
