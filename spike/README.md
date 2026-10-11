# Spike kit (week 1, 12–18 Oct 2026)

Everything needed to run the 21 tests in `docs/spike-results.md`. Throwaway: after G1 the
results live in the adapters and this folder can be deleted.

| Item | For tests | What it is |
| --- | --- | --- |
| `probe-skill/` | 1–5, 7–11, 13–17, 20, 21 | A tiny skill that answers `probe …` commands with known codes |
| `probe-skill/drive/probe-pack.md` | 3 | File to put in a shared Drive folder (not part of the skill) |
| `probe-latest.json` | 4, 17 | File to publish at a public URL |
| `apps-script-probe/` | 6, 7, 20 | Web app with only the `drive.file` scope |
| `make_probe_packages.py` | 1, 14–16 | Builds the zips, the Copilot files and the limits packages |

Codes the tools must return **exactly**:

| Code | Where it lives |
| --- | --- |
| `PROBE-REF-7Q2K` | `probe-skill/reference/probe-facts.md` |
| `PROBE-DRIVE-3M8X` (then `…3M8Y`) | `probe-skill/drive/probe-pack.md` in Drive |
| `PROBE-FETCH-9D4W` | `probe-latest.json` at a public URL |
| `PROBE-MAIL-5H2T` | Body of a mail you send yourself, subject `Spike letter` |
| `PROBE-CANVAS-2K6R` | `probe-skill/reference/probe-dashboard.html` |
| `PROBE-END-…` | End of each limits file; listed in `build/spike/limits-answers.md` |

## Prepare (about 20 minutes)

1. **Apps Script probe:** deploy it as in `apps-script-probe/README.md`. Copy the web app URL.
2. **Public fetch URL:** publish `spike/probe-latest.json` somewhere public over https. If the
   repo is public: `https://raw.githubusercontent.com/ajeetchouksey/theBudddy/main/spike/probe-latest.json`.
   Otherwise a GitHub Gist (raw link) works.
3. **Build the packages:**
   ```
   python spike/make_probe_packages.py --webapp-url <web app URL> --fetch-url <public URL>
   ```
   Output in `build/spike/` (not committed).
4. **Drive pack:** on a second Google account, make a folder `Spike packs`, put
   `probe-skill/drive/probe-pack.md` in it, share it with the test account (viewer). On the test
   account, add a shortcut to it in My Drive.
5. **Mail:** from another account, send the test account a mail with subject `Spike letter` and
   body `PROBE-MAIL-5H2T`.
6. **Sheet for test 5:** a sheet `Spike checklist` with columns `task_id, status` and rows
   `t1, open` and `t2, open`.

## Run

Follow the test cards in `docs/spike-results.md`. Log each result as a **Spike result** issue with
screenshots, then fill in the grid.

## Rules

- Test accounts only. No real names, addresses, ID numbers or mail in any test.
- A code the tool cannot return exactly is a fail, even if the answer looks plausible.
- A capability is `yes` only with an issue link as evidence.
