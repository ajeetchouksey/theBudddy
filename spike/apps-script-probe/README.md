# Apps Script probe (spike tests 6, 7, 20)

Throwaway web app that answers one question: can a script with **only** the `drive.file` scope
create a sheet and write to it through the Sheets API, without the "Google hasn't verified this
app" screen? It also checks long links and nonce replay. The real action-link app is task P8.

## Deploy (about 5 minutes, in the browser)

Use the **test** Google account, never a personal one with real data.

1. Open script.google.com → **New project**. Name it `Spike probe`.
2. Project Settings (gear) → tick **Show "appsscript.json" manifest file in editor**.
3. Replace `appsscript.json` with the one in this folder. Replace `Code.gs` with `Code.js` from
   this folder (paste the contents).
4. Services (+) → if the editor asks, confirm **Google Sheets API** v4 is added (the manifest
   already lists it).
5. **Deploy → New deployment → Web app**. Execute as: **Me**. Who has access: **Only myself**.
6. Copy the web app URL (`https://script.google.com/macros/s/…/exec`).

With `clasp` instead: `clasp create --type webapp --title "Spike probe"`, copy both files in,
`clasp push`, `clasp deploy`.

## Run test 6

1. Open `<web app URL>?a=setup`. **Screenshot the consent screen.** Record:
   - which permissions it lists (expected: only files this app creates)
   - whether "Google hasn't verified this app" appears
2. Expected page: "Created with drive.file only". A sheet `Spike probe` appears in Drive.
3. Open `?a=write&n=test-1` → "Written". Open it again → "Already done" (idempotency).
4. Open `?a=status` → `PROBE-STATUS-OK · rows: 1`.
5. Open the URL in a private window (signed out) → it must **not** write (Only myself).

## Use with the probe skill

Run `python spike/make_probe_packages.py --webapp-url <web app URL>` so the probe skill's
`probe link` and `probe write <n>` print links to your deployment.

## Clean up after G1

Archive the deployment, delete the project and the `Spike probe` sheet, and remove the app's
access under myaccount.google.com → Security → Third-party apps and services.
