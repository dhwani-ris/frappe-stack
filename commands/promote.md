---
description: Promote staging changes to production via PR. Runs the pre-promote checklist, opens the PR, monitors merge → migrate.
argument-hint: [--emergency]
---

# /frappe-stack:promote

The bridge from staging to production. Routes through the `deployer` agent.

## What it does

Per `agents/deployer.md` and `skills/process/promoting-changes.md`:

1. **Pre-promote checklist** — `/frappe-stack:diff` clean, all blueprints Applied, reviewer + tester clean, backup verified, role coverage on new workflow states, sample size on experiments.
2. **Snapshot** — exporter writes per-blueprint JSONs to a timestamped feature branch in the config repo.
3. **Commit + push** — committer.py runs `git add` + commit + push to `promote/<sprint>-<feature>-<YYYYMMDD-HHMM>`.
4. **Open PR** — pr_opener.py uses `gh` CLI (or REST API fallback) against the config repo.
5. **Tag reviewer** — pings the on-call rotation.
6. **Wait for merge.**
7. **Watch CI** — backup → migrate → restart on prod.
8. **Smoke-test prod** — runs the manual checklist for the changed blueprints.

## Flags

- `--emergency` — required to promote on Friday after 14:00 or on weekends. Sets a special label on the PR; pages on-call.

## Refuses if

- Pre-promote checklist fails any box (without `--emergency`).
- Friday after 14:00 / weekend without `--emergency`.
- Bundling more than 5 unrelated blueprints (forces split into multiple PRs).
- Config repo working tree has uncommitted changes outside `fixtures/`.
- `stack_core.github_token_secret_key` not configured (PR can't be opened).

## Output

```text
Pre-promote checklist...
  ✓ /frappe-stack:diff      clean
  ✓ blueprints              4/4 Applied
  ✓ reviewer                no CRITICAL/HIGH
  ✓ tester                  14/14 pass, 87% coverage
  ✓ backup                  prod backup taken 2026-05-03 13:00:00 UTC
  ✓ role coverage           Manager has 3 users; Field Officer has 27 users
  ⚠ Friday-evening guard    14:30 — passing only because day=Wednesday

Snapshotting to branch promote/sprint-15-beneficiary-20260503-1440 ...
Pushing ...
Opening PR ...

  → https://github.com/dhwani-ris/<config-repo>/pull/123

Reviewer tagged: @<rotation-on-call>

Waiting for merge ... (will watch CI)
```

## Examples

```text
# Standard promotion (Mon-Thu, or before Fri 14:00)
/frappe-stack:promote

# Emergency promotion (paged on-call)
/frappe-stack:promote --emergency
```
