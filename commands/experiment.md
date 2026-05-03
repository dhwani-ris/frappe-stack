---
description: Define, monitor, or promote an A/B experiment in a workflow. Powers the designing-experiments skill end-to-end.
argument-hint: <action> [args]
---

# /frappe-stack:experiment

Subcommand-style:

| Action | Use |
|---|---|
| `define <experiment_id>` | Create a new experiment from intent. Routes to engineer + designing-experiments skill. |
| `status <experiment_id>` | Show current numbers — assignments, conversions, cycle times, CI. |
| `pause <experiment_id>` | Stop new assignments. Existing in-flight docs continue. |
| `resume <experiment_id>` | Re-enable new assignments. |
| `promote <experiment_id> arm_a\|arm_b` | Strip the losing arm, open a PR with the simplified workflow. |
| `abandon <experiment_id>` | Mark experiment as abandoned. Existing assignments stay in audit; new docs follow no experiment. |

## What each does

### `define`

Walks the `designing-experiments` skill conversation. Outputs a Stack Workflow Def with a split state. PM confirms; engineer calls `stack_core.api.workflow_builder.build` with `experiment_id` set.

### `status`

Routes to `analyst` agent. Returns:

```text
Experiment exp_2026_05_fast_track   (started 2026-05-03, running 18 days)

  Assignments    arm_a: 412    arm_b: 408    total: 820
  Conversion     arm_a: 87.4%  arm_b: 84.1%  diff: +3.3pp  95% CI [-0.7, +7.3]
  Cycle time     arm_a: 4.2h   arm_b: 6.8h   diff: -2.6h   95% CI [-3.1, -2.0]

  Verdict        cycle_time difference is significant; conversion is not.
                 Decide based on which metric you optimize.
```

### `promote`

```text
/frappe-stack:experiment promote exp_2026_05_fast_track arm_a
```

1. Loads the workflow definition.
2. Builds a new version with the split state replaced by arm_a's path.
3. Sets `experiment_status = Promoted A` on the old version.
4. Opens a PR (via deployer-style flow).
5. Existing in-flight documents continue under their assigned arm; new docs follow the simplified path.

## Refuses if

- `define` on a target DocType that doesn't have a Stack Workflow Def yet (build the workflow first).
- `promote` when the chosen arm has < 100 assignments (under-powered).
- `promote` when the metric difference confidence interval crosses 0 (not significant — would reverse the loser by chance ≥ 5% of the time).
- `pause`/`resume` on an experiment in `Promoted A`/`Promoted B`/`Abandoned` status.

## Examples

```text
/frappe-stack:experiment define exp_2026_05_fast_track
/frappe-stack:experiment status exp_2026_05_fast_track
/frappe-stack:experiment promote exp_2026_05_fast_track arm_a
/frappe-stack:experiment abandon exp_2026_05_failed
```
