---
name: designing-forms
description: Use when a PM asks to create a new form, registration, intake, application, or DocType. Walks them through fields, validation, and permissions, then emits a Frappe DocType JSON payload posted via stock REST. Triggers on phrases like "I need a form for…", "let's add a registration", "create a new doctype for…", "intake form", "application form".
---

# Designing forms (DocTypes)

The PM's most common ask. This skill turns plain-language intent into a validated DocType JSON payload that the engineer agent posts to Frappe via `POST /api/resource/DocType`.

## Conversation flow (do not skip steps)

### Step 1. What is this form about?

- **Name** — domain noun, not a verb. "Beneficiary", "Grant Application", "Site Visit Report". *Refuse* names that collide with `frappe-permissions` reserved list (`User`, `Role`, `DocType`, …) or start with `Stack `.
- **Module** — defaults to `Custom`; ask if they want to group with other DocTypes.
- **Naming rule** — three options, pick one:
  - *Auto-numbered* (default): `BENF-2026-00001`. Fast, no collisions.
  - *By field*: name = the value of one field (e.g., Aadhaar). Risky — fix the field is unique.
  - *Random*: opaque hash. Use only for internal records.

### Step 2. What fields?

For each field, gather:

| Question | Maps to |
|---|---|
| What's the label? | `label` |
| Internal field name (lowercase, underscores)? | `fieldname` |
| What kind of value? | `fieldtype` (Data / Int / Date / Link / Select / Check / …) |
| Required? | `reqd: 1` |
| Default value? | `default` |
| Options (for Select / Link)? | `options` |
| In the list view? | `in_list_view: 1` |

**Refuse on sight** if the user requests `Code`, `Password`, `Attach`, `Long Text`, or `Signature` without elevated role. The `fieldtype_whitelist` guardrail will block it anyway, so it's better to refuse upfront with an explanation.

### Step 3. Who can see / edit this?

Hand off to the `frappe-permissions` skill. Don't invent permissions on the fly. The minimum is:

```python
"permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Stack Admin",    "read": 1, "write": 1, "create": 1, "delete": 0},
]
```

If the PM mentions "field officers" or any tier of restricted access, either:

- Pre-create the role (ask: should I add a "Field Officer" role?), then add row-level filtering as a separate Custom Field + permission_query_conditions in a follow-up.
- OR start with admin-only and grant access later.

### Step 4. Show, then build

Render the full blueprint payload as JSON, formatted, with every field annotated. Ask for confirmation. **Only after explicit "yes"**, call:

```text
curl -X POST <staging>/api/resource/DocType \
     -H "Authorization: token <api_key>:<api_secret>" \
     -H "Content-Type: application/json" \
     -d '<the-json>'
```

## Worked example

PM: "I want a beneficiary registration form. Name, village, age, Aadhaar, photo, and the field officer who registered them."

Engineer:

```json
{
  "name": "Beneficiary",
  "module": "Custom",
  "naming_rule": "By fieldname",
  "autoname": "field:aadhaar_number",
  "track_changes": 1,
  "fields": [
    {"fieldname": "full_name",        "fieldtype": "Data",  "label": "Full Name", "reqd": 1, "in_list_view": 1},
    {"fieldname": "village",          "fieldtype": "Data",  "label": "Village", "in_list_view": 1},
    {"fieldname": "age",              "fieldtype": "Int",   "label": "Age", "non_negative": 1},
    {"fieldname": "aadhaar_number",   "fieldtype": "Data",  "label": "Aadhaar", "reqd": 1, "unique": 1, "length": 12},
    {"fieldname": "field_officer",    "fieldtype": "Link",  "label": "Field Officer", "options": "User", "reqd": 1, "in_list_view": 1}
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "Stack Admin",    "read": 1, "write": 1, "create": 1, "delete": 0}
  ]
}
```

**Note to PM**: "Photo" was dropped — `Attach Image` is in the elevated fieldtype list. I'll either need a Stack Admin's approval to add it, or we use a separate Files area. Want me to flag that for review?

## What I refuse to do

- Auto-add a `Code` or `Password` field "because it's faster". Always escalate.
- Generate a DocType without permissions. Default-deny — empty permissions = nobody can see it.
- Skip the show-then-build confirmation step. The user always reviews JSON before mutation.
