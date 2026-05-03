#!/usr/bin/env python3
"""PreToolUse hook: refuse Edit/Write that contains hardcoded credentials."""

from __future__ import annotations

import json
import re
import sys

PATTERNS = [
    (re.compile(r"\bAKIA[A-Z0-9]{16}\b"), "AWS Access Key ID detected"),
    (re.compile(r"\bASIA[A-Z0-9]{16}\b"), "AWS temporary key detected"),
    (re.compile(r"\bgh[opusr]_[A-Za-z0-9]{36,}\b"), "GitHub token detected"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "Private key block detected"),
    (re.compile(r"\b(api[_-]?key|password|secret|token)\s*=\s*['\"][^'\"]{12,}['\"]", re.IGNORECASE),
     "Hardcoded credential literal detected. Move to env var or secret manager."),
    (re.compile(r"Authorization:\s*Bearer\s+[A-Za-z0-9._\-]{20,}"),
     "Hardcoded Bearer token detected. Read from frappe.conf or env at request time."),
]


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("new_string") or tool_input.get("content") or ""

    if file_path.endswith((".env.example", "test_fixtures.json")):
        print(json.dumps({"decision": "approve"}))
        return 0

    for pattern, reason in PATTERNS:
        m = pattern.search(content)
        if m:
            print(json.dumps({
                "decision": "block",
                "reason": f"{reason} in {file_path or '<inline>'}",
            }))
            return 0

    print(json.dumps({"decision": "approve"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
