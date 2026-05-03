import json

import frappe
from frappe.tests.utils import FrappeTestCase

from stack_core.api.doctype_builder import build


class TestApiDoctypeBuilder(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.cleanup_blueprints = []
        self.cleanup_doctypes = []

    def tearDown(self):
        for n in self.cleanup_doctypes:
            if frappe.db.exists("DocType", n):
                frappe.delete_doc("DocType", n, force=True, ignore_missing=True)
        for n in self.cleanup_blueprints:
            if frappe.db.exists("Stack Blueprint", n):
                frappe.delete_doc("Stack Blueprint", n, force=True, ignore_missing=True)

    def _payload(self, name: str = "_Test API Beneficiary") -> dict:
        return {
            "name": name,
            "module": "Custom",
            "fields": [
                {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name", "reqd": 1},
                {"fieldname": "village", "fieldtype": "Data", "label": "Village"},
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
            ],
        }

    def test_happy_path_creates_doctype_and_blueprint(self):
        bp_name = "_Test BP API_HappyPath"
        self.cleanup_blueprints.append(bp_name)
        self.cleanup_doctypes.append("_Test API Beneficiary")

        result = build(blueprint_name=bp_name, payload=json.dumps(self._payload()))

        self.assertEqual(result["status"], "Applied")
        self.assertEqual(result["doctype"], "_Test API Beneficiary")
        self.assertTrue(frappe.db.exists("DocType", "_Test API Beneficiary"))
        bp = frappe.get_doc("Stack Blueprint", bp_name)
        self.assertEqual(bp.status, "Applied")
        self.assertIsNotNone(bp.applied_at)

    def test_reserved_name_refused(self):
        payload = self._payload(name="User")
        bp_name = "_Test BP API_Reserved"
        self.cleanup_blueprints.append(bp_name)
        with self.assertRaises(Exception):
            build(blueprint_name=bp_name, payload=json.dumps(payload))

    def test_audit_log_written_on_success(self):
        bp_name = "_Test BP API_Audit"
        self.cleanup_blueprints.append(bp_name)
        self.cleanup_doctypes.append("_Test API Audit")
        before = frappe.db.count("Stack Audit Log", {"action": "api.build_doctype"})
        build(blueprint_name=bp_name, payload=json.dumps(self._payload(name="_Test API Audit")))
        after = frappe.db.count("Stack Audit Log", {"action": "api.build_doctype"})
        self.assertGreater(after, before)
