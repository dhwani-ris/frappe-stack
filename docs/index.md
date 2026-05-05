---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

<span class="status-pill">v0.1.0 · scaffold only — not yet runtime-tested</span>

# frappe-stack

<p class="tagline">A Claude Code plugin for building Frappe v15+ apps without writing code. You type a slash command, the plugin generates the DocType / Workflow / Dashboard / Report, validates it, and either applies it to a staging site or opens a pull request. Frappe site state and a GitHub config repo stay in sync both directions.</p>

[Read the first tutorial](walkthroughs/01-first-doctype.md){ .md-button .md-button--primary }
[See the architecture](architecture.md){ .md-button }
[View on GitHub :material-github:](https://github.com/dhwani-ris/frappe-stack){ .md-button }

</div>

## What it does

Three things, named precisely:

**1. Translates plain-language asks into Frappe configurations.** You write *"I need a beneficiary registration form with full name, village, age, Aadhaar number, and the registering officer."* The plugin walks you through fields, permissions, naming rule, and validation. It generates the JSON, calls `stack_core.api.doctype_builder.build` on your staging site, and the DocType appears in Frappe within seconds. No Python, no JSON written by hand.

**2. Mirrors site changes into git, both directions.** Every applied change is recorded as a `Stack Blueprint` row on the site and exported as a per-blueprint JSON file in your config repository. `/frappe-stack:pull` exports site state to git. `/frappe-stack:push` applies git state to a staging site. `/frappe-stack:promote` opens a pull request from staging to production. Production never accepts direct API writes — only `bench migrate` after a merge.

**3. Refuses unsafe inputs at multiple layers.** A small set of patterns are explicitly rejected: `ignore_permissions=True`, `allow_guest=True` without review, f-string SQL, hardcoded role-name checks, real Aadhaar / PAN / phone numbers in prompts, force-pushes to `main`, hard-deletes on audit-tagged DocTypes. Each is enforced at the layer closest to the user — typing-time hooks for prompts, edit-time hooks for code, validators inside the API, branch protection for git.

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

The full operator runbook is in [Installing stack_core](operators/installing-stack-core.md).

## What's verified, what isn't

| Capability | Written | Tested |
|---|---|---|
| Plugin manifest + marketplace listing | ✓ | ✗ never installed in a clean Claude Code session |
| `stack_core` Frappe app (4 DocTypes, 6 API endpoints, 5 validators) | ✓ | ✗ no Frappe v15+ bench available — tests written, never executed |
| Skills (17), agents (8), slash commands (9) | ✓ | ✗ never invoked end-to-end |
| Safety hooks (8) | ✓ | ✗ regression tests not yet written |
| `infra/` (Docker, CI, pre-commit) | ✗ | — deferred per decision D-09 |

Calling this v0.1.0 is honest because the artefacts are complete; calling it production-ready would not be. The tutorials work as written *if* the runtime behaves as designed.

## Reference

<div class="grid cards" markdown>

-   **[Skills](skills.md)** — 17 markdown files the engineer agent loads when the user's prompt matches a trigger. Each names what it teaches Claude, what conversation it runs, and what it refuses.

-   **[Agents](agents.md)** — 8 agents that own the work for one slash command each. Engineer turns intent into config. Reviewer + tester run after every build. Deployer owns promotion to production.

-   **[Commands](commands.md)** — 9 slash commands invoked as `/frappe-stack:<verb>`. `init` bootstraps a site, `build` creates a blueprint, `pull` / `push` / `diff` move state between site and git, `promote` opens the production PR.

-   **[Hooks](hooks.md)** — 8 hooks across 4 lifecycle events. They block dangerous shell commands, direct production API writes, permission bypasses, credential leaks, and f-string SQL. They also coach vague prompts toward the right slash command.

</div>

## Tutorials

<div class="grid cards" markdown>

-   **[1. First DocType](walkthroughs/01-first-doctype.md)** — Build a Beneficiary form, save it on staging, mirror to git. ~10 minutes.

-   **[2. First Workflow](walkthroughs/02-first-workflow.md)** — Add a three-stage approval flow on the form from tutorial 1.

-   **[3. First Experiment](walkthroughs/03-first-experiment.md)** — A/B test two approval paths and promote the faster one.

-   **[4. First Promotion](walkthroughs/04-first-promotion.md)** — Open a pull request from staging to production and watch the migrate complete.

</div>

## For operators

<div class="grid cards" markdown>

-   **[Installing stack_core](operators/installing-stack-core.md)** — bench install, `site_config.json` shape, role setup, smoke test.

-   **[Rotating keys](operators/rotating-keys.md)** — 90-day rotation steps for the API key, GitHub token, Frappe Administrator password, database root, and SSH keys. Incident protocol.

</div>

## Project files

The four working-memory files that frame the build are at the repo root:

- [PRD](PRD.md) — what we're building and why.
- [PLAN](PLAN.md) — phased plan with the decision register (D-01..D-09).
- [SECURITY](SECURITY.md) — threat model and the layered guardrail matrix.
- [HEARTBEAT](HEARTBEAT.md) — newest entry on top; the live state of the build.
- [CHANGELOG](CHANGELOG.md) — what landed when.
- [Contributing](CONTRIBUTING.md) — how to add a skill, agent, command, or hook.
