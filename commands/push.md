---
description: Apply local config-repo state to staging via Frappe's stock REST API. Refuses on production. Idempotent.
argument-hint: [--site=staging] [--dry-run]
---

# /frappe-stack:push

Git → site (staging only). Production is git-only via `/frappe-stack:promote` PRs.

## What it does

1. Reads `fixtures/app/doctypes/*.json` and `fixtures/app/workflows/*.json` from `config_repo.local_path`.
2. For each resource, calls the right Frappe REST endpoint:
   - DocType: `PUT /api/resource/DocType/<name>` if it exists, else `POST /api/resource/DocType`.
   - Workflow / Custom Field / Property Setter / Dashboard / Report: same upsert pattern.
3. Each resource is upserted: existing records updated, missing ones created.
4. Idempotent — re-running has no extra effect if the state already matches.

## Flags

- `--site=staging` — default and only allowed value.
- `--dry-run` — calls `/frappe-stack:diff` internally and surfaces the `only_in_git` and `changed` buckets without applying.

## Refuses if

- Target site has `is_production=true`.
- Working tree has uncommitted changes.
- Any resource fails Frappe validation (the plugin surfaces the error and stops).

## Examples

```text
/frappe-stack:push
/frappe-stack:push --dry-run
```
