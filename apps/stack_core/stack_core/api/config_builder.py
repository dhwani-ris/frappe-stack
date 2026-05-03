"""Whitelisted endpoint: apply Custom Field / Property Setter / single-doc settings."""

from __future__ import annotations

import json
from typing import Any

import frappe

from stack_core.api._decorators import audited
from stack_core.guardrails.permission_enforcer import refuse_on_production
from stack_core.guardrails.schema_validator import validate_blueprint_payload


@frappe.whitelist()
@audited(action="api.build_custom_field")
def build_custom_field(blueprint_name: str, payload: str | dict) -> dict[str, Any]:
    if not frappe.has_permission("Custom Field", ptype="create"):
        raise frappe.PermissionError("Need Custom Field create permission")

    refuse_on_production()

    parsed = json.loads(payload) if isinstance(payload, str) else (payload or {})
    validate_blueprint_payload("Custom Field", parsed)

    cf = frappe.get_doc(
        {
            "doctype": "Custom Field",
            **parsed,
        }
    )
    cf.insert(ignore_permissions=False)
    frappe.db.commit()
    return {"custom_field": cf.name, "blueprint": blueprint_name}


@frappe.whitelist()
@audited(action="api.build_property_setter")
def build_property_setter(blueprint_name: str, payload: str | dict) -> dict[str, Any]:
    if not frappe.has_permission("Property Setter", ptype="create"):
        raise frappe.PermissionError("Need Property Setter create permission")

    refuse_on_production()

    parsed = json.loads(payload) if isinstance(payload, str) else (payload or {})
    validate_blueprint_payload("Property Setter", parsed)

    ps = frappe.get_doc(
        {
            "doctype": "Property Setter",
            "doctype_or_field": "DocField" if parsed.get("field_name") else "DocType",
            **parsed,
        }
    )
    ps.insert(ignore_permissions=False)
    frappe.db.commit()
    return {"property_setter": ps.name, "blueprint": blueprint_name}
