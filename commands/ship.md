---
description: Tag a successful production migrate as a release. Updates CHANGELOG.md, creates a git tag, and posts release notes.
argument-hint: <version> [--notes-from=<pr-number>]
---

# /frappe-stack:ship

Run after a clean `/frappe-stack:promote` finishes (CI green, smoke-test passed). Closes the loop.

## What it does

1. **Verify last promote.** Looks at the most recent `Stack Audit Log` row with action `deploy.promote` and result `success`.
2. **Verify git state.** Config repo `main` is clean and up-to-date.
3. **Compute changelog entry.** Summarizes blueprints changed since the previous tag.
4. **Tag.** `git tag <version> origin/main` + `git push --tags`.
5. **Update `CHANGELOG.md`** in the config repo with the new entry.
6. **Optionally post release notes** to a configured Slack/Teams webhook.

## Arguments

- `<version>` — semver, e.g., `v0.2.0`. Refuses if not strictly greater than last tag.
- `--notes-from=<pr-number>` — pull the PR body into the changelog entry (default: auto-summarize commits).

## Refuses if

- Last promote action's result is not `success`.
- Working tree dirty.
- Version isn't strictly greater than the most recent tag.
- Slack/Teams webhook URL not configured (only blocks if `--notify` flag also used).

## Output

```text
Last promote:    deploy.promote success at 2026-05-03 14:55:00 UTC (PR #123)
Previous tag:    v0.1.0 (2026-04-22)
This tag:        v0.2.0

Changelog entry generated:
  ## [v0.2.0] - 2026-05-03
  ### Added
  - Beneficiary DocType + Beneficiary Approval workflow
  - Beneficiary Operations dashboard
  ### Changed
  - field_officer custom field added to Grant

Tag created: v0.2.0 → origin/main@<sha>
CHANGELOG.md updated and committed.
Release notes posted to #stack-releases.
```

## Examples

```text
# Standard release
/frappe-stack:ship v0.2.0

# Use the PR body as release notes
/frappe-stack:ship v0.2.0 --notes-from=123

# Patch release
/frappe-stack:ship v0.2.1
```
