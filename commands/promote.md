---
description: Promote staging changes to production via PR. Runs the pre-promote checklist, opens the PR, monitors merge → your CI runs bench migrate.
argument-hint: [--emergency]
---

# /frappe-stack:promote

The bridge from staging to production. Routes through the `deployer` agent.

## What it does

Per `agents/deployer.md` and `skills/process/promoting-changes.md`:

1. **Pre-promote checklist** — `/frappe-stack:diff` clean, all blueprints reflected in git, reviewer + tester clean, backup verified, role coverage on new workflow states, sample size on experiments.
2. **Snapshot** — exporter writes per-blueprint JSONs to a timestamped feature branch in the config repo (uses Frappe's stock REST for read).
3. **Commit + push** — `git add` + commit + push to `promote/<sprint>-<feature>-<YYYYMMDD-HHMM>`.
4. **Open PR** — `gh` CLI (or REST API fallback) against the config repo.
5. **Tag reviewer** — pings the on-call rotation.
6. **Wait for merge.**
7. **Watch your CI** — your existing pipeline on the config repo's `main` branch runs `bench backup` → `bench migrate` → `bench restart` against prod.
8. **Smoke-test prod** — runs the manual checklist for the changed blueprints.

## Flags

- `--emergency` — required to promote on Friday after 14:00 or on weekends. Sets a special label on the PR; pages on-call.

## Refuses if

- Pre-promote checklist fails any box (without `--emergency`).
- Friday after 14:00 / weekend without `--emergency`.
- Bundling more than 5 unrelated blueprints (forces split into multiple PRs).
- Working tree has uncommitted changes outside `fixtures/`.
- GitHub token not configured (PR can't be opened).

## Examples

```text
/frappe-stack:promote
/frappe-stack:promote --emergency
```

## Note on production deploys

`/frappe-stack:promote` only opens the PR. The actual `bench migrate` on production is run by **your CI/CD pipeline** on PR merge. Setting that up is the operator's responsibility — typically a GitHub Actions workflow on the config repo that SSHes into the bench host. The plugin doesn't ship this; it leaves the production-deploy machinery to your existing process.
