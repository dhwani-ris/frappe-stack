"""Fieldtype whitelist for Stack Blueprint DocType payloads.

Common types are open to all roles. Sensitive types (Code, Password, Attach,
Long Text with `is_pii=1`) require Stack Admin or System Manager. Stack Author
(the PM tier) cannot ship those without an admin approving the blueprint.
"""

from __future__ import annotations

import frappe

SAFE_FIELDTYPES: frozenset[str] = frozenset(
    {
        "Data",
        "Int",
        "Float",
        "Currency",
        "Check",
        "Select",
        "Date",
        "Datetime",
        "Time",
        "Text",
        "Small Text",
        "Text Editor",
        "Link",
        "Dynamic Link",
        "Table",
        "Section Break",
        "Column Break",
        "Tab Break",
        "HTML",
        "JSON",
        "Markdown Editor",
        "Read Only",
        "Percent",
        "Rating",
        "Color",
        "Duration",
        "Geolocation",
    }
)

ELEVATED_FIELDTYPES: frozenset[str] = frozenset(
    {
        "Code",
        "Password",
        "Attach",
        "Attach Image",
        "Signature",
        "Long Text",
    }
)

ELEVATED_ROLES: frozenset[str] = frozenset({"System Manager", "Stack Admin"})


def enforce_fieldtype_whitelist(fields: list[dict]) -> None:
    user_roles = set(frappe.get_roles(frappe.session.user)) if frappe.session.user else set()
    can_use_elevated = bool(ELEVATED_ROLES & user_roles)

    for field in fields:
        ftype = field.get("fieldtype")
        if not ftype:
            raise ValueError(f"Field {field.get('fieldname')!r} missing fieldtype")
        if ftype in SAFE_FIELDTYPES:
            continue
        if ftype in ELEVATED_FIELDTYPES:
            if not can_use_elevated:
                raise PermissionError(
                    f"Fieldtype {ftype!r} on field {field.get('fieldname')!r} requires "
                    f"one of {sorted(ELEVATED_ROLES)}; current roles: {sorted(user_roles)}"
                )
            continue
        raise ValueError(
            f"Fieldtype {ftype!r} is not on the whitelist. "
            f"Safe: {sorted(SAFE_FIELDTYPES)}; Elevated: {sorted(ELEVATED_FIELDTYPES)}"
        )
