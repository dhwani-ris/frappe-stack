---
name: composing-reports
description: Use when a PM asks for a report, export, list with filters, or printable summary. Picks the right report type (Report Builder vs Query vs Script) and emits the fixture. Triggers on phrases like "report on…", "export this list", "summary of…", "give me a CSV of…".
---

# Composing reports

Frappe has three report types. Picking the wrong one wastes hours. The decision tree:

| Need | Report Type | Why |
|---|---|---|
| Filter + sort one DocType, no joins, no calculations | **Report Builder** | UI-only, ships as a fixture, zero code |
| Joins across DocTypes, custom calculations, aggregates | **Query Report** | Raw SQL, runs on the server, exports cleanly |
| Conditional rendering, runtime business logic, charts in same view | **Script Report** | Python builds the columns + rows |

## Report Builder (the default — try this first)

Built in the UI. Saved to `Report` DocType. Exports as a fixture. PMs can iterate on it without engineering involvement.

Tell the PM: *"Open the list view of Beneficiary, click Menu → Report Builder, drag the columns you want, save with a name. I'll export it as a fixture."*

Then `/frappe-stack:pull` picks it up automatically.

## Query Report (raw SQL — the workhorse)

When the PM needs joins or aggregates:

```python
# in the report's <name>.py:

def execute(filters=None):
    columns = [
        {"label": "Beneficiary",     "fieldname": "beneficiary",     "fieldtype": "Link", "options": "Beneficiary", "width": 200},
        {"label": "District",        "fieldname": "district",        "fieldtype": "Data",                            "width": 120},
        {"label": "Active Grants",   "fieldname": "active_grants",   "fieldtype": "Int",                             "width": 100},
        {"label": "Total Disbursed", "fieldname": "total_disbursed", "fieldtype": "Currency",                        "width": 140},
    ]
    data = frappe.db.sql(
        """
        SELECT b.name AS beneficiary,
               b.district,
               COUNT(g.name) AS active_grants,
               COALESCE(SUM(g.amount), 0) AS total_disbursed
        FROM `tabBeneficiary` b
        LEFT JOIN `tabGrant` g
          ON g.beneficiary = b.name
         AND g.docstatus = 1
         AND g.status = %(status)s
        WHERE b.district = %(district)s OR %(district)s = ''
        GROUP BY b.name
        ORDER BY total_disbursed DESC
        """,
        {
            "status": (filters or {}).get("status", "Active"),
            "district": (filters or {}).get("district", ""),
        },
        as_dict=True,
    )
    return columns, data
```

**Mandatory rules:**
- Always `%s` or named params (`%(name)s`). Never f-strings or `.format()`. Frappe ships semgrep rules that block this at PR.
- Every Query Report has a `permission_query_conditions` for the underlying DocType — the user only sees rows they're allowed to see.
- `docstatus = 1` filters submitted rows. PMs forget this and end up showing draft data in summaries.

## Script Report (last resort)

Use only when:
- Columns vary based on filters (e.g., dynamic month columns).
- You need to call other Python (e.g., compute a score with a model).
- The report shows a chart inline.

Same shape as Query Report's `execute`, but instead of returning SQL data you build the rows in Python. Always more code, harder to test — prefer Query Report.

## Performance guardrails

- Run `EXPLAIN` on every Query Report's SQL before shipping. If it scans > 100k rows, add an index (it's a fixture too).
- Reports that take > 5s to render are unusable. Cache via `frappe.cache().get_value` keyed on filter hash.
- Never `SELECT *`. List the columns you actually need.

## Export

All three report types support CSV/XLSX export out of the box. PM doesn't need a separate "export" feature — point them to the export icon on the report toolbar.
