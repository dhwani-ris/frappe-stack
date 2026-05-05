# frappe-stack — documentation hub

The plugin in one diagram and a navigable index of every skill, agent, command, and hook.

## How the pieces fit

```
                    ┌──── User (PM in Claude Code) ────┐
                    │                                    │
                    │   /frappe-stack:build doctype …    │
                    │   "make a form for X"              │
                    │                                    │
                    └────────────────┬───────────────────┘
                                     │
        ┌────────────────────────────┼─────────────────────────────┐
        │                            │                             │
   ┌────▼─────┐               ┌──────▼──────┐               ┌──────▼─────┐
   │ Slash    │               │ User-       │               │ Pre-tool   │
   │ commands │               │ Prompt-     │               │ hooks      │
   │ (9)      │               │ Submit hook │               │ (5)        │
   │ init     │               │ blocks PII  │               │ block      │
   │ build    │               │ + coaches   │               │ unsafe     │
   │ pull/push│               │ vague asks  │               │ bash/edit  │
   │ diff     │               │             │               │            │
   │ promote  │               └─────────────┘               └────────────┘
   │ experim. │
   │ review   │       Each command spawns:
   │ ship     │       ┌──────────────────────────────────────┐
   └──────────┘       │  Agents (8)                          │
                      │  engineer / reviewer / tester /       │
                      │  deployer / analyst / migrator /      │
                      │  documenter / orchestrator            │
                      └────────────┬─────────────────────────┘
                                   │
                      ┌────────────▼─────────────┐
                      │  Skills (17)             │
                      │  platform/   building/   │
                      │  process/    builder-    │
                      │              protocol    │
                      └────────────┬─────────────┘
                                   │
                      ┌────────────▼─────────────────┐
                      │  stack_core Frappe app        │
                      │  (the API surface the plugin  │
                      │   actually calls)             │
                      │                               │
                      │  /api/method/stack_core.*    │
                      │  → guardrails (5)             │
                      │  → DocTypes (4)               │
                      │  → audit log                  │
                      │  → git_bridge → GitHub        │
                      └───────────────────────────────┘
```

## Index

| Layer | Catalog |
|---|---|
| **Skills (17)** — what the engineer agent loads | [`docs/skills.md`](./skills.md) |
| **Agents (8)** — who does what | [`docs/agents.md`](./agents.md) |
| **Slash commands (9)** — what PMs type | [`docs/commands.md`](./commands.md) |
| **Hooks (8)** — guardrails that fire automatically | [`docs/hooks.md`](./hooks.md) |
| **Architecture** — how staging↔git↔prod actually flows | [`docs/architecture.md`](./architecture.md) |
| **Walkthroughs (4)** — PM-facing tutorials | [`docs/walkthroughs/`](./walkthroughs/) |
| **Operator runbooks (2)** — DevOps installation + key rotation | [`docs/operators/`](./operators/) |

## For first-time readers

If you have 5 minutes:

1. Read [`docs/walkthroughs/01-first-doctype.md`](./walkthroughs/01-first-doctype.md) — that's the "before / after" for a PM.
2. Skim [`docs/architecture.md`](./architecture.md) — the data flow staging ↔ git ↔ prod.

If you have 30 minutes:

3. Read [`PRD.md`](../PRD.md) — what we're building and why.
4. Read [`SECURITY.md`](../SECURITY.md) — the guardrails matrix.
5. Skim [`docs/skills.md`](./skills.md) and [`docs/commands.md`](./commands.md) for the surface area.

If you're picking up a session mid-flight:

6. Read [`CLAUDE.md`](../CLAUDE.md) — order of precedence + working notes.
7. Read [`HEARTBEAT.md`](../HEARTBEAT.md) — current phase + blockers.
8. Read [`PLAN.md`](../PLAN.md) — decision register and remaining work.

## Status

v0.1.0 scaffold complete (~95 files across 9 phases). **Not yet validated end-to-end** — see [`HEARTBEAT.md`](../HEARTBEAT.md) for the pending list (bench smoke-test, plugin install smoke-test, infra/ deferred).
