# Testing safely

How non-developer builders test their work the same way developers do — without writing test code by hand, and without leaking real data into the test path.

## The four layers

A change you make through the plugin should pass all four before promoting:

<div class="grid cards" markdown>

-   :material-play-circle-outline:{ .lg .middle } **1 · Dry-run**

    `/frappe-stack:build doctype Beneficiary --dry-run`

    Generates the JSON, runs validators, shows the diff against staging — **does not POST**. The same way a developer trial-runs a fixture before `bench migrate`.

-   :material-database-clock:{ .lg .middle } **2 · Seed test data**

    The [`seeding-data`](../skills/building/seeding-data/SKILL.md) skill generates synthetic records via stock REST. Refuses real-shaped PII (real-looking Aadhaar / PAN / mobile patterns). Cleanup helper produces a ledger of created records for later removal.

-   :material-clipboard-check-outline:{ .lg .middle } **3 · Smoke-test**

    The [`running-qa`](../skills/process/running-qa/SKILL.md) skill walks a manual checklist per blueprint type (DocType / Workflow / Dashboard / Report / Integration). The `tester` agent additionally runs any auto-generated FrappeTestCase tests via `bench run-tests`.

-   :material-source-pull:{ .lg .middle } **4 · Pre-promote review**

    The `deployer` agent runs `reviewer` (security + style) and `tester` (auto + coverage) in parallel before opening the PR. Reports are auto-commented on the PR before the rotation is tagged. Same standard a developer's PR has to meet.

</div>

## Where each layer fires

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#F5E6DD',
    'primaryTextColor': '#2E2E2E',
    'primaryBorderColor': '#8B1E24',
    'lineColor': '#9E2A2F',
    'secondaryColor': '#E7C1AD',
    'tertiaryColor': '#ffffff',
    'fontFamily': 'Inter, system-ui, sans-serif',
    'fontSize': '13px'
  }
}}%%
flowchart LR
    Idea[PM intent]
    Dry["1 · Dry-run<br>--dry-run"]
    Build["/frappe-stack:build"]
    Seed["2 · Seed data<br>seeding-data skill"]
    QA["3 · Smoke-test<br>running-qa skill<br>+ tester agent"]
    Promote["/frappe-stack:promote"]
    Review["4 · Pre-promote review<br>reviewer + tester<br>auto-commented on PR"]
    PR{PR opens}

    Idea --> Dry --> Build --> Seed --> QA --> Promote --> Review --> PR

    classDef step fill:#F5E6DD,stroke:#8B1E24,stroke-width:1.5px,color:#2E2E2E,rx:10,ry:10
    classDef cmd fill:#ffffff,stroke:#8B1E24,stroke-width:1.5px,color:#2E2E2E
    classDef gate fill:#F28C38,stroke:#9E2A2F,stroke-width:1.5px,color:#ffffff
    classDef plain fill:#ffffff,stroke:#D9B3A0,stroke-width:1px,color:#6B6B6B
    class Dry,Seed,QA,Review step
    class Build,Promote cmd
    class PR gate
    class Idea plain
```

## Why this is dev-equivalent

A developer doing the same work would:

| Developer step | Plugin equivalent |
|---|---|
| Edit a fixture, eyeball the JSON | `--dry-run` shows the JSON + diff |
| Run `bench migrate` on local | `/frappe-stack:build` POSTs to staging |
| Insert test rows via console / `import-csv` | `seeding-data` skill |
| Run `bench run-tests --app <app>` | `tester` agent runs the same |
| Run `pre-commit` (semgrep, lint) | `reviewer` agent runs the same checks |
| `gh pr create`, self-review, then request review | `/frappe-stack:promote` does this and auto-comments the report |
| `git checkout <ref> && bench migrate` to roll back | `/frappe-stack:rollback <ref>` |

Same standards, same checks, different surface. The PM never writes Python; they get the same coverage gate.

## The PII boundary

Test data **must not** look like real data. The plugin enforces this at three layers:

1. **Typing time.** The `coach_user_prompt.py` UserPromptSubmit hook blocks real Aadhaar / PAN / Indian mobile patterns in PM prompts.
2. **Seeding time.** The `seeding-data` skill refuses to generate real-shaped PII even when asked. Synthetic Aadhaar starts with `0000` (real Aadhaar can't); synthetic phone never matches `[6-9]\d{9}`.
3. **Pre-promote.** The `reviewer` agent's semgrep rules catch any literal PII pattern that slipped through into a fixture or Server Script.

## Failure modes

| Failure | What surfaces |
|---|---|
| Dry-run shows a destructive diff (e.g., a field would be removed and rows have data) | Refuses to proceed; PM has to acknowledge the data loss explicitly or change the design |
| Seeding into a DocType with required `Link` to an empty linked DocType | Refuses; surfaces "seed the linked DocType first" |
| `tester` agent finds < 80% coverage on changed lines | Build is **not** blocked, but the deployer's pre-promote checklist refuses without `--emergency` |
| Real PII pattern found in the seeded data ledger | Refuses; cleanup procedure runs to remove the contaminated rows |
| Rollback target ref doesn't have a `fixtures/app/` tree | Refuses; surfaces "this commit predates the config-repo layout" |

## Quick reference

```text
# Try a design without committing to it
/frappe-stack:build doctype Beneficiary --dry-run

# Build for real
/frappe-stack:build doctype Beneficiary

# Fill it with synthetic data
(engineer agent loads seeding-data skill on demand)

# Run the QA checklist
(running-qa skill walks you through it; tester agent runs auto-tests)

# Pre-promote review (auto-runs inside /promote, but you can run it standalone)
/frappe-stack:review --since=origin/main

# Promote
/frappe-stack:promote

# If something goes wrong on staging, rewind
/frappe-stack:rollback HEAD~1
```
