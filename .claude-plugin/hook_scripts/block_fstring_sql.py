#!/usr/bin/env python3
"""PreToolUse hook: refuse Python content containing f-string / .format() / % SQL."""

from __future__ import annotations

import json
import re
import sys

# Heuristic: detect SQL keywords inside an f-string or .format() target.
SUSPECT = [
    re.compile(
        r"frappe\.db\.sql\s*\(\s*f['\"][^'\"]*\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"frappe\.db\.sql\s*\(\s*['\"][^'\"]*\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)\b[^'\"]*\.format\s*\(",
        re.IGNORECASE,
    ),
    re.compile(
        r"frappe\.db\.sql\s*\(\s*['\"][^'\"]*%s[^'\"]*['\"]\s*%\s*\(",
    ),
    re.compile(
        r"frappe\.db\.sql\s*\(\s*f['\"][^'\"]*\{[^}]+\}",
    ),
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

    if not file_path.endswith(".py"):
        print(json.dumps({"decision": "approve"}))
        return 0

    for pattern in SUSPECT:
        m = pattern.search(content)
        if m:
            print(json.dumps({
                "decision": "block",
                "reason": (
                    f"f-string / .format() / % SQL detected in {file_path}: {m.group(0)[:120]!r}. "
                    "Use parameterized queries: frappe.db.sql('… WHERE x = %s', (value,)) "
                    "or frappe.qb (the query builder)."
                ),
            }))
            return 0

    print(json.dumps({"decision": "approve"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
