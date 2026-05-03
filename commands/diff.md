---
description: Show the structured drift between site state and the configured config-repo HEAD. Three buckets — only on site, only in git, changed.
argument-hint: [--site=staging|prod]
---

# /frappe-stack:diff

The drift detector. Run before any promote, or any time the site might have diverged from git.

## What it does

1. Calls `stack_core.api.diff.diff` on the configured site.
2. The diff API itself calls `stack_core.api.fixtures.export` (current site state) and `git_bridge/differ.py` (compared against `config_repo.local_path` HEAD).
3. Returns three lists:
   - **only_on_site** — blueprints created on the site that aren't in git.
   - **only_in_git** — blueprints in git that haven't been applied.
   - **changed** — same name, different payload.

## Flags

- `--site=staging` — default.
- `--site=prod` — useful for confirming prod matches the merged config-repo HEAD.

## Output

```text
Diff: site=https://staging.example.com  vs  config-repo=main@<sha>

  only_on_site:    1
    - "Quick Test DocType"          (Stack Author created it on the UI)
  only_in_git:     0
  changed:         1
    - "Beneficiary"                  (3 fields differ)
        site:  age=Int(non_negative)
        git:   age=Int (no constraint)

Summary: 2 differences. Resolve before /frappe-stack:promote.
```

## Resolving conflicts (`changed` bucket)

Pick a direction per blueprint:

```text
# If site is canonical:
/frappe-stack:pull          # overwrites git with site state

# If git is canonical:
/frappe-stack:push          # overwrites site with git state (staging only)
```

Never both. The differ refuses to auto-resolve.

## Refuses if

- `config_repo.local_path` not configured.
- Git working tree has uncommitted changes (would confuse the comparison).

## Examples

```text
# Standard drift check
/frappe-stack:diff

# Verify prod matches the latest merge
/frappe-stack:diff --site=prod
```
