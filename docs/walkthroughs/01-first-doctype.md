# Walkthrough 1 — Your first DocType

**Audience:** PM / Analyst building their first form in frappe-stack.
**Time:** ~10 minutes.
**Prerequisites:** `/frappe-stack:init` completed against a staging site.

## Goal

Build a simple `Beneficiary` DocType with 5 fields, save it on staging, and commit it to git.

## Step 1 — Tell Claude what you want

In Claude Code, type:

```text
/frappe-stack:build doctype Beneficiary
```

The `engineer` agent loads the [`designing-forms`](../../skills/building/designing-forms/SKILL.md) skill and starts asking you questions.

## Step 2 — Answer the questions

The engineer walks you through:

1. **What is this form about?**
   - Name: `Beneficiary` ✓
   - Module: leave as `Custom`
   - Naming: pick *Auto-numbered* (`BENF-2026-00001`-style)

2. **What fields?**
   - `full_name` (Data, required, in list view)
   - `village` (Data, in list view)
   - `age` (Int)
   - `aadhaar_number` (Data, required, unique, length 12)
   - `field_officer` (Link to User, required, in list view)

3. **Who can see / edit?**
   - System Manager: full access
   - Stack Admin: read / write / create (no delete)

## Step 3 — Review the JSON

The engineer prints the full payload and asks:

> Ready to build? (yes/no)

Read it. Especially check `permissions` and `fields`. If something's wrong, say "no, change X" and the engineer iterates.

## Step 4 — Confirm

Say `yes`. The engineer calls Frappe's stock REST: `POST /api/resource/DocType`. Within seconds:

```text
Blueprint Beneficiary applied (status=Applied).
DocType created: https://staging.example.com/app/beneficiary

Auto-running reviewer + tester...
  reviewer: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 1 LOW (style)
  tester:   tests written (2 happy paths, 3 negative); coverage gate pending bench run.

Done. Run /frappe-stack:pull when ready to commit to git.
```

## Step 5 — See it on staging

Open `https://staging.example.com/app/beneficiary` in your browser. Click "+ New". Fill in the fields. Save. The doc gets `BENF-2026-00001`. Confirm it lands in the list view.

## Step 6 — Commit to git

```text
/frappe-stack:pull --commit
```

This:
1. Exports site state to `<config-repo>/fixtures/app/doctypes/beneficiary.json`.
2. Creates a local commit.
3. Doesn't push (you can `git push` manually, or run `/frappe-stack:promote` later to open a PR).

## What you just did

- Built a real DocType without writing Python or JSON by hand.
- Stack Blueprint row created with status=Applied, audit-log entry written.
- Guardrails (reserved name, fieldtype whitelist, permissions schema) all passed.
- Tests scaffolded; awaiting `bench run-tests` to confirm.
- Site state mirrored in git, ready for promotion.

## What's different from doing this in raw Frappe

| Raw Frappe | frappe-stack |
|---|---|
| Open Form Builder, drag fields, click Save | `/frappe-stack:build` walks you, refuses bad inputs upfront |
| Manually run `bench export-fixtures` to capture | `/frappe-stack:pull` does it per-blueprint |
| Hope you didn't accidentally name it `User` | Reserved-name guard refuses |
| No audit trail of who built what when | `Stack Audit Log` row + git history |
| Tests written later (or never) | Tests scaffolded automatically |

## Next: [Walkthrough 2 — your first workflow](./02-first-workflow.md)
