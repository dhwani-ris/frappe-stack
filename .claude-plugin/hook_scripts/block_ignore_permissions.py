#!/usr/bin/env python3
"""PreToolUse hook: scan Edit/Write content for permission-bypass patterns."""

from __future__ import annotations

import json
import re
import sys

BLOCKED = [
    (re.compile(r"\bignore_permissions\s*=\s*True\b"),
     "ignore_permissions=True bypasses the entire Frappe permission model. "
     "If this is justified, route through stack_core.api._decorators (audit-logged)."),
    (re.compile(r"@frappe\.whitelist\s*\(\s*allow_guest\s*=\s*True"),
     "allow_guest=True on a whitelisted method requires explicit security review. "
     "Default to allow_guest=False; if you need public access, route through a "
     "rate-limited public endpoint with HMAC verification."),
    (re.compile(r"if\s+frappe\.session\.user\s*==\s*['\"]"),
     "Hardcoded user-identity check refused. Use frappe.has_permission() or roles."),
    (re.compile(r"if\s+['\"][\w ]+['\"]\s+in\s+frappe\.get_roles\("),
     "Hardcoded role-string membership check is fragile. Prefer frappe.has_permission()."),
]


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    content = tool_input.get("new_string") or tool_input.get("content") or ""

    for pattern, reason in BLOCKED:
        m = pattern.search(content)
        if m:
            print(json.dumps({
                "decision": "block",
                "reason": f"{reason} (matched: {m.group(0)!r})",
            }))
            return 0

    print(json.dumps({"decision": "approve"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
