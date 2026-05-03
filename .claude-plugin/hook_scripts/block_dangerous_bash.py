#!/usr/bin/env python3
"""PreToolUse hook: refuse dangerous bash commands.

Reads the tool input from stdin (JSON), writes a decision JSON to stdout.
Decision schema: {"decision": "approve"|"block", "reason": "..."}
"""

from __future__ import annotations

import json
import re
import sys

DANGEROUS_PATTERNS = [
    (re.compile(r"\brm\s+-rf\s+/(\s|$)"), "rm -rf / refused"),
    (re.compile(r"\brm\s+-rf\s+\*\s*$"), "rm -rf * refused"),
    (re.compile(r"\bbench\s+(--site\s+\S+\s+)?drop-site\b"), "bench drop-site refused"),
    (re.compile(r"\bgit\s+push\s+(.*\s+)?--force\s+(.*\s+)?(main|master|develop|release/.*)"),
     "git push --force to protected branch refused"),
    (re.compile(r"\bDROP\s+(TABLE|DATABASE)\b", re.IGNORECASE), "DROP TABLE/DATABASE refused"),
    (re.compile(r"\bDELETE\s+FROM\s+\S+\s*;?\s*$", re.IGNORECASE),
     "DELETE without WHERE refused — add a WHERE clause or use a controlled API"),
    (re.compile(r"\bcurl\s+.*\|\s*sh\b"), "curl | sh refused — fetch and inspect first"),
]


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return 0

    cmd = (payload.get("tool_input", {}) or {}).get("command", "")
    for pattern, reason in DANGEROUS_PATTERNS:
        if pattern.search(cmd):
            print(json.dumps({"decision": "block", "reason": reason}))
            return 0

    print(json.dumps({"decision": "approve"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
