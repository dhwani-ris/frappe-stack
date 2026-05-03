"""Permission helpers and global doc_event hooks.

`block_hard_delete_on_audit_tagged` is wired in hooks.py as a `before_delete`
on `*` so it sees every delete attempt across the site. It refuses deletes on
DocTypes the operator has tagged as audit-protected (via the `is_audit_tagged`
flag on the DocType meta) regardless of who is asking.
"""

from __future__ import annotations

import frappe


def block_hard_delete_on_audit_tagged(doc, method=None) -> None:
    if doc.doctype in {"Stack Audit Log", "Experiment Assignment"}:
        frappe.throw(
            frappe._(
                "{0} is append-only by policy. Hard delete is blocked. "
                "Soft-archive via export instead."
            ).format(doc.doctype)
        )


def require_role(role: str) -> None:
    """Raise PermissionError if the current session user lacks `role`."""
    user = frappe.session.user
    if role not in frappe.get_roles(user):
        raise frappe.PermissionError(f"User {user!r} lacks required role {role!r}")


def is_production_site() -> bool:
    config = frappe.conf.get("stack_core", {}) or {}
    return bool(config.get("is_production"))


def refuse_on_production() -> None:
    """Refuse a mutating operation if site_config marks this site as production."""
    if is_production_site():
        frappe.throw(
            frappe._(
                "This site is marked is_production=1 in stack_core config. "
                "Direct API writes are blocked; route through /frappe-stack:promote instead."
            )
        )
