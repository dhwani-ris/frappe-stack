"""Reserved DocType names — blueprints are refused if they collide with these.

The list covers Frappe core DocTypes that PMs would commonly name-collide on,
plus the stack_core internals.
"""

from __future__ import annotations

RESERVED_NAMES: frozenset[str] = frozenset(
    {
        "User",
        "Role",
        "DocType",
        "DocField",
        "DocPerm",
        "Workflow",
        "Workflow State",
        "Workflow Action",
        "Custom Field",
        "Property Setter",
        "Server Script",
        "Client Script",
        "Web Form",
        "Report",
        "Print Format",
        "Letter Head",
        "Email Template",
        "Notification",
        "Webhook",
        "Communication",
        "File",
        "Tag",
        "Comment",
        "Address",
        "Contact",
        "Note",
        "Activity Log",
        "Error Log",
        "Scheduled Job Log",
        "Stack Blueprint",
        "Stack Workflow Def",
        "Stack Audit Log",
        "Experiment Assignment",
    }
)


def enforce_reserved_names(name: str) -> None:
    if not name:
        raise ValueError("DocType name is required")
    if name in RESERVED_NAMES:
        raise ValueError(
            f"DocType name {name!r} is reserved. Pick a unique name "
            f"(consider a domain prefix like 'Beneficiary' or 'Grant Application')."
        )
    if name.startswith("Stack "):
        raise ValueError(
            f"DocType name {name!r} uses the reserved 'Stack ' prefix. "
            f"That namespace is reserved for stack_core internals."
        )
