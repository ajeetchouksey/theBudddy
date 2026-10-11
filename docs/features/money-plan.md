# F13 · Money plan: financial planning and forecasting

Oct 11, 2026 · Status: **proposed** (extends F5 Budget and expenses)

Students worry most about one question: *"Will my money last, and how much must I add when my
permit ends?"* The Money plan answers it from the student's own Budget sheet, month by month,
with numbers that sheet formulas compute — never the model.

## 1. Student explanation (card text)

Plain English, B1. ✅ = sourced in packs today · ⏳ = waiting for the Kiel residence-permit run.

> **Your money for the visa, and after**
>
> 1. ✅ **Before the visa:** you show money for your first year: 11,904 euros (992 euros a month).
>    Most students use a blocked account (Sperrkonto).
> 2. ✅ **In Germany:** the bank pays you up to 992 euros each month from the blocked account.
> 3. ⏳ **Before your permit ends:** you ask to extend it. The immigration office checks again that
>    you have enough money for the next period.
> 4. ⏳ **Money you still have counts.** You only add what is missing.
>    Example: 3,000 euros left, 12 months needed → add 8,904 euros, not 11,904.
> 5. ⏳ **Other proof can also count:** a scholarship, your parents' income, sometimes a student job.
>
> Your Money plan shows how much you will have on the day your permit ends, and how much to save
> each month to be ready.

Until the Kiel run confirms points 3–5, the skill shows them with: *"Check this with the
immigration office. Rules can differ."*

## 2. What the student gets

**Questions it answers**

- "How long will my money last?" → runway and the first month the plan goes below zero.
- "How much must I add when my permit ends?" → top-up at the extension date.
- "How much should I save each month?" → top-up ÷ months left.
- "What if I get a job / pay a 900 € deposit / my rent goes up?" → the student changes one input
  through an action link; the sheet recalculates; the skill reads the new numbers.

**Money plan card** (text card, works on every tool and plan; 360 px wide)

```
💶 Money plan · checked 11 Oct 2026
Blocked account now ........ 11,904 €
Costs per month ............... 955 €
Permit ends ................. Oct 2027 (12 months)
On that day you will have:
  blocked account ............... 0 €
  other money ................. 238 €
Needed for 12 months ....... 11,904 € ⏳
To add ..................... 11,666 €
Save per month ................ 972 €
⚠ Your plan goes below zero in Oct 2027.
[Update a number]  [Add a one-off cost]  [See month by month]
```

Charts and the Canvas dashboard (where the adapter says yes) show the same numbers as a line of
the blocked account and free money over 24 months, with a marker at the extension date.

## 3. Data: two new tabs in the Budget sheet

Template **1.1**: adds tabs, changes nothing existing (minor version, add-only — NFR-POR.3).
No bank names, IBANs or account numbers anywhere (NFR-PRI.3).

### Plan tab (inputs)

| Field (named range) | Who fills it | Default / source |
| --- | --- | --- |
| `plan_start` | setup | first day of the current month |
| `blocked_start` | student, via action link | — |
| `free_start` | student, via action link | 0 |
| `payout` | skill proposes, student taps | 992 (pack `de.proof-of-funds.monthly-limit`) |
| `extension_date` | student (date on their permit) | — |
| `proof_months` | skill proposes, student taps | 12 ⏳ (pack entry from the Kiel run) |
| `monthly_need` | skill proposes, student taps | 992 (pack `de.proof-of-funds.amount`) |
| `job_income` | student | 0 |
| `family_support` | student | 0 |
| Costs table `costs` (category, € per month) | student; categories as in the Budget tab | rent, health insurance, phone, food, other |

**OneOffs tab:** `month` (first day), `amount` (positive cost, negative income), `note`. The skill
proposes known one-offs from packs, e.g. the semester fee (`cau.semester-fee.amount`) in the month
before each semester; the student confirms each with one tap.

### Forecast tab (formulas only, 24 rows)

Row 2 is the first month; rows 3–25 copy the formulas down.

| Col | Meaning | Row 2 | Row 3 and below |
| --- | --- | --- | --- |
| A | Month | `=plan_start` | `=EDATE(A2,1)` |
| B | Blocked, start of month | `=blocked_start` | `=D2` |
| C | Payout | `=MIN(payout,B2)` | same pattern |
| D | Blocked, end of month | `=B2-C2` | same pattern |
| E | Income | `=C2+job_income+family_support` | same pattern |
| F | Spending | `=SUM(costs_amounts)+SUMIFS(OneOffs!B:B,OneOffs!A:A,A2)` | same pattern |
| G | Free money, end of month | `=free_start+E2-F2` | `=G2+E3-F3` |

### Summary (on the Dashboard tab)

```
months_to_ext   =MAX(0, DATEDIF(plan_start, EOMONTH(extension_date,-1)+1, "M"))
blocked_at_ext  =IF(months_to_ext=0, blocked_start, INDEX(Forecast!D2:D25, months_to_ext))
free_at_ext     =IF(months_to_ext=0, free_start,    INDEX(Forecast!G2:G25, months_to_ext))
required        =proof_months*monthly_need
top_up          =MAX(0, required - blocked_at_ext - MAX(0, free_at_ext))
save_per_month  =IF(months_to_ext>0, ROUND(top_up/months_to_ext, 2), "")
below_zero      =IFERROR(INDEX(Forecast!A2:A25, MATCH(TRUE, ARRAYFORMULA(Forecast!G2:G25<0), 0)), "")
```

`scripts/money_plan.py` is the **reference model** for these formulas. The template tests (task
P7) fill a test sheet with the examples below and compare every summary cell with the model.

## 4. Writes: two new action links

Writes stay on the action-link path (rule 6, ADR 0006): token, nonce, Log, undo.

| Action | Params | Effect |
| --- | --- | --- |
| `plan` | `field`, `value` | Sets one Plan field; `field` from a fixed list; `value` a decimal or ISO date |
| `oneoff` | `month`, `amount`, `note` | Adds a OneOffs row; `revert` removes it |

Validation in the script: whitelist of fields, amounts −100,000…100,000 € with two decimals,
dates within 5 years, note ≤ 60 characters. Every change logs before/after for undo.

## 5. How the skill behaves

- **Reads, never computes:** all numbers on the card come from the Summary cells (FR-5.3). If it
  cannot read the sheet, it shows the `status` link fallback, not an estimate.
- **Facts from packs:** the benchmark (992 €), payout limit and semester fee come from pack entries
  with their source and date. `proof_months` shows ⏳ until a Kiel entry exists.
- **Asks before writing:** "Shall I set your blocked account to 11,904 €?" → one action link.
- **Plain warnings, no pressure:** "Your plan goes below zero in March." Then two options: lower a
  cost, or add income. Never shame, never panic.
- **Not financial advice:** no blocked-account providers, loans or investments are recommended.
  Refer to the Studentenwerk's social counselling or the International Center for money worries
  (referral entries to add in a later pack run).
- **Privacy:** never asks for or stores bank names, IBANs or card numbers; only amounts.

## 6. Requirements (proposed)

| ID | Requirement | Priority | Test |
| --- | --- | --- | --- |
| FR-13.1 | Budget template 1.1 adds Plan, OneOffs and Forecast tabs; nothing existing changes | Must | T |
| FR-13.2 | Forecast covers 24 months; all numbers by formula, matching `scripts/money_plan.py` | Must | T |
| FR-13.3 | Summary shows months to extension, balances at extension, required amount, top-up, save per month and first month below zero | Must | T |
| FR-13.4 | `plan` and `oneoff` action links with whitelist, validation, Log and undo | Must | T |
| FR-13.5 | The Money plan card reads only Summary cells and fits 360 px | Must | E/P |
| FR-13.6 | Default benchmark, payout and known one-offs are proposed from pack entries, with source | Must | E |
| FR-13.7 | Rules not yet confirmed for the student's city are marked "check with the immigration office" | Must | E |
| FR-13.8 | Chart or Canvas view of the forecast where the adapter says yes; card otherwise | Should | S |
| NFR-PRI.5 | No bank names, IBANs or account numbers in Plan, OneOffs or Log | Must | R/T |

## 7. Worked examples (reference model)

Invented student: plan starts Oct 2026, costs 955 €/month (rent 450, health insurance 140,
phone 15, food 250, other 100), 1,500 € free money, 900 € rent deposit in Oct 2026, semester fee
403 € in Feb and Aug 2027, permit ends Oct 2027, 12 months × 992 € needed.

| Case | Blocked at start | Job | Blocked at extension | Free at extension | Top-up | Save / month | Below zero from |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A: blocked account only | 11,904 € | 0 | 0 € | 238 € | 11,666 € | 972.17 € | Oct 2027 |
| B: 3,000 € extra | 14,904 € | 0 | 3,000 € | 238 € | **8,666 €** | 722.17 € | Jan 2028 |
| C: job 450 €/month | 11,904 € | 450 € | 0 € | 5,638 € | 6,266 € | 522.17 € | Sep 2028 |

Case B is the "3,000 € left" question: the student adds 8,666 €, not 11,904 €. (8,904 € if the free
money is not counted.)

## 8. Depends on

- **Kiel residence-permit run (P4):** how many months of proof at extension; whether remaining
  balance and job income count; documents. Until then `proof_months` = 12 with ⏳.
- **P7 sheet templates** (formulas above) and **P8 Apps Script** (`plan`, `oneoff` actions).
- **P9 skill:** a `money` intent and the card template.
- **P10 evals:** "can I afford…", top-up questions, refusal to recommend providers or loans.

## 9. Out of scope

Bank connections, importing statements, currency conversion, tax, investment advice, choosing a
blocked-account provider.

## Brief update

Add to section 2 (Decisions so far):

| Topic | Decision |
| --- | --- |
| Money plan | 24-month forecast in the student's Budget sheet (formulas only): runway, balances at the permit extension date, top-up and monthly saving target. Benchmark and payout from packs; Kiel extension rules pending. See `docs/features/money-plan.md`. |
