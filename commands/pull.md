---
description: Pull current site state into the local config-repo working tree as JSON files. Reads via Frappe's stock REST API. Does not auto-commit — leaves the diff for human review.
argument-hint: [--site=staging|prod] [--commit] [--push]
---

# /frappe-stack:pull

Site → git, no commit by default. Reads via stock Frappe REST.

## What it does

1. Fetches the relevant resources from the configured site:
   - `GET /api/resource/DocType?filters=[["custom","=",1]]&fields=["*"]&limit_page_length=0`
   - `GET /api/resource/Workflow?fields=["*"]&limit_page_length=0`
   - `GET /api/resource/Custom Field?fields=["*"]&limit_page_length=0`
   - `GET /api/resource/Property Setter?fields=["*"]&limit_page_length=0`
2. Writes per-resource JSON files into the configured `config_repo.local_path`:
   - `fixtures/app/doctypes/<name>.json`
   - `fixtures/app/workflows/<name>.json`
   - `fixtures/app/custom_fields.json`
   - `fixtures/app/property_setters.json`
3. Reports: which files changed, plus a `git diff --stat` summary.
4. **Stops there.** User inspects the diff and either commits manually or runs `/frappe-stack:promote`.

## Flags

- `--site=staging` — default.
- `--site=prod` — read-only, safe.
- `--commit` — commits the working tree changes locally with an auto-generated message. Does not push.
- `--push` — implies `--commit`, also pushes to a feature branch (not main).

## Refuses if

- Working tree has uncommitted changes that conflict with what would be written.
- `config_repo.local_path` not configured (run `/frappe-stack:init` first).
- Network error on the API call (after 3 retries with exponential backoff).
- 401/403 from Frappe — the API user lacks read permission for one of the resource types.

## Examples

```text
/frappe-stack:pull
/frappe-stack:pull --commit
/frappe-stack:pull --commit --push
/frappe-stack:pull --site=prod
```
