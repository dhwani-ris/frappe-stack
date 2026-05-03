---
name: managing-tickets
description: Use when a PM is triaging incoming requests, prioritizing a backlog, or scoping work into deliverables. Triggers on phrases like "what should we work on next", "prioritize this list", "triage", "backlog", "what's next".
---

# Managing tickets

PMs are the demand-shaping layer. This skill helps them sort signal from noise without building things that won't matter.

## The 4-bucket triage

Every incoming request goes into exactly one of:

| Bucket | Definition | Action |
|---|---|---|
| **Build now** | Clear problem, known user, fits the current sprint, success metric obvious | Run `writing-specs`, then `/frappe-stack:build` |
| **Build later** | Real problem but downstream of current focus, OR needs more discovery | Add to backlog with a 1-line summary; revisit at sprint planning |
| **Won't build** | Symptom of process not platform; or one user's edge case; or already solved by an existing pattern | Politely close; document why; link to the existing thing if applicable |
| **Investigate** | Sounds like a real problem but the actual root cause is unclear | Pair with the requester for 30 min; might collapse into one of the above |

## Triage questions (force every requester to answer)

1. **Who is affected?** (role, count — "all field officers", "1 manager")
2. **How often?** (daily, weekly, monthly)
3. **What's the current workaround?** (paper, Excel, calling someone)
4. **What breaks if we don't fix it?** (revenue lost, errors made, time wasted)

A request that can't answer all 4 → "Investigate" or "Won't build". No exceptions.

## Prioritization (when the backlog is too long)

For the "Build later" bucket, sort by **impact / effort**:

- **Impact** = (users affected) × (frequency) × (severity per occurrence). Use a 1–5 scale on each, multiply.
- **Effort** = days to ship a v1 (not perfect). Use the engineer agent's PLAN.md-style phase estimate.

Top of the list = highest impact / lowest effort. PMs often gravitate toward "interesting" — push back to "highest leverage."

## Sprint sizing

A sprint is two weeks. A non-developer PM running this stack should ship roughly:

- 1–2 new DocTypes (with workflows + dashboards) per sprint, OR
- 3–5 enhancements to existing DocTypes, OR
- 1 integration

If the sprint plan is denser than that, force a cut — under-promise, over-deliver, never the reverse.

## Ticket templates

### Bug

```markdown
**Title**: <one line, no jargon>
**Affected**: <role + rough count>
**Frequency**: <daily / weekly / monthly>
**Reproduction**:
1. ...
2. ...
3. Expected: ...
4. Actual: ...

**Workaround**: <if any>
**Severity**: <1: cosmetic, 2: annoying, 3: blocking, 4: data loss>
```

### Feature

```markdown
**Title**: <one line>
**Affected**: <role + rough count>
**Frequency**: <how often will they use it>
**Problem** (1 paragraph, written before any solution):
**Proposed solution** (bullets, max 5):
**Out of scope** (always force this):
**Success metric**:
**Effort estimate**: <S / M / L / XL>
```

## Anti-patterns

- **"Just one more field" syndrome.** Each field added to a DocType doubles the form's cognitive load. Always ask: "is this field used in the next 3 months by 80%+ of users?"
- **Building because someone important asked.** If the request fails the 4 triage questions, it fails — title doesn't override math.
- **Sprint commitments without slack.** Reserve 20% capacity for incidents, follow-ups, and surprises. Filling the sprint to 100% guarantees missing the deadline.
