---
name: modeling-workflows
description: Use when a PM asks to add an approval flow, status transitions, multi-stage review, or any process with states. Walks them through states, transitions, roles, and emits a Frappe Workflow JSON payload posted via stock REST. Triggers on phrases like "needs approval", "multi-step", "submit for review", "workflow", "status changes".
---

# Modeling workflows

Frappe's built-in Workflow plus a small A/B extension that the plugin builds out of stock primitives (Custom Field + Server Script + a regular Experiment Assignment DocType). PMs describe a process; the engineer turns it into a validated workflow definition.

## Conversation flow

### Step 1. What's the target DocType?

The workflow attaches to one DocType. "Beneficiary registration approval" → target = `Beneficiary`. If the PM wants the same flow on multiple DocTypes, that's N workflows, not one.

### Step 2. List the states

Each state needs:
- **name** — past-tense participle ideally: "Submitted", "Approved", "Rejected".
- **type** — `normal` (transient), `terminal` (final), or `split` (A/B branching, see designing-experiments).
- **role** — who can drive a document INTO this state. This is non-negotiable; the workflow validator refuses any state without a role.

### Step 3. List the transitions

Each transition: `from`, `to`, `action` (button label), `role`. Optionally `condition` (Python expression evaluated on the doc).

### Step 4. Sanity-check before saving

The workflow_validator runs these checks; preview them to the PM:

- ✓ At least one terminal state exists.
- ✓ Every state is reachable from the initial state.
- ✓ Every state has a role.
- ✓ Every transition's `from` and `to` exist in the state list.

If any fail, refuse the build call and explain which check tripped.

### Step 5. Show, then build

Same pattern as designing-forms — render the full payload, get explicit confirmation, then `POST /api/resource/Workflow`.

## Worked example (linear approval)

PM: "Beneficiary registrations should go: Draft → Submitted by field officer → Reviewed by program officer → Approved or Rejected by manager."

Engineer:

```json
{
  "target_doctype": "Beneficiary",
  "states": [
    {"name": "Draft",     "type": "normal",   "role": "Field Officer"},
    {"name": "Submitted", "type": "normal",   "role": "Field Officer"},
    {"name": "Reviewed",  "type": "normal",   "role": "Program Officer"},
    {"name": "Approved",  "type": "terminal", "role": "Manager"},
    {"name": "Rejected",  "type": "terminal", "role": "Manager"}
  ],
  "transitions": [
    {"from": "Draft",     "to": "Submitted", "action": "Submit",  "role": "Field Officer"},
    {"from": "Submitted", "to": "Reviewed",  "action": "Review",  "role": "Program Officer"},
    {"from": "Reviewed",  "to": "Approved",  "action": "Approve", "role": "Manager"},
    {"from": "Reviewed",  "to": "Rejected",  "action": "Reject",  "role": "Manager"}
  ]
}
```

Validator: ✓ terminals (Approved, Rejected), ✓ all states reachable, ✓ all roles set.

## Anti-patterns I refuse

- **A workflow with no terminal state.** Documents loop forever and clutter dashboards.
- **A state with no role assigned.** No human can advance it; it's a black hole.
- **A transition referencing a state that doesn't exist** (typos). The validator catches this; surface it as a friendly error not a stack trace.
- **Cycles without exit paths.** "Draft → Review → Draft" with no Approved/Rejected outlet is broken.
- **Bypass-conditions hardcoded as `frappe.session.user == 'admin@…'`.** Use roles. Always.

## Common follow-ups (PM might ask)

| Ask | Answer |
|---|---|
| "Can a user reject and send it back?" | Add `from: Reviewed, to: Draft, action: Send Back, role: Program Officer` |
| "Email the manager when it hits Reviewed?" | Use Frappe Notification (separate fixture) — not part of workflow itself |
| "Can we A/B-test the approval path?" | Yes — escalate to `designing-experiments` skill |
| "Can it skip Reviewed if amount < 1000?" | Add `condition` field on the Submitted→Approved transition. Surface to user as Python expression on doc fields. |
