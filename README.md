# frappe-stack

A Claude Code plugin that lets non-developers (PMs, analysts) build Frappe apps correctly — DocTypes, Workflows, Dashboards, Reports, Configs — via guided slash commands, with **two-way GitHub sync** so every site change is mirrored in code, and **best-practice guardrails** baked in at every layer.

> Status: **v0.1.0 scaffold complete** — all 9 phases written + committed. Pending: bench smoke-test, plugin install smoke-test in a clean Claude Code session, `infra/` (deferred per D-09). See [`HEARTBEAT.md`](./HEARTBEAT.md).

## What this is (and is not)

| It is | It is not |
|---|---|
| A Claude Code plugin (marketplace add) | A Frappe app (we ship a small support app `stack_core` *alongside* the plugin) |
| GitOps for Frappe configuration (site ↔ git round-trip) | A drag-and-drop low-code builder (Frappe's Form Builder already exists; we wrap it) |
| Guardrails-first — refuses unsafe configs at the plugin layer | A "trust the user" generator |
| Opinionated — one right way per task | A toolkit you assemble yourself |

## Quick links

**Start here:** [`docs/`](./docs/) — the documentation hub.

| Want to… | Read |
|---|---|
| Understand the surface area | [`docs/skills.md`](./docs/skills.md), [`docs/agents.md`](./docs/agents.md), [`docs/commands.md`](./docs/commands.md), [`docs/hooks.md`](./docs/hooks.md) |
| See the data flow | [`docs/architecture.md`](./docs/architecture.md) |
| Try it as a PM | [`docs/walkthroughs/01-first-doctype.md`](./docs/walkthroughs/01-first-doctype.md) → 02 → 03 → 04 |
| Install on a site | [`docs/operators/installing-stack-core.md`](./docs/operators/installing-stack-core.md) |
| Understand the security model | [`SECURITY.md`](./SECURITY.md) |
| Contribute | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| Pick up a session mid-flight | [`CLAUDE.md`](./CLAUDE.md) → [`HEARTBEAT.md`](./HEARTBEAT.md) → [`PLAN.md`](./PLAN.md) |

## Install

```text
/plugin marketplace add https://github.com/dhwani-ris/frappe-stack.git
/plugin install frappe-stack@frappe-stack
```

Then on each Frappe v15+ site you want to manage:

```bash
bench get-app stack_core /path/to/frappe-stack/apps/stack_core
bench --site <sitename> install-app stack_core
```

Full operator runbook: [`docs/operators/installing-stack-core.md`](./docs/operators/installing-stack-core.md).

## The four-document Builder Protocol

| File | Purpose |
|---|---|
| [`PLAN.md`](./PLAN.md) | Phased implementation plan + decision register |
| [`PRD.md`](./PRD.md) | Product requirements — who, what, why |
| [`SECURITY.md`](./SECURITY.md) | Threat model + non-negotiable guardrails |
| [`CLAUDE.md`](./CLAUDE.md) | Working memory for Claude Code sessions in this repo |
| [`HEARTBEAT.md`](./HEARTBEAT.md) | Current phase / blockers / next checkpoint |
| [`CHANGELOG.md`](./CHANGELOG.md) | What landed when |

## What's in the box

| Layer | Count | Catalog |
|---|---|---|
| Skills | 17 | [`docs/skills.md`](./docs/skills.md) |
| Agents | 8 | [`docs/agents.md`](./docs/agents.md) |
| Slash commands | 9 | [`docs/commands.md`](./docs/commands.md) |
| Safety hooks | 8 | [`docs/hooks.md`](./docs/hooks.md) |
| `stack_core` DocTypes | 4 | [`apps/stack_core/`](./apps/stack_core/) |
| `stack_core` API endpoints | 6 | (see DocType list) |
| Guardrail validators | 5 | [`apps/stack_core/stack_core/guardrails/`](./apps/stack_core/stack_core/guardrails/) |
| Git-bridge modules | 5 | [`apps/stack_core/stack_core/git_bridge/`](./apps/stack_core/stack_core/git_bridge/) |
| PM walkthroughs | 4 | [`docs/walkthroughs/`](./docs/walkthroughs/) |
| Operator runbooks | 2 | [`docs/operators/`](./docs/operators/) |

## License

MIT — see [`LICENSE`](./LICENSE).
