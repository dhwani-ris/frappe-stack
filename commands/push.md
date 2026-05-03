---
description: Apply local config-repo state to staging. Refuses on production. Idempotent — safe to re-run.
argument-hint: [--site=staging] [--dry-run]
---

# /frappe-stack:push

Git → site (staging only). Production is git-only via `/frappe-stack:promote` PRs.

## What it does

1. Reads `fixtures/app/doctypes/*.json` and `fixtures/app/workflows/*.json` from `config_repo.local_path`.
2. For each, calls `stack_core.git_bridge.applier.apply_from_working_tree` on the site.
3. Each blueprint is upserted: existing → version++ + payload replaced; missing → created with status=Applied.
4. The applier is idempotent — re-running has no extra effect if the state already matches.

## Flags

- `--site=staging` — default and only allowed value. Refuses any other.
- `--dry-run` — shows what *would* be applied without doing it. Calls `stack_core.api.diff.diff` and surfaces the `only_in_git` and `changed` buckets.

## Refuses if

- Target site has `is_production=1` in stack_core config.
- Config-repo working tree has uncommitted changes (avoid pushing half-baked state).
- Any blueprint fails its guardrails on the site (the applier surfaces the error and stops).

## Output

```text
Applying 4 blueprints to staging (https://staging.example.com)...
✓ Beneficiary               (new)
✓ Grant                     (version 1 → 2)
✓ Beneficiary Approval      (workflow, version 1)
✓ field_officer on Grant    (custom field)

All blueprints applied. status=Applied.
Site state now matches config-repo HEAD (commit <sha>).
```

## Examples

```text
# Apply current local state to staging
/frappe-stack:push

# See what would happen without applying
/frappe-stack:push --dry-run
```
