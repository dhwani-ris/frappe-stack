from frappe.tests.utils import FrappeTestCase
from jsonschema import ValidationError

from stack_core.guardrails.reserved_names import enforce_reserved_names
from stack_core.guardrails.schema_validator import validate_blueprint_payload
from stack_core.guardrails.workflow_validator import validate_workflow_definition


class TestSchemaValidator(FrappeTestCase):
    def test_valid_doctype_passes(self):
        validate_blueprint_payload(
            "DocType",
            {
                "name": "Beneficiary",
                "fields": [{"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name"}],
                "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}],
            },
        )

    def test_doctype_missing_fields_rejected(self):
        with self.assertRaises(ValidationError):
            validate_blueprint_payload(
                "DocType",
                {"name": "Foo", "permissions": [{"role": "System Manager"}]},
            )

    def test_doctype_with_extra_top_level_keys_rejected(self):
        with self.assertRaises(ValidationError):
            validate_blueprint_payload(
                "DocType",
                {
                    "name": "Foo",
                    "fields": [{"fieldname": "x", "fieldtype": "Data"}],
                    "permissions": [{"role": "System Manager"}],
                    "evil_extra": "yo",
                },
            )

    def test_doctype_invalid_fieldname_pattern_rejected(self):
        with self.assertRaises(ValidationError):
            validate_blueprint_payload(
                "DocType",
                {
                    "name": "Foo",
                    "fields": [{"fieldname": "BadName", "fieldtype": "Data"}],
                    "permissions": [{"role": "System Manager"}],
                },
            )


class TestReservedNames(FrappeTestCase):
    def test_user_blocked(self):
        with self.assertRaises(ValueError):
            enforce_reserved_names("User")

    def test_stack_prefix_blocked(self):
        with self.assertRaises(ValueError):
            enforce_reserved_names("Stack Foo")

    def test_normal_name_allowed(self):
        enforce_reserved_names("Beneficiary")


class TestWorkflowValidator(FrappeTestCase):
    def test_simple_linear_passes(self):
        validate_workflow_definition(
            states=[
                {"name": "Draft", "type": "normal", "role": "System Manager"},
                {"name": "Approved", "type": "terminal", "role": "System Manager"},
            ],
            transitions=[{"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}],
        )

    def test_no_terminal_rejected(self):
        with self.assertRaises(ValueError):
            validate_workflow_definition(
                states=[
                    {"name": "A", "type": "normal", "role": "System Manager"},
                    {"name": "B", "type": "normal", "role": "System Manager"},
                ],
                transitions=[{"from": "A", "to": "B", "action": "Move", "role": "System Manager"}],
            )

    def test_orphan_rejected(self):
        with self.assertRaises(ValueError):
            validate_workflow_definition(
                states=[
                    {"name": "Draft", "type": "normal", "role": "System Manager"},
                    {"name": "Approved", "type": "terminal", "role": "System Manager"},
                    {"name": "Lost", "type": "normal", "role": "System Manager"},
                ],
                transitions=[
                    {"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}
                ],
            )

    def test_split_with_imbalanced_traffic_rejected(self):
        with self.assertRaises(ValueError):
            validate_workflow_definition(
                states=[
                    {"name": "Draft", "type": "normal", "role": "System Manager"},
                    {
                        "name": "Review",
                        "type": "split",
                        "role": "System Manager",
                        "traffic_split": {"arm_a": 30, "arm_b": 30},
                        "next_states": {"arm_a": "M", "arm_b": "A"},
                    },
                    {"name": "M", "type": "terminal", "role": "System Manager"},
                    {"name": "A", "type": "terminal", "role": "System Manager"},
                ],
                transitions=[
                    {"from": "Draft", "to": "Review", "action": "Submit", "role": "System Manager"}
                ],
            )

    def test_state_missing_role_rejected(self):
        with self.assertRaises(ValueError):
            validate_workflow_definition(
                states=[
                    {"name": "Draft", "type": "normal"},
                    {"name": "Approved", "type": "terminal", "role": "System Manager"},
                ],
                transitions=[
                    {"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}
                ],
            )
