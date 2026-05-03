# Operator runbook — installing stack_core

**Audience:** DevOps installing the `stack_core` Frappe app on a site.
**Prerequisites:** `bench` with Frappe v15+.

## 1. Install on staging first

```bash
cd /path/to/frappe-bench
bench get-app stack_core /path/to/frappe-stack/apps/stack_core
bench --site <staging-site> install-app stack_core
bench --site <staging-site> migrate
```

After install, verify:

```bash
bench --site <staging-site> console
>>> import frappe
>>> frappe.db.exists("DocType", "Stack Blueprint")
'Stack Blueprint'
>>> frappe.db.exists("DocType", "Stack Audit Log")
'Stack Audit Log'
```

## 2. Configure site_config.json

```json
{
  "stack_core": {
    "is_production": 0,
    "config_repo": "https://github.com/<org>/<config-repo>.git",
    "config_repo_branch": "main",
    "config_repo_local_path": "/var/lib/frappe-stack/config-repo",
    "github_token_secret_key": "stack_core_github_token"
  },
  "stack_core_github_token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Notes:
- `is_production: 0` for staging. Set to `1` only on prod.
- `config_repo_local_path` must be a writable directory the bench user owns. The committer.py reads/writes here.
- `github_token_secret_key` is **the key** under which the actual token is stored — keep the indirection so the token can be rotated without code changes.

## 3. Create the Stack Author user + token

```bash
bench --site <staging-site> add-user --first-name Stack --last-name Author --email stack-author@<your-domain>
bench --site <staging-site> add-role stack-author@<your-domain> "Stack Author"
```

Then on the Frappe desk:

1. Open the Stack Author user.
2. Click **API Access** → **Generate Keys**.
3. Copy the API Key and API Secret.
4. Store both in your secret manager (e.g., `pass`, AWS Secrets Manager, Vault).

## 4. Roles to create

`stack_core` ships with three role names. Create them on the site if they don't exist:

```bash
bench --site <staging-site> console
>>> import frappe
>>> for role in ["Stack Author", "Stack Admin"]:
...     if not frappe.db.exists("Role", role):
...         frappe.get_doc({"doctype": "Role", "role_name": role}).insert()
... 
>>> frappe.db.commit()
```

Then assign:
- **Stack Author** to the user the plugin uses (least privilege; can build, can read audit log limited to own actions).
- **Stack Admin** to humans who review promotions and approve elevated fieldtypes.
- **System Manager** stays as Frappe ships it.

## 5. Production setup (different from staging)

When installing on prod:

1. Same install commands.
2. Set `is_production: 1` in site_config.
3. **Do not configure** the Stack Author API key on prod — the plugin should never have a prod token. Production mutations come only from `bench migrate`.
4. Restrict shell access to prod by SSH key + 2FA.
5. Set up the CI/CD pipeline to run `bench migrate` on PR merge. The pipeline needs:
   - Read-only access to the config-repo.
   - Bench user with permission to run `bench migrate` on prod.
   - Backup verification step that runs *before* migrate.

## 6. Backup verification

`SECURITY.md §4` requires a backup verified within last 30 days. Add a monthly cron:

```cron
# Verify prod backup integrity on the 1st of every month
0 3 1 * * /usr/local/bin/verify-frappe-backup.sh prod
```

Where `verify-frappe-backup.sh`:

1. Pulls the latest backup.
2. Restores into a throwaway site.
3. Runs `bench --site throwaway run-tests --app stack_core`.
4. Reports green/red to the operator.

## 7. Smoke test

```bash
curl -X GET "https://staging.example.com/api/method/ping"
# expect: {"message":"pong"}

curl -X GET "https://staging.example.com/api/method/stack_core.api.fixtures.export" \
     -H "Authorization: token <api-key>:<api-secret>"
# expect: 200 OK with empty blueprints list
```

If both succeed, hand off to the PM team for `/frappe-stack:init`.
