---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

<span class="status-pill">v0.1.0 · ready to explore</span>

# Build Frappe apps without writing code

<p class="tagline">frappe-stack is a Claude Code plugin for product managers and analysts. Describe what you need in plain language; the plugin generates the DocType, Workflow, Dashboard, or Report and applies it to your staging Frappe site. Every change is mirrored in GitHub automatically.</p>

[Try the first tutorial →](walkthroughs/01-first-doctype.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/dhwani-ris/frappe-stack){ .md-button }

</div>

## What you can do

<div class="grid cards" markdown>

-   :material-form-textbox:{ .lg .middle } **Ship a form in five minutes**

    *"I need a beneficiary registration form."* The plugin walks you through fields and permissions, validates the result, and the form is live on staging — no Python, no JSON.

    [Read the walkthrough →](walkthroughs/01-first-doctype.md)

-   :material-source-branch-sync:{ .lg .middle } **Stay in sync with GitHub**

    Site changes mirror to your config repository the moment you save. Production updates arrive through pull requests, so every change has a reviewer and a clear audit trail.

    [How the sync works →](architecture.md)

-   :material-flask:{ .lg .middle } **A/B test approval paths**

    Compare two workflow routes side-by-side. The plugin assigns documents deterministically, tracks outcomes, and promotes the winning path with one command.

    [Run an experiment →](walkthroughs/03-first-experiment.md)

-   :material-shield-check:{ .lg .middle } **Stay safe by default**

    The plugin refuses unsafe configurations before they ship — permission bypasses, SQL injection patterns, hardcoded credentials, sensitive data in prompts. You build correctly because the system makes correct the easy path.

    [See the safeguards →](hooks.md)

</div>

## Install in two commands

Inside a Claude Code session:

```text
/plugin marketplace add https://github.com/dhwani-ris/frappe-stack.git
/plugin install frappe-stack@frappe-stack
```

On any Frappe v15+ site you want to manage, install the support app once:

```bash
bench get-app stack_core /path/to/frappe-stack/apps/stack_core
bench --site <sitename> install-app stack_core
```

The full setup guide is in [Installing stack_core](operators/installing-stack-core.md).

## Where to next

<div class="grid cards" markdown>

-   **[Tutorials](walkthroughs/01-first-doctype.md)** — Four short walkthroughs. Each takes ten minutes.

-   **[Architecture](architecture.md)** — The data flow between your machine, your site, and GitHub.

-   **[Reference](skills.md)** — Every skill, agent, slash command, and safeguard, with examples.

</div>

---

<small>v0.1.0 ships the complete scaffold: 17 skills, 8 agents, 9 slash commands, 8 safeguards, and the `stack_core` Frappe app. Tests are written; runtime smoke-tests are next. Track progress in [HEARTBEAT](HEARTBEAT.md).</small>
