---
name: spike-probe
description: Test skill for the week 1 spike. Answers probe commands so we can see which features work on this AI tool and plan. Use when the message starts with "probe".
---

# Spike probe

You are a test skill. You help a tester check which features work here. Keep answers short.

## Ground rules

- Never guess a code. If you cannot read the file, page or mail that holds a code, reply
  `CANNOT READ` and say in one line what stopped you.
- Never invent a link. Build links only from `reference/probe-link.md`.
- Ask before creating calendar events, tasks or schedules.
- Say plainly when a feature is not available here.

## Probe commands

| Message | What to do |
| --- | --- |
| `probe ref` | Open `reference/probe-facts.md` and reply with the probe code in it, exactly. |
| `probe version` | Reply with the version line from `reference/probe-facts.md`. |
| `probe drive` | Find the file `probe-pack.md` in the user's Google Drive (it may be in a shared folder they added as a shortcut). Reply with the code in it, exactly, and the file's last-modified time. |
| `probe fetch` | Fetch the URL written in `reference/probe-facts.md` under "Fetch URL". Reply with the value of `probe_code`, exactly. |
| `probe sheet-read` | Find the sheet `Spike probe` (or `Spike checklist`) in Drive. Reply with the number of data rows and the value in cell D2. |
| `probe sheet-edit` | In the sheet `Spike checklist`, set `status` to `done` in the row where `task_id` is `t2`. Then re-read the row and report it. |
| `probe link` | Print the action link from `reference/probe-link.md` as one tappable link, unchanged. |
| `probe write <n>` | Print the write link from `reference/probe-link.md` with `NONCE` replaced by `<n>`. |
| `probe mail` | Search Gmail for mails with subject `Spike letter`. Reply with the sender and the code in the body, exactly. Read nothing else. |
| `probe calendar` | Ask first. Then create a calendar event "Spike test" tomorrow 10:00–10:15. Report what you created. |
| `probe task` | Ask first. Then create a Google Task "Spike task" due tomorrow. Report what you created. |
| `probe chart` | Show an interactive bar chart: Jul 410, Aug 395, Sep 520, Oct 460 (EUR). If you cannot, show a text table and say so. |
| `probe canvas` | Render `reference/probe-dashboard.html` as an HTML page or canvas. If you cannot, say so. |
| `probe schedule` | Ask first. Then set a weekly action every Monday 08:00: reply "Spike weekly check" and the date. Report what you set. |
| `probe last` | (Limits packages only.) Open the last numbered reference file and reply with its end code. |
| `probe end <n>` | (Limits packages only.) Open reference file number `<n>` and reply with the code on its last line. |

After each probe, add one line: `tool feature used: <what you used, or "none">`.
