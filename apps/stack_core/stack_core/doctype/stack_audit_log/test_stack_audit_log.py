import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime


class TestStackAuditLog(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")

    def test_audit_log_insert(self):
        doc = frappe.get_doc(
            {
                "doctype": "Stack Audit Log",
                "actor": "Administrator",
                "action": "blueprint.test",
                "timestamp": now_datetime(),
                "result": "success",
                "after_json": '{"x": 1}',
            }
        ).insert()
        self.assertEqual(doc.action, "blueprint.test")
        frappe.delete_doc("Stack Audit Log", doc.name, force=True)

    def test_hard_delete_blocked(self):
        doc = frappe.get_doc(
            {
                "doctype": "Stack Audit Log",
                "actor": "Administrator",
                "action": "blueprint.delete_test",
                "timestamp": now_datetime(),
                "result": "success",
            }
        ).insert()
        with self.assertRaises(frappe.ValidationError):
            doc.delete()
        frappe.db.delete("Stack Audit Log", {"name": doc.name})
        frappe.db.commit()

    def test_permission_query_for_admin(self):
        from stack_core.doctype.stack_audit_log.stack_audit_log import permission_query

        result = permission_query("Administrator")
        self.assertEqual(result, "")

    def test_permission_query_for_unknown_user(self):
        from stack_core.doctype.stack_audit_log.stack_audit_log import permission_query

        result = permission_query("nonexistent@example.com")
        self.assertIn("1=0", result)
