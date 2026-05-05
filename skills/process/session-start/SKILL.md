---
name: session-start
description: Use at the start of every AI session that will touch a Dhwani RIS repository. Mandatory pre-flight checks — Security_DRIS.md attached, CLAUDE.md context loaded, DeployControl token ready if pushing. Triggers on phrases like "start a session", "new session", "set up Claude Code for this repo", or any first-message context.
---

# Session-start protocol

The pre-flight that runs before any AI session on a Dhwani RIS repo. Three checks, none optional.

## Check 1 — `Security_DRIS.md` attached

**Mandatory, every session, every AI tool.**

| AI tool | How to attach |
|---|---|
| Claude Code (CLI) | Drag the file into the terminal at session start, or reference its path in your first prompt |
| Claude Chat | Click the attachment icon, upload `Security_DRIS.md` |
| Cursor | Add the file to the workspace; reference it in `.cursorrules` |
| Codex / other IDEs | Upload `Security_DRIS.md` as a file in the first turn |

If the file isn't attached, **stop and attach it before any other work.** The agent should refuse to mutate code without it.

## Check 2 — `CLAUDE.md` context

If the repo already has a `CLAUDE.md`, the agent will read it automatically. If not:

- The agent **creates one** during the session, capturing conventions, current state, and decisions.
- At the end of the session, the agent **updates `CLAUDE.md`** and **opens a PR** with the changes.

The CLAUDE.md is your working memory across sessions — see [`builder-protocol`](../../builder-protocol/SKILL.md) for the full template.

## Check 3 — DeployControl token (only if pushing)

If your session will run `/frappe-stack:promote`, push commits, or open a PR, you need a [DeployControl token](../../../docs/operators/deploy-control-tokens.md):

1. Open DeployControl.
2. **GitHub Token** tab.
3. Confirm the exact repo name with your developer.
4. Generate a 1-hour scoped token.
5. Provide it to the plugin via `/frappe-stack:init` or paste when prompted.

If your session is read-only (browsing code, asking questions, generating local-only configs), skip this check.

## Anti-patterns to refuse

- **Starting without `Security_DRIS.md`.** Stop. Attach. Restart.
- **Using a personal GitHub PAT instead of DeployControl.** Non-developer builders use DeployControl-issued tokens only. Personal PATs are out of scope and out of policy.
- **Skipping the CLAUDE.md update at session end.** The next session will be flying blind. Always update + PR.
- **Sharing a DeployControl token with another team member.** They generate their own. One token, one operator.

## What the agent does at session start

When the engineer agent (or any other plugin agent) initializes:

1. Looks for `Security_DRIS.md` in the conversation context. If not present, surface a top-level reminder and refuse to mutate code.
2. Looks for `CLAUDE.md` at the repo root. If present, loads it. If not, flags that one will be created.
3. Reads `.frappe-stack/config.json` for plugin state (does not load secrets — those stay in the OS keychain).
4. Reports the pre-flight result to the user before any other work.

## Why this exists

`Security_DRIS.md` carries the org-wide AI usage rules and red-lines — what data can/can't be shared, which actions require human review, what to do on incident. **The agent doesn't infer these from training data; it reads them at session start.**

DeployControl tokens close a separate gap: non-developer builders need write access to repos but don't have GitHub accounts on those repos. Issuing 1-hour scoped tokens via DeployControl gives them surgical push capability without expanding GitHub seat costs or bypass risk.

The two together — `Security_DRIS.md` for behavioral rules, DeployControl for repo authorization — are the policy layer non-developer builders operate inside.
