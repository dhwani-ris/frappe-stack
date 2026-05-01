# frappe-stack

A Claude Code plugin that lets non-developers (PMs, analysts) build Frappe apps correctly — DocTypes, Workflows, Dashboards, Reports, Configs — via guided slash commands, with **two-way GitHub sync** so every site change is mirrored in code, and **best-practice guardrails** baked in at every layer.

> Status: **Phase 0 — Planning.** This commit ships the alignment docs only. No skills, agents, or commands yet. See [`PLAN.md`](./PLAN.md).

## What this is (and is not)

| It is | It is not |
|---|---|
| A Claude Code plugin (marketplace add) | A Frappe app (we ship a small support app `stack_core` *alongside* the plugin) |
| Modeled on the [`prody-dris/mgrant-stack`](https://github.com/prody-dris/mgrant-stack) pattern (private) | A Frappe core fork |
| GitOps for Frappe configuration (site ↔ git round-trip) | A drag-and-drop low-code builder (Frappe's Form Builder already exists; we wrap it) |
| Guardrails-first — refuses unsafe configs at the plugin layer | A "trust the user" generator |

## The four-document Builder Protocol

| File | Purpose |
|---|---|
| [`PLAN.md`](./PLAN.md) | Phased implementation plan with checkpoints |
| [`PRD.md`](./PRD.md) | Product requirements — who, what, why |
| [`SECURITY.md`](./SECURITY.md) | Threat model + non-negotiable guardrails |
| [`CLAUDE.md`](./CLAUDE.md) | Working memory for Claude Code sessions in this repo |
| [`HEARTBEAT.md`](./HEARTBEAT.md) | Current phase / blockers / next checkpoint |

## Open decisions (need owner sign-off before Phase 1)

1. **Sync direction** — defaulting to **B+ hybrid** (staging interactive, prod git-only). See `PRD.md §3`.
2. **Plugin namespace** — defaulting to `/fs-` prefix.
3. **mgrant-stack access** — work from public README only unless collaborator access granted.

See `PLAN.md §0` for the full decision register.
