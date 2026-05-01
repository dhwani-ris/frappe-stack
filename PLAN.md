# PLAN — frappe-stack

> Phased implementation plan. Each phase has an exit checkpoint. Do not start phase N+1 until phase N's checkpoint signs off.

## 0. Decision register (must close before Phase 1)

| ID | Decision | Default | Owner | Status |
|---|---|---|---|---|
| D-01 | Sync direction | **B+ hybrid** (staging interactive, prod git-only) | Product | confirmed 2026-05-01 |
| D-02 | Plugin namespace | **`/fs-`** | Product | proposed |
| D-03 | mgrant-stack access | work from public README until collaborator granted | Eng | proposed |
| D-04 | Frappe target version | **v15+** only | Eng | proposed |
| D-05 | Plugin marketplace | private, install via direct git URL | Eng | proposed |
| D-06 | Test framework for `stack_core` | `frappe.tests.utils.FrappeTestCase` (per global frappe-testing rules) | Eng | proposed |
| D-07 | A/B in workflows — scope for v0.1 | binary split only (no n-arm); deterministic by `hash(doc.name)` | Product | proposed |
| D-08 | Audit log retention | append-only, no purge; archive after 365 days | Compliance | proposed |
| D-09 | infra/ (Docker, CI, pre-commit) | **deferred to post-v0.1** | Product | confirmed |

## 1. Architecture overview

```
┌──────────────────────── Claude Code (PM's machine) ────────────────────────┐
│  frappe-stack plugin                                                       │
│                                                                            │
│   .claude-plugin/        skills/         agents/       commands/    hooks/ │
│   ├── manifest.json      ├── platform/    ├── engineer  ├── fs-init  ├──── │
│   ├── README             ├── building/    ├── reviewer  ├── fs-build       │
│                          ├── process/     ├── tester    ├── fs-promote     │
│                          └── builder-     ├── deployer  ├── fs-pull/push   │
│                              protocol/    └── …         └── …              │
│                                                                            │
│        │                                                                   │
│        │ HTTPS + API key                                                   │
└────────┼───────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────── Frappe site (staging) ──────────────┐    ┌── GitHub ──┐
│  apps/stack_core/                                       │    │  config-   │
│   ├── api/             ←─────── plugin calls            │    │  repo      │
│   ├── doctype/                                          │    │            │
│   │   ├── stack_blueprint        (versioned config)     │    │  ┌──────┐  │
│   │   ├── stack_workflow_def                            │    │  │ PRs  │  │
│   │   ├── experiment_assignment                         │    │  │      │  │
│   │   └── stack_audit_log         (append-only)         │ ←─→│  │ main │  │
│   ├── guardrails/      (schema, fieldtype, reserved)    │    │  └──────┘  │
│   ├── git_bridge/      (export-fixtures + commit/PR)    │    │            │
│   └── hooks.py                                          │    └────────────┘
└─────────────────────────────────────────────────────────┘             │
                                                                        │ merge
                                                                        ▼
                                            ┌─── Frappe site (production) ───┐
                                            │  bench migrate (auto on merge) │
                                            └────────────────────────────────┘
```

## 2. Phase 1 — Plugin manifest + Builder Protocol scaffolding (1–2 days)

**Deliverables:**
- `.claude-plugin/manifest.json` (plugin metadata, version, namespace `fs-`)
- `.claude-plugin/README.md` (install instructions: register marketplace + add plugin)
- `CLAUDE.md` for the plugin itself (this repo's working memory)
- `HEARTBEAT.md` template that gets stamped on every phase transition
- Empty skill/agent/command directories with `.gitkeep`
- LICENSE (MIT, matching `frappe_dhwani_base`)

**Checkpoint:** plugin installs in Claude Code without errors; `/fs-` commands appear (even if they only print "not implemented").

## 3. Phase 2 — `stack_core` Frappe support app (3–5 days)

**Deliverables:**
- `apps/stack_core/` skeleton via `bench new-app`
- DocTypes:
  - `Stack Blueprint` — fields: name, version, type (doctype/workflow/dashboard/report/config), payload (JSON), status, applied_at, applied_by, git_commit_sha
  - `Stack Workflow Def` — extends Blueprint, adds split-state fields
  - `Experiment Assignment` — fields: doc_reference, blueprint, arm, assigned_at, outcome, outcome_at
  - `Stack Audit Log` — fields: actor, action, blueprint, before_json, after_json, timestamp, ip
- API endpoints (all `@frappe.whitelist()`, all permission-checked):
  - `POST /api/method/stack_core.api.build_doctype`
  - `POST /api/method/stack_core.api.build_workflow`
  - `POST /api/method/stack_core.api.build_config`
  - `POST /api/method/stack_core.api.export_fixtures` (returns JSON of all blueprints)
  - `GET  /api/method/stack_core.api.diff_against_git`
- Guardrail validators:
  - `guardrails/schema_validator.py` (JSON-Schema for each blueprint type)
  - `guardrails/fieldtype_whitelist.py` (Code/Password/Attach gated by role)
  - `guardrails/reserved_names.py` (block `User`, `Role`, `DocType`, …)
  - `guardrails/workflow_validator.py` (terminal state, role on every state, no orphans)
- Tests (per `frappe-testing.md`):
  - One `test_<doctype>.py` per DocType
  - API tests with valid + invalid + permission-denied paths
  - Negative tests for every guardrail (refuses bad input)

**Checkpoint:** all tests pass via `bench --site test_site run-tests --app stack_core --coverage`. Coverage ≥ 80%.

## 4. Phase 3 — High-value skills (3–5 days)

Order by PM impact. Each skill = `skills/<category>/<name>/SKILL.md` + supporting refs.

| Order | Skill | Why first |
|---|---|---|
| 1 | `building/designing-forms` | DocType creation = most common PM ask |
| 2 | `building/modeling-workflows` | Approval flows = second-most-common |
| 3 | `process/git-roundtrip` | The differentiator — without this, we're just an API wrapper |
| 4 | `platform/frappe-platform` | 4-layer stack + config-vs-code decision tree (port from mgrant-stack pattern) |
| 5 | `platform/frappe-permissions` | Required reading for every other skill |
| 6 | `platform/frappe-patterns` | Index of patterns from `sunandan89/mgrant-frappe-patterns` |
| 7+ | rest (`composing-reports`, `building-dashboards`, `wiring-integrations`, `designing-experiments`, `writing-specs`, `running-qa`, `promoting-changes`, `managing-tickets`, `builder-protocol`) | as needed |

Each skill must:
- Trigger on PM-natural phrases (e.g., "I need a form for…", not "create a DocType")
- Reference the global `~/.claude/rules/frappe/` files explicitly
- Include a worked example end-to-end
- List anti-patterns it refuses

**Checkpoint:** PM can run `/fs-build doctype Beneficiary` and the engineer agent uses `designing-forms` to walk them through fields, validation, permissions; emits a blueprint JSON; calls `stack_core` API; sees DocType live on staging.

## 5. Phase 4 — Agents (2–3 days)

Order:

| Order | Agent | Wraps |
|---|---|---|
| 1 | `engineer` | The default — turns PM intent into blueprint JSON |
| 2 | `reviewer` | Calls global `frappe-reviewer` agent + applies `~/.claude/rules/frappe/` rules |
| 3 | `tester` | Generates `test_<doctype>.py` + Playwright tests per `frappe-testing.md` |
| 4 | `deployer` | Runs `/fs-promote`, opens PR, monitors merge → migrate |
| 5 | `analyst` | Read-only — runs reports, queries dashboards, summarizes A/B results |
| 6 | `migrator` | Schema migration safety — uses global `database-reviewer` |
| 7 | `documenter` | Auto-updates `docs/` from blueprints |
| 8 | `orchestrator` | Routes multi-step asks across the others |

Each agent: short description, action triggers, minimum tools, model selection per `~/.claude/rules/common/performance.md`.

**Checkpoint:** `/fs-build doctype …` end-to-end uses engineer → reviewer → tester (parallel where independent), produces a working DocType + tests + audit log row + git commit.

## 6. Phase 5 — Slash commands (2 days)

| Command | Action |
|---|---|
| `/fs-init` | Bootstrap: install `stack_core` on a site, configure API key, register staging+prod sites in plugin config |
| `/fs-build <type> <name>` | Interactive build via engineer agent |
| `/fs-pull` | Fetch site state → write fixtures locally → commit |
| `/fs-push` | Apply local fixtures → staging site (refuses prod) |
| `/fs-diff` | Show drift between site and git |
| `/fs-promote` | Open PR from staging snapshot to prod-config repo |
| `/fs-experiment <action>` | Define / monitor / promote A/B in workflows |
| `/fs-review` | Pre-promote: runs reviewer + tester, surfaces issues |
| `/fs-ship` | Tag release after successful prod migrate |

**Checkpoint:** all commands have `--help`, all refuse cleanly on missing config, all complete a smoke test scenario documented in `docs/walkthroughs/`.

## 7. Phase 6 — Safety hooks (1 day)

`hooks/` ships JSON definitions for Claude Code:

- `block-direct-prod-api.json` — PreToolUse on Bash/WebFetch: any URL matching the configured prod host is blocked.
- `enforce-blueprint-schema.json` — PreToolUse on `mcp__stack_core__*` (or Bash curl to stack_core): validate JSON-Schema before send.
- `audit-every-mutation.json` — PostToolUse: append to local `.frappe-stack/audit.jsonl`.
- `block-ignore-permissions.json` — PreToolUse on Edit/Write: scan generated Python for `ignore_permissions=True`, refuse.
- `block-credential-leak.json` — PreToolUse on Edit/Write: scan for AKIA / Bearer / api_key= patterns, refuse.
- `block-force-push.json` — PreToolUse on Bash: refuse `git push --force` to protected branches.
- `block-bench-drop-site.json` — PreToolUse on Bash: refuse `bench drop-site`.

**Checkpoint:** every guardrail in `SECURITY.md §2.1` has a working hook, with a regression test that proves the hook fires.

## 8. Phase 7 — Git roundtrip engine (3–5 days)

`apps/stack_core/git_bridge/`:

- `exporter.py` — wraps `bench export-fixtures` with per-blueprint granularity (fixes ambiguity around app-level fixtures, addresses Frappe issue #34915 partially).
- `committer.py` — runs in a configurable git working directory (the **config repo**, not the Frappe app source). Stages, commits with structured message, pushes to a feature branch.
- `pr_opener.py` — uses `gh` CLI (or GitHub REST API) to open PR with auto-generated body: blueprint diff, audit log excerpt, test results.
- `differ.py` — compares site fixtures vs config-repo `main` HEAD, outputs structured diff.
- `applier.py` — opposite direction: pulls config repo, applies fixtures via `bench migrate`, idempotent.

Special-cases:
- App-level fixtures vs site-specific overrides (per Frappe issue #36398) — config repo has both `fixtures/app/` (shipped with app) and `fixtures/site/<sitename>/` (site overrides applied post-migrate).
- Conflict resolution when site state and git state both changed: surface as `/fs-diff` output, refuse `/fs-promote` until resolved.

**Checkpoint:** round-trip drill — make a change on staging, run `/fs-pull`, verify git diff matches; revert site, run `/fs-push`, verify site state matches git; run `/fs-promote`, verify PR opens with correct content; merge PR, verify prod migrates idempotently.

## 9. Phase 8 — A/B experiments in workflows (3–4 days)

Schema additions to `Stack Workflow Def`:
```json
{
  "states": [
    { "name": "Initial Review", "type": "split", "traffic_split": { "arm_a": 50, "arm_b": 50 },
      "next_states": { "arm_a": "Manager Approval", "arm_b": "Auto-Approval" } }
  ]
}
```

Implementation:
- New `Experiment Assignment` row created on workflow entry into a split state.
- Assignment is deterministic: `hash(doc.name + experiment_id) % 100 < traffic_split.arm_a` → arm_a, else arm_b.
- Document gets a Custom Field `experiment_arm` (linked to assignment row).
- Subsequent `next_states` lookup keys off `experiment_arm`.
- Outcome captured when document reaches a terminal state — `Experiment Assignment.outcome` updated.
- Dashboard skill: `building/designing-experiments` ships a default Frappe Dashboard config showing per-arm conversion rate, mean cycle time, current sample size.
- `/fs-experiment promote arm_a` → mutates blueprint to remove split, fixes path to arm_a's, opens PR.

**Checkpoint:** end-to-end test: define experiment, simulate 100 documents, verify ~50/50 split, verify outcomes captured, verify dashboard reads correct numbers, verify promotion strips losing arm.

## 10. Phase 9 — Polish + docs + v0.1 release (2 days)

- `docs/walkthroughs/` — 4 PM-facing screen-recorded walkthroughs:
  1. First DocType
  2. First workflow with approvals
  3. First A/B experiment
  4. First promotion to prod
- `docs/operators/` — DevOps runbook for installing `stack_core` + configuring sites + rotating keys
- `CHANGELOG.md` — start tracking
- Tag `v0.1.0`

## 11. Effort summary

| Phase | Days |
|---|---|
| 0 — decisions closed | 0.5 |
| 1 — manifest + protocol | 1–2 |
| 2 — `stack_core` | 3–5 |
| 3 — skills | 3–5 |
| 4 — agents | 2–3 |
| 5 — commands | 2 |
| 6 — hooks | 1 |
| 7 — git roundtrip | 3–5 |
| 8 — A/B experiments | 3–4 |
| 9 — release polish | 2 |
| **Total** | **20–30 working days** |

## 12. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Frappe issue #34915 (fixture sync) bites us mid-Phase 7 | Medium | Phase 7 includes per-blueprint export to sidestep it |
| App fixtures vs site overrides clash on real sites | High | Two-tier `fixtures/app/` + `fixtures/site/<sitename>/` from day 1 |
| PM creates a DocType with a name that already exists in a different module | High | Reserved-name check + namespace prefix enforcement |
| API key leak on PM laptop | Medium | Plugin stores in OS keychain, not in plain config |
| `gh` CLI not installed on PM machine | Low | Fallback to GitHub REST API in `pr_opener.py` |
| mgrant-stack patterns we copy turn out to be private/proprietary | Medium | Only the structural pattern is borrowed; all skills/agents are written from scratch against public docs |
