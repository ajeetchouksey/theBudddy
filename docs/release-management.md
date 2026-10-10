# Germany Student Companion — Release Management

Oct 10, 2026 · @Ajeet Chouksey

## Release model

Two channels and a weekly train: facts can move fast, but anything that changes how the companion behaves goes out on a schedule.

| Channel | Fed by | Who uses it | Promoted to stable when |
| --- | --- | --- | --- |
| `next` | Every merge to `main` (`build-next`) | Maintainers, testers, eval runs | Release checklist passes |
| `stable` | Signed tag `vX.Y.Z` (`release`) | Pilot students, later everyone | — |

**Cadence**

| Release type | When | Contains | Approval |
| --- | --- | --- | --- |
| Weekly train | Fridays during the pilot | Skill, adapters, packs, templates | 1 maintainer + green gates |
| Packs-only | Any weekday | Fact fixes and new entries only | 1 maintainer |
| Hotfix | Any time | S1/S2 fixes (see Security Plan) | 2 maintainers; `critical` notice if students must act |

**Freeze:** no skill, adapter or template change in the 48 hours before a pilot milestone (G3 on 8 Nov, pilot start on 9 Nov, review on 23 Nov); packs-only fixes are still allowed.

## What ships and how it reaches students

Only packs update without the student doing anything; the skill and the script need a student action. So skill and script releases must be rare, backward compatible and clearly announced.

| Artefact | Version | Reaches the student by | Student action | Rule that follows |
| --- | --- | --- | --- | --- |
| Packs (live) | Date per layer | Drive shortcut to the public folder | None | Packs-only releases can go any day |
| Packs (bundled snapshot) | Same date, inside the skill build | Next skill re-import | Re-import | Snapshot is the floor; live packs carry urgent fixes |
| Skill package (per tool) | SemVer | Re-import or re-upload in the AI app | Re-import (1–2 min) | Minor/patch must work with the previous template and script |
| Adapters | `schema` + `last_verified` | Inside the skill package | Re-import | Ship with the skill |
| Sheet templates | Major.minor | Sheet menu "Update template" | One tap | Never touches data tabs; majors include a migration |
| Action-link script | SemVer, in `index.md` | "Update template" redeploys from the released source | One tap + Google consent if scopes changed | Scopes never change in MVP 1; old links keep working for one major |
| `latest.json` | Release tag | Fetched where the tool can | None | Tells students when a re-import or update is worth doing |
| MCP server (phase 2) | SemVer | Deploy | None | Read-only; old tool names kept for one major |

**Compatibility rule:** any stable skill must work with the current and the previous minor version of the template and script, so a student who skips one update loses nothing.

## Release process

Five stages from cut to follow-up; every stage has an owner and a check that must pass before the next starts. The `release-manager` developer skill prepares stages 1–2; people do stages 3–5.

**1 · Cut (Thursday)**

- [ ] `release-manager` opens a release PR: version bumps, changelog, draft `latest.json`, list of changed facts.
- [ ] Confirm nothing in the release PR touches scopes, data-contract renames or the guardrail block without an ADR.

**2 · Verify (Thursday)**

- [ ] `validate` green on the release PR; no entries past `expires`.
- [ ] `evals` on `next` for every tool and plan in the adapters: ≥ 45/50 factual on Gemini, all guardrail zero-tolerance sets pass.
- [ ] Install the `next` build fresh on one test account per tool; run the smoke script: setup, `done`, `expense`, undo, `status`, `handover`, switch tools.
- [ ] Template and script: update an existing test Journey from the previous version; data tabs unchanged.

**3 · Approve (Friday morning)**

- [ ] Maintainer reviews the changelog and fact diff; approves the release PR.
- [ ] For `critical` notices or hotfixes, a second maintainer approves.

**4 · Publish (Friday)**

- [ ] Maintainer pushes the signed tag; `release` workflow builds from the tag and publishes after the `production` environment approval.
- [ ] Check: checksums attached; public packs folder updated; `latest.json` live; skill zips downloadable.

**5 · Follow up (Friday–Monday)**

- [ ] Post student-facing notes to the pilot group (see section 6).
- [ ] Watch issues and pilot feedback for 72 hours; any S1/S2 → hotfix path.
- [ ] Close the milestone; move unfinished items to the next train.

## Roles and approvals

AI agents prepare; people approve and publish. Until a second maintainer joins, every two-person step is a gap to close (Security Plan, first open item).

| Step | Release manager (maintainer) | Second maintainer | Content reviewer (layer CODEOWNER) | AI agents |
| --- | --- | --- | --- | --- |
| Release PR and changelog | Approves | — | — | Prepares (`release-manager`) |
| Fact changes | Informed | — | Approves per layer | Draft and pre-check (`pack-author`, `pack-reviewer`) |
| Evals and smoke tests | Runs or supervises | — | — | Run (`eval-runner`) |
| Signed tag and publish | Does | — | — | Never |
| `critical` notice | Proposes | Approves | Confirms the fact | Drafts text |
| Hotfix | Leads | Approves | If a fact | Drafts fix |
| Scope or data-contract change | Proposes ADR | Approves | — | Never on their own |

## Hotfix and rollback

Rollback is easy for anything we host and hard for anything the student has installed, so fixes for installed parts go forward, never backward.

| Artefact | Rollback | Fix forward | Time to students |
| --- | --- | --- | --- |
| Packs (live) | Re-publish the previous tag's packs to the public folder | Packs-only release with the corrected entry | Minutes to hours (Drive sync) |
| `latest.json` | Re-publish previous file | New file with `critical` | Next chat on tools that fetch |
| Skill package | Mark the release as bad; `latest.json` points to the previous one | Patch release + `critical` asking students to re-import | When students re-import |
| Template | Not possible in place | "Update template" to a patch version | When students tap update |
| Action-link script | Not possible in place | Patch via "Update template"; if dangerous, ask students to rotate the token, which disables old links | When students tap update |
| MCP server (phase 2) | `wrangler rollback` to the previous Worker version | Patch deploy | Immediate |

**Hotfix path**

1. Branch `hotfix/<issue>` from the last stable tag.
2. Fix, with a new test or eval that fails before the fix.
3. `validate` + targeted evals + smoke script on one tool.
4. Second-maintainer approval; tag `vX.Y.Z+1`; publish.
5. Merge the hotfix back to `main`; post-incident review within a week.

## Release notes and communication

Every release has two sets of notes: a technical changelog for contributors and a short student note that says only what changes for them.

**Changelog (`CHANGELOG.md`, Keep a Changelog format):** Added, Changed, Fixed, Facts (with entry IDs and sources), Security. Generated from Conventional Commit messages, edited by the release manager.

**Student note (pilot group and `latest.json` `notes`), at most 5 lines:**

```markdown
**Companion update · {date}**
- {what's new or fixed, in plain words}
- {fact change that affects them, with the old → new value}
Do you need to do anything? {No. | Re-add the skill in your AI app (2 min). | Tap "Update template" in your Checklist sheet.}
```

**`critical` notices** follow the same shape, start with "Important:", and say exactly what the student must do and by when.

## Release calendar

Three internal releases on `next` lead to v1.0.0 on Friday 6 November, two days before G3; the pilot then gets two weekly patches.

&#91;embedded content: release calendar · 6 releases, 4 gates\]

| Release | Channel | Main content |
| --- | --- | --- |
| v0.1.0 | next | Repo scaffold, schemas, CI, first national packs, adapters from the spike |
| v0.2.0 | next | Schleswig-Holstein, Kiel and CAU packs; top 10 letters; eval set v1 |
| v0.3.0 | next | Starter kit and action-link script; setup flow |
| v1.0.0 | stable | Skill packages for 3 tools; G3 evals passed; pilot release |
| v1.0.1, v1.0.2 | stable | Pilot fixes; packs-only releases in between as needed |

Freeze for v1.0.0 runs from Wednesday 4 November; after that, only packs-only fixes and S1/S2 hotfixes.
