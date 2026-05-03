---
name: running-qa
description: Use after a build to verify the site behaves as the spec says. Combines automated tests + a manual smoke-test checklist. Triggers on phrases like "QA this", "test the…", "smoke test", "verify it works", "check the build".
---

# Running QA

After every `/frappe-stack:build` (or chain of builds), QA must run before the change is considered done. The `tester` agent automates most of it; the manual smoke-test catches what tests miss (UI, layout, real-world flow).

## Layer 1 — automated tests

Per `~/.claude/rules/frappe/frappe-testing.md`:

```bash
bench --site staging run-tests --app stack_core --coverage
bench --site staging run-tests --app <user-app> --coverage
```

Pass criteria:
- ✓ All tests pass (zero failures, zero errors).
- ✓ Coverage on changed lines ≥ 80%.
- ✓ No deprecation warnings introduced.
- ✓ No `frappe.log_error` calls fired during normal-path tests.

If tests fail, do **not** smoke-test. Fix tests first.

## Layer 2 — Frappe semgrep

```bash
semgrep --config=https://github.com/frappe/semgrep-rules
```

Catches: `ignore_permissions=True`, `allow_guest=True` without review, f-string SQL, hardcoded role checks, raw `print()` statements with PII patterns. Pass criteria: zero CRITICAL / HIGH findings.

## Layer 3 — manual smoke-test (always)

For each blueprint type the PM built, run the matching checklist.

### DocType checklist

```
□ Open the list view as Administrator — list loads, all columns marked in_list_view appear.
□ Open the list view as a non-admin user — they see only rows they should see.
□ Click "+ New" — every reqd=1 field is starred; non-reqd fields are not.
□ Save with reqd fields blank — error message shown, save blocked.
□ Save with valid data — saves, redirects to the new doc, name auto-generated correctly.
□ Edit, save again — track_changes adds an entry to Activity Log.
□ Delete (if delete permitted) — succeeds; verify cascades didn't break anything.
□ Print format — opens, fields render, no Jinja errors.
□ Mobile viewport — form is usable; child tables don't overflow horizontally.
```

### Workflow checklist

```
□ A new doc starts in the initial state.
□ Each transition button appears only for users with the matching role.
□ Each action moves the doc to the correct state.
□ Email notifications fire if configured.
□ Documents in terminal states cannot be transitioned further.
□ Workflow state visible in list view (add as in_list_view custom field).
□ For experiments: assignment row created on entering split state; outcome captured on terminal.
```

### Dashboard checklist

```
□ Dashboard loads in < 3 seconds.
□ Cards show numbers; no "Error" placeholders.
□ Charts render with data; legends/axes labeled.
□ Filters work; date ranges adjust correctly.
□ As a restricted user, only their data appears.
```

### Report checklist

```
□ Default filters produce results.
□ All filter combinations work (try 3–4 random combos).
□ Empty result set renders cleanly (no "undefined").
□ CSV export contains the visible columns + the visible rows.
□ Sums / aggregates match a hand-calculated spot-check on 5 rows.
```

### Integration checklist (webhooks / external APIs)

```
□ Trigger the source event; confirm the webhook fires with correct payload.
□ External system confirms receipt.
□ For inbound webhooks: replay test (POST same payload twice → second is rejected as duplicate).
□ Network failure: external system down → graceful retry, no data loss.
□ Secret rotation: rotate the token; verify next call uses the new one without restart.
```

## QA report template

```markdown
# QA report — <feature name>

## Automated
- Unit tests:        14/14 ✓
- Integration tests: 6/6   ✓
- Coverage:          87%   ✓
- Semgrep:           0 H/C ✓

## Manual smoke-test
DocType Beneficiary:
- ✓ all 9 boxes
Workflow Beneficiary Approval:
- ✓ all 7 boxes
- ⚠️ Manager email notification fired but landed in spam — non-blocker, opening separate ticket
Dashboard Beneficiary Operations:
- ✓ all 5 boxes

## Issues
- (1 non-blocker, see above)

## Recommendation
✓ Ready to /frappe-stack:promote
```

## Anti-patterns

- **Skipping manual smoke-test "because tests passed".** Tests miss layout bugs, slow loads, role-gating mistakes.
- **QA on production.** Always staging. Always.
- **"It works on my machine".** Run on the staging Docker compose, not local bench. The smoke-test is environment-truth, not laptop-truth.
