---
name: frappe-platform
description: Use when planning anything that touches Frappe internals — DocTypes, hooks, fixtures, permissions, scheduled jobs. Loads the 4-layer model and the config-vs-code decision tree before code is generated. Triggers on phrases like "what's the right way to…", "should this be a fixture…", "how does Frappe handle…".
---

# Frappe platform — the 4-layer model

A Frappe site is four layers, and the **lowest layer that solves the problem wins.** Generating code at the wrong layer is the single biggest non-developer footgun.

```
Layer 4: Custom code in app           (Python, JS, requires bench update + migrate)
Layer 3: Fixtures shipped with app    (JSON in fixtures/, applied on bench migrate)
Layer 2: Custom Field / Property Setter / Workflow  (DB rows, exportable as fixtures)
Layer 1: Standard DocType + Form Builder + Workflow Builder  (UI-driven, no code)
```

## Decision tree (run this before generating anything)

| Need | First try | Fallback | Last resort |
|---|---|---|---|
| Add a field to existing DocType | Layer 2: Custom Field | Layer 3: ship as fixture | Layer 4: edit app DocType JSON |
| Hide a field for a role | Layer 2: Property Setter (`depends_on` / `permlevel`) | Layer 4: server-side check |
| Multi-step approval | Layer 1: Workflow Builder | Layer 2: workflow stored as Stack Workflow Def | Layer 4: Server Script |
| Auto-fill on save | Layer 2: Custom Field with default + fetch_from | Layer 4: `before_insert` hook in app |
| Conditional validation | Layer 2: Custom Script (client) | Layer 4: `validate()` controller |
| New DocType | Layer 1: Form Builder, then export as Layer 3 fixture |
| Periodic task | Layer 4 only — `scheduler_events` in `hooks.py` |
| External integration | Layer 4 only — REST endpoint + `@frappe.whitelist()` |

## Why fixtures (Layer 3) are the spine

- Fixtures are JSON. JSON diffs cleanly. Git diffs cleanly. Code review works.
- `bench migrate` re-applies fixtures every deploy → environments stay in sync.
- Layer 2 changes made via UI are invisible to git. Always export them to Layer 3 before merging.

The `frappe-stack` plugin's job is to make Layer 3 the **default** for non-developers. PMs operate the Form Builder (Layer 1) → plugin auto-exports as fixtures (Layer 3) → git commits → other sites pick up via migrate.

## Anti-patterns (refuse on sight)

- **Editing a Frappe-core DocType JSON directly.** Use Layer 2 Custom Field instead. The next `bench update` will overwrite your edit.
- **Hardcoding a role check in Python.** Use Frappe's permission system. `if frappe.get_roles(user) == ["..."]` is a security bug waiting to happen.
- **`bench migrate` without a backup.** Always backup first. Always.
- **Editing fixtures by hand on a running site.** Modify on staging via UI → export → commit. Hand-edited fixtures cause drift the differ catches but the user has to resolve.

## Required reading

- `~/.claude/rules/frappe/frappe-coding-style.md` — global Frappe coding rules
- `~/.claude/rules/frappe/frappe-security.md` — security non-negotiables
- [`SECURITY.md`](../../../SECURITY.md) — repo-specific guardrails

When in doubt, surface the layer choice to the user and ask. Don't guess.
