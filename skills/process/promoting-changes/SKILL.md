---
name: promoting-changes
description: Use when staging changes are ready to ship to production. Walks through the pre-promote checklist, runs the reviewer + tester agents, and opens the promotion PR. Triggers on phrases like "promote to prod", "ship this", "deploy", "go live", "release".
---

# Promoting changes — staging → production

Staging is the playground. Production is git-only. Promotion is the only way changes land on prod.

## Pre-promote checklist (refuse if any fails)

```
□ /frappe-stack:diff shows site == staging-config-repo (no drift)
□ All Stack Blueprint rows on staging have status=Applied (none Failed/Validating)
□ Reviewer agent ran clean (no CRITICAL/HIGH issues)
□ Tester agent ran clean (≥80% coverage on changed code, all tests pass)
□ For workflow changes: new states have at least 1 user with the role
□ For schema changes: backup verified within last 24h
□ For experiment promotions: significance check passes (CI doesn't cross 0)
```

The `deployer` agent runs this checklist. Any failure = refuse + surface the failed box.

## The flow (no shortcuts)

```
  staging                  config repo               prod
  ─────────                 ─────────────              ──────
  /pull → working tree
                            git add + commit
                            git push branch
                            gh pr create (PR opens)
                                  ↓
                            (human review + approve)
                                  ↓
                            merge to main
                                  ↓                    ↑
                            CI: bench migrate ─────────┘
                                                       (idempotent applier
                                                        upserts blueprints)
                                                       prod state matches git
```

## PR body the deployer generates

```markdown
## Summary
Promote 3 changes from staging.

## Blueprints changed
| Name | Type | Action |
|------|------|--------|
| Beneficiary           | DocType    | new        |
| Beneficiary Approval  | Workflow   | new        |
| field_officer (Custom Field on Grant) | Custom Field | new |

## Audit log
- 2026-05-03 14:22:11 user@example.com api.build_doctype Beneficiary success
- 2026-05-03 14:23:05 user@example.com api.build_workflow Beneficiary Approval success
- 2026-05-03 14:23:48 user@example.com api.build_custom_field grant_field_officer success

## Tests
- Reviewer agent: ✓ no CRITICAL / HIGH
- Tester agent:  ✓ 14/14 tests pass, 87% coverage on changed lines
- Semgrep: ✓ no findings
- pip-audit: ✓ no high/critical CVEs

## Rollback
`bench --site prod restore <backup-id>` (taken 2026-05-03 13:00:00 UTC).

## Reviewer
@<rotation-on-call>
```

## The merge → migrate handshake

CI workflow on `main` merge runs:

```bash
bench --site prod backup
bench --site prod migrate          # idempotent applier upserts blueprints
bench --site prod restart
```

If migrate fails, CI:
1. Restores the backup automatically.
2. Reverts the merge (or comments the PR with a force-push request).
3. Pages the deployer.

## Anti-patterns

- **Promoting Friday afternoon.** Deferred until Monday morning unless explicitly emergency.
- **Bundling 10 unrelated changes** in one PR. Hard to roll back. One blueprint family per PR.
- **Skipping the diff check** ("it's just a tiny change"). The differ catches drift you forgot about. Always run it.
- **Force-merging without an approval.** Branch protection on `main` is non-negotiable; the bypass is logged and reviewed.

## Emergency rollback

If a bad change reaches prod despite the checklist:

```text
/frappe-stack:rollback --to <git-sha>
```

The applier picks up the older blueprint payloads; `bench migrate` upserts; site state matches the older git SHA. Audit log row written for the rollback action.
