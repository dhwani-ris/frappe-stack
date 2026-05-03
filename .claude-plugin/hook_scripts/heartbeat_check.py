#!/usr/bin/env python3
"""Stop hook: if PLAN.md changed this session and HEARTBEAT.md didn't, prompt."""

from __future__ import annotations

import json
import subprocess
import sys


def changed_in_session(path: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", path],
            capture_output=True, text=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return path in (out.stdout or "")


def main() -> int:
    plan_changed = changed_in_session("PLAN.md")
    heartbeat_changed = changed_in_session("HEARTBEAT.md")

    if plan_changed and not heartbeat_changed:
        print(json.dumps({
            "decision": "approve",
            "reason": "PLAN.md changed but HEARTBEAT.md not stamped. "
                      "Per Builder Protocol, every phase transition gets a HEARTBEAT entry. "
                      "Consider adding one before this session ends.",
        }))
        return 0

    print(json.dumps({"decision": "approve"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
