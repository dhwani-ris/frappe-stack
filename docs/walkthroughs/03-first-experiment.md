# Walkthrough 3 — Your first A/B experiment

**Audience:** PM who wants to test which approval path performs better.
**Time:** ~15 minutes setup + days of data collection.
**Prerequisites:** A workflow already exists (Walkthrough 2).

## Goal

Replace a single approval path with a split: 50% of submitted Beneficiaries go through the Manager (slow but careful), 50% auto-approve under a value threshold (fast). After 3 weeks, see which arm wins on cycle time and rejection rate.

## Step 1 — Frame the question

The `designing-experiments` skill forces you to write the question as:

> "At <Initial Review>, do documents that go via <Manager Approval> have a better/worse <cycle time + rejection rate> than documents via <Auto Approval>?"

If you can't write that sentence cleanly, the experiment isn't ready. Don't skip this step.

## Step 2 — Define the experiment

```text
/frappe-stack:experiment define exp_2026_05_fast_track
```

Engineer walks the [`designing-experiments`](../../skills/building/designing-experiments/SKILL.md) skill:

1. Target DocType: Beneficiary
2. Target workflow: Beneficiary Approval
3. Where does the split go? On exit from `Submitted`.
4. What's the split? 50/50 (default; you can change to e.g., 80/20 if rolling out cautiously).
5. What are the two arms?
   - `arm_a`: Manager Approval (existing path)
   - `arm_b`: Auto Approval (new path — terminal state with role System Manager)
6. What's the metric?
   - Primary: cycle_time_seconds (lower is better)
   - Secondary: outcome (rate of `approved` vs `rejected`)

Engineer prints the new workflow JSON. Confirm. API applied. Experiment is now live; new Submitted documents start being assigned.

## Step 3 — Watch it run

After a few days:

```text
/frappe-stack:experiment status exp_2026_05_fast_track
```

```text
Experiment exp_2026_05_fast_track   (started 2026-05-03, running 5 days)

  Assignments    arm_a: 47    arm_b: 51    total: 98
  Conversion     arm_a: 89.4% arm_b: 88.2%   diff: -1.2pp  95% CI [-13.1, +10.7]
  Cycle time     arm_a: 4.3h  arm_b: 1.1h    diff: -3.2h   95% CI [-3.8, -2.6]

  Verdict        cycle_time strongly favors arm_b.
                 Conversion difference is not significant — sample size too small.
                 Continue running until n ≥ 400 per arm.
```

Don't promote yet. Wait for sample size + clear signal.

## Step 4 — Promote when significant

After 3 weeks, suppose arm_b is clearly faster *and* has equivalent (or better) approval rate:

```text
/frappe-stack:experiment promote exp_2026_05_fast_track arm_b
```

This:
1. Builds a new Stack Workflow Def version with `arm_b`'s path replacing the split state.
2. Sets `experiment_status = Promoted B` on the old version.
3. Opens a PR against the config repo.
4. New Submitted documents follow the simplified path; in-flight documents continue under their assigned arm.

## Step 5 — Merge the PR

The deployer flow takes over. Reviewer + tester run on the simplified workflow. PR merged → `bench migrate` on prod → workflow updated. Old experiment data preserved in `Experiment Assignment` for the audit trail.

## What I refused to do

- Promote before n ≥ 100 per arm (under-powered).
- Promote when CI on the primary metric crosses 0 (not significant).
- Promote on Friday afternoon without `--emergency`.
- Drop the losing arm's existing Experiment Assignment rows (audit-log integrity).

## Common questions

| Q | A |
|---|---|
| Can I run two experiments at once? | On different workflows, yes. On the same workflow, no — assignment becomes ambiguous. |
| Can I change the split mid-run? | No. Doing so resets all existing assignments — bad analysis. End the experiment, define a new one. |
| What if a document gets stuck in arm_a? | Same as any stuck workflow — fix transitions, run `/frappe-stack:diff`, push. |
| Can I see which arm a specific doc is in? | Yes — every doc gets a `experiment_arm` Custom Field auto-added. Visible in the form. |

## Next: [Walkthrough 4 — your first promotion](./04-first-promotion.md)
