---
description: Bootstrap frappe-stack on a Frappe site. Installs stack_core, configures API key + git config-repo, registers staging and production sites in plugin config.
argument-hint: <site-url> [--prod]
---

# /frappe-stack:init

First command run on a new project. Idempotent — safe to re-run if config got out of sync.

## What it does

1. **Verify Frappe site reachable.** `curl <site>/api/method/ping` returns `pong`.
2. **Confirm version.** Refuse if Frappe < v15.
3. **Install `stack_core`** if not already installed:
   ```bash
   bench --site <site> install-app stack_core
   ```
4. **Generate or import API key** for a dedicated `Stack Author` user.
5. **Configure local plugin state** at `.frappe-stack/config.json`:
   ```json
   {
     "sites": {
       "staging": {
         "url": "...",
         "api_key_secret_ref": "<keychain entry>",
         "is_production": false
       },
       "prod": {
         "url": "...",
         "api_key_secret_ref": "<keychain entry>",
         "is_production": true
       }
     },
     "config_repo": {
       "url": "...",
       "local_path": "...",
       "branch": "main"
     }
   }
   ```
6. **Smoke-test:** call `stack_core.api.fixtures.export` on the site; expect `200 OK` with empty blueprints list.

## Arguments

- `<site-url>` — required. The Frappe site URL, e.g., `https://staging.example.com`.
- `--prod` — flag. Marks this as the production site. Without it, defaults to `staging`.

## Refuses if

- The site is < Frappe v15.
- `stack_core` install fails.
- The API key generation user lacks `System Manager` role.
- Adding a `--prod` site when staging isn't configured yet (force order: staging first, prod second).

## Examples

```text
# First-time setup
/frappe-stack:init https://staging.example.com

# Add prod after staging is happy
/frappe-stack:init https://prod.example.com --prod

# Re-run after rotating the API key
/frappe-stack:init https://staging.example.com
```
