# CLAUDE.md — frappe-stack

> Working memory for Claude Code sessions in this repo. Read first, every session.

## What this repo is

A Claude Code plugin (marketplace add) that lets non-developers build Frappe apps via guided slash commands, with two-way GitHub sync and best-practice guardrails.

**Pair this file with**:
- [`PRD.md`](./PRD.md) — what we're building and why
- [`PLAN.md`](./PLAN.md) — phased implementation
- [`SECURITY.md`](./SECURITY.md) — non-negotiable guardrails
- [`HEARTBEAT.md`](./HEARTBEAT.md) — current phase / blockers

## Layered rules — order of precedence

When rules conflict, lower number wins:

1. **`SECURITY.md`** in this repo — strictest, always applies.
2. **`~/.claude/rules/frappe/`** — Frappe coding style, security, testing rules (already loaded via global instructions).
3. **`~/.claude/rules/common/`** — universal coding/git/testing standards.
4. **This `CLAUDE.md`** — repo-specific working notes.
5. **`PLAN.md`** — defines phase order; do not skip phases.

## Working notes

### Phase discipline

- Do not start Phase N+1 until Phase N's checkpoint in `PLAN.md` signs off.
- Update `HEARTBEAT.md` at every phase transition.
- If blocked, write the blocker into `HEARTBEAT.md` and stop — do not improvise across phases.

### Commit style

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`, `ci:`.
- Body explains *why*, not *what*.
- Co-authorship attribution is **disabled globally** (per user settings) — do not append `Co-Authored-By` lines.
- One logical change per commit; do not bundle phases.

### When generating Frappe code

Always check the global rules `~/.claude/rules/frappe/` first. The non-negotiables (also in `SECURITY.md`):

- ❌ Never `ignore_permissions=True`.
- ❌ Never `allow_guest=True` on whitelisted methods without explicit security review.
- ❌ Never f-string / `.format()` / `%` SQL — use `frappe.qb` or parameterized `%s`.
- ❌ Never hardcoded role checks — use `frappe.has_permission()`.
- ❌ Never hard-delete govt / audit-tagged data — soft-delete via status flag.
- ✓ Every `@frappe.whitelist()` calls `frappe.has_permission()` first.
- ✓ Every blueprint mutation writes a `stack_audit_log` row.
- ✓ Every PII field uses Fernet encryption + role-gated masking.
- ✓ Every test extends `frappe.tests.utils.FrappeTestCase`.
- ✓ Every test creates its own data, cleans up after.

### When generating plugin artifacts (skills/agents/commands/hooks)

- **Skills** trigger on PM-natural phrases ("I need a form for…"), not jargon ("create DocType").
- **Agents** must list their `description`, `tools` (minimum needed), and `model` (per `~/.claude/rules/common/performance.md`).
- **Commands** must support `--help` and refuse cleanly on missing config.
- **Hooks** must include a regression test that proves the hook fires.

### Agents to invoke (from `~/.claude/agents/`)

| Task | Agent |
|---|---|
| Frappe code review | `frappe-reviewer` |
| Security review | `security-reviewer` |
| Plan a phase | `planner` |
| Write tests first | `tdd-guide` |
| Final code review | `code-reviewer` |
| Architecture decision | `architect` |
| Database migration safety | `database-reviewer` |

Use parallel `Agent` calls when independent. Do not duplicate work — if an agent is researching, do not re-research the same thing in the main thread.

### Skills to invoke (from `~/.claude/skills/`)

| Task | Skill |
|---|---|
| Frappe testing patterns | (already in `~/.claude/rules/frappe/frappe-testing.md`) |
| Frappe security patterns | (already in `~/.claude/rules/frappe/frappe-security.md`) |
| Document API behavior | `docs-lookup` (Context7) |
| Update repo docs after a change | `doc-updater` |
| Deduplicate / refactor | `refactor-cleaner` |

## Repo structure (target — mostly empty in Phase 0)

```
frappe-stack/
├── README.md
├── PRD.md
├── PLAN.md
├── SECURITY.md
├── CLAUDE.md
├── HEARTBEAT.md
├── .gitignore
├── .claude-plugin/         (Phase 1)
├── skills/                 (Phase 3)
├── agents/                 (Phase 4)
├── commands/               (Phase 5)
├── hooks/                  (Phase 6)
(no apps/ — the plugin uses stock Frappe via REST; D-10 confirmed)
└── docs/                   (Phase 9)
```

## Owners (placeholder — fill in when team confirmed)

- Product: TBD
- Eng lead: TBD
- Security: TBD
- Compliance: TBD

Update via PR, not directly.

## Things I should ask before doing

- **Anything in Phase N+1 when Phase N isn't checkpointed.** Ask the user to confirm phase transition.
- **Any decision in `PLAN.md §0` that's still `proposed`.** Surface defaults and ask for sign-off.
- **Any hook bypass.** Never `--no-verify`. If a hook fails, find the root cause.
- **Any push to `main` of this repo or any downstream config repo.** Treat every push as user-confirmed-once-only.
