# Walkthrough 4 — Your first promotion to production

**Audience:** PM with a stable feature on staging, ready for prod.
**Time:** ~15 minutes (active) + waiting on review/CI.
**Prerequisites:** All previous walkthroughs.

## Goal

Promote everything from Walkthroughs 1–3 to production with a clean PR, code review, and idempotent migrate.

## Step 1 — Final QA on staging

Before promoting, run the full QA dance:

```text
/frappe-stack:review --since=origin/main
```

This runs `reviewer` + `tester` in parallel. Output:

```text
reviewer: 0 CRITICAL, 0 HIGH, 1 MEDIUM (a magic number in your custom field default), 3 LOW
tester:   14/14 tests pass, 87% coverage on changed lines

Recommendation: ✓ ready to promote.
```

If any CRITICAL or HIGH: fix first. If MEDIUM: optional — fix or note in the PR.

## Step 2 — Diff check

```text
/frappe-stack:diff
```

```text
Diff: site=https://staging.example.com  vs  config-repo=main@<sha>

  only_on_site:    0
  only_in_git:     0
  changed:         0

Summary: clean. Ready to promote.
```

If anything appears here, resolve before continuing — see [the git-roundtrip skill](../../skills/process/git-roundtrip/SKILL.md) for conflict resolution.

## Step 3 — Promote

```text
/frappe-stack:promote
```

The `deployer` agent runs:

```text
Pre-promote checklist...
  ✓ /frappe-stack:diff      clean
  ✓ blueprints              5/5 Applied
  ✓ reviewer                no CRITICAL/HIGH
  ✓ tester                  14/14 pass, 87% coverage
  ✓ backup                  prod backup taken 13:00 UTC
  ✓ role coverage           Manager(3), Field Officer(27), Program Officer(8)
  ✓ Friday-evening guard    Wednesday 14:30, fine

Snapshotting to branch promote/sprint-15-beneficiary-20260503-1432 ...
Pushing ...
Opening PR ...

  → https://github.com/dhwani-ris/<config-repo>/pull/124

Reviewer tagged: @<rotation>
```

## Step 4 — Wait for review

Reviewer reads the PR (the `documenter` agent has filled it with: blueprints changed, audit-log excerpt, test results, rollback command). They approve or request changes.

If changes requested: deployer surfaces them, you fix on staging, re-run `/frappe-stack:review`, re-run `/frappe-stack:diff`, then `/frappe-stack:promote` again. The PR gets new commits.

## Step 5 — Merge → prod migrates

Once merged, CI runs:

```bash
bench --site prod backup
bench --site prod migrate    # applier upserts blueprints; idempotent
bench --site prod restart
```

Deployer watches for migrate failure. If anything errors, automatic rollback:

```bash
bench --site prod restore <backup-id>
gh pr revert <pr-number>
```

## Step 6 — Smoke-test prod

For the changed blueprints, run the manual checklist from [`process/running-qa`](../../skills/process/running-qa/SKILL.md):

- Open Beneficiary list view on prod. Loads, columns visible.
- Click into one row. Workflow toolbar appears. Transitions are role-gated correctly.
- Open the dashboard. Cards populate.
- Spot-check the experiment dashboard. Assignments are accumulating.

If clean, declare success.

## Step 7 — Tag the release

```text
/frappe-stack:ship v0.1.0
```

This tags `main` at `v0.1.0`, updates `CHANGELOG.md`, optionally posts release notes to Slack.

## What I refused to do

- Promote with any CRITICAL or HIGH from reviewer.
- Promote on Friday after 14:00 (without `--emergency`).
- Bundle 10 unrelated changes in one PR (forces split).
- Skip the diff check.
- Force-merge to bypass branch protection.

## You're done

Production is now in lock-step with git. Future changes follow the same path: build on staging → `/frappe-stack:review` → `/frappe-stack:promote` → merge → migrate → tag.
