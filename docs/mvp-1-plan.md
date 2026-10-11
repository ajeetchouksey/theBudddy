# Germany Student Companion — MVP 1 Plan

Oct 10, 2026 · @Ajeet Chouksey

## Goal and scope

MVP 1 pilots one companion skill with 10 CAU Kiel students on Gemini, Claude and Microsoft Copilot from 9 to 22 November 2026, and free plans must be enough. Students can switch tools at any time without losing progress.

**In scope**

- One generic `SKILL.md` with an adapter per tool and plan. No city, university or tool names in the core.
- Knowledge packs: national, Schleswig-Holstein, Kiel and CAU, covering phases 1–3 and the top 10 letters.
- Starter kit in the student's Drive: Checklist and Budget sheets, `index.md`, `profile.md`, Log tab.
- Apps Script action links: setup, `done`/`undo`, `expense`, `status`, `handover`.
- Reads through each tool's native Google connectors: Drive, Gmail by sender, Calendar.

**Out of scope:** MCP server, PWA, ChatGPT, other cities, phases 4–7, study quizzes.

**Rules that shape every task**

1. No personal data on project servers; state lives only in the student's Google account.
2. Numbers from sheet formulas, facts from packs with source, date and reviewer.
3. A shared floor works on every tool and plan; extras switch on only where the adapter says yes.
4. Setup stays at 3 student actions on any tool.

## Tools and plans

Every student gets the floor; extras depend on the tool and plan they use. All extras stay `unknown` until the spike records `yes` or `no`.

| Capability | Floor? | Gemini | Claude | Copilot | Fallback |
| --- | --- | --- | --- | --- | --- |
| Chat with skill instructions | Yes | Skill | Skill | Agent or instructions | Starter prompt |
| Bundled pack snapshot | Yes | Yes | Yes | Yes | — |
| Text cards | Yes | Yes | Yes | Yes | — |
| Action links (writes) | Yes | Yes | Yes | Yes | Prefilled Google Form |
| Drive read (sheets, `profile.md`) | Extra | Native | Connector | Connector | `status` / `handover` links |
| Gmail search by sender | Extra | Native | Connector | Connector | Student pastes mail |
| Calendar write | Extra | ? | ? | ? | `.ics` action link |
| Live packs via URL | Extra | ? | ? | ? | Bundled snapshot |
| Charts in chat | Extra | Pro model | ? | ? | Text cards |
| HTML dashboard | Extra | Canvas | ? | ? | Charts, then text cards |
| Sheets canvas tab | Extra | AI Pro/Ultra | — | — | HTML dashboard |

**Plans:** each adapter has `free`, `paid` and `education` profiles; paid and education list only what they add. The plan is detected by use and saved in `profile.md` as `ai_plans`. University logins may have fewer features than free personal accounts.

**Switching tools:** progress lives only in Drive, every tool runs the same release, and action links carry the student's token, not a tool id. Each link has a unique id, so a change tapped in two tools counts once.

## Plan by week

Six weeks of evenings, 12 October to the review on 23 November; the spike result at G1 shapes everything after it.

&#91;embedded content: MVP 1 timeline · 6 workstreams, 4 gates\]

Adapters run across weeks 2–4 because each tool's flags arrive from the spike and are finalised with the skill.

| Workstream | Done when |
| --- | --- |
| Spike | 21 tests recorded; flags written into the 3 adapter files |
| Knowledge packs | Phases 1–3 and top 10 letters; every entry has source, `last_verified` and reviewer; schema CI green |
| Starter kit + script | Setup builds the Journey folder in under a minute; `done`, `undo`, `expense`, `status`, `handover` work with token and Log |
| Adapters | Gemini, Claude and Copilot files with `free`, `paid`, `education` profiles and fallbacks |
| Skill + evals | One `SKILL.md` imports on all 3 tools; G3 criteria met |
| Pilot | 10 students set up, weekly feedback logged, switching tested |

## Gates

Four gates decide whether the next block of work starts as planned or switches to its fallback.

| Gate | Date | Passes when | If it fails |
| --- | --- | --- | --- |
| G1 · Spike | 18 Oct | All 21 tests recorded; edit path, pack delivery and capability flags set per tool and plan | Use each test's fallback; floor-only on that tool |
| G2 · Setup | 1 Nov | A new user finishes setup alone in under 10 minutes on each tool | Simplify setup page; onboarding call does the rest |
| G3 · Quality | 8 Nov | ≥ 45/50 evals pass on Gemini; floor flows pass on Claude and Copilot free; no unsourced facts | Fix and re-run; pilot drops the failing tool |
| G4 · Review | 23 Nov | Pilot results checked against the targets below | Harden before any new features |

## Spike tests (12–18 Oct)

21 tests, each with a fallback, recorded in `docs/spike-results.md` and the adapter files. Full table in the build plan.

| Group | Tests | What it decides |
| --- | --- | --- |
| Gemini skill basics | 1–4, 14 | Skill on free accounts, share link, packs via Drive or bundled, `latest.json` fetch, file limits |
| Writes | 5–7 | Direct Sheet edits or action links; Apps Script with `drive.file` and no warning; links tappable |
| Google features | 8, 9, 21 | Calendar, Tasks and Gmail on every tool; native reads vs fallbacks |
| Visuals | 10–12 | Charts, Canvas dashboard, Sheets canvas tab |
| Other tools | 15–17 | Claude and Copilot free at floor level; URL fetch per free plan |
| Plans | 18, 19 | Education login vs personal; one paid plan per tool |
| Switching | 20 | One student moves Gemini → Claude → Copilot without lost or doubled changes |
| Scheduling | 13 | Monday briefing on free accounts |

Test accounts: one free personal Google account, one CAU login, one paid plan per tool where available, plus web and phone.

## Pilot (9–22 Nov)

10 CAU international students across all three tools, free plans first. Proposed mix: 6 on Gemini, 2 on Claude, 2 on Copilot; at least 2 switch tool in week 2.

- Recruit through the CAU International Center, AStA and Indian and international student groups in Kiel.
- 15-minute onboarding call: the student sets up alone while we watch.
- 10-minute feedback chat each week, plus an unanswered-questions log that becomes the content backlog.

| Metric | Proposed target |
| --- | --- |
| Setup finished without help | 8 of 10, under 10 minutes |
| Checklist tasks done by due date | 80% |
| Still using it in week 2 | 6 of 10 |
| Factual errors left unfixed after 48 hours | 0 |
| Switchers who lose no progress | 2 of 2 |
| Would recommend to a friend | 7 of 10 |

## Decisions needed

Five decisions block the plan; each is due before the work that needs it.

- [ ] Kiel and CAU content verifier (a CAU student ambassador?), by Oct 19, 2026
- [ ] Licence: MIT code, CC BY-SA content (proposed), by Oct 25, 2026
- [ ] Product and repo name, by Oct 25, 2026
- [ ] Auto-write `handover.md` after each session, or only on tap, by Nov 1, 2026
- [ ] Final pilot targets, by Nov 8, 2026

Legal reviewer for rights content can wait until phases 4–7, as long as rights content stays out of the MVP packs.

## This week (12–18 Oct)

- [ ] Create the repo under `ajeetchouksey` and push the scaffold: folders, schemas, README, licence files
- [ ] Write the adapter schema and draft `gemini.yaml`, `claude.yaml`, `copilot.yaml` with every flag `unknown`
- [ ] Write the spike test script; set up the test accounts (free Google, CAU login, one paid plan per tool)
- [ ] Run tests 1–14 on Gemini, then 15–21 on Claude, Copilot and the switching path
- [ ] Write `SKILL.md` v0.1 and three sample Kiel and CAU pack entries
- [ ] Pack schema and CI validation in GitHub Actions; start national and Schleswig-Holstein packs
- [ ] Contact the CAU International Center and AStA about the pilot
- [ ] Record results and decide at G1 on 18 Oct
