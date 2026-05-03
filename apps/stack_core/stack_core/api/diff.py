"""Whitelisted endpoint: compare on-site state to the configured git config-repo."""

from __future__ import annotations

from typing import Any

import frappe

from stack_core.api._decorators import audited
from stack_core.api.fixtures import export as export_fixtures


@frappe.whitelist()
@audited(action="api.diff_against_git")
def diff() -> dict[str, Any]:
    if not frappe.has_permission("Stack Blueprint", ptype="read"):
        raise frappe.PermissionError("Need Stack Blueprint read permission")

    from stack_core.git_bridge.differ import diff_site_vs_git

    site_state = export_fixtures()
    return diff_site_vs_git(site_state)
