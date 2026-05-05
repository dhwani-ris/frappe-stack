---
name: claude-md-template
description: Use at session-start when a repository does not yet have a CLAUDE.md. Generates the working-memory file from a known-good template and stages it for the end-of-session PR. Triggers on phrases like "CLAUDE.md missing", "create CLAUDE.md", "this repo has no agent context".
---

# CLAUDE.md template

The session-start protocol requires every Dhwani RIS repo to have a `CLAUDE.md` at the root. This skill generates one when missing.

## When to fire

Automatically — the session-start protocol fires this skill when `CLAUDE.md` is absent at session-load time. The PM doesn't need to invoke it directly.

## What gets generated

A new `CLAUDE.md` at the repo root, populated from this template:

````markdown
# CLAUDE.md — <repo name>

> Working memory for Claude Code sessions in this repo. Read first, every session.

## What this repo is

<one paragraph the agent fills in from the README + the first-session conversation>

## Pair this file with

- `Security_DRIS.md` — org-wide AI usage rules. Mandatory attachment to every session.
- `PRD.md` (if present) — what we're building and why.
- `PLAN.md` (if present) — phased plan and decision register.
- `SECURITY.md` (if present) — repo-specific guardrails.
- `HEARTBEAT.md` (if present) — current phase, blockers, next checkpoint.

## Rules — order of precedence

When rules conflict, lower number wins:

1. `Security_DRIS.md` — org-wide rules. Strictest.
2. `SECURITY.md` in this repo — repo-specific guardrails.
3. `~/.claude/rules/<framework>/` — language-specific global rules.
4. `~/.claude/rules/common/` — universal global rules.
5. This `CLAUDE.md` — repo-local working notes.
6. `PLAN.md` (if present) — phase order; do not skip.

## Working notes

### Repo conventions

- Branch model: <fill in — e.g., feature branches off `main`, PR required>.
- Commit style: <fill in — typically conventional commits>.
- Test command: <fill in — e.g., `bench --site test_site run-tests --app <app>`>.
- Local dev setup: <fill in — link to README install section>.

### Authentication for git push

- Non-developer builders: use a DeployControl-issued token (1 hour, repo-scoped) — see [DeployControl runbook](https://github.com/dhwani-ris/frappe-stack/blob/main/docs/operators/deploy-control-tokens.md).
- The plugin handles this via `/frappe-stack:init`.
- Personal GitHub PATs are not used.

### Agents to invoke (from `~/.claude/agents/`)

| Task | Agent |
|---|---|
| Frappe code review | `frappe-reviewer` |
| Security review | `security-reviewer` |
| Plan a feature | `planner` |
| Test-first new code | `tdd-guide` |
| Final code review | `code-reviewer` |
| Schema changes | `database-reviewer` |

### When generating Frappe code

Always check the global rules `~/.claude/rules/frappe/` first. Non-negotiables:

- ❌ Never `ignore_permissions=True`
- ❌ Never `allow_guest=True` without explicit security review
- ❌ Never f-string / `.format()` / `%` SQL
- ❌ Never hardcoded role string checks
- ✓ Every `@frappe.whitelist()` calls `frappe.has_permission()` first
- ✓ Every test extends `frappe.tests.utils.FrappeTestCase`

## Owners (placeholder — fill in when team confirmed)

- Product: TBD
- Eng lead: TBD
- Security: TBD

Update via PR, not directly.

## Session log

The session-start protocol auto-stamps this section at the end of each session.

<!-- session log entries appended below this marker -->
````

## End-of-session PR

When the session ends, the agent:

1. Updates the **Session log** section with a one-paragraph summary of what changed.
2. Opens a PR with the new/updated `CLAUDE.md` against `main`, branch named `chore/update-claude-md-<YYYYMMDD-HHMM>`.
3. Tags the rotation reviewer if configured.

## Anti-patterns

- **Generating CLAUDE.md without filling in repo-specific bits** (test command, branch model, owners). The template marks these with `<fill in>` — leave those visible if the PM doesn't know yet, rather than guessing.
- **Embedding secrets in CLAUDE.md.** It's a tracked file. API keys, tokens, even site URLs should be in `.frappe-stack/config.json` or the OS keychain.
- **Committing CLAUDE.md with the working tree dirty.** The end-of-session PR should contain only the CLAUDE.md change.
- **Skipping the Session log update.** That's the breadcrumb for the next session.

## Pairs with

- [`session-start`](../../process/session-start/SKILL.md) — the protocol that triggers this skill when CLAUDE.md is absent.
- [`builder-protocol`](../../builder-protocol/SKILL.md) — the broader four-document working memory model this CLAUDE.md slots into.
