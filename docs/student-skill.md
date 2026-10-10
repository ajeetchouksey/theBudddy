# Germany Student Companion — Student Skill

Oct 10, 2026 · @Ajeet Chouksey

## Purpose and packaging

Students get one skill, `germany-companion`, that does everything through ordinary chat: no commands to learn. The same source becomes a package per tool; only the adapter and the wrapper differ.

| Tool | How the student adds it | Package contents | Status |
| --- | --- | --- | --- |
| Gemini | Import the skill (SKILL.md + reference files) | Core + `gemini.yaml` + bundled packs | Verify in spike (tests 1–2, 14) |
| Claude | Upload the skill zip | Core + `claude.yaml` + bundled packs | Verify in spike (test 15) |
| Copilot | Custom agent or saved instructions, plus pack file upload | Core flattened into one instruction file + `copilot.yaml` + packs file | Packaging decided at G1 (test 16) |

**Design rules for the student skill**

- One skill, many intents; students just talk.
- Core `SKILL.md` stays short; detail lives in reference files read only when needed.
- No city, university or tool names in the core; those come from packs and the adapter.
- The guardrail block from the AI Guardrails doc sits at the top of `SKILL.md`.

## Package layout

The core file routes; reference files hold the detail for each intent, so the model reads only what the current question needs.

```
skill/
  SKILL.md                 guardrails, start-of-chat routine, intent routing
  reference/
    intents/
      setup.md             first chat, 3 questions, Drive setup link
      next.md              what's next, checklist logic
      ask.md               answering from packs, grounding levels
      letter.md            letter helper, sender list, scam check
      budget.md            expenses, dashboard reading
      deadline.md          calendar, .ics, tasks
      progress.md          cards and visuals by capability
      switch.md            new tool, handover
      help.md              sensitive topics, referrals, crisis rule
      briefing.md          weekly summary
    cards.md               card templates
    action-links.md        link template, actions, params, nonce rules
    data-contracts.md      index.md, profile.md, sheet columns
    adapters/<tool>.yaml   one per build
    packs/                 bundled snapshot (generated)
    dashboard.html         Canvas template (where supported)
```

Size budget: `SKILL.md` under 400 lines; each intent file under 150 lines; snapshot size set per tool from spike test 14.

## What students can ask for

Ten intents map to the 12 features; students never need to name them.

| Intent | Student might say | Feature | Writes? | Floor |
| --- | --- | --- | --- | --- |
| `setup` | "Hi, I'm starting at university in Germany" | F1 | Setup link | Yes |
| `next` | "What should I do now?" | F2 | `done`, `add_task` | Yes |
| `ask` | "Do I need to register my address?" | F3 | No | Yes |
| `letter` | "I got a letter from Beitragsservice" | F4 | Task or reminder link | Yes (paste); Gmail extra |
| `budget` | "Spent 45 euros on books" · "How long will my money last?" | F5 | `expense` | Yes |
| `deadline` | "Remind me about the residence permit appointment" | F6 | `.ics` or native event | Yes (`.ics`) |
| `progress` | "How am I doing?" | F7 | No | Yes (card) |
| `switch` | "I'm moving to another AI app" | F9 | `handover` | Yes |
| `help` | "My landlord won't return my deposit" · "I feel really alone" | F11 | No | Yes |
| `briefing` | "Give me my week" | F12 | No | Yes (on request) |

Cross-cutting: action links and undo (F8) appear inside any intent that writes; update notices (F10) are checked at the start of every chat.

## Intent specs

Each intent follows the same pattern: what it reads, what it does, what the student sees, and what happens when a capability is missing.

### setup

- **Reads:** nothing yet; checks for an existing Journey folder first (returning student → `switch`).
- **Does:** asks home country, university, semester start; resolves packs; checks the Google connector.
- **Shows:** a welcome card, the "Set up my Drive" link, then the first 3 tasks.
- **Fallback:** no Drive read → keeps answers in chat; asks the student to paste the `status` page after setup.

### next

- **Reads:** Checklist (open, unblocked, by due date), packs for `why`.
- **Does:** picks the next 3 tasks; explains the first one fully.
- **Shows:** next-steps card with `done` links.
- **Fallback:** no Drive read → `status` link, then works from the pasted summary.

### ask

- **Reads:** packs (university → city → state → national).
- **Does:** answers at the right grounding level; logs unknowns.
- **Shows:** answer, source line, optional "add as task" link.
- **Fallback:** none needed; bundled packs cover the floor.

### letter

- **Reads:** Gmail by sender list, or pasted text or photo; letter packs.
- **Does:** identifies type, runs the scam check, explains, finds the deadline.
- **Shows:** letter card + task or reminder link.
- **Fallback:** no Gmail → asks the student to paste or photograph the letter.

### budget

- **Reads:** Budget and Dashboard tabs.
- **Does:** parses amount, category, note; proposes `expense`; quotes runway from the sheet.
- **Shows:** budget card; chart where supported.
- **Fallback:** no Drive read → `status` for runway; logging still works by link.

### deadline

- **Reads:** Checklist due dates, packs for official deadlines.
- **Does:** asks first; proposes an event.
- **Shows:** reminder card with native add or `.ics` link.
- **Fallback:** `.ics` link always works.

### progress

- **Reads:** Dashboard formulas.
- **Does:** picks the best visual the adapter allows.
- **Shows:** progress card → chart → HTML dashboard → Sheets canvas.
- **Fallback:** text card.

### switch

- **Reads:** Journey folder, `index.md`, `profile.md`; or uploaded `handover.md`.
- **Does:** skips onboarding; records `ai_tool`; offers `handover` when leaving a tool.
- **Shows:** "Welcome back" card with phase and next task.
- **Fallback:** no Drive read → asks for `handover.md` upload.

### help

- **Reads:** sensitive-topic and referral pack entries.
- **Does:** general information, disclaimer, referral; crisis rule overrides everything.
- **Shows:** help card with who to contact.
- **Fallback:** none needed.

### briefing

- **Reads:** Checklist (next 7 days), Budget runway, update notices.
- **Does:** summarises the week in 5 lines.
- **Shows:** week card; offers a weekly reminder where scheduling is missing.
- **Fallback:** on request only.

## Card templates

Cards are plain Markdown so they render on every tool and phone; values in `{braces}` come from sheets or packs, never from the model. Four of the eight templates are shown; the rest follow the same shape in `reference/cards.md`.

**Next steps**

```markdown
**Phase {n}: {phase_name}** · {done}/{total} done

1. **{task_1}** · due {date_1}
   {why_1} ([source]({source_1}))
   ✅ [Mark done]({link_done_1})
2. **{task_2}** · due {date_2}
3. **{task_3}** · due {date_3}
```

**Budget**

```markdown
**Budget · {month}**
Spent {spent} € of {planned} € · Runway {runway_months} months
{over_budget_line}
➕ [Log {amount} € for {category}]({link_expense}) · ↩️ Undo after tapping
```

**Letter**

```markdown
**Letter from {sender}** · {letter_type}
What it means: {meaning}
Deadline: **{deadline}** · If you miss it: {consequence}
Next step: {next_step}
📅 [Add reminder]({link_reminder}) · ([source]({source}))
{scam_warning_if_any}
```

**Help**

```markdown
{general_answer}

_This is general information, not legal advice._
**Who can help:** {referral_name} · {referral_contact} ([source]({source}))
```

Also in `cards.md`: welcome, progress, reminder, week.

## SKILL.md skeleton

The core file in full outline; the guardrail block is pasted where marked, and every intent detail lives in its reference file.

```markdown
---
name: germany-companion
description: Companion for international students settling into life and study in Germany. Use for checklists, official letters, budget, deadlines, questions about German rules and offices, and switching from another AI app.
---

# Germany student companion

<!-- Paste the guardrail block from the AI Guardrails doc here. -->

## Start of every chat
1. Read reference/adapters/<this tool>.yaml. Use only capabilities marked yes.
2. Look for the Journey folder.
   - Found: read index.md, then profile.md. Note versions and the action-link template.
   - Not found, but handover.md uploaded: read it and continue as a returning student.
   - Neither: this is a new student. Go to setup.
3. If fetch works, read latest.json. Show any critical notice first.
4. Resolve packs for the student: university, city, state, national.

## Route the message
Pick one intent, read its file, then answer.
- Starting out, or no Journey folder → reference/intents/setup.md
- What to do, tasks, done → next.md
- Question about a rule, office, fee, process → ask.md
- A letter or official email → letter.md
- Money spent, runway, blocked account → budget.md
- Dates, reminders, appointments → deadline.md
- "How am I doing", charts → progress.md
- Moving to or from another AI app → switch.md
- Rights, problems, stress, health, crisis → help.md (crisis rule first)
- "My week", summary → briefing.md
If two intents fit, answer the main one and offer the other in one line.

## Every answer
- Answer first, in plain English. Explain German terms the first time.
- Use a card from reference/cards.md when showing tasks, money, letters or help.
- For any change, describe it in words, then give one action link built from reference/action-links.md.
- Show the source and verified date for every fact.

## Versions
Skill {skill_version} · packs {packs_date} · adapter {adapter_last_verified}
When asked "which version", show this line.
```
