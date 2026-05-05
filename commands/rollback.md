---
description: Roll the staging site back to a previous config-repo commit. Reapplies the older per-blueprint JSONs via stock Frappe REST. Idempotent.
argument-hint: <git-ref> [--site=staging] [--dry-run]
---

# /frappe-stack:rollback

Sometimes a PM builds something on staging that turns out wrong — a bad workflow transition, a permission misstep, a fieldtype that doesn't fit. The fix is to rewind staging to a known-good config-repo commit.

This is the equivalent of what a developer does with `git checkout <ref> && bench migrate`.

## What it does

1. Reads the per-blueprint JSONs from the given git ref in the config-repo.
2. Computes a diff against the current site state.
3. For each resource that needs to change, calls the stock Frappe REST endpoint:
   - `PUT /api/resource/<DocType>/<name>` to update
   - `DELETE /api/resource/<DocType>/<name>` only if the older state didn't have the resource (and the resource is *not* audit-tagged — see refusals)
4. Writes a row to `.frappe-stack/audit.jsonl` capturing the rollback action and the diff applied.

## Arguments

- `<git-ref>` — required. Any git ref the local config-repo can resolve: a commit SHA, branch name, tag, or `HEAD~3`.
- `--site=staging` — default and only allowed value for the destructive path. (`--site=prod --dry-run` is allowed for inspection.)
- `--dry-run` — shows the diff that would be applied without doing anything.

## Refuses if

- Target site is `is_production=true` (production rolls back through reverting the merge in GitHub, not via this command).
- Working tree is dirty (commit or stash first).
- Any resource being rolled-back-and-deleted is audit-tagged (`Stack Audit Log`-equivalents, `Experiment Assignment`). Manual cleanup required for those.
- The git ref doesn't exist or doesn't contain a `fixtures/app/` tree.
- The DeployControl GitHub token has expired (need a fresh one to read the config-repo even if local).

## Output

```text
Rolling back staging to commit a1b2c3d (5 commits ago, "promote: beneficiary form v2")...

Plan (3 changes):
  ~ DocType "Beneficiary"           field 'age' constraint changed
  ~ Workflow "Beneficiary Approval" transition Draft -> Approved removed
  - Custom Field "field_officer on Grant"  (this resource didn't exist at a1b2c3d)

Apply? [y/N]
```

The plan is shown before any mutation. Confirm explicitly to proceed.

## When to use this vs `/frappe-stack:push`

| Situation | Use |
|---|---|
| Apply current config-repo HEAD to staging (forward) | `/frappe-stack:push` |
| Apply an older config-repo commit to staging (rewind) | `/frappe-stack:rollback <commit>` |
| Revert a production change | revert the merge in GitHub; CI re-runs `bench migrate` against the reverted state |

## Examples

```text
# Roll staging back to the last successful promote
/frappe-stack:rollback HEAD~1

# Inspect what a rollback would do without doing it
/frappe-stack:rollback v0.1.2 --dry-run

# Rewind to a specific known-good commit
/frappe-stack:rollback a1b2c3d
```
