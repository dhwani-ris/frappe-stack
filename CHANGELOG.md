# Changelog

All notable changes to `frappe-stack` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (Phase 0 — 2026-05-01)

- Initial Builder Protocol docs: `README.md`, `PRD.md`, `PLAN.md`, `SECURITY.md`, `CLAUDE.md`, `HEARTBEAT.md`.
- Decision register opened with D-01..D-09 (D-09 confirmed: `infra/` deferred to post-v0.1).

### Added (Phase 1 — 2026-05-03)

- `.claude-plugin/plugin.json` — manifest, `name=frappe-stack`, `version=0.1.0`.
- `.claude-plugin/marketplace.json` — single-plugin self-marketplace.
- `.claude-plugin/README.md` — install + namespace docs.
- `LICENSE` (MIT).
- D-02..D-08 confirmed.

### Added (Phase 2 + 7 — 2026-05-03)

- `apps/stack_core/` Frappe support app with:
  - DocTypes: `Stack Blueprint`, `Stack Workflow Def`, `Experiment Assignment`, `Stack Audit Log` (+ tests).
  - API: `doctype_builder`, `workflow_builder`, `config_builder`, `fixtures.export`, `diff.diff`. All whitelisted, permission-checked, audit-logged via `@audited` decorator.
  - Guardrails: `schema_validator` (Draft 2020-12 JSON-Schema per blueprint type), `fieldtype_whitelist` (Code/Password/Attach gated), `reserved_names` (refuses Frappe core + 'Stack ' prefix), `workflow_validator` (terminal-state, role-on-state, traffic-split-sums-to-100), `permission_enforcer` (refuses prod direct writes, blocks audit-tagged hard-delete).
  - Git bridge (Phase 7): `exporter` (per-blueprint JSON), `committer` (GitPython), `pr_opener` (gh CLI + REST fallback), `differ` (3-bucket structured diff), `applier` (idempotent git→site), daily `reconcile_drift` scheduled task.
- 5 test modules covering DocType controllers, guardrails, git bridge, API endpoints. Coverage target: ≥ 80%.

### Added (Phase 3 — 2026-05-03)

- 16 skills:
  - `platform/`: `frappe-platform` (4-layer model, config-vs-code decision tree), `frappe-permissions`, `frappe-patterns`, `frappe-api`.
  - `building/`: `designing-forms`, `modeling-workflows`, `building-dashboards`, `composing-reports`, `wiring-integrations`, `designing-experiments`.
  - `process/`: `git-roundtrip`, `promoting-changes`, `writing-specs`, `running-qa`, `managing-tickets`.
  - `builder-protocol/` (the meta-skill — when to use the four protocol files).

### Added (Phases 4–6 — 2026-05-03)

- 8 agents: `engineer`, `reviewer`, `tester`, `deployer`, `analyst`, `migrator`, `documenter`, `orchestrator`.
- 9 slash commands: `/frappe-stack:init`, `:build`, `:pull`, `:push`, `:diff`, `:promote`, `:experiment`, `:review`, `:ship`.
- 6 safety hooks declared in `hooks/hooks.json`:
  - `block_dangerous_bash` — `rm -rf /`, `bench drop-site`, `git push --force` to protected branches, `DROP`, `DELETE` without `WHERE`.
  - `block_direct_prod_api` — refuses mutating call to host flagged `is_production=1`.
  - `block_ignore_permissions` — `ignore_permissions=True`, `allow_guest=True`, hardcoded role checks.
  - `block_credential_leak` — AKIA*, GitHub tokens, private keys, hardcoded `api_key=`/`Bearer` literals.
  - `block_fstring_sql` — f-string / `.format()` / `%` SQL in `*.py`.
  - `audit_local` (PostToolUse) — append `.frappe-stack/audit.jsonl` row per Bash/Edit/Write.
  - `heartbeat_check` (Stop) — prompts if `PLAN.md` changed but `HEARTBEAT.md` didn't.

### Added (Phase 8 — 2026-05-03)

- A/B in workflows is integrated across phases 2/3/5:
  - `Stack Workflow Def.experiment_id` + `experiment_status` fields.
  - `Experiment Assignment` DocType (deterministic by `hash(experiment_id || doc.name)`).
  - Split-state validator in `workflow_validator.py`.
  - `building/designing-experiments` skill.
  - `/frappe-stack:experiment` command (define / status / pause / resume / promote / abandon).

### Added (Phase 9 — 2026-05-03)

- `docs/walkthroughs/` — 4 PM-facing walkthroughs (first DocType, first workflow, first experiment, first promotion).
- `docs/operators/` — 2 DevOps runbooks (installing `stack_core`, rotating keys).

### Deferred to post-v0.1 (D-09)

- `infra/`: Docker compose, CI workflows, pre-commit hooks. Will port from `dhwani-ris/frappe_dhwani_base` when reopened.
- Smoke-test of plugin install in a clean Claude Code session (cannot be done from inside a session).
- Live `bench` test execution to confirm coverage meets the 80% target.
