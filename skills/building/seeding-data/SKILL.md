---
name: seeding-data
description: Use when a PM wants to test a freshly-built form or workflow with realistic synthetic data — multiple records, dates, edge cases. Generates synthetic records via stock POST /api/resource. Refuses real PII patterns. Triggers on phrases like "seed test data", "fill the form for testing", "create dummy records", "add sample data".
---

# Seeding test data

After a `/frappe-stack:build`, the PM has an empty DocType. Testing it manually means typing 10 records by hand. This skill generates synthetic records in seconds — and refuses anything that looks like real PII.

This is the equivalent of what a developer does with `bench --site test_site execute frappe.utils.data.create_test_records` or a custom `import-csv` step.

## When to use

- Right after a `/frappe-stack:build doctype` to populate test data for QA.
- Before running an A/B experiment to seed enough records for statistical significance.
- When demoing a new form to a stakeholder.

## When NOT to use

- On production sites (refused by the `is_production` guard anyway).
- For load testing — use a proper load tool, not this.
- To populate real customer data — never. The skill refuses real PII.

## Conversation flow

### Step 1. How many records?

Default: 10. Maximum without elevated approval: 100. Beyond that, the skill refuses — that's not testing, that's a load test or a data import, neither of which belongs here.

### Step 2. What field values?

For each field on the target DocType, the skill picks a generator:

| Frappe fieldtype | Default generator |
|---|---|
| `Data` (name-shaped) | Faker `name()` |
| `Data` (other) | Faker `word()` or paragraph by length |
| `Int` | Random integer respecting `non_negative` and any range |
| `Float` / `Currency` | Random float in a sensible range |
| `Date` | Random date in last 90 days |
| `Datetime` | Random datetime in last 90 days |
| `Select` | Random pick from `options` |
| `Link` | Random pick from existing records on the linked DocType (if any exist) — else refuses with a clear message |
| `Check` | 50/50 |
| `Email` | Faker `email()` against a fixed test domain (`@example.test`) |
| `Phone` | Synthetic — never a valid Indian mobile pattern |
| `Aadhaar`-shaped Data | Synthetic 12-digit starting with `0000` (Aadhaar never starts with 0–1) |

The PM reviews the generator picks. They can override per field.

### Step 3. Refuse real PII

Before generation, the skill scans any field marked sensitive (Aadhaar, PAN, phone) and confirms the generator outputs values that would *fail* a real-PII check. The same rules `coach_user_prompt.py` enforces at typing time.

If the PM explicitly asks for "realistic phone numbers in the test data," the skill **refuses** and explains why: real-shaped PII in test data leaks across logs, dashboards, and exports.

### Step 4. Generate and POST

```bash
for record in synthetic_records:
    POST /api/resource/<DocType> with the record body
```

Each POST is independent. Failures are surfaced; partial success is logged.

### Step 5. Cleanup helper

The skill writes a `.frappe-stack/seeded/<doctype>-<timestamp>.txt` file listing the names of every record it created. To clean up later:

```text
/frappe-stack:cleanup-seeded <doctype>-<timestamp>
```

(See `commands/cleanup-seeded.md` — companion command.)

## Anti-patterns

- **Real-shaped PII for "realism".** Refused. The same value will be filtered by every audit-log scan and every PII hook downstream — it's not actually realistic for test purposes.
- **Seeding 10,000 records on a small staging instance.** Refuses past 100. Use a proper data import path (and a developer).
- **Seeding into a DocType with required Link fields when no linked records exist.** Surfaces and asks the PM to seed the linked DocType first or override that field.
- **Seeding workflow-managed DocTypes without setting `workflow_state`.** Each record gets the initial state by default; the skill warns if the PM wants a different distribution and routes to the experiment skill if it's actually about A/B sampling.

## Pairs with

- [`running-qa`](../../process/running-qa/SKILL.md) — after seeding, run the QA checklist to verify the new DocType behaves correctly under realistic data shape.
- [`designing-experiments`](../designing-experiments/SKILL.md) — A/B experiments need ≥ 100 docs per arm; this skill is the fastest way to get there for testing the experiment plumbing (not for real-data analysis).
