# Germany Student Companion — Requirements (MVP 1)

Oct 10, 2026 · @Ajeet Chouksey

## How to read this

MVP 1 has 12 features, 46 functional and 30 non-functional requirements; all Must items have to pass before the pilot on 9 November 2026.

- **Scope:** CAU Kiel students, phases 0–3, on Gemini, Claude and Microsoft Copilot, free plans as the floor.
- **IDs:** `F` = feature, `FR-<feature>.<n>` = functional, `NFR-<area>.<n>` = non-functional. IDs never change; retired items are struck through, not reused.
- **Priority:** Must (pilot blocker) · Should (pilot if time allows) · Could (after pilot).
- **Floor:** Yes = works on every tool and plan with no flag; Extra = uses a capability from the adapter, with a fallback.
- **Verified by:** E = eval set · T = automated test or CI · S = spike · P = pilot observation · R = review.
- **Sources of truth:** decisions in the brief, design in the Technical Architecture doc, dates in the MVP 1 Plan.

## Feature catalogue

Ten of the 12 features work on the floor of every tool; Letters and Deadlines lean on Google connectors but keep a manual fallback.

| ID | Feature | What the student gets | Priority | Floor |
| --- | --- | --- | --- | --- |
| F1 | Setup and onboarding | Ready in 3 actions, under 10 minutes | Must | Yes |
| F2 | Personal checklist | Phase-by-phase tasks with why, due date and source | Must | Yes |
| F3 | Ask about Germany | Plain answers from packs, with source and date | Must | Yes |
| F4 | Letter helper | What a German letter means, the deadline, what to do | Must | Extra (Gmail) |
| F5 | Budget and expenses | Log spending, see runway and over-budget date | Must | Yes |
| F6 | Deadlines and reminders | Calendar events or `.ics`, Google Tasks | Should | Extra (Calendar) |
| F7 | Progress and visuals | Text cards always; charts and dashboards where supported | Must | Yes (cards) |
| F8 | Action links and undo | One-tap changes, undo, audit log | Must | Yes |
| F9 | Switch AI tool | Move between Gemini, Claude and Copilot, nothing lost | Must | Yes |
| F10 | Updates and freshness | Notice of new facts and urgent fixes | Should | Yes |
| F11 | Safety and referral | Legal disclaimer, referral to AStA, Mieterverein or help lines | Must | Yes |
| F12 | Weekly briefing | Monday summary of what is due | Could | Extra (scheduling) |

## Feature details

Each feature below gives the student's goal, how the companion behaves, and what the pilot must show.

### F1 Setup and onboarding

*As a new student, I want to start in minutes, so I don't give up before it helps.*

- Three actions: add the skill, answer 3 questions (home country, university, semester start), tap "Set up my Drive".
- Setup creates the Journey folder, Checklist, Budget, Log, `index.md` and `profile.md`, then loads phase 0–3 tasks for the student's dates.
- If the tool's Google connector is off, the first chat explains how to switch it on, in one step.
- **Done when:** 8 of 10 pilot students finish alone in under 10 minutes.

### F2 Personal checklist

*As a student, I want to know what to do next and why, so I don't miss a step.*

- Tasks per phase with `why`, `due_date`, `depends_on`, `source_url`; due dates computed from semester start and arrival.
- "What's next?" returns the next 3 open tasks, blocked tasks last.
- German terms explained on first use, e.g. Anmeldung = address registration.
- **Done when:** 80% of pilot tasks are done by their due date.

### F3 Ask about Germany

*As a student, I want trustworthy answers in plain English, so I can act on them.*

- Answers come from packs, most specific layer first (university → city → state → national), with source link and verified date.
- No pack entry → says it doesn't know, points to the right office, logs the question for the backlog.
- **Done when:** at least 45 of 50 eval questions pass; zero unsourced facts.

### F4 Letter helper

*As a student, I want to understand official letters, so I don't miss a deadline or pay a fine.*

- Covers the 10 most common letters (e.g. Rundfunkbeitrag = broadcast fee, health insurance, Bürgeramt).
- Reads mail from a known sender list via the tool's Gmail connector, or a pasted or photographed letter.
- Returns: who sent it, what it means, the deadline, the next step, and a task or reminder link.
- **Done when:** all 10 letter types pass their evals on every tool.

### F5 Budget and expenses

*As a student on a blocked account, I want to see how long my money lasts.*

- Log by chat → `expense` link; categories fixed; amounts in EUR.
- Dashboard tab: monthly totals, runway in months, over-budget date, all by formula.
- **Done when:** totals in chat always match the sheet.

### F6 Deadlines and reminders

*As a student, I want deadlines in my calendar, so I'm reminded in time.*

- Proposes an event only after the student says yes; native Calendar write where flagged, else `.ics` link.
- Google Tasks where supported, else a Checklist row.
- **Done when:** a deadline lands in the calendar on every tool, natively or by `.ics`.

### F7 Progress and visuals

*As a student, I want to see my progress at a glance.*

- Text card in every relevant reply: phase, done/total, next task, runway.
- Charts, HTML dashboard or Sheets canvas only where the adapter says yes.
- **Done when:** cards render on all tools on web and phone.

### F8 Action links and undo

*As a student, I want changes to be one tap and reversible.*

- Every change is a link with token and nonce; result page with Undo; Log records it with the tool name.
- **Done when:** no lost or doubled change in the pilot Log.

### F9 Switch AI tool

*As a student, I want to change AI tool without starting over.*

- New tool finds the Journey folder or asks for `handover.md`; skips onboarding; same links work.
- **Done when:** 2 of 2 pilot switchers keep all progress.

### F10 Updates and freshness

*As a student, I want to know when a rule I rely on changed.*

- Reads `latest.json` where it can; else checks the bundled snapshot date; urgent fixes (`critical`) shown first.
- **Done when:** a test `critical` release reaches every pilot tool within a day.

### F11 Safety and referral

*As a student, I want help with problems without being misled.*

- Rights, rent and work-law answers carry a general-information disclaimer and a referral (AStA, Mieterverein, a lawyer).
- Signs of distress → kind reply and local help options; no diagnosis.
- **Done when:** all safety evals pass.

### F12 Weekly briefing

*As a student, I want a short Monday summary.*

- Scheduled action where the tool offers it; else a weekly calendar reminder to ask.
- **Done when:** briefing or reminder works for every pilot student.

## Functional requirements

46 requirements, 33 of them Must; each states the testable behaviour.

| ID | Requirement | Priority | Verified |
| --- | --- | --- | --- |
| FR-1.1 | Setup takes at most 3 student actions on every tool | Must | P |
| FR-1.2 | First chat asks exactly 3 questions and writes the answers to `profile.md` | Must | E |
| FR-1.3 | "Set up my Drive" creates Journey folder, Checklist, Budget, Log, `index.md` (URL, token) and `profile.md` in under 60 s | Must | T |
| FR-1.4 | Setup loads phase 0–3 tasks with due dates computed from semester start | Must | T |
| FR-1.5 | If the Google connector is off, the skill gives one-step instructions and keeps working on the floor | Should | S |
| FR-2.1 | Each task has `task_id, phase, title, why, status, due_date, depends_on, source_url, last_verified` | Must | T |
| FR-2.2 | "What's next?" returns the next 3 open, unblocked tasks by due date | Must | E |
| FR-2.3 | Overdue tasks show days overdue, computed by formula | Must | T |
| FR-2.4 | German terms are explained the first time they appear in a session | Should | E |
| FR-2.5 | The student can add their own tasks through `add_task` | Must | T |
| FR-3.1 | Every factual answer shows the `source_url` and `last_verified` of the entry used | Must | E |
| FR-3.2 | Packs resolve university → city → state → national; the most specific entry wins | Must | T |
| FR-3.3 | With no matching entry, the skill says so, names the right office and logs the question | Must | E |
| FR-3.4 | Answers use plain English; average sentence under 20 words | Should | R |
| FR-3.5 | The skill never states a fee, deadline or rule that is not in a pack | Must | E |
| FR-4.1 | Recognises the 10 MVP letter types from Gmail (sender list), pasted text or a photo | Must | E |
| FR-4.2 | For each letter: sender, meaning, deadline, next step, consequence of missing it | Must | E |
| FR-4.3 | Offers a task or reminder link for each letter deadline | Must | E |
| FR-4.4 | Gmail is read only and searched by the known sender list; the skill never sends mail | Must | S |
| FR-5.1 | `expense` appends date, category, amount and note; category from a fixed list | Must | T |
| FR-5.2 | Dashboard tab computes monthly totals, runway and over-budget date by formula | Must | T |
| FR-5.3 | Budget numbers in chat are read from the sheet, never calculated by the model | Must | E |
| FR-5.4 | Expenses can be corrected through undo or `revert` | Must | T |
| FR-6.1 | Calendar events are proposed only after the student says yes | Must | E |
| FR-6.2 | Native Calendar write where the adapter says yes; otherwise an `.ics` link | Should | S |
| FR-6.3 | Google Tasks where the adapter says yes; otherwise a Checklist row | Could | S |
| FR-7.1 | Relevant replies include a progress card: phase, done/total, next task, runway | Must | E |
| FR-7.2 | Charts and dashboards appear only where the adapter says yes; otherwise the card | Should | S |
| FR-7.3 | Cards read on a 360 px phone screen with no sideways scrolling | Must | P |
| FR-8.1 | Every write is an action link carrying `v`, token, nonce and `src` | Must | T |
| FR-8.2 | A repeated nonce causes no second write and returns the first result | Must | T |
| FR-8.3 | Every write is logged with before, after and tool; `revert` restores before | Must | T |
| FR-8.4 | The result page says what changed in plain words and offers Undo | Must | P |
| FR-8.5 | Token rotation from the sheet menu; old links fail with a clear message | Should | T |
| FR-9.1 | On a new tool, the first chat finds the Journey folder or `handover.md` and skips onboarding | Must | S |
| FR-9.2 | `handover` writes profile, phase, open tasks and last 5 changes, with no ID numbers | Must | T |
| FR-9.3 | `profile.md` records `ai_tool` and the detected plan per tool in `ai_plans` | Should | T |
| FR-9.4 | Every tool runs the same release; the skill states its version on request | Must | T |
| FR-10.1 | Where `fetch_url` works, the skill reads `latest.json` and notes newer versions | Should | S |
| FR-10.2 | A `critical` notice is shown before the answer | Should | E |
| FR-10.3 | Without fetch, time-sensitive answers state the snapshot date if it is over 90 days old | Should | E |
| FR-11.1 | Rights, rent and work-law answers carry a disclaimer and a referral | Must | E |
| FR-11.2 | Signs of distress get a kind reply and local support options, with no diagnosis | Must | E |
| FR-11.3 | The skill never asks for or stores passport, visa, tax or bank numbers | Must | E |
| FR-12.1 | Weekly briefing runs as a scheduled action where the tool offers one | Could | S |
| FR-12.2 | Otherwise the skill offers a weekly calendar reminder to ask | Could | S |

## Non-functional requirements

30 requirements across 9 areas; privacy and accuracy carry the strictest targets because they protect the student.

| ID | Requirement | Target | Priority | Verified |
| --- | --- | --- | --- | --- |
| NFR-PRI.1 | No personal data stored or processed on project infrastructure | 0 personal fields in any project store | Must | R |
| NFR-PRI.2 | Apps Script uses only the `drive.file` scope | 1 scope | Must | T |
| NFR-PRI.3 | Templates have no fields for passport, visa, tax, bank or card numbers | 0 such fields | Must | R |
| NFR-PRI.4 | `status` and `handover.md` output contain no ID numbers | 0 | Must | T |
| NFR-ACC.1 | Every pack entry has `source_url`, `last_verified`, `reviewer` | 100% | Must | T |
| NFR-ACC.2 | No entry ships past its `expires` date without re-review | 0 expired entries | Must | T |
| NFR-ACC.3 | Eval pass rate on Gemini; floor evals on Claude and Copilot | ≥ 45/50; all floor evals | Must | E |
| NFR-ACC.4 | Reported factual errors fixed and released | ≤ 48 h | Must | P |
| NFR-POR.1 | All floor features work on the free plans of Gemini, Claude and Copilot | 3 of 3 tools | Must | S |
| NFR-POR.2 | One `SKILL.md` source with no city, university or tool names | 0 names, CI rule | Must | T |
| NFR-POR.3 | Data contracts are identical across tools; minor versions only add fields | 0 renames in minor | Must | T |
| NFR-POR.4 | A new city or university needs only pack files | 0 skill changes | Should | R |
| NFR-USA.1 | Setup without help | 8 of 10 under 10 min | Must | P |
| NFR-USA.2 | Student-facing text readable at CEFR B1 English | B1 | Should | R |
| NFR-USA.3 | Works on phone and web | 360 px, no sideways scroll | Must | P |
| NFR-USA.4 | Action-link result pages make sense without the chat | 10 of 10 pilot students | Should | P |
| NFR-PER.1 | Action-link round trip | ≤ 5 s p95 | Should | T |
| NFR-PER.2 | "Set up my Drive" completes | ≤ 60 s | Must | T |
| NFR-PER.3 | Skill build fits each tool's reference-file limits | within limits from spike | Must | S |
| NFR-REL.1 | No lost or doubled writes | 0 in pilot Log | Must | T |
| NFR-REL.2 | Every extra capability has a fallback | 100%, CI rule | Must | T |
| NFR-REL.3 | Template updates keep student data tabs intact | 0 rows lost | Should | T |
| NFR-SEC.1 | Web app access Only myself; token checked on every request | 100% of requests | Must | T |
| NFR-SEC.2 | Action and parameter whitelist, type and length checks | 100% of params | Must | T |
| NFR-SEC.3 | Token rotation available to the student | 1 menu action | Should | T |
| NFR-SEC.4 | Pack and adapter changes need CODEOWNERS review; release tags signed | 100% | Should | T |
| NFR-COM.1 | Legal topics framed as general information with disclaimer; legal review before public launch | 100% of legal answers | Must | R |
| NFR-COM.2 | Open licences published: MIT code, CC BY-SA content (proposed) | Licence files in repo | Should | R |
| NFR-MAI.1 | Adapter flags re-verified for each release | `last_verified` ≤ 90 days | Should | T |
| NFR-MAI.2 | Each architectural decision recorded as an ADR | 100% | Should | R |

## Out of scope for MVP 1

These wait for the pilot review on 23 November 2026; the data contracts already leave room for them.

- Phases 4–7: semesters, exam registration, Werkstudent work limits, graduation, permit renewal.
- Study companion: quizzes, revision plans, exam readiness.
- Cities and universities other than Kiel and CAU.
- MCP server, PWA and a ChatGPT adapter.
- Contract and benefit checks, form filling, sending mail on the student's behalf.
- Languages other than English for student-facing text.
