# Operator runbook — rotating keys

**Audience:** anyone managing the credentials the plugin uses.
**Frequency:** Frappe API keys every 90 days minimum, immediately after any suspected leak. DeployControl tokens auto-expire every 1 hour.

## What needs rotating

| Credential | Where it's stored | Rotation cadence | Rotation impact |
|---|---|---|---|
| **DeployControl GitHub token** | OS keychain on the PM's machine, ref'd from `.frappe-stack/config.json` | **Auto-expires every 1 hour** — generate fresh per session via DeployControl | Re-run `/frappe-stack:init` mid-session if you cross the hour |
| Frappe API Key + Secret | OS keychain on the PM's machine, ref'd from `.frappe-stack/config.json` | Every 90 days, or after any suspected leak | All PMs need to re-init |
| Frappe Administrator password | Frappe core | Per-user IT policy | Every Administrator needs a new password |
| SSH keys (if your CI deploys via SSH) | DevOps key store | Per-DevOps policy | Per-DevOps |

> **Why the GitHub token is different:** non-developer builders authenticate to `dhwani-ris/*` repos via DeployControl, which issues 1-hour scoped tokens under the `dhwani-jenkins` service account. They are not personal PATs; they are not long-lived. Rotation is not a periodic event — it's a per-session generation step. See [DeployControl runbook](./deploy-control-tokens.md).

## Rotating the DeployControl token

This isn't really "rotation" — it's "generate a fresh one when the previous expires."

```text
# 1. Open DeployControl, GitHub Token tab.
# 2. Confirm exact repo name with your developer.
# 3. Click Generate Scoped Token. Copy.
# 4. In Claude Code:
/frappe-stack:init https://your-staging-site.example.com
# Paste the new token when prompted.
```

The plugin updates the OS keychain entry that `.frappe-stack/config.json` references. PM smoke-tests by running `/frappe-stack:diff`.

The OLD token is auto-revoked by DeployControl when its 1 hour ends, so there's no "revoke" step. If you want to invalidate it sooner (suspected leak), DevOps can revoke it via DeployControl's admin tab.

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

## Rotating the Frappe Administrator password

```bash
bench --site <site> set-admin-password
```

Notify all admins. Their session cookies are unaffected; only fresh logins use the new password.

## After any leak — incident protocol

1. **Stop deployments.** Hold all pending `/frappe-stack:promote` PRs.
2. **DeployControl token leak:** the token expires within the hour regardless. DevOps can revoke it sooner via DeployControl's admin tab. Audit any `dhwani-jenkins`-authored commits in the leak window and revert anything unauthorized.
3. **Frappe API key leak:** rotate immediately (above). Audit Frappe's built-in Activity Log for the time window the leaked key was active. Surface every change made by that user.
4. **Audit locally:** check `.frappe-stack/audit.jsonl` on the affected PM's machine for what the plugin issued.
5. **Revert if needed:** if any audit entry corresponds to an unauthorized blueprint change, revert the corresponding commit in your config repo and re-run `bench migrate`.
6. **Patch** the leak source (if a hook missed it, add the regex; if a PM laptop was compromised, IT handles).
7. **Document** the incident in a postmortem doc inside the config-repo.
