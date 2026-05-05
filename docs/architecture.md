# Architecture

How the plugin, the support app, and the GitHub config repo flow together.

## The three actors

```mermaid
flowchart LR
    subgraph PM["1 · Claude Code on PM machine"]
        direction TB
        P1["Slash commands<br>/frappe-stack:*"]
        P2["Skills loaded by<br>engineer agent"]
        P3["Hooks: prompt / pre-tool /<br>post-tool / stop"]
        P4["Local audit log<br>.frappe-stack/audit.jsonl"]
    end

    subgraph SITE["2 · Frappe site + stack_core"]
        direction TB
        S1["DocTypes: Stack Blueprint,<br>Workflow Def, Experiment<br>Assignment, Audit Log"]
        S2["API endpoints<br>stack_core.api.*"]
        S3["Guardrails: schema, fieldtype,<br>reserved names, workflow,<br>permission enforcer"]
        S4["git_bridge: exporter, committer,<br>pr_opener, differ, applier"]
    end

    subgraph GIT["3 · GitHub config repo"]
        direction TB
        G1["fixtures/app/doctypes/*.json"]
        G2["fixtures/app/workflows/*.json"]
        G3["fixtures/site/[sitename]/<br>overrides.json"]
        G4["main protected, CI runs<br>bench migrate on prod"]
    end

    PM ==>|"HTTPS + API key"| SITE
    SITE ==>|"pull / push fixtures"| GIT
    GIT ==>|"PR merge → bench migrate"| SITE

    classDef actorBox fill:#F5E6DD,stroke:#8B1E24,stroke-width:2px,color:#2E2E2E
    classDef itemBox fill:#ffffff,stroke:#D9B3A0,stroke-width:1px,color:#2E2E2E
    class PM,SITE,GIT actorBox
    class P1,P2,P3,P4,S1,S2,S3,S4,G1,G2,G3,G4 itemBox
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

```mermaid
sequenceDiagram
    autonumber
    actor PM
    participant Hook as UserPromptSubmit hook
    participant Eng as engineer agent
    participant API as stack_core API
    participant DB as Frappe DB
    participant Auto as reviewer plus tester

    PM->>Hook: make a beneficiary form
    Hook->>Eng: route to /frappe-stack:build doctype
    Eng->>Eng: load designing-forms skill
    Eng->>PM: print JSON, ask for confirmation
    PM->>Eng: confirms
    Eng->>API: POST stack_core.api.doctype_builder.build
    API->>API: permission check
    API->>API: refuse_on_production
    API->>API: schema and reserved-name validators
    API->>DB: upsert Stack Blueprint
    API->>DB: materialize DocType
    API->>DB: audit log row written
    API-->>Eng: status equals Applied
    Eng->>Auto: spawn reviewer and tester in parallel
    Auto-->>PM: ready to /pull or /promote
```

## End-to-end promote flow

```mermaid
sequenceDiagram
    autonumber
    actor PM
    participant Dep as deployer
    participant Repo as config repo
    participant GH as GitHub PR
    participant CI as prod CI
    participant Prod as production site

    PM->>Dep: /frappe-stack:promote
    Dep->>Dep: run pre-promote checklist
    Note right of Dep: diff clean, all Applied,<br>reviewer green, tester at 80% or more,<br>backup recent, roles covered,<br>not Friday afternoon
    Dep->>Repo: exporter writes per-blueprint JSONs
    Dep->>Repo: committer creates branch and commits
    Dep->>GH: pr_opener via gh CLI or REST fallback
    GH->>GH: reviewer rotation tagged
    GH->>GH: reviewer approves
    GH->>CI: merge triggers CI
    CI->>Prod: bench backup
    CI->>Prod: bench migrate (idempotent)
    CI->>Prod: bench restart
    alt migrate fails
        CI->>Prod: restore backup
        CI->>GH: revert merge and page on-call
    else migrate succeeds
        Dep->>Prod: smoke-test changed surface
        Dep-->>PM: done, ready to ship
    end
```

## DocType layout (`stack_core`)

```mermaid
erDiagram
    STACK_BLUEPRINT ||--o{ STACK_AUDIT_LOG : "logs mutations of"
    STACK_BLUEPRINT ||--o| STACK_WORKFLOW_DEF : "may extend as"
    STACK_WORKFLOW_DEF ||--o{ EXPERIMENT_ASSIGNMENT : "tracks A-B in"

    STACK_BLUEPRINT {
        string blueprint_name PK
        string blueprint_type "DocType, Workflow, Dashboard, Report, etc"
        int    version "increments on every save"
        string status "Draft, Validating, Applied, Failed, Reverted"
        json   payload "schema-validated per blueprint type"
        string git_commit_sha "set on /push"
        datetime applied_at
        link applied_by "User"
    }
    STACK_WORKFLOW_DEF {
        string workflow_name PK
        link   target_doctype
        json   states_json "validated by workflow_validator"
        json   transitions_json
        string experiment_id "empty means no experiment"
        string experiment_status "Running, Paused, Promoted, Abandoned"
    }
    EXPERIMENT_ASSIGNMENT {
        link   doc_reference "Dynamic Link to experimented doc"
        link   workflow
        string experiment_id "indexed"
        string arm "arm_a or arm_b"
        datetime assigned_at
        string outcome "pending, approved, rejected, cancelled, expired"
        datetime outcome_at
        int cycle_time_seconds
    }
    STACK_AUDIT_LOG {
        link   actor "User, indexed"
        string action "api.build_doctype, blueprint.update, etc"
        link   blueprint "optional"
        datetime timestamp "indexed"
        string result "success, failure, denied"
        string ip_address
        text   before_json
        text   after_json
    }
```

`Stack Audit Log` is append-only. Hard delete is blocked by an `on_trash` hook plus a `before_delete` doc event registered on `*` in `hooks.py`. `permission_query` exposes only own-rows to `Stack Author`; full table to `System Manager` and `Stack Admin`.

## Layered enforcement

The same rule appears at multiple layers — defense in depth.

| Concern | Plugin layer | API layer | DB layer | CI layer |
|---|---|---|---|---|
| Reserved DocType name | UserPromptSubmit nudge | `guardrails/reserved_names.py` | n/a | n/a |
| Fieldtype whitelist | n/a | `guardrails/fieldtype_whitelist.py` (role-gated) | n/a | n/a |
| `ignore_permissions=True` | UserPromptSubmit nudge | PreToolUse `block_ignore_permissions.py` | refused if blueprint requests it | semgrep |
| Direct prod API write | UserPromptSubmit nudge | PreToolUse `block_direct_prod_api.py` | `permission_enforcer.refuse_on_production` | n/a |
| Hard delete on audit-tagged | n/a | n/a | `before_delete` + DocType `on_trash` | n/a |
| f-string SQL | n/a | PreToolUse `block_fstring_sql.py` | n/a | semgrep + frappe-semgrep-rules |
| Force-push to protected | UserPromptSubmit nudge | PreToolUse `block_dangerous_bash.py` | n/a | GitHub branch protection |
| Real PII in prompt | UserPromptSubmit block | n/a | n/a | n/a |

## Local audit + remote audit

Two audit trails, deliberately:

- **`.frappe-stack/audit.jsonl`** (local) — every tool call (Bash / Edit / Write) by the PM in their session. Independent of network. Useful when the site is unreachable.
- **`Stack Audit Log` DocType** (remote, on the site) — every API call, every blueprint mutation, with actor + IP + before / after. Append-only, queryable from desk.

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
| Blueprint validation fails on apply | Stack Blueprint marked `status=Failed` with `validation_errors` set |
| Drift detected daily | `applier.reconcile_drift` logs an Error Log entry |

See [`SECURITY.md §5`](../SECURITY.md#5-incident-response) for the formal incident protocol.
