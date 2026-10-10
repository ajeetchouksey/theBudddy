# ADR 0004: Apps Script with drive.file scope only

- **Status:** Accepted, verify in spike
- **Date:** 2026-10-10
- **Source:** Decision log in `docs/technical-architecture.md`

## Context

Writes need code running in the student's account. Broad OAuth scopes trigger Google verification and unverified-app warnings that would scare students and slow setup.

## Decision

The Apps Script web app requests only `drive.file` (files it created) plus the web-app runtime. No Gmail, Calendar or full-Drive scopes. Gmail and Calendar access is granted by the student to their AI tool, not to us.

## Consequences

- The script can only touch the Germany Journey files it created.
- Spike test 6 must confirm there is no unverified-app warning; the fallback is a prefilled Google Form.
- CI checks the manifest scopes on every PR touching `apps-script/`.
