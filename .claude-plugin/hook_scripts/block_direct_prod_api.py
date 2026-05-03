#!/usr/bin/env python3
"""PreToolUse hook: refuse direct API writes to a production site.

Reads .frappe-stack/config.json, identifies which hosts are flagged
is_production=true, and refuses any Bash/WebFetch tool call that hits
those hosts with a non-GET method or a method=POST/PUT/DELETE.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def load_prod_hosts() -> set[str]:
    config_path = Path(".frappe-stack/config.json")
    if not config_path.exists():
        return set()
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    prod_hosts: set[str] = set()
    for site in (config.get("sites") or {}).values():
        if site.get("is_production"):
            host = urlparse(site.get("url", "")).hostname
            if host:
                prod_hosts.add(host.lower())
    return prod_hosts


def is_mutating_call(cmd: str, url: str | None) -> bool:
    if url:
        return True
    upper = cmd.upper()
    if any(verb in upper for verb in ("POST ", "PUT ", "DELETE ", "PATCH ")):
        return True
    if re.search(r"\bcurl\b.*-X\s+(POST|PUT|DELETE|PATCH)", cmd, re.IGNORECASE):
        return True
    if re.search(r"\bcurl\b.*--data\b", cmd):
        return True
    return False


def extract_host(cmd: str, url: str | None) -> str | None:
    if url:
        return urlparse(url).hostname or None
    m = re.search(r"https?://([\w.\-]+)", cmd)
    return m.group(1).lower() if m else None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    cmd = tool_input.get("command", "")
    url = tool_input.get("url")

    prod_hosts = load_prod_hosts()
    if not prod_hosts:
        print(json.dumps({"decision": "approve"}))
        return 0

    host = extract_host(cmd, url)
    if host and host in prod_hosts and is_mutating_call(cmd, url):
        print(json.dumps({
            "decision": "block",
            "reason": f"Refusing mutating call to production host {host!r}. "
                      f"Production is git-only; use /frappe-stack:promote instead.",
        }))
        return 0

    print(json.dumps({"decision": "approve"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
