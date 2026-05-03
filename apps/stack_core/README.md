# stack_core

Frappe support app for the [`frappe-stack`](../../) Claude Code plugin. Installed onto every Frappe site (staging and production) that the plugin manages.

## What it provides

| Surface | Purpose |
|---|---|
| **API endpoints** (`api/`) | The interface the plugin calls — `build_doctype`, `build_workflow`, `build_config`, `export_fixtures`, `diff_against_git` |
| **DocTypes** (`stack_core/doctype/`) | `Stack Blueprint` (versioned config), `Stack Workflow Def` (workflow + experiments), `Experiment Assignment` (A/B tracking), `Stack Audit Log` (append-only mutation log) |
| **Guardrails** (`stack_core/guardrails/`) | JSON-Schema validator, fieldtype whitelist, reserved-name check, workflow validator, permission enforcer |
| **Git bridge** (`stack_core/git_bridge/`) | Site ↔ GitHub two-way sync engine — exporter, committer, PR opener, differ, applier |

## Install

Inside a Frappe v15+ bench:

```bash
bench get-app stack_core /path/to/frappe-stack/apps/stack_core
bench --site <sitename> install-app stack_core
```

## Configure

After install, set in `site_config.json`:

```json
{
  "stack_core": {
    "is_production": 0,
    "config_repo": "https://github.com/<org>/<config-repo>.git",
    "config_repo_branch": "main",
    "config_repo_local_path": "/path/to/working/checkout",
    "github_token_secret_key": "stack_core_github_token"
  }
}
```

`is_production: 1` enables the prod-only guards (refuses direct API writes; only `bench migrate` may mutate).

## Test

```bash
bench --site test_site run-tests --app stack_core --coverage
```

Coverage target: ≥ 80% (per `~/.claude/rules/frappe/frappe-testing.md`).

## Security

See [`../../SECURITY.md`](../../SECURITY.md). The non-negotiables (every PR must satisfy):

- Every `@frappe.whitelist()` calls `frappe.has_permission()` first.
- No `ignore_permissions=True`. No `allow_guest=True`. No f-string SQL.
- Every mutation API call writes a `Stack Audit Log` row.
- PII fields (Aadhaar / PAN / phone) Fernet-encrypted at rest.
- Hard delete blocked at framework level — soft-delete via status flag.
