"""Export site state to per-blueprint JSON files in the config-repo working tree.

Avoids the issues of `bench export-fixtures` lumping everything together
(see Frappe issue #34915) by writing one file per blueprint, with deterministic
ordering so diffs are minimal.

Layout written:

  <config_repo>/
    fixtures/
      app/
        doctypes/<blueprint_name>.json
        workflows/<workflow_name>.json
        custom_fields.json
        property_setters.json
      site/<sitename>/
        overrides.json
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import frappe


def export_to_working_tree(working_path: str, sitename: str | None = None) -> dict[str, Any]:
    site = sitename or frappe.local.site
    root = Path(working_path)
    if not root.exists():
        raise FileNotFoundError(f"Config repo working path not found: {root}")

    app_dir = root / "fixtures" / "app"
    site_dir = root / "fixtures" / "site" / site

    (app_dir / "doctypes").mkdir(parents=True, exist_ok=True)
    (app_dir / "workflows").mkdir(parents=True, exist_ok=True)
    site_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []

    for bp in _applied_blueprints("DocType"):
        rel = _write_json(app_dir / "doctypes" / f"{_slug(bp['blueprint_name'])}.json", bp)
        written.append(rel)

    for wf in _all_workflows():
        rel = _write_json(app_dir / "workflows" / f"{_slug(wf['workflow_name'])}.json", wf)
        written.append(rel)

    for category, file in (("Custom Field", "custom_fields.json"), ("Property Setter", "property_setters.json")):
        rows = _applied_blueprints(category)
        rel = _write_json(app_dir / file, rows)
        written.append(rel)

    return {"site": site, "files_written": written, "root": str(root)}


def _applied_blueprints(blueprint_type: str) -> list[dict[str, Any]]:
    rows = frappe.get_all(
        "Stack Blueprint",
        filters={"status": "Applied", "blueprint_type": blueprint_type},
        fields=["blueprint_name", "blueprint_type", "version", "payload", "git_commit_sha"],
        order_by="blueprint_name",
    )
    for r in rows:
        if isinstance(r.get("payload"), str):
            try:
                r["payload"] = json.loads(r["payload"])
            except json.JSONDecodeError:
                pass
    return rows


def _all_workflows() -> list[dict[str, Any]]:
    rows = frappe.get_all(
        "Stack Workflow Def",
        fields=[
            "workflow_name", "target_doctype", "is_active",
            "states_json", "transitions_json",
            "experiment_id", "experiment_status",
        ],
        order_by="workflow_name",
    )
    for r in rows:
        for k in ("states_json", "transitions_json"):
            if isinstance(r.get(k), str):
                try:
                    r[k.replace("_json", "")] = json.loads(r.pop(k))
                except json.JSONDecodeError:
                    r[k.replace("_json", "")] = None
    return rows


def _write_json(path: Path, data: Any) -> str:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return os.path.relpath(path, path.parents[2])


def _slug(name: str) -> str:
    return name.strip().replace(" ", "_").replace("/", "_").lower()
