"""Open a PR on the configured config-repo. Prefers `gh` CLI; falls back to REST API."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

import frappe
import requests


def open_pr(
    config_repo: str,
    head_branch: str,
    base_branch: str,
    title: str,
    body: str,
) -> dict[str, Any]:
    if shutil.which("gh"):
        return _open_via_gh(head_branch, base_branch, title, body)
    return _open_via_rest(config_repo, head_branch, base_branch, title, body)


def _open_via_gh(head: str, base: str, title: str, body: str) -> dict[str, Any]:
    cmd = [
        "gh", "pr", "create",
        "--head", head,
        "--base", base,
        "--title", title,
        "--body", body,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"gh pr create failed: {proc.stderr.strip()}")
    return {"method": "gh", "url": proc.stdout.strip()}


def _open_via_rest(repo_url: str, head: str, base: str, title: str, body: str) -> dict[str, Any]:
    owner, repo = _parse_github_url(repo_url)
    token = _read_token()
    resp = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        data=json.dumps({"title": title, "head": head, "base": base, "body": body}),
        timeout=30,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"GitHub REST PR create failed: {resp.status_code} {resp.text[:200]}")
    return {"method": "rest", "url": resp.json().get("html_url"), "number": resp.json().get("number")}


def _parse_github_url(url: str) -> tuple[str, str]:
    cleaned = url.rstrip("/").removesuffix(".git")
    parts = cleaned.split("/")
    return parts[-2], parts[-1]


def _read_token() -> str:
    config = frappe.conf.get("stack_core", {}) or {}
    secret_key = config.get("github_token_secret_key")
    if not secret_key:
        raise RuntimeError("stack_core.github_token_secret_key not configured in site_config.json")
    token = frappe.conf.get(secret_key)
    if not token:
        raise RuntimeError(f"GitHub token under key {secret_key!r} is empty")
    return token
