"""Structured diff: site state vs the configured git config-repo HEAD."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import frappe


def diff_site_vs_git(site_state: dict[str, Any]) -> dict[str, Any]:
    config = frappe.conf.get("stack_core", {}) or {}
    working = config.get("config_repo_local_path")
    if not working:
        return {
            "ok": False,
            "reason": "stack_core.config_repo_local_path not configured",
        }

    git_state = _read_git_state(Path(working), frappe.local.site)

    only_on_site, only_in_git, changed = _diff(site_state, git_state)

    return {
        "ok": True,
        "site": frappe.local.site,
        "git_root": str(working),
        "summary": {
            "only_on_site": len(only_on_site),
            "only_in_git": len(only_in_git),
            "changed": len(changed),
        },
        "only_on_site": only_on_site,
        "only_in_git": only_in_git,
        "changed": changed,
    }


def _read_git_state(working: Path, sitename: str) -> dict[str, Any]:
    blueprints: list[dict] = []
    workflows: list[dict] = []

    doctypes_dir = working / "fixtures" / "app" / "doctypes"
    workflows_dir = working / "fixtures" / "app" / "workflows"

    if doctypes_dir.exists():
        for f in sorted(doctypes_dir.glob("*.json")):
            try:
                blueprints.append(json.loads(f.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue

    if workflows_dir.exists():
        for f in sorted(workflows_dir.glob("*.json")):
            try:
                workflows.append(json.loads(f.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue

    return {"site": sitename, "blueprints": blueprints, "workflows": workflows}


def _diff(site: dict, git: dict) -> tuple[list, list, list]:
    site_bp = {b["blueprint_name"]: b for b in site.get("blueprints", [])}
    git_bp = {b["blueprint_name"]: b for b in git.get("blueprints", [])}

    only_site = [n for n in site_bp if n not in git_bp]
    only_git = [n for n in git_bp if n not in site_bp]
    changed = [n for n in site_bp if n in git_bp and site_bp[n].get("payload") != git_bp[n].get("payload")]
    return only_site, only_git, changed
