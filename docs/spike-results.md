# Spike results — week 1 (12–18 Oct 2026)

The build depends on AI features that change quickly and differ by tool and plan. This file is
both the **runbook** for the 21 spike tests and the **record** of their results. Gate G1 on
18 October reads it to decide: Skill or Gem, where packs live, how edits work, and the
capability flags for each tool and plan.

Source of the test list: the build plan (Week 1 spike) and `docs/mvp-1-plan.md`.

## How to run

**Accounts** (no real personal data on any of them):

| Account | Used for |
| --- | --- |
| Free personal Google account, web + phone | Gemini free (tests 1–14, 17, 21), Apps Script probe (6, 7) |
| Free Claude account, connected to the same Google account | Tests 15, 17, 20, 21 |
| Free Copilot account (Microsoft account), connected to the same Google account | Tests 16, 17, 20, 21 |
| CAU login (a volunteer student runs it, we watch) | Test 18 |
| One paid plan per tool, where you have one | Test 19 |

**Kit:** everything you need to run the tests is in `spike/` (see `spike/README.md`): a small
probe skill with known codes in its reference files, a size generator for the limits test, and
an Apps Script probe that only uses the `drive.file` scope.

**Order:** Gemini free first (1–14), then the floor on Claude and Copilot (15–17), then
connectors (21), plans (18–19) and switching (20). A failure does not stop the spike: every
test has a fallback, and the fallback becomes the design.

**Recording rules**

1. One **spike-result issue** per test × tool × plan (template in `.github/ISSUE_TEMPLATE`), with
   screenshots or a screen recording, the date, and web or phone.
2. Results are `yes`, `partial`, `no` or `n/a`. **`yes` needs evidence**: a link to the issue.
   No evidence means `unknown`, never `yes` (CI rule A5 enforces this in the adapters).
3. Copy the result into the grid below and into the adapter file (task P6) with the issue link
   in `notes`.
4. Write down anything surprising in **Notes** at the end, even if the test passed.

**Probe codes:** the probe skill's reference files contain codes such as `PROBE-REF-7Q2K`. A
test that reads a file passes only if the tool returns the **exact** code. A tool that guesses
or invents a code fails, and that also tells us something about grounding.

## Results grid

`·` not run yet · `y` yes · `p` partial · `n` no · `–` not applicable. Fill in as you go.

| # | Test | Gemini free | Gemini edu | Gemini paid | Claude free | Claude paid | Copilot free | Copilot paid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Skill import | · | · | · | – | – | – | – |
| 2 | Skill shared by link | · | – | – | – | – | – | – |
| 3 | Packs via Drive shortcut | · | · | · | · | · | · | · |
| 4 | `latest.json` from a URL | · | – | – | – | – | – | – |
| 5 | Edit an existing Sheet | · | · | · | · | · | · | · |
| 6 | Apps Script `drive.file`, no warning | · | · | – | – | – | – | – |
| 7 | Long links tappable | · | – | – | · | – | · | – |
| 8 | Calendar event + Tasks | · | · | · | · | · | · | · |
| 9 | Gmail search by sender | · | · | · | · | · | · | · |
| 10 | Charts in chat, web + phone | · | · | · | · | · | · | · |
| 11 | Canvas HTML dashboard | · | · | · | · | · | · | · |
| 12 | Sheets canvas tab survives Make a copy | – | – | · | – | – | – | – |
| 13 | Scheduled actions | · | · | · | · | · | · | · |
| 14 | Reference file limits | · | – | – | · | – | · | – |
| 15 | Claude free floor | – | – | – | · | – | – | – |
| 16 | Copilot free floor | – | – | – | – | – | · | – |
| 17 | URL fetch | · | – | · | · | · | · | · |
| 18 | Education login vs personal | – | · | – | – | – | – | – |
| 19 | One paid plan per tool | – | – | · | – | · | – | · |
| 20 | Switch Gemini → Claude → Copilot | · | – | – | · | – | · | – |
| 21 | Native connectors (Sheet read, Gmail, Calendar) | · | · | · | · | · | · | · |

## Test cards

Each card: what we want to know, steps, what counts as yes / partial / no, what it sets, and the
fallback if it fails.

### 1 · Skill import on a free account (Gemini)

- **Why:** the whole MVP is a Skill. The brief records that personal accounts move from Gems to
  Skills from November 2026, so in October a free account may not offer Skills yet.
- **Steps:** on the free account, look for a way to add a skill. Import `spike/probe-skill`
  (SKILL.md + reference files). Start a chat and say `probe ref`.
- **Yes:** the skill imports, appears in chat and returns `PROBE-REF-7Q2K` exactly.
  **Partial:** imports but cannot read reference files. **No:** Skills not offered.
- **Sets:** packaging decision for Gemini (Skill or Gem); record the date Skills became
  available if it is later than the test date.
- **Fallback:** a Gem for the pilot (same instructions, packs as files), or a starter prompt.

### 2 · Skill shared by link

- **Steps:** from the account that imported the probe skill, look for a share or install link.
  Open it on a second free account.
- **Yes:** one click installs it. **Partial:** link works but needs several manual steps.
  **No:** no sharing.
- **Sets:** setup step 1 in `docs/what-you-need.md`.
- **Fallback:** download-and-import guide with screenshots.

### 3 · Skill reads packs through a Drive shortcut

- **Steps:** put `spike/probe-skill/drive/probe-pack.md` in a folder on a second account and
  share it read-only. On the test account, add a shortcut to that folder in My Drive. Ask
  `probe drive`.
- **Yes:** returns `PROBE-DRIVE-3M8X` exactly, and returns the new code after you edit the file
  (proves it reads the live file). **Partial:** reads only after a re-upload or re-share.
  **No:** cannot read it.
- **Sets:** `drive_read` (for packs); where packs live.
- **Fallback:** packs bundled in the skill; re-import for updates.

### 4 · Skill reads `latest.json` from a URL (Gemini)

- **Steps:** publish `spike/probe-latest.json` at a public URL (see `spike/README.md`). Ask
  `probe fetch`.
- **Yes:** returns `PROBE-FETCH-9D4W` exactly. **No:** refuses, invents, or cannot fetch.
- **Sets:** `fetch_url` for Gemini free.
- **Fallback:** version file in the packs folder; snapshot version stamp.

### 5 · Edit an existing Sheet from chat

- **Steps:** create a sheet `Spike checklist` with columns `task_id, status` and two rows. Ask
  `probe sheet-edit`: mark row `t2` as done.
- **Yes:** the cell changes in the sheet without leaving chat. **Partial:** it creates a new
  copy instead of editing. **No:** cannot write.
- **Sets:** `sheets_edit`.
- **Fallback:** action links (the default design, ADR 0006).

### 6 · Apps Script with `drive.file`, no unverified-app warning

- **Steps:** deploy `spike/apps-script-probe` as in its README (web app, execute as me, access
  Only myself). Open `?a=setup`, then `?a=write&n=test-1`.
- **Yes:** consent screen asks only for "files created by this app", **no** "Google hasn't
  verified this app" screen, a sheet `Spike probe` appears and gets a row.
  **Partial:** works but shows the unverified screen. **No:** needs a broader scope.
- **Also record:** exact consent text (screenshot); whether the deploying user sees a warning on
  their own script; replay `?a=write&n=test-1` returns "already done" (idempotency).
- **Sets:** ADR 0004 status; `docs/what-you-need.md` "isn't verified" row.
- **Fallback:** prefilled Google Form.

### 7 · Long links stay tappable in replies

- **Steps:** ask `probe link`. The skill prints an action link of about 400 characters (from
  `reference/probe-link.md`). Tap it on the phone app and on web.
- **Yes:** the link is one tappable link and opens the probe with every parameter intact (the
  page shows `params ok`). **Partial:** works on web only, or after copy-paste.
  **No:** broken or truncated.
- **Sets:** action-link design; maximum safe link length (write it down).
- **Fallback:** short codes resolved by the script.

### 8 · Calendar events and Google Tasks from the skill

- **Steps:** ask `probe calendar` (an event tomorrow 10:00, "Spike test"). Then `probe task`.
- **Yes:** asks first, then the event and the task appear. **Partial:** event only.
  **No:** neither.
- **Sets:** `calendar_write`, `tasks_write`.
- **Fallback:** `.ics` action link; Checklist row via `add_task`.

### 9 · Gmail search by sender

- **Steps:** from another account, send the test account a mail with subject `Spike letter` and
  the body `PROBE-MAIL-5H2T`. Ask `probe mail`.
- **Yes:** finds the mail by sender and returns the code. **No:** cannot search or read.
- **Also record:** whether it can be limited to one sender (privacy: FR-4.4).
- **Sets:** `gmail_search`.
- **Fallback:** student pastes or forwards the mail.

### 10 · Interactive charts while the skill is active, web and phone

- **Steps:** ask `probe chart` (a bar chart of four invented monthly totals).
- **Yes:** an interactive chart on web **and** phone. **Partial:** web only, or a static image.
  **No:** text only.
- **Sets:** `charts_inline`.
- **Fallback:** text cards (tier 1).

### 11 · Canvas builds the HTML dashboard from the template

- **Steps:** ask `probe canvas`. The skill renders `reference/probe-dashboard.html` with invented
  numbers.
- **Yes:** the dashboard renders in the app and shows `PROBE-CANVAS-2K6R`. **Partial:** renders
  only outside the skill. **No:** no HTML rendering.
- **Sets:** `canvas_html`.
- **Fallback:** charts, then text cards.

### 12 · Sheets canvas tab survives Make a copy (paid Google plan only)

- **Steps:** on a plan with Sheets canvas, add a canvas tab to a test sheet, then File → Make a
  copy.
- **Yes:** the copy keeps a working canvas tab. **No:** lost on copy.
- **Sets:** `sheets_canvas` for paid; whether tier 3 ships in the template.
- **Fallback:** a one-line prompt the student pastes to create it.

### 13 · Scheduled actions on free accounts

- **Steps:** ask `probe schedule` (a weekly Monday 08:00 summary). Wait for the next trigger, or
  use a time 10 minutes ahead if the tool allows it.
- **Yes:** it runs on schedule with the skill active. **Partial:** runs without the skill.
  **No:** not available.
- **Sets:** `scheduled_actions`.
- **Fallback:** weekly calendar reminder to ask.

### 14 · Reference file count and size limits

- **Steps:** run `python spike/make_probe_packages.py` (see `spike/README.md`). Import each
  `limits-*` package. In each, ask `probe last` (the code in the last file) and
  `probe end <n>` (the code at the end of file n).
- **Yes:** record the largest package that imports **and** answers both correctly.
- **Sets:** `NFR-PER.3`: bundled snapshot size per tool; how many layers ship in the floor
  (open question in `docs/technical-architecture.md`).
- **Fallback:** move packs to Drive sooner.

### 15 · Claude free: skill import, reference limits, links on mobile

- **Steps:** upload the probe skill zip (`build/spike/probe-skill.zip`). Ask `probe ref`,
  `probe link` (tap on phone), and run the limits packages from test 14.
- **Yes:** all three work. **Partial:** some. **No:** skill upload not available on free.
- **Sets:** Claude adapter at floor level.
- **Fallback:** starter prompt plus pack file upload.

### 16 · Copilot free: instructions or agent, file grounding, links

- **Steps:** try, in order: a custom agent; saved custom instructions; a starter prompt. Use
  `build/spike/probe-copilot/instructions.md` and upload `packs.md`. Ask `probe ref` and
  `probe link`.
- **Yes:** one of the three works with the uploaded file and tappable links. Record **which**.
- **Sets:** Copilot packaging (open question at G1); Copilot adapter at floor level.
- **Fallback:** starter prompt plus pack file upload.

### 17 · URL fetch on each free plan

- **Steps:** as test 4, on Claude free and Copilot free (and paid where available).
- **Yes / No:** as test 4.
- **Sets:** `fetch_url` per tool and plan.
- **Fallback:** bundled snapshot with version stamp.

### 18 · Gemini on a CAU education login vs a personal account

- **Steps:** a volunteer runs tests 1, 3, 5, 8, 9, 10, 11 on their CAU login while you watch.
  Never ask for their password; they type it themselves.
- **Yes:** record each feature as for free. Note anything blocked by the university admin.
- **Sets:** `education` plan flags; whether we recommend a personal account
  (`docs/what-you-need.md` already does).
- **Fallback:** recommend a personal account.

### 19 · One paid plan per tool

- **Steps:** repeat tests 3, 5, 8–13, 17, 21 on one paid plan per tool you have.
- **Sets:** `paid` plan flags. Without evidence they stay `unknown`; the floor still works.

### 20 · Switch Gemini → Claude → Copilot mid-journey

- **Steps:** with the Apps Script probe set up (test 6): on Gemini, tap a write link
  (`n=switch-1`). Move to Claude with only the skill and the Google connector. Ask it to find
  the probe sheet and tap the same link again, then a new one (`n=switch-2`). Repeat on Copilot.
- **Yes:** each tool finds the state by itself; the sheet ends with exactly two rows (no lost or
  doubled changes). **Partial:** needs `handover.md`. **No:** state not found.
- **Sets:** ADR 0010 confirmed; FR-9.1.
- **Fallback:** student uploads `handover.md` and repeats the first chat.

### 21 · Native Google connectors per tool and plan

- **Steps:** on each tool: connect Google. Ask `probe sheet-read` (a value from the probe sheet),
  `probe mail` (test 9) and `probe calendar` (test 8).
- **Yes:** each read works through the tool's own connector. Record cell values vs text export
  (open question: can it read Sheets cell values?).
- **Sets:** `drive_read`, `gmail_search`, `calendar_write` per tool and plan (ADR 0011).
- **Fallback:** `status` and `handover` links; `.ics` action link; student pastes mail.

## Decisions at G1 (18 Oct)

Fill in after the spike; each line links the issues it rests on.

| Decision | Result | Evidence |
| --- | --- | --- |
| Gemini packaging: Skill or Gem for the pilot | | |
| Where packs live: Drive shortcut, URL, or bundled only | | |
| Edit path: native Sheet edits or action links | | |
| Action links: Only-myself access works; max link length | | |
| Unverified-app screen: none / shown → Form fallback | | |
| Copilot packaging: agent, instructions or starter prompt | | |
| Bundled snapshot size per tool (test 14) | | |
| Can connectors read Sheets cell values? | | |

## Notes

Anything surprising, with the date and the issue link.
