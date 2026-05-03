---
name: builder-protocol
description: Use at the start of every project (or every long session) to establish the four memory-layer files that keep work disciplined and resumable. Triggers on phrases like "start a project", "init", "set up the protocol", "what files do I need".
---

# Builder Protocol

Memory-layer discipline. Four documents, written once, updated continuously. If you're building anything bigger than a one-off task, you need them.

## The four files

| File | Owns | Updated when |
|---|---|---|
| `CLAUDE.md` | Working memory for Claude Code sessions in this repo. Conventions, agents-to-use, rule precedence. | Rarely — only when conventions change |
| `PRD.md` | Product requirements: who, what, why. The *what* of the project. | When scope changes |
| `SECURITY.md` | Threat model + non-negotiable guardrails. The *must-not* of the project. | When a new attack surface is added |
| `HEARTBEAT.md` | Phase tracker. Newest entry on top. Current phase, what's done, what's blocked. | At every phase transition (and on session start, briefly) |

Plus a fifth, `PLAN.md`, for projects with > 1 phase: phased implementation, decision register, exit checkpoints.

## Why this works

- **You forget.** A long project pauses; weeks later, you need to know what was decided. The four files reload context faster than re-reading code.
- **Claude forgets.** Each session starts fresh. These five files = the smallest portable working memory.
- **Reviewers don't know.** They read the four files first; they don't have to read every commit.
- **Future-you is grateful.** "Why did we choose B+ hybrid?" — the decision register has the answer with a date and an owner.

## Order of precedence (when rules conflict)

1. `SECURITY.md` in the repo — strictest, always applies.
2. Global rules in `~/.claude/rules/<framework>/`.
3. Global rules in `~/.claude/rules/common/`.
4. `CLAUDE.md` in the repo — local conventions.
5. `PLAN.md` — phase order, do not skip.

Lower number wins.

## The CLAUDE.md template

```markdown
# CLAUDE.md — <repo name>

## What this repo is
<one paragraph>

## Pair this file with
- PRD.md / PLAN.md / SECURITY.md / HEARTBEAT.md (one-line each)

## Rules — order of precedence
1. SECURITY.md in this repo
2. ~/.claude/rules/<framework>/
3. ~/.claude/rules/common/
4. This file
5. PLAN.md

## Working notes
- Phase discipline rules
- Commit style
- When generating <framework> code: non-negotiables
- Agents to invoke: table
- Skills to invoke: table

## Owners (TBD until confirmed)
- Product / Eng / Security / Compliance
```

## The HEARTBEAT.md cadence

Each entry stamped with date + phase, *newest on top*. Three sections per entry:

- **Done** — what landed since the last stamp.
- **Blocked / pending** — what's stuck, with the question that would unblock it.
- **Next** — what's about to start.

Old entries are never deleted. Scrolling down = scrolling backward through time.

## Decision register (lives in PLAN.md)

| ID | Decision | Default | Owner | Status |
|---|---|---|---|---|
| D-01 | <thing to decide> | <proposed answer> | <who decides> | proposed / confirmed YYYY-MM-DD |

Decisions move from `proposed` → `confirmed` (with a date). They never get deleted; superseded ones get a strikethrough + new ID.

## When to update each

| File | Frequency |
|---|---|
| `CLAUDE.md` | Maybe once a quarter |
| `PRD.md` | When the *what* changes (rare in mid-project) |
| `SECURITY.md` | When a new threat is identified or a guardrail added |
| `HEARTBEAT.md` | Every phase transition; ideally also at the start of every session |
| `PLAN.md` | Every decision close; every checkpoint pass; never to remove old phases |

## Anti-patterns

- **Skipping HEARTBEAT for "I'll catch up later".** You won't.
- **Updating PRD instead of opening a new decision row.** PRD is the *current* state; how you got there belongs in `PLAN.md`'s decision register.
- **Long, narrative `CLAUDE.md`.** It's a working-memory cheat sheet, not a manual. If it grows past 200 lines, refactor.
- **Putting code in these files.** They reference code; they don't contain it.
