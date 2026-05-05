---
name: frappe-permissions
description: Use whenever generating any DocType, Workflow, or API endpoint. The Frappe permission model is the single biggest source of bugs in PM-built apps. Triggers on phrases like "who can see…", "permission denied…", "restrict access…", "row-level security…".
---

# Frappe permissions — the only correct mental model

Frappe permissions are evaluated in a strict order. Skip any layer and you ship a security bug.

## The 5 layers (in evaluation order)

1. **Role permissions** — `read/write/create/delete/submit/cancel/amend` per role on the DocType.
2. **User permissions** — restricts which *rows* a user can see (e.g., user X only sees rows where `district = "Pune"`).
3. **DocType `permission_query_conditions`** hook — server-side SQL filter applied to every query.
4. **`has_permission` controller hook** — per-document check the framework calls before read/write.
5. **DocType `if_owner` flag** — owner-only access for matching role.

## Non-negotiable rules

- **Every `@frappe.whitelist()` calls `frappe.has_permission()` first.** No exceptions, even for "internal" endpoints. If you forget, an attacker who knows the path can hit it.
- **Never `ignore_permissions=True`** in user-facing code paths. The only legitimate use is within scheduled tasks running as Administrator, and even there it must be commented with *why*.
- **Never `allow_guest=True`** without explicit security review and a rate limit. Default is `allow_guest=False`.
- **Never hardcode role-name string checks.** Use `frappe.has_permission()` or `frappe.get_roles()` membership tests.

## How to grant access (correct order)

```
PM ask: "Field officers should see only their own beneficiaries"

1. Create Role 'Field Officer'.
2. Add DocType permissions: read/write/create on Beneficiary for that role.
3. Add User Permission per officer linking them to their region/district.
4. (If district-level needed) Add permission_query_conditions hook so SQL itself filters.

Wrong order:
✗ Hardcode `if user.email.endswith('@field')` in controller
✗ Add a global filter to the list view JS (client-side bypass)
```

## API endpoint template

```python
import frappe

@frappe.whitelist()
def do_thing(name: str) -> dict:
    # 1. permission first, before anything else.
    if not frappe.has_permission("Beneficiary", ptype="write", doc=name):
        raise frappe.PermissionError("write on Beneficiary")

    # 2. defensive parse — Frappe sends args as strings.
    name = frappe.utils.cstr(name)

    # 3. Use frappe.qb or parameterized SQL. Never f-strings.
    # 4. Append a row to the local audit log (.frappe-stack/audit.jsonl)
    #    after success — the plugin handles this automatically.
    ...
```

## Row-level security (the pattern PMs trip on)

Use `permission_query_conditions` in `hooks.py`:

```python
permission_query_conditions = {
    "Beneficiary": "myapp.permissions.beneficiary_query",
}
```

```python
def beneficiary_query(user: str) -> str:
    if not user:
        user = frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return ""  # admins see all
    return f"`tabBeneficiary`.field_officer = {frappe.db.escape(user)}"
```

The escape is non-optional. SQL injection through the query-conditions function has been a real CVE class in Frappe.

## When PM says "I want it locked down"

Ask three questions before generating anything:

1. **Who can read?** (role names + any user-permission filters)
2. **Who can write/create/delete?**
3. **Should the document submit/cancel/amend?** (govt projects: yes, with audit)

Convert their answers into the DocType `permissions` array and (if needed) a `permission_query_conditions` function. Surface the table to them in plain English before saving.
