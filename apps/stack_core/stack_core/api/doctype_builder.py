"""Whitelisted endpoint: build (or update) a DocType from a blueprint payload.

Flow:
  1. Permission check (must hold Stack Author or higher).
  2. Refuse if the site is marked is_production=1.
  3. Validate payload against the DocType schema.
  4. Run reserved-name + fieldtype guardrails.
  5. Persist as Stack Blueprint (status=Draft initially; flips to Applied on success).
  6. Materialize the actual Frappe DocType via the framework.
  7. Audit log row written via @audited.
"""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe.utils import cstr, now_datetime

from stack_core.api._decorators import audited
from stack_core.guardrails.fieldtype_whitelist import enforce_fieldtype_whitelist
from stack_core.guardrails.permission_enforcer import refuse_on_production
from stack_core.guardrails.reserved_names import enforce_reserved_names
from stack_core.guardrails.schema_validator import validate_blueprint_payload


@frappe.whitelist()
@audited(action="api.build_doctype")
def build(blueprint_name: str, payload: str | dict) -> dict[str, Any]:
    if not frappe.has_permission("Stack Blueprint", ptype="create"):
        raise frappe.PermissionError("Need Stack Blueprint create permission")

    refuse_on_production()

    parsed = _parse_payload(payload)

    validate_blueprint_payload("DocType", parsed)
    enforce_reserved_names(parsed["name"])
    enforce_fieldtype_whitelist(parsed.get("fields", []))

    blueprint = _upsert_blueprint(blueprint_name, parsed)

    try:
        materialized = _materialize_doctype(parsed)
        blueprint.status = "Applied"
        blueprint.applied_at = now_datetime()
        blueprint.applied_by = frappe.session.user
    except Exception as e:
        blueprint.status = "Failed"
        blueprint.validation_errors = cstr(e)
        blueprint.save(ignore_permissions=False)
        raise

    blueprint.save(ignore_permissions=False)
    frappe.db.commit()

    return {
        "blueprint": blueprint.name,
        "doctype": materialized,
        "status": blueprint.status,
    }


def _parse_payload(payload: str | dict) -> dict:
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError as e:
            frappe.throw(frappe._("payload is not valid JSON: {0}").format(e))
    return payload or {}


def _upsert_blueprint(name: str, parsed: dict) -> Any:
    if frappe.db.exists("Stack Blueprint", name):
        bp = frappe.get_doc("Stack Blueprint", name)
        bp.payload = json.dumps(parsed)
        bp.version = (bp.version or 0) + 1
        bp.status = "Validating"
    else:
        bp = frappe.get_doc(
            {
                "doctype": "Stack Blueprint",
                "blueprint_name": name,
                "blueprint_type": "DocType",
                "version": 1,
                "status": "Validating",
                "payload": json.dumps(parsed),
            }
        )
    bp.save(ignore_permissions=False)
    return bp


def _materialize_doctype(parsed: dict) -> str:
    """Create the Frappe DocType row + meta. Idempotent — updates if exists."""
    name = parsed["name"]
    is_new = not frappe.db.exists("DocType", name)

    doc = frappe.get_doc(
        {
            "doctype": "DocType",
            "name": name,
            "module": parsed.get("module", "Custom"),
            "custom": 1,
            "track_changes": int(parsed.get("track_changes", 1)),
            "naming_rule": parsed.get("naming_rule", "Random"),
            "autoname": parsed.get("autoname"),
            "fields": parsed["fields"],
            "permissions": parsed["permissions"],
        }
        if is_new
        else frappe.get_doc("DocType", name).update(
            {
                "fields": parsed["fields"],
                "permissions": parsed["permissions"],
            }
        )
    )
    doc.save(ignore_permissions=False)
    return name
