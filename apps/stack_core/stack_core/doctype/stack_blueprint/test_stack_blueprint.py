import json

import frappe
from frappe.tests.utils import FrappeTestCase


class TestStackBlueprint(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.cleanup_names = []

    def tearDown(self):
        for name in self.cleanup_names:
            if frappe.db.exists("Stack Blueprint", name):
                frappe.delete_doc("Stack Blueprint", name, force=True)

    def _make(self, name: str, blueprint_type: str, payload: dict):
        doc = frappe.get_doc(
            {
                "doctype": "Stack Blueprint",
                "blueprint_name": name,
                "blueprint_type": blueprint_type,
                "version": 1,
                "status": "Draft",
                "payload": json.dumps(payload),
            }
        )
        self.cleanup_names.append(name)
        return doc

    def test_valid_doctype_blueprint_saves(self):
        payload = {
            "name": "_Test Beneficiary",
            "fields": [
                {"fieldname": "full_name", "fieldtype": "Data", "label": "Full Name", "reqd": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}],
        }
        doc = self._make("_Test BP Valid", "DocType", payload)
        doc.insert()
        self.assertEqual(doc.status, "Draft")
        self.assertIsNone(doc.validation_errors)

    def test_reserved_name_rejected(self):
        payload = {
            "name": "User",
            "fields": [{"fieldname": "x", "fieldtype": "Data", "label": "X"}],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}],
        }
        doc = self._make("_Test BP Reserved", "DocType", payload)
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_disallowed_fieldtype_rejected(self):
        payload = {
            "name": "_Test BadField",
            "fields": [
                {"fieldname": "secret", "fieldtype": "Password", "label": "Secret"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}],
        }
        doc = self._make("_Test BP BadField", "DocType", payload)
        frappe.set_user("test_author@example.com") if frappe.db.exists("User", "test_author@example.com") else None
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_invalid_json_payload_rejected(self):
        doc = frappe.get_doc(
            {
                "doctype": "Stack Blueprint",
                "blueprint_name": "_Test BP BadJSON",
                "blueprint_type": "DocType",
                "version": 1,
                "status": "Draft",
                "payload": "{not valid json",
            }
        )
        self.cleanup_names.append("_Test BP BadJSON")
        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_unique_blueprint_name(self):
        payload = {
            "name": "_Test UniqueOne",
            "fields": [{"fieldname": "x", "fieldtype": "Data", "label": "X"}],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}],
        }
        first = self._make("_Test BP Unique", "DocType", payload)
        first.insert()
        second = self._make("_Test BP Unique", "DocType", payload)
        with self.assertRaises(frappe.DuplicateEntryError):
            second.insert()
