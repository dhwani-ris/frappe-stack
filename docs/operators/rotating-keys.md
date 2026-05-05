# Operator runbook — rotating keys

**Audience:** anyone managing the credentials the plugin uses.
**Frequency:** every 90 days minimum, plus immediately after any suspected leak.

## What needs rotating

| Credential | Where it's stored | Rotation impact |
|---|---|---|
| Frappe API Key + Secret | OS keychain on the PM's machine, referenced from `.frappe-stack/config.json` | All PMs need to re-init |
| GitHub token (for `/frappe-stack:promote` PRs) | OS keychain on the PM's machine, or `gh auth login` if using `gh` CLI | None visible to others; deployer picks up the new token next call |
| Frappe Administrator password | Frappe core | Every Administrator needs a new password |
| SSH keys (if your CI deploys via SSH) | DevOps key store | Per-DevOps |

## Rotating the Frappe API key

```bash
# 1. On your Frappe Desk, regenerate the keys:
#    User > the API user > API Access > Regenerate Keys
#
# The OLD key/secret stops working immediately. The plugin will see 401
# until step 2.
```

Then on each PM's machine:

```text
# 2. In Claude Code:
/frappe-stack:init https://your-staging-site.example.com
```

The init flow re-prompts for the new API key + secret and updates the OS-keychain entry referenced in `.frappe-stack/config.json`. PM smoke-tests by running `/frappe-stack:diff`.

**Recovery if rotation goes wrong:** the old key is gone — there's no rollback. Fix forward by re-running init.

## Rotating the GitHub token

If using `gh` CLI:

```bash
gh auth refresh
# or
gh auth login
```

If using a fine-grained PAT directly:

```bash
# 1. Generate a new fine-grained Personal Access Token on GitHub.
#    Required scopes: repo (read+write) on the config-repo only.
# 2. Update your .frappe-stack/config.json (or OS keychain entry)
#    so the plugin picks up the new token on next /promote.
# 3. Verify next /frappe-stack:promote works.
# 4. Revoke the OLD token on GitHub (Developer settings > PATs).
```

## Rotating the Frappe Administrator password

```bash
bench --site <site> set-admin-password
```

Notify all admins. Their session cookies are unaffected; only fresh logins use the new password.

## After any leak — incident protocol

1. **Stop deployments.** Hold all pending `/frappe-stack:promote` PRs.
2. **Rotate all keys** (above order).
3. **Audit:** check Frappe's built-in Activity Log for the time window the leaked key was active. Surface every change made by that user.
4. **Audit locally:** check `.frappe-stack/audit.jsonl` on the PM's machine for what the plugin issued.
5. **Revert if needed:** if any audit entry corresponds to an unauthorized blueprint change, revert the corresponding commit in your config repo and re-run `bench migrate`.
6. **Patch** the leak source (if pre-commit hook missed it, add the regex; if a PM laptop was compromised, IT handles).
7. **Document** the incident in a postmortem doc inside the config-repo.
