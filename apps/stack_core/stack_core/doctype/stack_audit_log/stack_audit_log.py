import frappe
from frappe.model.document import Document


class StackAuditLog(Document):
    def on_trash(self):
        frappe.throw(
            frappe._(
                "Stack Audit Log rows are append-only. "
                "Hard delete is blocked by policy (D-08). Archive via export instead."
            )
        )


def permission_query(user: str) -> str:
    """Restrict audit log visibility:
    - System Manager + Stack Admin see everything (no filter -> empty string).
    - Stack Author sees only rows where they were the actor.
    - Everyone else sees nothing.
    """
    if not user:
        user = frappe.session.user
    roles = set(frappe.get_roles(user))
    if {"System Manager", "Stack Admin"} & roles:
        return ""
    if "Stack Author" in roles:
        return f"`tabStack Audit Log`.actor = {frappe.db.escape(user)}"
    return "1=0"
