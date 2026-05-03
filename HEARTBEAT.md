# HEARTBEAT — frappe-stack

> Stamped at every phase transition. Newest entry on top.

---

## 2026-05-03 — Phase 1 artifacts complete

**Phase:** 1 — Plugin manifest + Builder Protocol scaffolding
**State:** artifacts written; smoke-test pending

### Done

- D-02..D-08 confirmed (all defaults locked).
- D-02 amended: namespace auto-derives from manifest `name` field. Original `/fs-` proposal isn't supported by Claude Code's plugin schema; commands now invoke as `/frappe-stack:<verb>`.
- `.claude-plugin/plugin.json` written (minimal valid manifest, `version: 0.1.0`).
- `.claude-plugin/marketplace.json` written (single-plugin self-marketplace pattern, `source: "./"`).
- `.claude-plugin/README.md` written (install + namespace docs).
- `LICENSE` (MIT) added.
- Stub directories committed: `skills/`, `agents/`, `commands/`, `hooks/`, `apps/stack_core/` (each with `.gitkeep`).

### Pending checkpoint

- Smoke-test: in a clean Claude Code session, run `/plugin marketplace add https://github.com/dhwani-ris/frappe-stack.git` then `/plugin install frappe-stack@frappe-stack` — confirm install succeeds with no errors. (Cannot run from inside Claude Code; needs manual operator step.)

### Next

Phase 2 — `stack_core` Frappe support app. DocTypes, API endpoints, guardrail validators, tests. Per `PLAN.md §3`, blocked only on a `bench` environment to scaffold against; can write the DocType JSON specs and validator code without bench, but cannot run tests until a Frappe v15+ site is available.

---

## 2026-05-01 — D-01 confirmed

**Decision:** D-01 (sync direction) = **B+ hybrid**. Staging is interactive (PM API writes allowed); production is git-only (PR-merge → `bench migrate`). Phase 7 (git roundtrip) and Phase 5 (`/fs-promote`) build against this.

Open: D-02..D-08 still proposed.

---

## 2026-05-01 — Phase 0 opened

**Phase:** 0 — Planning & alignment
**State:** in progress
**Owner:** TBD (awaiting product sign-off)

### Done

- Initial commit: `README.md`, `PRD.md`, `PLAN.md`, `SECURITY.md`, `CLAUDE.md`, `HEARTBEAT.md`, `.gitignore`.
- Research complete:
  - mgrant-stack pattern documented (Claude Code plugin, not a Frappe app).
  - Frappe ecosystem prior art surveyed (`awesome-frappe`, `frappe_dhwani_base`, `sunandan89/mgrant-frappe-patterns`).
  - Frappe issue #34915 + #36398 (fixture sync gaps) noted in `PLAN.md §12 Risks`.
  - No existing GitOps tool for Frappe found — confirms this is novel.
  - No existing A/B in Frappe Workflow found — confirms this is novel.

### Blocked / pending

- **D-01 to D-08** in `PLAN.md §0` — all proposed, none confirmed by product yet.
- **mgrant-stack collaborator access** — work continues from public README only until granted.
- **`stack_core` API key strategy** — placeholder; needs IT/secrets-manager decision before Phase 2.

### Next checkpoint

Close Phase 0 by getting D-01..D-08 confirmed (or amended) by product owner. Then begin Phase 1 (plugin manifest + Builder Protocol scaffolding).

### Notes for next session

- The `infra/` directory is **deferred** per stakeholder direction (D-09 confirmed). Pre-commit hooks, Docker, CI workflows all wait until post-v0.1.
- `frappe_dhwani_base` already has the pre-commit / CI setup we want — **port from there** when `infra/` reopens, don't write from scratch.
- The cloned upstream `dhwani-ris/frappe-stack` was empty — this commit initializes it.
