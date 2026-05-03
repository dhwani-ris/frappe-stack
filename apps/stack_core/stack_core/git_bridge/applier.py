"""Apply git config-repo state to the site. Idempotent — safe to re-run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import frappe
from frappe.utils import now_datetime


def apply_from_working_tree(working_path: str) -> dict[str, Any]:
    root = Path(working_path)
    if not root.exists():
        raise FileNotFoundError(f"Config repo working path not found: {root}")

    applied: list[str] = []
    skipped: list[dict[str, str]] = []

    doctypes_dir = root / "fixtures" / "app" / "doctypes"
    if doctypes_dir.exists():
        for f in sorted(doctypes_dir.glob("*.json")):
            try:
                bp = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                skipped.append({"file": str(f), "reason": f"json decode: {e}"})
                continue
            try:
                _upsert_blueprint(bp)
                applied.append(bp["blueprint_name"])
            except Exception as e:
                skipped.append({"file": str(f), "reason": str(e)})

    return {"applied": applied, "skipped": skipped, "applied_at": now_datetime().isoformat()}


def _upsert_blueprint(bp: dict[str, Any]) -> None:
    name = bp["blueprint_name"]
    payload = bp.get("payload")
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    if frappe.db.exists("Stack Blueprint", name):
        doc = frappe.get_doc("Stack Blueprint", name)
        doc.payload = payload
        doc.version = (doc.version or 0) + 1
        doc.status = "Applied"
        doc.git_commit_sha = bp.get("git_commit_sha") or doc.git_commit_sha
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Stack Blueprint",
                "blueprint_name": name,
                "blueprint_type": bp.get("blueprint_type", "DocType"),
                "version": bp.get("version", 1),
                "status": "Applied",
                "payload": payload,
                "git_commit_sha": bp.get("git_commit_sha"),
            }
        )
    doc.applied_at = now_datetime()
    doc.applied_by = frappe.session.user
    doc.save(ignore_permissions=False)


def reconcile_drift() -> None:
    """Daily scheduled hook: log drift if site state diverges from git."""
    config = frappe.conf.get("stack_core", {}) or {}
    if not config.get("config_repo_local_path"):
        return

    from stack_core.api.fixtures import export as export_fixtures
    from stack_core.git_bridge.differ import diff_site_vs_git

    site_state = export_fixtures()
    diff = diff_site_vs_git(site_state)
    summary = diff.get("summary", {})
    if any(summary.get(k, 0) for k in ("only_on_site", "only_in_git", "changed")):
        frappe.log_error(
            title="stack_core: drift detected",
            message=json.dumps(diff, indent=2)[:30000],
        )
