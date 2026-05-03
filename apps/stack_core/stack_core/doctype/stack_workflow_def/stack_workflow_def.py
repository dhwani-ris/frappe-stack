import json

import frappe
from frappe.model.document import Document

from stack_core.guardrails.workflow_validator import validate_workflow_definition


class StackWorkflowDef(Document):
    def validate(self):
        states = self._parse_json_field("states_json")
        transitions = self._parse_json_field("transitions_json")

        try:
            validate_workflow_definition(states, transitions)
        except Exception as e:
            self.validation_errors = str(e)
            frappe.throw(frappe._("Workflow validation failed: {0}").format(e))

        self.validation_errors = None

        if self.experiment_id and not self._has_split_state(states):
            frappe.throw(
                frappe._(
                    "Experiment ID set but no split state found. "
                    "Add a state with type='split' and traffic_split, or clear the experiment ID."
                )
            )

    def _parse_json_field(self, fieldname: str):
        value = self.get(fieldname)
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                frappe.throw(frappe._("{0} is not valid JSON: {1}").format(fieldname, e))
        return []

    @staticmethod
    def _has_split_state(states: list[dict]) -> bool:
        return any(s.get("type") == "split" for s in states)
