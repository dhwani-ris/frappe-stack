---
name: frappe-api
description: Use when calling Frappe APIs from outside (the plugin), or designing a new whitelisted endpoint inside an app. Covers token auth, rate limits, CORS, and the secure-by-default endpoint template. Triggers on phrases like "API key", "calling Frappe from…", "whitelisted method", "REST endpoint".
---

# Frappe API — secure by default

## Authentication: only one acceptable mode

**Token-based: `Authorization: token <api_key>:<api_secret>`**

- One token per User row in Frappe.
- Generate via Desk → User → API Access.
- Both halves required; missing secret = 403.
- Token inherits all the User's roles + permissions — there is no separate "service account" abstraction.

For the `frappe-stack` plugin: create a dedicated user per environment (staging vs prod) with `System Manager` and any other roles needed for the resource types you'll create. Never reuse a human's token for the plugin.

```http
POST /api/resource/DocType
Authorization: token a1b2c3d4:secret_xyz
Content-Type: application/json

{
  "name": "Beneficiary",
  "module": "Custom",
  "custom": 1,
  "fields": [...],
  "permissions": [...]
}
```

## Whitelisted endpoint template

```python
import frappe
from frappe.utils import cstr

@frappe.whitelist()           # implicit allow_guest=False — keep it that way
def my_endpoint(name: str, payload: str) -> dict:
    # 1. Permission FIRST
    if not frappe.has_permission("Stack Blueprint", ptype="write"):
        raise frappe.PermissionError("write on Stack Blueprint")

    # 2. Sanitize string args (Frappe sends everything as strings)
    name = cstr(name)

    # 3. Validate JSON payloads explicitly
    import json
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as e:
        frappe.throw(f"payload not valid JSON: {e}")

    # 4. Use frappe.qb or parameterized SQL — never f-strings
    # 5. Return only what the caller needs (no full document dumps with internals)
    return {"name": name, "ok": True}
```

## Rate limits

Configure in `site_config.json`:

```json
{
  "rate_limit": {
    "limit": 60,
    "window": 60,
    "per": "ip"
  }
}
```

Plus per-endpoint limits in the route handler when the default is too lenient.

## CORS

```json
{
  "allow_cors": "https://app.example.com,https://staging.app.example.com"
}
```

Never `*` on a production site. Even with token auth, `*` lets any origin probe your endpoints' shape.

## Error responses

Frappe's default error responses leak a Python traceback when `developer_mode = 1`. Always:

```json
{ "developer_mode": 0 }
```

on production. Plus a custom error handler in `hooks.py` if you want bespoke shapes:

```python
def custom_response(response, exception):
    return frappe.utils.response.report_error(http_status_code=500)
```

## What the plugin does for you

The plugin works with stock Frappe — no custom server-side endpoints. It still adds value at the client side:

- Validators (schema + reserved-name + fieldtype whitelist + workflow shape) run before any REST call. Bad inputs never reach Frappe.
- Refuses to call any site flagged `is_production=true` in `.frappe-stack/config.json`. Production goes through `/frappe-stack:promote` only.
- Every Bash / Edit / Write done by the plugin appends a JSONL row to `.frappe-stack/audit.jsonl`. Frappe's built-in Activity Log captures the server-side mutation independently.

If you're writing a new Server Script that lives on the Frappe site, follow the secure-endpoint template above — `frappe.has_permission` first, parameterized SQL, no `ignore_permissions=True`.
