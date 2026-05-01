# PRD — frappe-stack

> Product Requirements Document. Owns the *what* and *why*. Pairs with `PLAN.md` (the *how*) and `SECURITY.md` (the *must-not*).

## 1. Problem

Building Frappe apps today requires a developer for every change. PMs, analysts, and business analysts have to:

- File a ticket, wait for a developer to add a DocType / Custom Field / Workflow.
- Trust that the developer remembered fixtures (so the change ships with the app).
- Trust that permissions, audit log, and site-vs-app-fixture conflicts were handled.

This forces non-developers into manual workarounds (spreadsheets, paper forms, off-platform approvals). Meanwhile, even when developers do the work, **site changes routinely drift from GitHub** — the audit trail is the change log of a single site, not git history.

## 2. Users & their jobs

### Primary: PM / Analyst (non-developer)

> "I need to add a beneficiary registration form with three approval levels and a dashboard. I don't want to write Python."

Jobs:
- Create DocTypes, Custom Fields, Workflows, Dashboards, Reports, Configs.
- See what they built committed to GitHub automatically.
- Promote staging changes to production with confidence (review + approval).
- Run A/B experiments on workflows to compare approval paths.

### Secondary: Developer / DevOps

Jobs:
- Review PM-generated PRs before merge to production.
- Trust that the plugin already enforced security/best-practice — review = sanity check, not full audit.
- Diff site state vs git state when troubleshooting.

### Tertiary: Director / Compliance

Jobs:
- Audit every change via git history + the on-site audit log DocType.
- Confirm no PII bypass, no `ignore_permissions=True`, no hard deletes.

## 3. Solution shape

### 3.1 Two layers

1. **The Claude Code plugin (`frappe-stack`)** — slash commands, skills, agents, hooks. PM types intent; plugin generates correct config.
2. **The Frappe support app (`stack_core`)** — API surface the plugin calls, audit log, blueprint storage, git-bridge engine. Installed on every Frappe site that uses this stack.

### 3.2 Sync model — B+ hybrid (default decision)

```
Staging site                    GitHub                   Production site
──────────────                  ──────                  ─────────────────
[ PM uses plugin ]              (config repo)           [ no direct API   ]
       │                            │                   [ writes allowed  ]
       ↓ /fs-build                  │                            ↑
  API call to stack_core            │                            │
       │                            │                       bench migrate
       ↓                            │                            ↑
  site mutates                      │                            │
       │                            │                            │
       ↓ post-hook                  │                            │
  export fixtures                   │                            │
       │                            │                            │
       └─── /fs-promote ────→ open PR ────→ review/merge ────────┘
```

- Staging is the playground — fast iteration, instant feedback.
- Production is git-only — the audit trail *is* git history.
- `/fs-promote` is the bridge: snapshots staging fixtures, opens a PR, lets a reviewer approve, merges, triggers prod migrate.

### 3.3 A/B experiments in workflows

A new **Split state** in Frappe Workflow with deterministic traffic assignment by `hash(doc.name)`. Tracked in a dedicated `Experiment Assignment` DocType. Promotable via `/fs-experiment promote arm_a`, which strips the losing arm from the blueprint and opens a PR.

Full spec in `PLAN.md §8`.

## 4. Non-goals

- Replacing Frappe's Form Builder UI. We *call* it.
- Cross-Frappe-version magic. We target **Frappe v15+** only.
- Multi-tenant federation. One plugin install = one stack of (staging, prod) sites.
- Generic workflow engine. Only Frappe Workflow extensions.

## 5. Success metrics (post-MVP)

| Metric | Target |
|---|---|
| Time from PM intent → DocType live on staging | < 5 minutes |
| % of site changes reflected in git within 1 commit | 100% (enforced — non-negotiable) |
| % of PR-promoted changes that pass `frappe-semgrep-rules` | 100% (block at hook) |
| `ignore_permissions=True` instances introduced via plugin | 0 (block at hook) |
| `allow_guest=True` instances introduced via plugin | 0 (block at hook) |

## 6. Out of scope for v0.1

- `infra/` (Docker compose, CI workflows, pre-commit) — deferred per stakeholder direction.
- Mobile/Flutter integration (`frappe-mobile-sdk` already exists separately).
- Print format builder (Frappe core handles this).
- Multi-language UI (Frappe `__()` is enough for now).

## 7. Inspiration & prior art

- [`prody-dris/mgrant-stack`](https://github.com/prody-dris/mgrant-stack) — the structural template (Claude Code plugin shipping skills/agents/commands/hooks for a Frappe codebase).
- [`sunandan89/mgrant-frappe-patterns`](https://github.com/sunandan89/mgrant-frappe-patterns) — patterns catalog to absorb into our `frappe-patterns` skill.
- [`dhwani-ris/frappe_dhwani_base`](https://github.com/dhwani-ris/frappe_dhwani_base) — ruff/eslint/prettier/pyupgrade pre-commit + Frappe Semgrep + pip-audit setup, when we get to `infra/`.
- [`gavindsouza/awesome-frappe`](https://github.com/gavindsouza/awesome-frappe) — survey before building anything new.
