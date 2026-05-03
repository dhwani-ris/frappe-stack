---
name: git-roundtrip
description: Use when site state needs to land in GitHub, or GitHub state needs to land on a site. Powers /frappe-stack:pull, push, diff, promote. Triggers on phrases like "save to git", "commit my changes", "what's different", "drift", "fixtures out of sync".
---

# Git roundtrip — site ↔ GitHub two-way sync

The core differentiator. Site mutations that bypass git create silent drift; PRs that bypass the site break on `bench migrate`. The sync engine refuses both.

## The model (B+ hybrid, locked decision D-01)

| Site role | Direction | Allowed |
|---|---|---|
| **Staging** | Site → git via `/frappe-stack:pull` | ✓ |
| **Staging** | git → site via `/frappe-stack:push` | ✓ |
| **Production** | Site → git | ✓ (read-only export, no API mutation) |
| **Production** | git → site | ✓ (only via `bench migrate` after PR merge) |
| **Production** | direct API write | ✗ blocked by `is_production=1` guardrail |

`/frappe-stack:promote` is the bridge: snapshot staging state, open a PR against the config repo's `main`, merge → CI runs `bench migrate` on prod.

## Layout the sync engine writes

```
<config-repo>/
└── fixtures/
    ├── app/                  ← shared across sites
    │   ├── doctypes/
    │   │   ├── beneficiary.json
    │   │   └── grant.json
    │   ├── workflows/
    │   │   └── beneficiary_approval.json
    │   ├── custom_fields.json
    │   └── property_setters.json
    └── site/<sitename>/      ← per-site overrides (rare; mostly empty)
        └── overrides.json
```

Per-blueprint files mean diffs are minimal — adding one Custom Field changes one file, not a 5000-line `custom_fields.json`. Sidesteps Frappe issue #34915.

## Operations

### `/frappe-stack:pull`

```
[ site ] → exporter.py → [ config repo working tree ]
                          (per-blueprint JSONs written, no commit)
```

Then user inspects via `git diff`. If happy, commit + push manually OR run `/frappe-stack:promote`.

### `/frappe-stack:push`

Refuses on production. On staging:

```
[ config repo ] → applier.py → [ site ]
                  (idempotent — re-running is safe)
```

Each blueprint upserted: existing → version++ + payload replaced; missing → created.

### `/frappe-stack:diff`

Three-way report:

| Bucket | Meaning | Action |
|---|---|---|
| `only_on_site` | Created on site since last pull | Run `/pull` to capture in git |
| `only_in_git` | In git but not yet applied | Run `/push` (staging) or wait for `bench migrate` (prod) |
| `changed` | Same name, different payload | **Conflict.** Inspect and choose direction. Don't auto-resolve. |

### `/frappe-stack:promote`

```
1. Run differ.py on staging → assert clean (no only_on_site / changed)
2. exporter.py writes the entire current state to a timestamped branch
3. committer.py: stage + commit with structured message + push
4. pr_opener.py: open PR with body = audit-log excerpt + diff summary
5. Display PR URL to user
```

PR merge triggers prod CI, which runs `bench migrate` against the prod site. The applier's idempotency means re-running the migrate is safe — you can roll forward without rolling back.

## Conflict resolution

When `/frappe-stack:diff` shows `changed: ["Beneficiary"]`:

1. The differ refuses to auto-resolve.
2. Surface a JSON diff to the user.
3. Ask: "Site has X, git has Y. Which is canonical?"
4. If site wins: `/frappe-stack:pull` overwrites git.
5. If git wins: `/frappe-stack:push` overwrites site.
6. **Never both — pick one direction per blueprint.**

## Daily drift watcher

`hooks.py` registers `git_bridge.applier.reconcile_drift` as a daily scheduled job. If drift is detected (any of the three buckets non-empty), it logs an Error Log entry. The daily report skill (when it ships) surfaces these to the project's owner.

## Failure modes the engine handles

| Failure | What happens |
|---|---|
| `gh` CLI not installed | `pr_opener.py` falls back to GitHub REST API |
| GitHub token absent | Raises `RuntimeError` — operator must configure `stack_core.github_token_secret_key` |
| Working tree dirty before push | committer.py refuses; surfaces existing changes for the user to commit/stash first |
| Network down during commit | committer.py commits locally; push fails; can be retried |
| Schema migration needed (DocType field added) | applier writes blueprint; framework runs schema migration on save; if migration fails, blueprint marked Failed and rolled back |
