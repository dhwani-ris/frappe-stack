---
name: wiring-integrations
description: Use when integrating Frappe with external systems — webhooks, REST callbacks, SMS gateways, payment gateways, file storage. Triggers on phrases like "send to Zapier", "webhook from…", "SMS notification", "S3 upload", "payment gateway".
---

# Wiring integrations

Frappe has three native integration mechanisms. Pick the lightest one.

## Decision tree

| Use case | Mechanism | Layer |
|---|---|---|
| "When a beneficiary is approved, POST to https://…" | **Webhook** (DocType built-in) | Layer 2 — fixture |
| "Send SMS via MSG91 on workflow state change" | **Notification + custom action** OR `frappe_msg91_integration` | Layer 2 + Layer 4 |
| "Pull data from external API on a schedule" | **Scheduled task** in `hooks.py` | Layer 4 |
| "Receive callback from payment gateway" | **Whitelisted endpoint** + signature verification | Layer 4 |
| "Upload all attachments to S3" | **`frappe-cloud-storage`** app | Layer 4 — install separately |

## Webhook (zero-code outbound)

Create a `Webhook` row (it's a DocType — ships as fixture):

```json
{
  "webhook_doctype": "Beneficiary",
  "webhook_docevent": "after_insert",
  "request_url": "https://hook.example.com/beneficiaries/new",
  "request_method": "POST",
  "request_structure": "JSON",
  "webhook_data": [
    {"fieldname": "name",       "key": "id"},
    {"fieldname": "full_name",  "key": "name"},
    {"fieldname": "district",   "key": "district"}
  ],
  "webhook_headers": [
    {"key": "X-API-Key", "value": "{{ frappe.get_doc('Webhook Secret', 'main').secret }}"}
  ]
}
```

**Mandatory:** never embed the secret as a literal in `webhook_headers.value`. Always indirect through a Frappe doc the value is fetched from at send time. Otherwise the secret hits the fixture and the git repo.

## Inbound webhook (the dangerous direction)

External system POSTs to your Frappe site. Three things you must do:

1. **Signature verification.** Almost every gateway sends `X-Signature` or `X-Hub-Signature-256`. Compute HMAC over the raw body, constant-time compare.
2. **Idempotency.** They retry on timeout. Store a request ID and refuse duplicates.
3. **Permission scope.** Even though the endpoint may need to be publicly reachable (`allow_guest=True`), it must do the minimum work — write to a queue DocType, return 200. A scheduled job processes the queue with full permissions.

Template:

```python
import hmac
import hashlib
import json

import frappe

@frappe.whitelist(allow_guest=True)  # required for inbound webhooks; rate-limit in site_config
def receive_callback():
    raw = frappe.request.get_data(cache=False)
    signature = frappe.get_request_header("X-Signature") or ""
    secret = frappe.conf.get("payment_gateway_webhook_secret")
    if not _verify(raw, signature, secret):
        frappe.local.response.http_status_code = 401
        return {"ok": False}

    payload = json.loads(raw)
    request_id = payload.get("event_id")
    if not request_id or frappe.db.exists("Payment Callback Queue", request_id):
        return {"ok": True, "duplicate": True}

    frappe.get_doc({
        "doctype": "Payment Callback Queue",
        "name": request_id,
        "raw_payload": raw.decode("utf-8"),
        "status": "Pending",
    }).insert(ignore_permissions=True)  # justified: pre-auth queue write
    frappe.db.commit()
    return {"ok": True}


def _verify(raw: bytes, sig: str, secret: str | None) -> bool:
    if not secret or not sig:
        return False
    expected = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)
```

Note the **only** time `ignore_permissions=True` is acceptable: pre-auth queue write where the next-stage processor runs with proper permission. The audit log catches it; the security review whitelists it.

## Outbound to APIs that need OAuth

Frappe ships an OAuth Provider DocType. For storing credentials of external systems you call:

```python
# Store the access_token in a Connected App row, not in code.
ca = frappe.get_doc("Connected App", "Zapier")
token = ca.get_token()
```

Never hardcode `Bearer xxx`. The semgrep rule `block-credential-leak` catches this at PR.

## Rate limit yourself

External APIs throttle. Wrap every call in a retry-with-backoff helper:

```python
from time import sleep
import requests

def call_with_backoff(url, *, headers, json_body, max_retries=3):
    for attempt in range(max_retries):
        r = requests.post(url, headers=headers, json=json_body, timeout=10)
        if r.status_code == 429 and attempt < max_retries - 1:
            retry_after = int(r.headers.get("Retry-After", 2 ** attempt))
            sleep(retry_after)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("max retries exceeded")
```
