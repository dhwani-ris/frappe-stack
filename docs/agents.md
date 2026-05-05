# Agents catalog

8 agents. Each is a markdown file under [`agents/`](../agents/) with frontmatter declaring its tools and model.

| Agent | Model | Tools | When it fires | What it produces |
|---|---|---|---|---|
| [`engineer`](../agents/engineer.md) | sonnet | Read, Grep, Glob, Bash, Write, Edit | Default for every `/frappe-stack:build`. Turns PM intent into a Stack Blueprint payload. | A live blueprint on staging, status=Applied. |
| [`reviewer`](../agents/reviewer.md) | sonnet | Read, Grep, Glob, Bash | After every build, before every promote. | A CRITICAL/HIGH/MEDIUM/LOW report. Blocks promote on any CRITICAL or HIGH. |
| [`tester`](../agents/tester.md) | sonnet | Read, Grep, Glob, Bash, Write, Edit | After every build that adds or modifies code. | FrappeTestCase tests + Playwright E2E + a coverage report. Gate ≥ 80% on changed lines. |
| [`deployer`](../agents/deployer.md) | sonnet | Read, Grep, Glob, Bash | Owns `/frappe-stack:promote` end-to-end. | Pre-promote checklist run, branch + commit + PR + merge watch + smoke-test. |
| [`analyst`](../agents/analyst.md) | haiku | Read, Grep, Glob, Bash | Read-only reports — counts, A/B results, audit-log queries. | A table + 1-line interpretation + the exact filter used. |
| [`migrator`](../agents/migrator.md) | sonnet | Read, Grep, Glob, Bash | Schema changes — rename, fieldtype change, naming-rule change. | A migration plan with patches.txt entry, rollback DDL, test plan. |
| [`documenter`](../agents/documenter.md) | haiku | Read, Grep, Glob, Write, Edit | After every successful build, on `/pull`, before every promote. | Auto-generated `docs/doctypes/<name>.md`, `docs/workflows/<name>.md`, CHANGELOG entry. |
| [`orchestrator`](../agents/orchestrator.md) | sonnet | Read, Grep, Glob | Multi-step requests spanning multiple agents. | An ordered plan (sequential vs parallel steps); dispatches the chain. |

## How they pair up

| Trigger | Sequence (→ = sequential, ‖ = parallel) |
|---|---|
| `/frappe-stack:build doctype X` | engineer → (reviewer ‖ tester) → documenter |
| `/frappe-stack:build` chain (DocType + Workflow) | engineer (DocType) → engineer (Workflow) → (reviewer ‖ tester) → documenter |
| `/frappe-stack:review` | reviewer ‖ tester (combined report) |
| `/frappe-stack:promote` | deployer (which calls reviewer + tester internally) |
| Schema change | migrator → engineer → tester → reviewer → documenter |
| "Show me the experiment results" | analyst |

## Model choice rationale (per `~/.claude/rules/common/performance.md`)

- **Haiku** (analyst, documenter): high-frequency, read-only or templated. 90% capability at 3× cost savings.
- **Sonnet** (everything else): code generation + reasoning, where wrongness is expensive.
- **Opus** (none): reserved for architectural decisions and deep analysis. None of these agents need it.

## Pairing with global agents

The plugin's agents wrap and extend global ones from `~/.claude/agents/`:

| Plugin agent | Calls global agent |
|---|---|
| `reviewer` | `frappe-reviewer` (hard rule layer) + `security-reviewer` (when novel attack surface) |
| `migrator` | `database-reviewer` |
| `tester` | `tdd-guide` |

## What they refuse

Each agent's `.md` file lists its refusals. Quick highlights:

- **engineer**: refuse blueprints failing local guardrails (reserved name, fieldtype whitelist, workflow shape). Refuse to run on `is_production=1` site. Refuse to skip user confirmation step.
- **reviewer**: refuse to approve any build with even one CRITICAL or HIGH finding. Refuse to run without semgrep available.
- **tester**: refuse to mock the database. Refuse to skip negative-path tests. Refuse to delete hard-to-test code to game coverage.
- **deployer**: refuse Friday-after-14:00 without `--emergency`. Refuse bundling >5 unrelated changes. Refuse force-merge bypassing branch protection.
- **migrator**: refuse one-shot renames. Refuse migrations without a backup verified in last 24h.
- **analyst**: refuse to mutate. Period.
- **orchestrator**: refuse to run agents in parallel when they share state. Refuse to skip reviewer "because the build was straightforward."

## Adding an agent

1. Create `agents/<name>.md` with frontmatter:
   ```yaml
   ---
   name: <name>
   description: <when to invoke — proactively / when triggered / never>
   tools: <minimum needed; smaller is safer>
   model: haiku | sonnet | opus
   ---
   ```
2. Body: workflow steps, refuses, pairs-with.
3. Add a row to the table above.
4. If it wraps a global agent, document the wrap in the row.
