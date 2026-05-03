# Operator runbook — rotating keys

**Audience:** DevOps rotating credentials.
**Frequency:** Every 90 days minimum, plus immediately after any suspected leak.

## What needs rotating

| Credential | Where it's stored | Rotation impact |
|---|---|---|
| Stack Author API Key + Secret (staging) | Operator's secret manager + `.frappe-stack/config.json` (per PM laptop) | All PMs need to re-init |
| GitHub token (for config-repo PR creation) | `site_config.json` under `stack_core_github_token` (key indirected) | None visible to PMs; deployer picks up next call |
| Frappe site Administrator password | Frappe core | Every Administrator needs new password |
| Database root password | site_config.json | None visible to users |
| SSH keys (DevOps to bench host) | DevOps key store | Per-DevOps |

## Rotating the Stack Author API key

```bash
# 1. On staging Frappe desk, regenerate the API key:
#    User > Stack Author > API Access > Regenerate Keys
# 2. The OLD key is invalidated immediately. Calls fail.
```

Then:

```bash
# 3. Store new key in your secret manager.
# 4. Notify PMs: each runs /frappe-stack:init <staging-url>
#    - The init command re-reads from the secret manager
#    - Updates the local .frappe-stack/config.json reference
# 5. PM smoke-tests by running /frappe-stack:diff
```

**Recovery if rotation goes wrong**: the old key is gone — there's no rollback. Fix forward by re-running init.

## Rotating the GitHub token

```bash
# 1. Generate a new fine-grained Personal Access Token on GitHub.
#    Required scopes: repo (read+write) on the config-repo only.
# 2. Update site_config.json on each Frappe site:

bench --site <site> set-config stack_core_github_token "ghp_new..."

# 3. Verify next /frappe-stack:promote works.
# 4. Revoke the OLD token on GitHub (via GitHub > Developer settings > PATs).
```

Why indirect through `github_token_secret_key`: changing the key in code requires a code review + deploy. With indirection, the rotation is a config change only.

## Rotating the Frappe Administrator password

```bash
bench --site <site> set-admin-password
```

Notify all admins. Their session cookies are unaffected; only fresh logins use the new password.

## Rotating the database root password

```bash
# 1. Connect to the DB as root, change password.
# 2. Update site_config.json:
bench --site <site> set-config db_password "<new>"
# 3. Restart bench:
bench restart
```

Test:

```bash
bench --site <site> console
>>> import frappe
>>> frappe.db.sql("SELECT 1")
```

## After any leak — incident protocol

1. **Stop deployments.** Hold all pending `/frappe-stack:promote` PRs.
2. **Rotate all keys** (above order).
3. **Audit:** query `Stack Audit Log` for the actor whose key leaked, in the relevant time window. Surface every action they took.
4. **Revert if needed:** if any audit-log row corresponds to an unauthorized blueprint change, roll back via `/frappe-stack:rollback --to <git-sha>`.
5. **Patch** the leak source (if pre-commit hook missed it, add the regex; if a PM laptop was compromised, IT handles).
6. **Document** the incident in a postmortem doc inside the config-repo.
