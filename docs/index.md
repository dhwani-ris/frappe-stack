---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

<span class="status-pill">v0.1.0 · scaffold complete</span>

# frappe-stack

<p class="tagline">A Claude Code plugin that lets non-developers build Frappe apps correctly — DocTypes, Workflows, Dashboards, Reports — via guided slash commands. Two-way GitHub sync. Best-practice guardrails baked in at every layer.</p>

[Walkthrough →](walkthroughs/01-first-doctype.md){ .md-button .md-button--primary }
[Architecture](architecture.md){ .md-button }
[GitHub :material-github:](https://github.com/dhwani-ris/frappe-stack){ .md-button }

</div>

## What it does

<div class="grid cards" markdown>

-   :material-form-textbox:{ .lg .middle } **Build forms in plain English**

    ---

    PMs type *"I need a beneficiary registration form"* — engineer agent walks fields, permissions, validation. DocType lives on staging in five minutes.

    [:octicons-arrow-right-24: First DocType walkthrough](walkthroughs/01-first-doctype.md)

-   :material-source-branch-sync:{ .lg .middle } **Two-way GitHub sync**

    ---

    Site changes mirror to git automatically (`/pull`). Production is git-only — promotion via PR (`/promote`). The audit trail *is* git history.

    [:octicons-arrow-right-24: Architecture](architecture.md)

-   :material-shield-check:{ .lg .middle } **Guardrails at every layer**

    ---

    Refuses `ignore_permissions=True`, `allow_guest=True`, f-string SQL, hardcoded role checks, real PII in prompts. Defense in depth across plugin / API / DB / CI.

    [:octicons-arrow-right-24: Hooks catalog](hooks.md)

-   :material-flask:{ .lg .middle } **A/B in workflows**

    ---

    Split states route documents deterministically by `hash(experiment_id ‖ doc.name)`. Outcomes tracked. Promote the winner with one command.

    [:octicons-arrow-right-24: First experiment walkthrough](walkthroughs/03-first-experiment.md)

-   :material-school-outline:{ .lg .middle } **Coaching at typing time**

    ---

    Vague asks get nudged to the right slash command. Risky asks get blocked with reasons. Real PII in prompts is refused before Claude sees it.

    [:octicons-arrow-right-24: Prompt coaching](hooks.md)

-   :material-book-multiple:{ .lg .middle } **17 skills, 8 agents, 9 commands**

    ---

    Each is a markdown file with explicit triggers and refusals. PMs use them implicitly; reviewers can audit them directly.

    [:octicons-arrow-right-24: Reference](skills.md)

</div>

## Reference

<div class="grid cards" markdown>

-   **[Skills](skills.md)** — 17 skills the engineer agent loads. Building (forms / workflows / dashboards / reports / integrations / experiments). Shipping (git roundtrip / promotion). Process (specs / triage / QA / coaching). Platform background.

-   **[Agents](agents.md)** — 8 agents (engineer / reviewer / tester / deployer / analyst / migrator / documenter / orchestrator). Each pairs with the others according to a documented routing chart.

-   **[Commands](commands.md)** — 9 slash commands (`/init` / `/build` / `/pull` / `/push` / `/diff` / `/promote` / `/experiment` / `/review` / `/ship`). Each refuses on specific conditions.

-   **[Hooks](hooks.md)** — 8 hooks across 4 lifecycle events. Block dangerous bash, prod-API writes, permission bypass, credential leaks, f-string SQL. Coach vague prompts.

</div>

## Tutorials

<div class="grid cards" markdown>

-   **[1. First DocType](walkthroughs/01-first-doctype.md)** — Build a Beneficiary form in 10 minutes.

-   **[2. First Workflow](walkthroughs/02-first-workflow.md)** — 3-stage approval flow.

-   **[3. First Experiment](walkthroughs/03-first-experiment.md)** — A/B test approval paths.

-   **[4. First Promotion](walkthroughs/04-first-promotion.md)** — Staging → prod via PR.

</div>

## For operators

<div class="grid cards" markdown>

-   **[Installing stack_core](operators/installing-stack-core.md)** — bench install, site_config, role setup, smoke test.

-   **[Rotating keys](operators/rotating-keys.md)** — 90-day rotation per credential type. Incident protocol.

</div>

## Project status

v0.1.0 scaffold complete — all 9 phases written + committed.
**Pending validation:** bench smoke-test, plugin install smoke-test in a clean Claude Code session, `infra/` (deferred per D-09).

See [HEARTBEAT](HEARTBEAT.md) for the live phase tracker and [PLAN](PLAN.md) for the decision register.
