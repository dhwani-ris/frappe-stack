# Architecture

How the plugin, the support app, and the GitHub config-repo flow together.

## The three actors

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   1. Claude Code  + frappe-stack plugin   (PM's machine)            │
│      ─────────────────────────────────                              │
│      • slash commands  /frappe-stack:*                              │
│      • skills loaded by engineer agent                              │
│      • hooks (UserPromptSubmit / PreToolUse / PostToolUse / Stop)   │
│      • local audit log  .frappe-stack/audit.jsonl                   │
│                                                                     │
│                  ────── calls API ───────                           │
│                                                                     │
│   2. Frappe site (staging) + stack_core support app                 │
│      ────────────────────────────────────────                       │
│      • DocTypes:  Stack Blueprint, Stack Workflow Def,              │
│                   Experiment Assignment, Stack Audit Log            │
│      • API:       /api/method/stack_core.api.*                      │
│      • Guardrails: schema_validator, fieldtype_whitelist,           │
│                   reserved_names, workflow_validator,               │
│                   permission_enforcer                               │
│      • git_bridge: exporter, committer, pr_opener, differ, applier  │
│                                                                     │
│                  ────── pull/push fixtures ──────                   │
│                                                                     │
│   3. GitHub config-repo                                             │
│      ──────────────                                                 │
│      • fixtures/app/doctypes/*.json                                 │
│      • fixtures/app/workflows/*.json                                │
│      • fixtures/app/{custom_fields,property_setters}.json           │
│      • fixtures/site/<sitename>/overrides.json                      │
│      • PR-protected main → CI runs bench migrate on prod            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## The B+ hybrid sync model (D-01 confirmed)

| Site role | Direction | Allowed |
|---|---|---|
| **Staging** | Site → git via `/pull` | ✓ |
| **Staging** | git → site via `/push` | ✓ |
| **Production** | Site → git (read-only export) | ✓ |
| **Production** | git → site via `bench migrate` (on PR merge) | ✓ |
| **Production** | direct API write | ✗ blocked by `is_production=1` |

`/promote` is the bridge: snapshot staging → PR against config-repo `main` → review → merge → CI migrates prod.

## End-to-end build flow

```
PM types: "make a beneficiary form"
                            │
                            ▼
        UserPromptSubmit: coach_user_prompt.py
                            │
            (injects: suggest /frappe-stack:build doctype)
                            │
                            ▼
                  Claude routes to:
        /frappe-stack:build doctype Beneficiary
                            │
                            ▼
      engineer agent loads designing-forms skill
                            │
            (walks fields + permissions)
                            │
                            ▼
            engineer prints JSON, asks "yes?"
                            │
                            ▼ (user confirms)
                            │
        Bash: curl https://staging…/api/method/
              stack_core.api.doctype_builder.build
                            │
            (PreToolUse: block_direct_prod_api passes — staging)
                            │
                            ▼
                  stack_core API:
              ┌──── permission check ────┐
              │  refuse_on_production    │
              │  validate_payload        │
              │  enforce_reserved_names  │
              │  enforce_fieldtype_whitelist
              │  upsert Stack Blueprint  │
              │  materialize DocType     │
              │  @audited writes log row │
              └──────────────────────────┘
                            │
                            ▼
              DocType live on staging
                            │
                            ▼
        engineer auto-spawns:
        ┌────────────────────┬────────────────────┐
        │   reviewer         │   tester           │  (parallel)
        │   - SECURITY.md    │   - FrappeTestCase │
        │   - frappe-rules   │   - Playwright     │
        │   - semgrep        │   - coverage gate  │
        └────────────────────┴────────────────────┘
                            │
                            ▼
              ✓ "ready to /pull or /promote"
```

## End-to-end promote flow

```
/frappe-stack:promote
        │
        ▼
deployer agent runs pre-promote checklist:
  ✓ /diff clean
  ✓ blueprints all status=Applied
  ✓ reviewer 0 CRITICAL/HIGH
  ✓ tester 14/14 + 80%+ coverage
  ✓ backup verified <24h
  ✓ role coverage on new states
  ✓ Friday-evening guard
        │
        ▼ (any failure → refuse + surface)
        │
        ▼
git_bridge/exporter.py runs in config-repo working tree
  → fixtures/app/doctypes/beneficiary.json (per-blueprint)
  → fixtures/app/workflows/beneficiary_approval.json
        │
        ▼
git_bridge/committer.py
  → branch promote/sprint-15-beneficiary-20260503-1432
  → git add + commit + push
        │
        ▼
git_bridge/pr_opener.py
  → gh pr create (or REST fallback)
  → tags reviewer rotation
        │
        ▼
(human review + approve)
        │
        ▼
merge to main
        │
        ▼
CI on the config-repo:
  bench --site prod backup
  bench --site prod migrate    ← applier upserts blueprints idempotently
  bench --site prod restart
        │
        ▼ (failure → automatic restore + revert)
        │
        ▼
deployer smoke-tests prod
        │
        ▼
✓ done. /frappe-stack:ship v0.X.0
```

## DocType layout (stack_core)

```
Stack Blueprint  (versioned config — the "source of truth on this site")
  ├── blueprint_name           (unique, autoname)
  ├── blueprint_type           (DocType / Workflow / Dashboard / Report / Custom Field / …)
  ├── version                  (++ on every save)
  ├── status                   (Draft / Validating / Applied / Failed / Reverted)
  ├── payload                  (JSON, schema-validated per blueprint_type)
  ├── git_commit_sha           (set on /push)
  └── (audit fields)

Stack Workflow Def  (extends Blueprint with experiment fields)
  ├── workflow_name
  ├── target_doctype
  ├── states_json              (validated by workflow_validator)
  ├── transitions_json
  ├── experiment_id            (empty = no experiment)
  └── experiment_status        (Running / Paused / Promoted A / Promoted B / Abandoned)

Experiment Assignment  (A/B tracking, append-only)
  ├── doc_reference            (Dynamic Link to the experimented doc)
  ├── workflow                 (Link to Stack Workflow Def)
  ├── experiment_id            (indexed)
  ├── arm                      (arm_a / arm_b)
  ├── assigned_at
  ├── outcome                  (pending / approved / rejected / cancelled / expired)
  ├── outcome_at
  └── cycle_time_seconds

Stack Audit Log  (append-only — hard-delete blocked by on_trash hook)
  ├── actor (User Link, indexed)
  ├── action (api.build_doctype / api.build_workflow / blueprint.update / …)
  ├── blueprint (Link, optional)
  ├── timestamp (indexed)
  ├── result (success / failure / denied)
  ├── ip_address
  ├── before_json / after_json
  └── permission_query: own-rows-only for Stack Author; full for SM + Stack Admin
```

## Layered enforcement

The same rule appears at multiple layers — defense in depth.

| Concern | Plugin layer | API layer | DB layer | CI layer |
|---|---|---|---|---|
| Reserved DocType name | UserPromptSubmit nudge | guardrails/reserved_names.py | n/a | n/a |
| Fieldtype whitelist | n/a | guardrails/fieldtype_whitelist.py (role-gated) | n/a | n/a |
| `ignore_permissions=True` | UserPromptSubmit nudge | PreToolUse block_ignore_permissions.py | (refused if blueprint requests it) | semgrep |
| Direct prod API write | UserPromptSubmit nudge ("redirect to /promote") | PreToolUse block_direct_prod_api.py | guardrails/permission_enforcer.refuse_on_production | n/a |
| Hard delete on audit-tagged | n/a | n/a | doc_events `before_delete` + DocType `on_trash` | n/a |
| f-string SQL | n/a | PreToolUse block_fstring_sql.py | n/a | semgrep + frappe-semgrep-rules |
| Force-push to protected | UserPromptSubmit nudge | PreToolUse block_dangerous_bash.py | n/a | GitHub branch protection |
| Real PII in prompt | UserPromptSubmit block | n/a | n/a | n/a |

## Local audit + remote audit

Two audit trails, deliberately:

- **`.frappe-stack/audit.jsonl`** (local) — every tool call (Bash / Edit / Write) by the PM in their session. Independent of network. Useful when the site is unreachable.
- **`Stack Audit Log` DocType** (remote, on the site) — every API call, every blueprint mutation, with actor + IP + before/after. Append-only, queryable from desk.

Both are durable and inspectable. Disagreement between them is itself diagnostic — surfaced by the `analyst` agent on demand.

## Failure modes the system handles

| Failure | What happens |
|---|---|
| `gh` CLI not installed | `pr_opener.py` falls back to GitHub REST API |
| GitHub token absent | `pr_opener.py` raises clear error; operator must configure |
| Working tree dirty before promote | `committer.py` refuses; surfaces existing changes |
| Network down during commit | Commits locally; push fails; can be retried later |
| Schema migration fails on prod | CI auto-restores backup + reverts merge + pages on-call |
| Token leaked | Operator runs the rotate-keys runbook; old token invalidated immediately |
| Blueprint validation fails on apply | Stack Blueprint marked status=Failed with `validation_errors` set |
| Drift detected daily | `applier.reconcile_drift` logs an Error Log entry |

See [`SECURITY.md §5`](../SECURITY.md#5-incident-response) for the formal incident protocol.
