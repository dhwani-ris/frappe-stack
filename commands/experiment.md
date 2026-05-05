---
description: Define, monitor, or promote an A/B experiment in a workflow. Powers the designing-experiments skill end-to-end.
argument-hint: <action> [args]
---

# /frappe-stack:experiment

Subcommand-style:

| Action | Use |
|---|---|
| `define <experiment_id>` | Create a new experiment. Routes to engineer + designing-experiments skill. |
| `status <experiment_id>` | Show current numbers — assignments, conversions, cycle times, CI. |
| `pause <experiment_id>` | Stop new assignments. Existing in-flight docs continue. |
| `resume <experiment_id>` | Re-enable new assignments. |
| `promote <experiment_id> arm_a\|arm_b` | Strip the losing arm, open a PR with the simplified workflow. |
| `abandon <experiment_id>` | Mark experiment as abandoned. |

## How A/B is implemented (no custom Frappe app needed)

The plugin uses stock Frappe primitives:

- **Assignment** — a Custom Field `experiment_arm` on the target DocType, set by a Server Script that runs on workflow state change. The script computes a deterministic hash on `(experiment_id || doc.name)`.
- **Tracking** — a regular DocType called `Experiment Assignment` that the plugin creates on your site the first time you run `/frappe-stack:experiment define`. This is just a normal DocType — created via `POST /api/resource/DocType` like any other config.

## What each action does

### `define`

Walks the `designing-experiments` skill conversation. Outputs four config changes, each applied via stock Frappe REST:

1. The `Experiment Assignment` DocType (if not yet on your site) — `POST /api/resource/DocType`.
2. A Custom Field `experiment_arm` on the target DocType — `POST /api/resource/Custom Field`.
3. A Server Script on the target DocType's workflow `on_state_change` event that computes and stores the assignment — `POST /api/resource/Server Script`.
4. An updated Workflow with the split-state path — `PUT /api/resource/Workflow/<name>`.

PM confirms each before the plugin POSTs them.

### `status`

Routes to `analyst` agent. Returns:

```text
Experiment exp_2026_05_fast_track   (started 2026-05-03, running 18 days)

  Assignments    arm_a: 412    arm_b: 408    total: 820
  Conversion     arm_a: 87.4%  arm_b: 84.1%  diff: +3.3pp  95% CI [-0.7, +7.3]
  Cycle time     arm_a: 4.2h   arm_b: 6.8h   diff: -2.6h   95% CI [-3.1, -2.0]

  Verdict        cycle_time difference is significant; conversion is not.
```

### `promote`

```text
/frappe-stack:experiment promote exp_2026_05_fast_track arm_a
```

1. Generates a new Workflow JSON with the split state replaced by arm_a's path.
2. Updates the workflow on staging via `PUT /api/resource/Workflow/<name>`.
3. Opens a PR (via deployer flow). Existing in-flight docs continue under their assigned arm; new docs follow the simplified path.

## Refuses if

- `define` on a target DocType that doesn't have a Workflow yet.
- `promote` when the chosen arm has < 100 assignments.
- `promote` when the metric difference confidence interval crosses 0.
- `pause`/`resume` on an experiment in `Promoted A` / `Promoted B` / `Abandoned` status.

## Examples

```text
/frappe-stack:experiment define exp_2026_05_fast_track
/frappe-stack:experiment status exp_2026_05_fast_track
/frappe-stack:experiment promote exp_2026_05_fast_track arm_a
/frappe-stack:experiment abandon exp_2026_05_failed
```
