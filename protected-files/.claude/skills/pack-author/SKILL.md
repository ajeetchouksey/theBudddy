---
name: pack-author
description: Draft sourced knowledge-pack entries for the Germany Student Companion. Use when asked to add or update facts for a topic, layer (national, state, city, university) or letter type.
---

# Pack author

## Before you start
1. Read knowledge/_schema/fact.json and every existing entry for the topic in all layers.
2. Confirm topic, layer, scope and phase with the requester if any is missing.

## Sources
- Use official sources only: federal, state, city and university sites, the AStA, the Studierendenwerk.
- Never use blogs, forums, agencies or AI answers as a source_url.
- If no official source states the fact, do not write the entry. List it under "Could not source".

## Writing entries
- One fact per entry. id = <scope>.<topic>.<slug>.
- Plain English at B1. Short sentences. Explain German terms the first time.
- No personal data, no example names or numbers from real people.
- Set last_verified to today. Leave reviewer empty.
- Set expires to 6 months ahead, or sooner if the source says the rule changes.
- Use the most specific layer that the source covers. Don't copy a national fact into a city file.

## Checks before the PR
- Run: make validate (yamllint, schema and content rules)
- Run: lychee <changed files>

## Pull request
- Title: "packs(<scope>): <topic>"
- Body: one line per entry with its source_url and a quote under 15 words showing the fact.
- Section "Could not source" with each missing fact and where you looked.
- Request review from the CODEOWNERS for that layer. Never approve or merge.
