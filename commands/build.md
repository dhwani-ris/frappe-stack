---
description: Build a DocType, Workflow, Dashboard, Report, Custom Field, or Property Setter. Routes to the engineer agent which loads the matching skill, generates the JSON, and POSTs to Frappe's stock REST API.
argument-hint: <type> <name> [--from-spec=<path>]
---

# /frappe-stack:build

The most common command. Engineer agent turns intent into a Frappe configuration that lands on staging via stock REST.

## Arguments

- `<type>` — one of: `doctype`, `workflow`, `dashboard`, `report`, `customfield`, `propertysetter`.
- `<name>` — the human-readable name (e.g., `Beneficiary` for a DocType).
- `--from-spec=<path>` — optional. If provided, engineer reads the spec section first instead of asking the PM from scratch.

## What it does

1. Refuses on `--prod` sites (configured in `.frappe-stack/config.json`). Production is git-only.
2. Loads the matching `skills/building/<skill>` (designing-forms, modeling-workflows, etc.).
3. Spawns the `engineer` agent to walk the conversation.
4. Engineer runs validators locally (reserved name, fieldtype whitelist, workflow shape).
5. Engineer shows the JSON payload, asks for confirmation.
6. On confirmation, calls Frappe's stock REST endpoint:

| Type | Endpoint |
|---|---|
| doctype | `POST /api/resource/DocType` |
| workflow | `POST /api/resource/Workflow` |
| dashboard | `POST /api/resource/Dashboard` |
| report | `POST /api/resource/Report` |
| customfield | `POST /api/resource/Custom Field` |
| propertysetter | `POST /api/resource/Property Setter` |

7. Verifies the response (`201 Created` + the new record's `name`). Surfaces errors otherwise.
8. Hands off to `tester` + `reviewer` agents (parallel) automatically.
9. Appends a row to `.frappe-stack/audit.jsonl`.

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

- Run on a site marked `is_production=true`.
- Frappe site unreachable (verify with `/frappe-stack:init` first).
- Reserved name (`User`, `Role`, `DocType`, etc.).
- Disallowed fieldtype (`Code`, `Password`, `Attach`, `Signature`) without elevated role.
- Workflow without terminal state, with orphan states, or with traffic_split that doesn't sum to 100.
- 401/403 from Frappe — the API user lacks the required role for this resource type.

## Output

- Resource name + status (Created / Failed).
- Direct URL to the new record on the staging Frappe Desk.
- Auto-spawned reviewer + tester reports (in parallel).
- Reminder to run `/frappe-stack:pull` to commit the JSON to git.
