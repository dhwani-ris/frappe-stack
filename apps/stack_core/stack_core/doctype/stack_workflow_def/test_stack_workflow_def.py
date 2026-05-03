import json

import frappe
from frappe.tests.utils import FrappeTestCase


class TestStackWorkflowDef(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.cleanup = []

    def tearDown(self):
        for name in self.cleanup:
            if frappe.db.exists("Stack Workflow Def", name):
                frappe.delete_doc("Stack Workflow Def", name, force=True)

    def _make(self, name: str, states: list, transitions: list, **extra):
        doc = frappe.get_doc(
            {
                "doctype": "Stack Workflow Def",
                "workflow_name": name,
                "target_doctype": "ToDo",
                "states_json": json.dumps(states),
                "transitions_json": json.dumps(transitions),
                **extra,
            }
        )
        self.cleanup.append(name)
        return doc

    def test_simple_linear_workflow(self):
        doc = self._make(
            "_Test WF Linear",
            states=[
                {"name": "Draft", "type": "normal", "role": "System Manager"},
                {"name": "Approved", "type": "terminal", "role": "System Manager"},
            ],
            transitions=[{"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}],
        )
        doc.insert()
        self.assertIsNone(doc.validation_errors)

    def test_workflow_without_terminal_state_rejected(self):
        doc = self._make(
            "_Test WF NoTerminal",
            states=[
                {"name": "A", "type": "normal", "role": "System Manager"},
                {"name": "B", "type": "normal", "role": "System Manager"},
            ],
            transitions=[{"from": "A", "to": "B", "action": "Move", "role": "System Manager"}],
        )
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_workflow_with_orphan_state_rejected(self):
        doc = self._make(
            "_Test WF Orphan",
            states=[
                {"name": "Draft", "type": "normal", "role": "System Manager"},
                {"name": "Approved", "type": "terminal", "role": "System Manager"},
                {"name": "Orphan", "type": "normal", "role": "System Manager"},
            ],
            transitions=[{"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}],
        )
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_split_state_with_experiment(self):
        doc = self._make(
            "_Test WF Split",
            states=[
                {"name": "Draft", "type": "normal", "role": "System Manager"},
                {
                    "name": "Review",
                    "type": "split",
                    "role": "System Manager",
                    "traffic_split": {"arm_a": 50, "arm_b": 50},
                    "next_states": {"arm_a": "Manager", "arm_b": "Auto"},
                },
                {"name": "Manager", "type": "terminal", "role": "System Manager"},
                {"name": "Auto", "type": "terminal", "role": "System Manager"},
            ],
            transitions=[{"from": "Draft", "to": "Review", "action": "Submit", "role": "System Manager"}],
            experiment_id="exp_001",
            experiment_status="Running",
        )
        doc.insert()
        self.assertIsNone(doc.validation_errors)

    def test_experiment_id_without_split_state_rejected(self):
        doc = self._make(
            "_Test WF ExpNoSplit",
            states=[
                {"name": "Draft", "type": "normal", "role": "System Manager"},
                {"name": "Approved", "type": "terminal", "role": "System Manager"},
            ],
            transitions=[{"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}],
            experiment_id="exp_002",
        )
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_state_missing_role_rejected(self):
        doc = self._make(
            "_Test WF NoRole",
            states=[
                {"name": "Draft", "type": "normal"},
                {"name": "Approved", "type": "terminal", "role": "System Manager"},
            ],
            transitions=[{"from": "Draft", "to": "Approved", "action": "Approve", "role": "System Manager"}],
        )
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_traffic_split_must_sum_to_100(self):
        doc = self._make(
            "_Test WF BadSplit",
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
            transitions=[{"from": "Draft", "to": "Review", "action": "Submit", "role": "System Manager"}],
        )
        with self.assertRaises(frappe.ValidationError):
            doc.insert()
