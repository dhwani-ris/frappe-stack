---
description: Pull current site state into the local config-repo working tree as JSON fixtures. Does not auto-commit — leaves the diff for human review.
argument-hint: [--site=staging|prod] [--commit] [--push]
---

# /frappe-stack:pull

Site → git, no commit by default.

## What it does

1. Calls `stack_core.api.fixtures.export` on the site.
2. Runs `stack_core.git_bridge.exporter` against the configured `config_repo.local_path`.
3. Per-blueprint JSON files written under `fixtures/app/doctypes/`, `fixtures/app/workflows/`, etc.
4. Reports: which files changed, `git diff --stat` output.
5. **Stops there.** User inspects the diff and either commits manually or runs `/frappe-stack:promote`.

## Flags

- `--site=staging` — default. Pulls from the staging site.
- `--site=prod` — pulls from production. Read-only, safe.
- `--commit` — commits the working tree changes locally with an auto-generated message. Does not push.
- `--push` — implies `--commit`, also pushes to a feature branch (not main).

## Refuses if

- Working tree has uncommitted changes that conflict with what would be written. (Surfaces the conflict, asks the user to stash/commit first.)
- `config_repo.local_path` not configured.
- Network error on the API call (after 3 retries with backoff).

## Output

```text
Pulled 3 blueprints from staging (https://staging.example.com).
Files written:
  fixtures/app/doctypes/beneficiary.json (modified)
  fixtures/app/workflows/beneficiary_approval.json (new)
  fixtures/app/custom_fields.json (modified)

Run `git diff` to review. Then either:
  - /frappe-stack:promote   to open a PR
  - git commit              to commit locally
  - git stash               to discard
```

## Examples

```text
# Default — pull staging, leave for review
/frappe-stack:pull

# Pull and auto-commit
/frappe-stack:pull --commit

# Pull, commit, push to a feature branch
/frappe-stack:pull --commit --push

# Pull from prod (read-only — useful for "what's actually on prod right now?")
/frappe-stack:pull --site=prod
```
