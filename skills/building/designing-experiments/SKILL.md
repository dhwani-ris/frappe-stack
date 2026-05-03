---
name: designing-experiments
description: Use when a PM wants to A/B-test a workflow path, compare approval routes, or measure which of two variants performs better. Triggers on phrases like "A/B test", "compare two flows", "split traffic", "experiment with…", "measure which variant…".
---

# Designing experiments (A/B in workflows)

stack_core extends Frappe Workflow with **split states**. Documents are deterministically routed into one of two arms; outcomes are tracked; once a winner is clear, the losing arm is stripped via `/frappe-stack:experiment promote`.

## When this is the right tool

- ✓ Measuring which approval path produces fewer rejections.
- ✓ Comparing fast-track auto-approval vs manual review for low-amount records.
- ✓ Testing whether an extra reviewer step adds value.
- ✗ Personalizing UI or copy — that's a different problem (use Frappe's translation system or feature flags).
- ✗ Testing form fields — change the form once you know what works; don't experiment in production data shapes.

## How assignment works

`hash(experiment_id || doc.name) → bucket 0..99`

Same document → same bucket → same arm, even if the workflow re-evaluates. Two arms only (binary split). 50/50 is the default; PMs can pick any split that sums to exactly 100.

## Conversation flow

### Step 1. What's the question?

Force the PM to write the question as: **"At <state>, do documents that go via <arm A> have a better/worse <metric> than documents via <arm B>?"**

If they can't write that sentence, the experiment isn't ready.

### Step 2. Pick the metric

The `Experiment Assignment` DocType records:
- `outcome` — approved / rejected / cancelled / expired (the categorical metric)
- `cycle_time_seconds` — assignment-to-terminal-state duration

You get **conversion rate per arm** and **cycle time per arm** for free. Anything richer (e.g., "post-approval grievance count") needs a custom field on Experiment Assignment + a hook that fills it.

### Step 3. Sample size sanity check

PM says "let's run for 2 weeks" — push back. The dashboard skill builds a small calculator (or use a back-of-envelope: at 50/50 split with 10% effect size you need ~400 docs per arm for 80% power). If they don't have ~800 documents in 2 weeks, the experiment will be inconclusive and they'll guess. Push for 4–6 weeks or wait until volume picks up.

### Step 4. Define the workflow with a split state

```json
{
  "target_doctype": "Beneficiary",
  "experiment_id": "exp_2026_05_fast_track",
  "states": [
    {"name": "Submitted", "type": "normal", "role": "Field Officer"},
    {
      "name": "Initial Review",
      "type": "split",
      "role": "System Manager",
      "traffic_split": {"arm_a": 50, "arm_b": 50},
      "next_states": {
        "arm_a": "Manager Approval",
        "arm_b": "Auto Approval"
      }
    },
    {"name": "Manager Approval", "type": "terminal", "role": "Manager"},
    {"name": "Auto Approval",    "type": "terminal", "role": "System Manager"}
  ],
  "transitions": [
    {"from": "Submitted",        "to": "Initial Review",    "action": "Submit",  "role": "Field Officer"},
    {"from": "Initial Review",   "to": "Manager Approval",  "action": "Route",   "role": "System Manager", "condition": "experiment_arm == 'arm_a'"},
    {"from": "Initial Review",   "to": "Auto Approval",     "action": "Route",   "role": "System Manager", "condition": "experiment_arm == 'arm_b'"}
  ]
}
```

### Step 5. Promote a winner

After enough data:

```text
/frappe-stack:experiment promote arm_a
```

This:
1. Builds a new Stack Workflow Def version with the split state replaced by the winning path.
2. Sets `experiment_status = "Promoted A"` on the old definition.
3. Opens a PR against the config repo with the new workflow.
4. Existing in-flight documents continue under their assigned arm; new documents follow the promoted path.

## Anti-patterns

- **Changing the experiment_id mid-run.** Resets every existing assignment. Catastrophic for analysis.
- **Three or more arms.** v0.1 supports binary only. If they need three, run two sequential experiments.
- **Routing on user identity instead of doc.name hash.** "Half the field officers go path A" is a different experiment (cluster-randomized) and the simple hash function is wrong for it.
- **Promoting before significance.** Show the PM a confidence interval on the dashboard; if it crosses 0, hold.

## Dashboard companion

`/frappe-stack:build dashboard experiment_<exp_id>_dashboard` ships a default 4-panel dashboard:

- Cumulative assignments per arm (line)
- Conversion rate per arm with 95% CI (bar with error bars)
- Mean cycle time per arm (bar)
- Sample size + power achieved (number cards)

The dashboard reads from `Experiment Assignment` directly and updates as outcomes are recorded.
