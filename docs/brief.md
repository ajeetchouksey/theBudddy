# Germany Student Companion — Project Brief

Last updated: 10 October 2026
Build plan (living doc): https://claude.ai/code/artifact/57ef7deb-931e-4446-b44f-972e6964c72f

> Source of truth is the project brief in the claude.ai project "theBuddy". Keep this copy in sync.

## 1. What it is
An AI companion for international students moving to Germany (first audience: students from India). It covers two halves:
- **Settle in:** visa, blocked account, insurance, Anmeldung, bank, transport, letters, money, food, culture, homesickness, rights.
- **Succeed in study:** German university style (self-registration for exams, final-exam weighting), study plans, exam readiness.

## 2. Decisions so far
| Topic | Decision |
| --- | --- |
| First university / city | CAU Kiel, Kiel, Schleswig-Holstein |
| First platform | Gemini, built as a **Skill** (SKILL.md + reference files). Gems are being replaced by Skills (personal accounts from Nov 2026) |
| Second platform | Claude (same SKILL.md imports) |
| Product shape | Chat-first. PWA only if the pilot shows a need |
| Data | No personal data on project servers; everything personal in the student's Google account |
| Knowledge | Layered packs: national → state → city → university, built from YAML with schema checks |
| Scaling | One generic skill; new places = new pack files via pull requests; coverage levels 0/1/2 |
| Setup | 3 actions: add skill → first chat (3 questions) → "Set up my Drive" link (Apps Script, `drive.file` only) |
| Writes | One-tap **action links** to the student's own Apps Script (token, undo log). Fallbacks: prefilled Google Form, sheet checkboxes |
| Integrations | Through Gemini: Drive, Gmail (read, search by sender list — no filter needed), Calendar (after a yes), Google Tasks, Maps |
| Visuals | Tier 1 text cards · Tier 2 interactive charts in chat · Tier 2b Canvas HTML dashboard from our `dashboard.html` template · Tier 3 Sheets canvas tab (paid) |
| Updates | Packs via Drive shortcut to a public folder (auto) · skill re-import (rare) · sheet menu "Update template" · `latest.json` with `critical` flag |
| MCP server | Phase 2 (Claude, Copilot, ChatGPT), Azure Container Apps, no personal data |

## 3. Architecture
- **Project (public):** GitHub repo → CI build → skill release, public packs folder (Drive), `latest.json` (GitHub Pages).
- **Gemini app:** the skill `/germany-companion` reads packs and versions, talks to the student, shows text cards and charts, proposes events, gives action links.
- **Student's Google account:** `Germany Journey` folder (Checklist + Budget sheets, `index.md`, `profile.md`, Letters, Documents, Courses, Packs shortcut), Gmail, Calendar, Tasks, Apps Script web app (setup + action links).

## 4. Data contracts (v1)
- `index.md`: versions (skill, template, packs), file → purpose map, action-link URL + token. Read first in every chat.
- `profile.md`: country, city, university, course, degree, semester start, phase, German level, goals. No passport/visa numbers.
- Checklist: `task_id, phase, title, why, status, due_date, depends_on, source_url, last_verified`.
- Budget: `date, category, amount, note` + Dashboard tab (monthly totals, runway, over-budget date).
- Log tab: every action-link change (for undo).
- Pack entry: `id, layer, topic, text, source_url, last_verified, reviewer`.
- `latest.json`: `skill, template, packs{}, critical, notes`.
- Action links: `done/undo(task)`, `add_task(title, due)`, `expense(amount, category, note)`, `study(module, minutes)`, `phase(n)`.
- Rule: minor versions only add fields; renames need a major version + migration.

## 5. Checklist phases
0 Admission · 1 Visa & finance · 2 First 2 weeks · 3 First 90 days · 4 Each semester · 5 Exams · 6 Ongoing (work limit 140 full / 280 half days, tax refund, permit renewal) · 7 Graduation.

## 6. Repo layout
```
germany-student-companion/
  knowledge/{national, national/letters, states, cities, universities, _schema}
  skill/{SKILL.md, reference/}        # incl. dashboard.html template
  templates/{checklist.md, budget.md, index.md, profile.md}
  apps-script/                        # setup + action links (clasp)
  build/  evals/  site/  .github/workflows/
```

## 7. MVP timeline (2026)
| Dates | Work |
| --- | --- |
| 12–18 Oct | Week 1 spike on a free Google account + phone; decision 18 Oct |
| 12–25 Oct | Knowledge packs: national, Schleswig-Holstein, Kiel, CAU (phases 1–3, top 10 letters) |
| 26 Oct–1 Nov | Starter kit + Apps Script (setup, done, expense) |
| 2–8 Nov | Skill package + 50-question evals (target ≥ 45 pass) |
| 9–22 Nov | Pilot, 10 CAU students |
| 23 Nov | Pilot review |

## 8. Week 1 spike tests
1 Skill on free account · 2 Skill share link · 3 Packs via Drive shortcut · 4 Read `latest.json` URL · 5 Gemini edits existing Sheet · 6 Apps Script `drive.file` + Sheets API, no unverified warning · 7 Long links tappable · 8 Calendar events + Google Tasks from skill · 9 Gmail search by sender · 10 Interactive charts in skill, web + mobile · 11 Canvas HTML dashboard from template · 12 Canvas tab survives Make a copy · 13 Scheduled actions on free accounts · 14 Skill reference file limits.
Each has a fallback (see build plan doc).

## 9. Pilot targets (proposed)
Setup without help 8/10 under 10 min · tasks on time 80% · still using in week 2 6/10 · factual errors fixed within 48 h · would recommend 7/10.

## 10. Roadmap after MVP
1 Harden + phases 4–7 + legal review · 2 MCP server + Claude/Copilot/ChatGPT adapters · 3 PWA companion · 4 Study companion (maybe aaryaai engine) · 5 More cities (Frankfurt next) via ambassador PRs.

## 11. Open decisions
- Licence (proposed: MIT code, CC BY-SA content)
- Product and repo name
- Who verifies Kiel/CAU content
- Legal reviewer for rights content
- Final pilot targets

## 12. Verified facts so far (check again before use)
- CAU students get the Deutschland-Semesterticket via the semester fee; digital ticket, chip card on application via AStA ([AStA CAU](https://asta.uni-kiel.de/en/semesterticket/de-semesterticket/)). Current fee amount to verify.
- CAU uses HISinOne/QIS for exam registration.
- Gemini Skills replace Gems; SKILL.md import; reference files since 30 Sep 2026; personal accounts migrate from Nov 2026 ([Unite.AI](https://www.unite.ai/google-brings-reusable-skills-to-gemini-chat-replacing-gems/), [DEV](https://dev.to/alifar/google-gemini-will-replace-gems-with-skills-migration-dates-and-transition-limits-1enc)).
- Gemini interactive visualizations in chat for all app users with the Pro model, not Education/Workspace accounts yet (Apr 2026, [Google](https://blog.google/innovation-and-ai/products/gemini-app/3d-models-charts/)).
- Sheets canvas: live mini-apps on sheet data, Google AI Pro/Ultra and some Workspace plans (Aug 2026, [Google](https://blog.google/products-and-platforms/products/workspace/sheets-canvas-for-google-sheets-spreadsheets/)).
- No evidence that the consumer Gemini app connects to custom MCP servers.

## 13. Mockups produced
Full app screens, dashboards and charts, user flow (6 stages), chat visuals (3 tiers), Gemini Canvas dashboard — HTML files in project knowledge.
