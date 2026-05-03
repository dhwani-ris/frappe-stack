"""Whitelisted endpoint: dump every Stack Blueprint as JSON for git export."""

from __future__ import annotations

import json
from typing import Any

import frappe

from stack_core.api._decorators import audited


@frappe.whitelist()
@audited(action="api.export_fixtures")
def export() -> dict[str, Any]:
    if not frappe.has_permission("Stack Blueprint", ptype="export"):
        raise frappe.PermissionError("Need Stack Blueprint export permission")

    blueprints = frappe.get_all(
        "Stack Blueprint",
        filters={"status": "Applied"},
        fields=["name", "blueprint_name", "blueprint_type", "version", "payload", "git_commit_sha"],
        order_by="blueprint_type, blueprint_name",
    )

    workflows = frappe.get_all(
        "Stack Workflow Def",
        fields=["name", "workflow_name", "target_doctype", "is_active",
                "states_json", "transitions_json", "experiment_id", "experiment_status"],
        order_by="workflow_name",
    )

    return {
        "schema_version": "0.1",
        "exported_at": frappe.utils.now(),
        "site": frappe.local.site,
        "blueprints": [{**b, "payload": _safe_json(b.get("payload"))} for b in blueprints],
        "workflows": [
            {**w, "states": _safe_json(w.get("states_json")), "transitions": _safe_json(w.get("transitions_json"))}
            for w in workflows
        ],
    }


def _safe_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value
