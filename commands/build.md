---
description: Build a DocType, Workflow, Dashboard, Report, Custom Field, or Property Setter. Routes to the engineer agent which loads the matching skill and walks the conversation.
argument-hint: <type> <name> [--from-spec=<path>]
---

# /frappe-stack:build

The most common command. Use the engineer agent to turn intent into a Stack Blueprint that lands on staging.

## Arguments

- `<type>` — one of: `doctype`, `workflow`, `dashboard`, `report`, `customfield`, `propertysetter`.
- `<name>` — the blueprint name. For DocTypes, this is the human-readable name (e.g., `Beneficiary`).
- `--from-spec=<path>` — optional. If provided, engineer reads the spec section first instead of asking the PM from scratch.

## What it does

1. Refuses on `--prod` sites (configured in `.frappe-stack/config.json`). Prod is git-only.
2. Loads the matching `skills/building/<skill>` (designing-forms, modeling-workflows, etc.).
3. Spawns the `engineer` agent to walk the conversation.
4. Engineer runs guardrails locally (reserved name, fieldtype whitelist, workflow shape).
5. Engineer shows the JSON payload, asks for confirmation.
6. On confirmation, calls `stack_core.api.<type>_builder.build`.
7. Verifies the response: `status=Applied`. Surfaces validation errors otherwise.
8. Hands off to `tester` + `reviewer` agents (parallel) automatically.

## Examples

```text
/frappe-stack:build doctype Beneficiary
/frappe-stack:build workflow "Beneficiary Approval"
/frappe-stack:build doctype Grant --from-spec=docs/specs/grant-v1.md
/frappe-stack:build dashboard "Beneficiary Operations"
/frappe-stack:build report "Disbursement Summary"
/frappe-stack:build customfield "field_officer on Grant"
```

## Refuses if

- Run on a site marked `is_production=1`.
- `stack_core` not installed or unreachable on the configured staging site.
- Reserved name (User, Role, etc., or `Stack ` prefix).
- Disallowed fieldtype (Code, Password, Attach) without elevated role.
- Workflow without terminal state, with orphan states, or with traffic_split that doesn't sum to 100.

## Output

- Blueprint name + status (Applied / Failed).
- Link to the new doc on staging.
- Auto-spawned reviewer + tester reports (in parallel).
- Reminder to run `/frappe-stack:pull` to commit to git.
