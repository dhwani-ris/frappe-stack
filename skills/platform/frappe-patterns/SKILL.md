---
name: frappe-patterns
description: Use when implementing common UI / data patterns on Frappe forms and lists — fuzzy search, sticky table headers, sequential save, client-side XLSX export, and similar reusable client-side patterns. Triggers on phrases like "make this list filter as you type", "freeze the header", "export to Excel", "save in order".
---

# Frappe patterns catalog

Indexed reference of v15+ client-side patterns, absorbed from `sunandan89/mgrant-frappe-patterns` and adapted for the frappe-stack plugin. Each pattern lives at `patterns/<name>/` (added incrementally; this index is the entry point).

## Catalog (v0.1)

| Pattern | When to use | Layer |
|---|---|---|
| `fuzzy-search` | List view filter that matches across multiple fields with typo tolerance | 4 (client script) |
| `sticky-table-freeze` | Long child tables — keep header visible while scrolling | 4 (client script) |
| `frappe-sequential-save` | Save a parent + N children in deterministic order without race conditions | 4 (server method) |
| `client-side-xlsx-export` | Export filtered list view to XLSX in browser, no server roundtrip | 4 (client script) |
| `paste-from-excel` | Paste tabular data into a child table cell-by-cell | 4 (client script) |
| `multi-select-add-row` | Quick-add many child rows from a Link autocomplete | 4 (client script) |
| `dependent-link-filter` | Filter Link field B based on Link field A's selection | 1 (Form Builder) + 4 (client script) |
| `inline-edit-list-view` | Edit a single field directly from the list view | 4 (client script) |
| `realtime-counter-badge` | Show a live count in the sidebar (uses `frappe.realtime`) | 4 (client + server) |
| `pdf-bulk-print` | Print N selected list-view rows as one combined PDF | 4 (server method) |
| `searchable-tree-view` | Tree view with a search box that highlights matches and auto-expands | 4 (client script) |
| `session-storage-form-draft` | Auto-save form-in-progress to localStorage, restore on reload | 4 (client script) |

## When to apply

The plugin's `engineer` agent autoloads this index on every build task. When the user describes a UI need that maps to one of these patterns, the engineer:

1. Names the pattern explicitly to the user.
2. Loads the full pattern reference (planned: `patterns/<name>/README.md`).
3. Copies the pattern into the user's app, adjusting only the DocType / fieldnames.
4. Notes in the audit log that pattern X version Y was used (for future upgrades).

## Adding a new pattern

A pattern earns a slot in the catalog when:

- It's been used in at least 2 production sites without issue.
- It's < 200 lines of client/server code.
- It works on Frappe v15+ (test on v15 specifically).
- It has zero `ignore_permissions=True`, zero hardcoded role checks, zero raw-SQL string interpolation.

Open a PR adding `patterns/<name>/` with a README, the actual JS/Python, and an example DocType showing usage. The skill file gets a new row in the table above.

## Anti-patterns to refuse

- jQuery plugins from third parties without a security audit.
- Patterns that bypass `frappe.call()` for direct `$.ajax` to the API — loses CSRF + audit hook integration.
- Patterns that store state in `window.<global>` — breaks when the user opens two tabs.
