---
name: writing-specs
description: Use when a PM is starting a new feature and needs to write a spec before building. Forces a structured spec doc that the engineer agent can turn into blueprints. Triggers on phrases like "write a spec", "PRD for…", "scope this out", "what should we build", "requirements doc".
---

# Writing specs

PMs often jump from "I need this" to "build it". A spec slows them down by ~10 minutes and saves ~10 hours of rework.

## The 5-section template

Every spec the PM writes against this skill has exactly these sections in this order:

### 1. Problem (1 paragraph)

What is broken today? Who is affected? What does it cost (time / money / errors)?

Refuse if the PM writes "we need to build X" — that's a solution, not a problem. Push them back to the *symptom* the X solves.

### 2. User & job (1 paragraph)

Which user role experiences the problem? What are they trying to accomplish? Use *role* (Field Officer) not *person* (Ravi). Personas drift; roles persist.

### 3. Solution shape (bullets, not prose)

- 3–7 bullets describing the major pieces.
- Each bullet should map to one Stack Blueprint type (DocType / Workflow / Dashboard / Report / Custom Field / Property Setter).
- If a bullet doesn't map to one, push: either it needs to split, or it's actually two specs.

### 4. Out of scope (bullets)

What you are *not* building. PMs love to omit this — every omission means they'll be asked "but what about…" and have to defend the choice. Listing it upfront protects the timeline.

### 5. Success metric (1 line)

How will we know it worked? Concrete, measurable. "Field officers will find it useful" is not a metric. "Time-to-register a beneficiary drops from 14 minutes to under 5 minutes within 30 days of launch" is.

## Worked example

**Spec: Beneficiary Registration v1**

**1. Problem.** Field officers register beneficiaries on paper, then a back-office team re-types them into Excel. About 15% of records have data-entry errors that surface 2–4 weeks later as failed disbursements. Re-keying takes the back-office ~3 person-hours per day.

**2. User & job.** Field Officer registers a beneficiary while in the village; needs to enter name, village, age, Aadhaar, photo; needs to associate themselves as the registering officer.

**3. Solution shape.**
- DocType `Beneficiary` with the 5 fields above + `field_officer` Link to User.
- Workflow `Beneficiary Approval` (Field Officer submits → Program Officer reviews → Manager approves/rejects).
- Dashboard `Beneficiary Operations` with cards (total, pending, this-month) + bar chart by district.
- Custom Field on Grant: `field_officer` (auto-fill from Beneficiary).
- Notification: Manager pinged when state hits Reviewed.

**4. Out of scope.**
- Photo capture (deferred to v1.1; for now use Files area).
- Bulk import (deferred).
- Mobile UI customization (use default Frappe responsive).
- Multi-language UI (English-only at launch).

**5. Success metric.** Time-to-register drops from 14 min → under 5 min within 30 days of launch, measured via the workflow `cycle_time_seconds` field on Submitted state.

## Hand-off to engineer

Once the spec is approved, the PM (or engineer agent on their behalf) runs:

```text
/frappe-stack:build doctype Beneficiary
/frappe-stack:build workflow "Beneficiary Approval"
/frappe-stack:build dashboard "Beneficiary Operations"
...
```

Each command loads the relevant `building/*` skill, walks the conversation, and emits a blueprint.

## Anti-patterns

- **30-page specs.** This is not a govt RFP. Five sections, one page each at most.
- **"TBD" in success metrics.** No metric = no done. Refuse the spec.
- **Tech-stack opinions in section 3.** "Build with React" is not a solution shape. The platform is fixed (Frappe v15+); the spec describes *what*, not *how*.
- **Skipping out-of-scope.** Always force this section, even if it's "no constraints called out at this time."
