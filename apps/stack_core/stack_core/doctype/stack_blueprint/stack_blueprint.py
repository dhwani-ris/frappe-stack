import json

import frappe
from frappe.model.document import Document

from stack_core.guardrails.fieldtype_whitelist import enforce_fieldtype_whitelist
from stack_core.guardrails.reserved_names import enforce_reserved_names
from stack_core.guardrails.schema_validator import validate_blueprint_payload


class StackBlueprint(Document):
    def validate(self):
        self._parse_payload()
        self._run_guardrails()

    def _parse_payload(self):
        if isinstance(self.payload, str):
            try:
                self._parsed_payload = json.loads(self.payload)
            except json.JSONDecodeError as e:
                frappe.throw(frappe._("Payload is not valid JSON: {0}").format(str(e)))
        else:
            self._parsed_payload = self.payload or {}

    def _run_guardrails(self):
        errors: list[str] = []

        try:
            validate_blueprint_payload(self.blueprint_type, self._parsed_payload)
        except Exception as e:
            errors.append(f"schema: {e}")

        if self.blueprint_type == "DocType":
            try:
                enforce_reserved_names(self._parsed_payload.get("name", ""))
            except Exception as e:
                errors.append(f"reserved_name: {e}")
            try:
                enforce_fieldtype_whitelist(self._parsed_payload.get("fields", []))
            except Exception as e:
                errors.append(f"fieldtype: {e}")

        if errors:
            self.validation_errors = "\n".join(errors)
            self.status = "Failed"
            frappe.throw(frappe._("Blueprint validation failed:\n{0}").format(self.validation_errors))

        self.validation_errors = None

    def on_update(self):
        from stack_core.api._decorators import write_audit_log

        write_audit_log(
            action="blueprint.update",
            blueprint=self.name,
            after_json=self.as_dict(),
        )
