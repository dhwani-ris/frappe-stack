# frappe-stack

A Claude Code plugin for building Frappe v15+ apps without writing code. You type a slash command, the plugin generates the DocType / Workflow / Dashboard / Report, validates it against a fixed list of refusals, and either applies it to a staging site or opens a pull request. Frappe site state and a GitHub config repository stay in sync both directions.

> **Status: v0.1.0 — scaffold only.** All artefacts are written and committed. Nothing has been runtime-tested yet: no clean Claude Code session has installed the plugin, no Frappe bench has installed `stack_core`, no test suite has run. Calling this "ready" would be incorrect. See [`HEARTBEAT.md`](./HEARTBEAT.md) for what's pending.

## What it does

1. **Translates plain-language asks into Frappe configurations.** "I need a beneficiary form" → the plugin walks fields, permissions, validation; calls `stack_core.api.doctype_builder.build`; the DocType appears in Frappe.
2. **Mirrors site changes into git, both directions.** Every change is a `Stack Blueprint` row + a JSON file in the config repository. `/pull` is site → git. `/push` is git → staging. `/promote` is staging → PR → production.
3. **Refuses unsafe inputs at multiple layers.** `ignore_permissions=True`, `allow_guest=True` without review, f-string SQL, hardcoded role checks, real PII in prompts, force-push to `main`, hard-delete on audit-tagged DocTypes.

## What it is not

- **Not a Frappe app.** It ships a small support app `stack_core` that lives alongside, but the plugin itself is markdown + JSON for Claude Code.
- **Not a drag-and-drop builder.** Frappe's Form Builder already exists; this plugin wraps and constrains it.
- **Not opinionated about everything — but opinionated where it matters.** One sync model (B+ hybrid). One naming convention (auto-derived from the manifest `name` field). One promotion path.

## Install

Inside a Claude Code session:

```text
/plugin marketplace add https://github.com/dhwani-ris/frappe-stack.git
/plugin install frappe-stack@frappe-stack
```

On every Frappe v15+ site you want the plugin to manage:

```bash
bench get-app stack_core /path/to/frappe-stack/apps/stack_core
bench --site <sitename> install-app stack_core
```

Full instructions in [`docs/operators/installing-stack-core.md`](./docs/operators/installing-stack-core.md).

## Documentation

The browsable docs site is at https://dhwani-ris.github.io/frappe-stack/ (deploys automatically from `main`).

In the repo:

| You want | Read |
|---|---|
| The first walkthrough | [`docs/walkthroughs/01-first-doctype.md`](./docs/walkthroughs/01-first-doctype.md) |
| The data flow | [`docs/architecture.md`](./docs/architecture.md) |
| The full surface area (skills / agents / commands / hooks) | [`docs/skills.md`](./docs/skills.md), [`docs/agents.md`](./docs/agents.md), [`docs/commands.md`](./docs/commands.md), [`docs/hooks.md`](./docs/hooks.md) |
| To install on a site | [`docs/operators/installing-stack-core.md`](./docs/operators/installing-stack-core.md) |
| The threat model | [`SECURITY.md`](./SECURITY.md) |
| To contribute | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| To pick up a session mid-flight | [`CLAUDE.md`](./CLAUDE.md) → [`HEARTBEAT.md`](./HEARTBEAT.md) → [`PLAN.md`](./PLAN.md) |

## Working-memory files

Four files at the repo root capture state across sessions, plus PLAN.md:

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
| `stack_core` DocTypes | 4 | [`apps/stack_core/stack_core/doctype/`](./apps/stack_core/stack_core/doctype/) |
| `stack_core` API endpoints | 6 | [`apps/stack_core/stack_core/api/`](./apps/stack_core/stack_core/api/) |
| Guardrail validators | 5 | [`apps/stack_core/stack_core/guardrails/`](./apps/stack_core/stack_core/guardrails/) |
| Git-bridge modules | 5 | [`apps/stack_core/stack_core/git_bridge/`](./apps/stack_core/stack_core/git_bridge/) |
| Tutorials | 4 | [`docs/walkthroughs/`](./docs/walkthroughs/) |
| Operator runbooks | 2 | [`docs/operators/`](./docs/operators/) |

## License

MIT — see [`LICENSE`](./LICENSE).
