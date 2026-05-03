#!/usr/bin/env python3
"""PostToolUse hook: append every Bash/Edit/Write to a local audit log.

Independent of the on-site Stack Audit Log. The local log helps when a session
later needs to reconstruct what happened, even if the site's audit log is
unavailable (e.g., debugging a build that failed before any API call).
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path


AUDIT_PATH = Path(".frappe-stack") / "audit.jsonl"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    tool_response = payload.get("tool_response", {}) or {}

    entry = {
        "ts": dt.datetime.utcnow().isoformat() + "Z",
        "tool": tool_name,
        "input_summary": _summarize_input(tool_name, tool_input),
        "ok": not bool(tool_response.get("error")),
    }

    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return 0


def _summarize_input(tool: str, ti: dict) -> dict:
    if tool == "Bash":
        cmd = ti.get("command", "") or ""
        return {"cmd": cmd[:200]}
    if tool in ("Edit", "Write"):
        return {"file": ti.get("file_path", "")}
    return {k: str(v)[:120] for k, v in ti.items()}


if __name__ == "__main__":
    sys.exit(main())
