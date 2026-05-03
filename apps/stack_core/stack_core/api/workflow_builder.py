"""Whitelisted endpoint: build (or update) a Workflow + experiment definition."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe.utils import now_datetime

from stack_core.api._decorators import audited
from stack_core.guardrails.permission_enforcer import refuse_on_production
from stack_core.guardrails.schema_validator import validate_blueprint_payload
from stack_core.guardrails.workflow_validator import validate_workflow_definition


@frappe.whitelist()
@audited(action="api.build_workflow")
def build(workflow_name: str, payload: str | dict) -> dict[str, Any]:
    if not frappe.has_permission("Stack Workflow Def", ptype="create"):
        raise frappe.PermissionError("Need Stack Workflow Def create permission")

    refuse_on_production()

    parsed = json.loads(payload) if isinstance(payload, str) else (payload or {})

    validate_blueprint_payload("Workflow", parsed)
    validate_workflow_definition(parsed["states"], parsed["transitions"])

    if frappe.db.exists("Stack Workflow Def", workflow_name):
        wf = frappe.get_doc("Stack Workflow Def", workflow_name)
    else:
        wf = frappe.get_doc(
            {
                "doctype": "Stack Workflow Def",
                "workflow_name": workflow_name,
                "target_doctype": parsed["target_doctype"],
                "is_active": 0,
            }
        )
    wf.target_doctype = parsed["target_doctype"]
    wf.states_json = json.dumps(parsed["states"])
    wf.transitions_json = json.dumps(parsed["transitions"])
    if parsed.get("experiment_id"):
        wf.experiment_id = parsed["experiment_id"]
        wf.experiment_status = parsed.get("experiment_status", "Running")
    wf.save(ignore_permissions=False)
    frappe.db.commit()

    return {
        "workflow": wf.name,
        "experiment_id": wf.experiment_id,
        "applied_at": now_datetime().isoformat(),
    }
