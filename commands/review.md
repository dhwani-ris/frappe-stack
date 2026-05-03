---
description: Pre-promote review. Runs reviewer + tester agents in parallel, surfaces issues, blocks promote on CRITICAL/HIGH.
argument-hint: [--blueprint=<name>] [--since=<git-ref>]
---

# /frappe-stack:review

Standalone review without promoting. Useful when iterating on a build before deciding to ship.

## What it does

Runs `reviewer` + `tester` in parallel against either:

- A single blueprint (`--blueprint=Beneficiary`), or
- Everything changed since a git ref (`--since=main`).

Outputs the combined report. Does **not** open a PR, does **not** modify state.

## Flags

- `--blueprint=<name>` — review just this Stack Blueprint.
- `--since=<git-ref>` — review everything that's new in the working tree since the given ref. Default: `main`.

## Refuses if

- Both flags omitted **and** there are no uncommitted changes — nothing to review.
- `--since=<ref>` resolves to a non-existent commit.

## Output

```text
Review: 3 changed blueprints since origin/main

reviewer agent
  CRITICAL: 0
  HIGH:     0
  MEDIUM:   2
    - apps/<user-app>/.../grant.py:42 magic number 1000 in cap check
    - fixtures/app/workflows/beneficiary_approval.json:38 transition without condition (works but ambiguous to readers)
  LOW:      4
    - (style, formatting)

tester agent
  Tests:    14/14 pass
  Coverage: 87% on changed lines (target: ≥ 80%)
  Missing:  apps/<user-app>/.../grant.py:55-58 (validation branch)

Recommendation: ✓ ready to /frappe-stack:promote.
                Optional: address 2 MEDIUM findings + uncovered branch first.
```

## When to run

- After every `/frappe-stack:build` (the build command auto-runs reviewer + tester, but `/frappe-stack:review` re-runs after edits).
- Before `/frappe-stack:promote` (deployer runs this internally; calling explicitly is a sanity check).
- After resolving a `/frappe-stack:diff` conflict.

## Examples

```text
# Review the Beneficiary blueprint
/frappe-stack:review --blueprint=Beneficiary

# Review everything new vs origin/main
/frappe-stack:review --since=origin/main

# Review since the last release tag
/frappe-stack:review --since=v0.2.0
```
