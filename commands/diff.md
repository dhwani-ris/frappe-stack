---
description: Show structured drift between site state (read via Frappe's stock REST) and the configured config-repo HEAD. Three buckets — only on site, only in git, changed.
argument-hint: [--site=staging|prod]
---

# /frappe-stack:diff

The drift detector. Run before any promote, or any time the site might have diverged from git.

## What it does

1. Fetches current site state via stock Frappe REST (same calls as `/frappe-stack:pull`, but without writing files).
2. Reads the configured `config_repo.local_path` HEAD.
3. Compares the two. Returns three lists:
   - **only_on_site** — resources created on the site that aren't in git.
   - **only_in_git** — resources in git that haven't been applied.
   - **changed** — same name, different payload.

## Flags

- `--site=staging` — default.
- `--site=prod` — useful for confirming prod matches the merged config-repo HEAD.

## Output

```text
Diff: site=https://staging.example.com  vs  config-repo=main@<sha>

  only_on_site:    1
    - DocType "Quick Test"           (someone built it directly on the desk)
  only_in_git:     0
  changed:         1
    - DocType "Beneficiary"          (3 fields differ)
        site:  age = Int (no constraint)
        git:   age = Int (non_negative=1)

Summary: 2 differences. Resolve before /frappe-stack:promote.
```

## Resolving conflicts

Pick a direction per resource. If the site is canonical: `/frappe-stack:pull`. If git is canonical: `/frappe-stack:push` (staging only). The diff refuses to auto-resolve.

## Refuses if

- `config_repo.local_path` not configured.
- Git working tree has uncommitted changes.

## Examples

```text
/frappe-stack:diff
/frappe-stack:diff --site=prod
```
