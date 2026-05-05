# DeployControl — short-lived GitHub tokens

**Audience:** non-developer builders (PMs, analysts) using the plugin to push code to a `dhwani-ris/<repo>` repository through an AI tool.

**What it is:** DeployControl (the platform.2010 GitHub Token Generator) mints short-lived, repo-scoped GitHub tokens for AI tools. You don't need a personal GitHub account or push access on the repo — DeployControl issues a 1-hour token under the `dhwani-jenkins` service account.

This is the **only supported way** for non-developer builders to authenticate `/frappe-stack:promote` and any direct `git push` from AI sessions on Dhwani RIS repositories.

## Before you start

You need:

- DeployControl login credentials.
- The exact repository name (without the `dhwani-ris/` prefix). **No validation on the field — wrong name = token generated but won't work.** Confirm with your developer.
- An AI tool ready (Claude Code, Cursor, Codex, or similar).
- The `Security_DRIS.md` file. Attach it to every AI session — see [the session-start protocol](../../skills/process/session-start/SKILL.md).

## Generate a token

1. Log in to DeployControl.
2. Click the **GitHub Token** tab. The repo input field has `dhwani-ris/` pre-filled.
3. Type the exact repo name (no org prefix).
4. Click **Generate Scoped Token**.
5. You'll see "Token Ready" — copy the token and the quick-use git commands.

## Token details

| Field | Value |
|---|---|
| Lifetime | 1 hour |
| Scope | per-repo only (the one repo you typed) |
| Permissions | read + write |
| Service account | `dhwani-jenkins` |
| Git username | `x-access-token` |

## Quick-use git commands (copy from DeployControl)

```bash
# Clone (first-time setup of the local working tree)
git clone https://x-access-token:<TOKEN>@github.com/dhwani-ris/<repo>

# Re-point an existing local clone at the token-authenticated URL
git remote set-url origin https://x-access-token:<TOKEN>@github.com/dhwani-ris/<repo>

# Set your commit identity (required — token alone doesn't author commits)
git config user.name "dhwani-jenkins"
```

## Using the token with the plugin

Once you've cloned the config repo locally with the token URL, run:

```text
/frappe-stack:init https://your-staging-site.example.com
```

When the plugin prompts for the GitHub token, paste the DeployControl token. It's stored in your OS keychain (macOS Keychain / Windows Credential Manager / `pass` / etc.) and referenced from `.frappe-stack/config.json` — never written to a plain config file.

The plugin uses this token automatically when `/frappe-stack:promote` opens a PR.

## When the hour runs out

Tokens are 1-hour. If the token expires mid-session (e.g., during a long `/frappe-stack:promote` flow):

1. Open DeployControl.
2. Generate a fresh token for the same repo.
3. Run `/frappe-stack:init` again with the new token. Or update the keychain entry directly.
4. Resume.

The plugin surfaces the expiry via a clear `401 Unauthorized` error from `git push` or `gh pr create` — no silent failures.

## Anti-patterns to refuse

- **Using a personal GitHub PAT.** Don't. Non-developer builders use DeployControl tokens only. Personal PATs leak attribution + scope.
- **Pasting the token into a plain config file or chat.** It belongs in the OS keychain. The plugin handles this for you when you run `/frappe-stack:init`.
- **Reusing a token across repos.** DeployControl tokens are per-repo by design. If you need to push to two repos, generate two tokens.
- **Sharing tokens between team members.** Each PM generates their own. Audit trails depend on it.
- **Skipping `Security_DRIS.md`.** Mandatory attachment to every AI session, every time. See [session-start](../../skills/process/session-start/SKILL.md).

## Incident — leaked token

DeployControl tokens are short-lived (1 hour), so the blast radius is small. Still:

1. **Stop the session immediately.**
2. Notify your team lead and DevOps.
3. The token expires within the hour regardless. DeployControl logs every issuance — DevOps can confirm whether the leaked token was used.
4. Audit the repo for any commits authored by `dhwani-jenkins` during the window the token was active. Revert anything you didn't authorize.
5. Generate a fresh token and continue.
