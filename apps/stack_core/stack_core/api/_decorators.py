"""Cross-cutting helpers for stack_core API endpoints.

Every mutating endpoint is decorated with `@audited` so an audit log row is
written regardless of success or failure. Permission checks are explicit at
each endpoint (we don't auto-derive them — that's a footgun).
"""

from __future__ import annotations

import functools
import json
from typing import Any, Callable

import frappe
from frappe.utils import now_datetime


def write_audit_log(
    *,
    action: str,
    blueprint: str | None = None,
    before_json: Any = None,
    after_json: Any = None,
    result: str = "success",
) -> None:
    try:
        frappe.get_doc(
            {
                "doctype": "Stack Audit Log",
                "actor": frappe.session.user or "Guest",
                "action": action,
                "blueprint": blueprint,
                "timestamp": now_datetime(),
                "ip_address": (frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None),
                "user_agent": _safe_user_agent(),
                "result": result,
                "before_json": _serialize(before_json),
                "after_json": _serialize(after_json),
            }
        ).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(message=frappe.get_traceback(), title="stack_core audit log write failed")


def _safe_user_agent() -> str | None:
    req = getattr(frappe.local, "request", None)
    if not req:
        return None
    return (req.headers.get("User-Agent") or "")[:140]


def _serialize(payload: Any) -> str | None:
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload[:65000]
    try:
        return json.dumps(payload, default=str)[:65000]
    except (TypeError, ValueError):
        return str(payload)[:65000]


def audited(action: str) -> Callable:
    """Wrap a whitelisted API endpoint so every call writes an audit row."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            blueprint_hint = kwargs.get("blueprint_name") or kwargs.get("name")
            try:
                result = fn(*args, **kwargs)
                write_audit_log(
                    action=action,
                    blueprint=blueprint_hint,
                    after_json=result,
                    result="success",
                )
                return result
            except frappe.PermissionError:
                write_audit_log(
                    action=action,
                    blueprint=blueprint_hint,
                    after_json={"error": "PermissionError"},
                    result="denied",
                )
                raise
            except Exception as e:
                write_audit_log(
                    action=action,
                    blueprint=blueprint_hint,
                    after_json={"error": type(e).__name__, "message": str(e)[:1000]},
                    result="failure",
                )
                raise

        return wrapper

    return decorator


def boot_session(bootinfo: dict) -> None:
    """Surface a simple flag so the desk knows this site has stack_core."""
    bootinfo["stack_core"] = {
        "version": "0.1.0",
        "is_production": bool(frappe.conf.get("stack_core", {}).get("is_production", 0)),
    }
