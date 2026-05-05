# frappe-stack

A Claude Code plugin for building Frappe v15+ apps without writing code. You type a slash command, the plugin generates the DocType / Workflow / Dashboard / Report, validates it, and either applies it to your staging Frappe site (via Frappe's stock REST API) or opens a pull request against your config repository.

> **Status: v0.1.0 — scaffold complete.** The plugin's skills, agents, slash commands, and safety hooks are all in place. Runtime smoke-tests against a real Frappe site are pending. See [`HEARTBEAT.md`](./HEARTBEAT.md) for the live state.

## What it does

1. **Plain-language asks become Frappe configurations.** "I need a beneficiary form" → the plugin walks fields, permissions, validation; calls Frappe's stock REST API; the DocType appears on your site.
2. **Site changes mirror to git, both directions.** Each blueprint becomes a JSON file in your config repository. `/pull` is site → git, `/push` is git → staging, `/promote` opens a pull request from staging to production.
3. **Unsafe inputs refused at multiple layers.** Real PII in prompts, `ignore_permissions=True`, `allow_guest=True` without review, f-string SQL, hardcoded role checks, force-push to `main`. Each rejection happens at the layer closest to the user — typing-time hooks for prompts, edit-time hooks for code.

## What it is not

- **Not a Frappe app.** It's a Claude Code plugin. There's nothing to install on the Frappe site beyond what Frappe v15+ already ships. The plugin authenticates with a token and uses stock REST endpoints (`/api/resource/DocType`, `/api/resource/Workflow`, etc.).
- **Not a drag-and-drop builder.** Frappe's Form Builder already exists — this plugin generates valid configs and applies them.
- **Not a managed service.** It runs inside your Claude Code session. Your data stays on your Frappe site and your GitHub repository.

## Install

Inside a Claude Code session, run two commands:

```text
/plugin marketplace add https://github.com/dhwani-ris/frappe-stack.git
/plugin install frappe-stack@frappe-stack
```

Then point the plugin at your Frappe site:

```text
/frappe-stack:init https://your-staging-site.example.com
```

The `init` command will prompt for an API key + secret (generate them via Frappe Desk → User → API Access) and a path to a local checkout of your config repository.

## Documentation

The browsable docs site is at https://dhwani-ris.github.io/frappe-stack/ (deploys automatically from `main`).

In the repo:

| You want | Read |
|---|---|
| The first walkthrough | [`docs/walkthroughs/01-first-doctype.md`](./docs/walkthroughs/01-first-doctype.md) |
| The data flow | [`docs/architecture.md`](./docs/architecture.md) |
| Skills / agents / commands / hooks reference | [`docs/skills.md`](./docs/skills.md), [`docs/agents.md`](./docs/agents.md), [`docs/commands.md`](./docs/commands.md), [`docs/hooks.md`](./docs/hooks.md) |
| Token rotation runbook | [`docs/operators/rotating-keys.md`](./docs/operators/rotating-keys.md) |
| The threat model | [`SECURITY.md`](./SECURITY.md) |
| To contribute | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| To pick up a session mid-flight | [`CLAUDE.md`](./CLAUDE.md) → [`HEARTBEAT.md`](./HEARTBEAT.md) → [`PLAN.md`](./PLAN.md) |

## Working-memory files

Six files at the repo root capture state across sessions:

| File | What it owns |
|---|---|
| [`PRD.md`](./PRD.md) | What we're building and why. The *what*. |
| [`PLAN.md`](./PLAN.md) | Phased plan + decision register. The *how*. |
| [`SECURITY.md`](./SECURITY.md) | Threat model + non-negotiable refusals. The *must-not*. |
| [`CLAUDE.md`](./CLAUDE.md) | Working memory for Claude Code sessions in this repo. |
| [`HEARTBEAT.md`](./HEARTBEAT.md) | Newest entry on top; current phase, blockers, next checkpoint. |
| [`CHANGELOG.md`](./CHANGELOG.md) | What landed when. |

## Inventory

| Layer | Count | Where |
|---|---|---|
| Skills | 17 | [`skills/`](./skills/) — see [`docs/skills.md`](./docs/skills.md) |
| Agents | 8 | [`agents/`](./agents/) — see [`docs/agents.md`](./docs/agents.md) |
| Slash commands | 9 | [`commands/`](./commands/) — see [`docs/commands.md`](./docs/commands.md) |
| Safety hooks | 8 | [`hooks/`](./hooks/) + [`.claude-plugin/hook_scripts/`](./.claude-plugin/hook_scripts/) — see [`docs/hooks.md`](./docs/hooks.md) |
| Tutorials | 4 | [`docs/walkthroughs/`](./docs/walkthroughs/) |
| Operator runbook | 1 | [`docs/operators/rotating-keys.md`](./docs/operators/rotating-keys.md) |

## License

MIT — see [`LICENSE`](./LICENSE).
