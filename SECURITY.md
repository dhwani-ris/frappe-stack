# SECURITY — frappe-stack

> Threat model and non-negotiable guardrails. Every line below is enforced at one of three layers: **plugin hook** (PreToolUse, blocks at typing), **`stack_core` validator** (blocks at API), or **CI/PR check** (blocks at merge). When all three exist, all three must pass.

## 1. Trust model

| Actor | Trust | Failure mode if compromised |
|---|---|---|
| PM using plugin in Claude Code | Authenticated to staging via API key, **no prod write access** | Bad blueprint on staging — caught at `/fs-promote` review |
| Developer reviewing PR | Trusted to read & approve | Bad merge → caught by CI semgrep + tests |
| `stack_core` admin | Full | Compromise = full takeover. Treat the API key as a production secret. |
| Anonymous internet | Untrusted | Must never reach mutating endpoints (`allow_guest=False` enforced). |

## 2. Non-negotiable guardrails

### 2.1 Blocked patterns (refused at plugin hook + semgrep)

| Pattern | Where | Reason |
|---|---|---|
| `ignore_permissions=True` | any Python in PR | Bypasses entire Frappe permission model |
| `allow_guest=True` on `@frappe.whitelist()` | any Python in PR | Public mutation endpoint without review |
| f-string / `.format()` / `%` in SQL | any Python in PR | SQL injection |
| Hardcoded role string check (`if user.role == "..."`) | any Python in PR | Bypasses Role Permission Manager |
| `frappe.db.sql("DROP …")` / `DELETE FROM` without WHERE | any Python in PR | Mass data loss |
| `bench --site * drop-site` | any shell command suggested by plugin | Site destruction |
| `git push --force` to `main` / `develop` / `release/*` | any shell command suggested by plugin | History rewrite |
| `.env`, credentials, API keys in commit | pre-commit secret scan | Credential leak |
| Direct API call to **production** site from `/fs-build`, `/fs-push` | plugin hook | Prod is git-only |
| Hard delete of govt / audit-tagged DocType row | `stack_core` validator | Compliance — no purge |

### 2.2 Required patterns (refused if absent)

| Requirement | Where checked |
|---|---|
| Every `@frappe.whitelist()` calls `frappe.has_permission()` or `doc.check_permission()` before mutation | semgrep |
| Every blueprint mutation writes a `stack_audit_log` row | `stack_core` API decorator |
| Every PII fieldtype (Aadhaar / PAN / phone / email when tagged sensitive) is encrypted at rest via Fernet | `stack_core` field validator |
| Every workflow state has at least one role assigned | `stack_core` workflow validator |
| Every workflow has at least one terminal state reachable from initial | `stack_core` workflow validator |
| Every DocType creation passes a JSON-Schema validation against the blueprint schema | `stack_core` API |
| Every DocType name is checked against the reserved-name list (Frappe core DocTypes) | `stack_core` API |
| Every fieldtype is in the whitelist; `Code` / `Password` / `Attach` / `Long Text` require elevated role | `stack_core` API |

## 3. Layer enforcement matrix

| Guardrail | Plugin hook (PreToolUse) | stack_core API | CI / PR check |
|---|---|---|---|
| `ignore_permissions=True` | ✓ scan generated code | ✓ refuse if blueprint requests it | ✓ semgrep |
| `allow_guest=True` | ✓ scan generated code | n/a | ✓ semgrep |
| SQL injection patterns | ✓ scan generated code | n/a | ✓ semgrep |
| Direct prod API write | ✓ inspect URL/host | ✓ refuse if site_config marks `is_production=1` | n/a |
| Audit log row written | n/a | ✓ decorator on every mutation API | n/a |
| Workflow has terminal state | n/a | ✓ validator | ✓ test suite |
| PII encrypted | n/a | ✓ field validator | ✓ semgrep custom rule |
| Reserved DocType name | ✓ pre-API check | ✓ validator | n/a |
| `bench drop-site`, `git push --force main` | ✓ blocked at hook | n/a | n/a |
| Secrets in commit | ✓ pre-commit | n/a | ✓ CI secret scan |

## 4. Production hardening checklist (for operators)

Before pointing `/fs-promote` at a real production site:

```
□ site_config.json has developer_mode = 0
□ site_config.json has disable_website_cache = 0
□ site_config.json has session_expiry ≤ 6h
□ site_config.json has rate_limit configured for API endpoints
□ allow_cors restricted to known domains (no "*")
□ HTTPS enforced with valid SSL
□ Two-factor auth required for System Manager + Stack Admin roles
□ Failed-login lockout: 5 attempts
□ stack_core API key stored in secret manager, not site_config plain
□ Backup verified (restore test within last 30 days)
□ stack_audit_log retention policy set (no purge — archive only)
```

## 5. Incident response

If the plugin is suspected of generating insecure code:

1. **Stop pushing.** Hold all pending `/fs-promote` PRs.
2. **Capture evidence** — the Claude Code transcript, the generated blueprint JSON, the audit log row.
3. **Notify** the security owner listed in `CLAUDE.md`.
4. **Rotate** the `stack_core` API key.
5. **Patch the hook / validator** that should have caught it. Add a regression test.
6. **Backfill** — re-run the new check against existing fixtures. Open cleanup PRs for any hits.

## 6. Data classification (mirror of org rules)

| Level | Examples | Plugin behavior |
|---|---|---|
| Public | Marketing copy, docs | Anything goes |
| Internal | Process docs, blueprints | Default — fine |
| Confidential | Real beneficiary names, financials | Refuse to paste into prompts; warn user |
| Restricted | Aadhaar, PAN, credentials | **Hard block** — refuse generation, log incident |

## 7. Out of scope (handled elsewhere)

- Frappe core CVEs — track upstream, patch via `bench update`.
- DDoS / network layer — Cloudflare/WAF, not this repo.
- Endpoint security on PM laptops — IT handles.
- Backup integrity — DevOps owns.
