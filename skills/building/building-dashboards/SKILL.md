---
name: building-dashboards
description: Use when a PM asks for a dashboard, chart, KPI tile, or summary view. Builds Frappe Number Card + Chart + Dashboard fixtures. Triggers on phrases like "show me a dashboard", "chart of…", "KPI", "summary view", "by month / by district".
---

# Building dashboards

Frappe ships Number Cards, Charts, and Dashboards. They're DocTypes themselves — that means we ship them as fixtures, version them in git, and the differ catches drift.

## What a dashboard is, mechanically

```
Dashboard ─┬─ Dashboard Chart 1 (line / bar / pie / heatmap)
           ├─ Dashboard Chart 2
           └─ Number Card 1 / 2 / 3 (single-value KPI tiles)
```

Each chart and card has:
- A **document_type** — what's it counting?
- A **filters** JSON — which rows count?
- An **aggregate function** — count / sum / average / min / max
- A **group_by** field — for charts, the X-axis or slice key.

## Conversation flow

### Step 1. What question does the dashboard answer?

PMs often jump to "show me a bar chart by district". Push back: *what decision* does the chart support? If they can't say, the dashboard is decoration.

### Step 2. Identify the source DocType(s)

One Dashboard can span multiple DocTypes (one chart per DocType). Confirm each one exists and the user has permission to read it (the dashboard inherits the viewer's permissions — admin sees all, field officer sees their rows).

### Step 3. Cards first, charts second

Number Cards are cheap — single SQL aggregate. Always start with 3–5 cards (totals, this-month, pending-approval, …) before building charts. PMs often realize they don't need the chart once the cards answer the question.

### Step 4. Build the fixture set

```json
{
  "dashboard_name": "Beneficiary Operations",
  "module": "Custom",
  "is_default": 0,
  "charts": [
    {
      "chart_name": "Beneficiaries by District",
      "document_type": "Beneficiary",
      "type": "Bar",
      "based_on": "district",
      "value_based_on": "name",
      "aggregate_function": "count",
      "filters_json": "[]"
    }
  ],
  "cards": [
    {
      "card_name": "Total Beneficiaries",
      "document_type": "Beneficiary",
      "function": "Count",
      "filters_json": "[]"
    },
    {
      "card_name": "Pending Approval",
      "document_type": "Beneficiary",
      "function": "Count",
      "filters_json": "[[\"workflow_state\", \"=\", \"Submitted\"]]"
    }
  ]
}
```

### Step 5. Permission-check the source

Every chart/card runs on the viewer's permission. If a Field Officer opens this dashboard, they only see *their* rows. If you've designed for an aggregate that needs admin scope (e.g., total across all districts), say so and either:

- Restrict the dashboard to System Manager + Stack Admin, or
- Build a Server Script that aggregates with `ignore_permissions=True` *and* has a permission check at the start (only admins call it). Document the why.

## Anti-patterns

- **Dashboard with 20+ charts** — cognitive overload, slow to render. Cap at 6.
- **Real-time charts on million-row tables** — Frappe Charts re-runs the SQL on each load. Cache via `frappe.cache().get_value` with a 5-minute TTL or precompute via scheduled job.
- **Filters embedded in chart that should be parameters** — use Dashboard Chart's date-range parameter so users can re-scope without editing the fixture.

## India Map pattern (when needed)

PM asks: "Show beneficiaries per state on a map of India."

Frappe doesn't ship a map widget. Use the `india-map` pattern in [`frappe-patterns`](../../platform/frappe-patterns/SKILL.md) (added when the catalog grows). The pattern:

- Aggregates count per state via a Frappe Report.
- Renders as an SVG choropleth client-side.
- Color-scale generated from min/max in the data.
- Click-through to filtered list view.

Until the pattern is in the catalog, fall back to a Bar chart by state with `group_by: state`.
