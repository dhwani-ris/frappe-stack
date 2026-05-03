# Walkthrough 2 — Your first workflow

**Audience:** PM with a DocType (e.g., Beneficiary from Walkthrough 1) ready for an approval flow.
**Time:** ~10 minutes.
**Prerequisites:** Walkthrough 1 completed.

## Goal

Add a 3-stage approval flow: Field Officer submits → Program Officer reviews → Manager approves or rejects.

## Step 1 — Tell Claude what you want

```text
/frappe-stack:build workflow "Beneficiary Approval"
```

The `engineer` loads [`modeling-workflows`](../../skills/building/modeling-workflows/SKILL.md).

## Step 2 — Define states

Engineer asks: *what states does a Beneficiary go through?*

You answer:

- `Draft` (Field Officer)
- `Submitted` (Field Officer)
- `Reviewed` (Program Officer)
- `Approved` (Manager) — terminal
- `Rejected` (Manager) — terminal

The validator will refuse if:
- No terminal state exists
- A state has no role
- Any state isn't reachable from the initial state

## Step 3 — Define transitions

Engineer asks: *who can move what to where, with what action?*

| From | To | Action | Role |
|---|---|---|---|
| Draft | Submitted | Submit | Field Officer |
| Submitted | Reviewed | Review | Program Officer |
| Reviewed | Approved | Approve | Manager |
| Reviewed | Rejected | Reject | Manager |

## Step 4 — Confirm and apply

Engineer prints the workflow JSON. You confirm. API call goes through. Workflow is saved.

```text
Workflow Beneficiary Approval applied. is_active=0 (you'll need to activate manually).
```

## Step 5 — Activate and test

On the Frappe desk:

1. Go to `Stack Workflow Def` list, open `Beneficiary Approval`.
2. Toggle `is_active` to checked. Save.
3. Open any existing Beneficiary doc. The workflow toolbar appears.
4. Click `Submit` (you must have Field Officer role; if you're admin, you have all roles by default).
5. State transitions to `Submitted`. Try the other transitions.

## Step 6 — Pull + commit

```text
/frappe-stack:pull --commit
```

Writes `<config-repo>/fixtures/app/workflows/beneficiary_approval.json`. Locally committed.

## Common gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Workflow toolbar doesn't appear | `is_active=0` | Activate it |
| Transition button missing | User lacks the role | Assign role via Frappe User row |
| "Workflow validation failed: state Reviewed is unreachable" | Typo in transition `from`/`to` | Re-run `/frappe-stack:build`, fix the typo |
| Documents stuck in a state | No transition exits that state | Add a transition or mark the state as `terminal` |

## Next: [Walkthrough 3 — your first A/B experiment](./03-first-experiment.md)
