#!/usr/bin/env python3
"""UserPromptSubmit hook: coach PMs as they type.

Three response modes:
  - approve unchanged  (most prompts — say nothing, don't be annoying)
  - inject context     (gentle nudge — Claude sees the suggestion as system reminder)
  - block              (only for hard-no — refuses with a user-visible reason)

Default to approve. False positives are worse than missed nudges.

Patterns we coach (see SECURITY.md and PRD.md):
  - Vague build intent       -> suggest the matching slash command
  - Production write intent  -> redirect to /frappe-stack:promote
  - Permission bypass intent -> remind default-deny
  - Risky fieldtype intent   -> mention elevated-role gate + alternatives
  - Missing spec for feature -> nudge writing-specs skill
  - A/B intent w/o question  -> force the question format
Patterns we BLOCK (refuse, never coach away):
  - Real PII in prompt              (Aadhaar/PAN/phone)
  - Hard delete on stack_core data  (audit-tagged)
  - Force-merge / bypass-review     (compliance violation)
"""

from __future__ import annotations

import json
import re
import sys


# ----- BLOCK patterns ---------------------------------------------------

PII_AADHAAR = re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")
PII_PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
PII_PHONE_IN = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")

BLOCK_RULES: list[tuple[re.Pattern[str], str]] = [
    (
        PII_AADHAAR,
        "Real Aadhaar number detected in prompt. Use a synthetic value like '1111-2222-3333' "
        "or simply '<aadhaar>' as a placeholder. Real PII must never appear in prompts.",
    ),
    (
        PII_PAN,
        "Real PAN number detected in prompt. Use a synthetic value or '<pan>' as a placeholder.",
    ),
    (
        PII_PHONE_IN,
        "Real Indian mobile number detected in prompt. Use a synthetic value or '<phone>'.",
    ),
    (
        re.compile(r"\b(drop|truncate)\s+table\b", re.IGNORECASE),
        "Hard delete refused. Stack Audit Log and Experiment Assignment are append-only. "
        "Use status flags for soft-delete on user data.",
    ),
    (
        re.compile(r"\b(force[- ]merge|bypass(?:\s+the)?\s+review|skip(?:\s+the)?\s+review)\b",
                   re.IGNORECASE),
        "Reviewer + tester are non-negotiable before /frappe-stack:promote. "
        "Refusing per SECURITY.md §2.1.",
    ),
    (
        re.compile(r"\bgit\s+push\s+--?force\s+(?:.*\s+)?(main|master|develop|release/)",
                   re.IGNORECASE),
        "Force-push to a protected branch is refused. "
        "If history needs rewriting, open a separate revert PR.",
    ),
]


# ----- COACH patterns (inject context, don't block) --------------------

# Each entry: (pattern, context_to_inject)
# Context is appended as a system-reminder for Claude; the user does not see it.

COACH_RULES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"\b(make|build|create|add)\s+(?:a\s+)?(form|doctype|registration|intake|application)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] The user is asking to build a DocType in plain language. "
        "Suggest using `/frappe-stack:build doctype <Name>` so the engineer agent loads "
        "skills/building/designing-forms and walks them through fields + permissions correctly.",
    ),
    (
        re.compile(
            r"\b(make|build|create|add)\s+(?:a\s+)?(workflow|approval|approval flow|review flow)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User is asking for a workflow. Suggest "
        "`/frappe-stack:build workflow \"<Name>\"`. The modeling-workflows skill will walk "
        "states, transitions, and roles; the validator refuses bad shapes (no terminal, "
        "orphan states, traffic_split that doesn't sum to 100).",
    ),
    (
        re.compile(
            r"\b(make|build|create|add)\s+(?:a\s+)?(dashboard|chart|kpi|tile)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User is asking for a dashboard/chart. Suggest "
        "`/frappe-stack:build dashboard \"<Name>\"`. Push back: what decision does the "
        "chart support? If they can't say, the dashboard is decoration.",
    ),
    (
        re.compile(
            r"\b(make|build|create|add|export)\s+(?:a\s+)?(report|csv|export)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User is asking for a report. Suggest "
        "`/frappe-stack:build report \"<Name>\"`. The composing-reports skill picks the "
        "right report type (Report Builder vs Query Report vs Script Report).",
    ),
    (
        re.compile(
            r"\b(deploy|push|ship|release|move)\s+to\s+(prod|production|live)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User wants to push to production. Production is git-only "
        "(D-01 confirmed). The only path is `/frappe-stack:promote` which runs the full "
        "pre-promote checklist. NEVER suggest direct API writes to prod — those are blocked "
        "by the is_production guardrail anyway.",
    ),
    (
        re.compile(
            r"\b(no permissions|skip permissions|anyone can|public form|allow guest|allow_guest)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User is asking for permissionless access. Default-deny is "
        "the rule (SECURITY.md §2.2). Refuse to generate `allow_guest=True` or empty "
        "permissions. Minimum is System Manager + Stack Admin. If they truly need guest "
        "access for a public form, escalate to security review and use a rate-limited "
        "queue endpoint (see skills/building/wiring-integrations).",
    ),
    (
        re.compile(
            r"\b(code field|password field|attach field|signature field)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User is asking for an elevated fieldtype (Code / Password / "
        "Attach / Signature). The fieldtype_whitelist guardrail gates these to "
        "System Manager / Stack Admin. Either ask if they hold that role, or suggest the "
        "common alternatives: Long Text instead of Code, Markdown Editor instead of Code, "
        "Files area instead of Attach. Document the trade-off.",
    ),
    (
        re.compile(
            r"\b(rename|change\s+the\s+name\s+of)\s+(?:the\s+)?(field|column)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User wants to rename a field. Schema renames are HIGH risk — "
        "Frappe creates a new column and orphans the old data. Route to the migrator agent "
        "and force the add-new-column → patch-copies-data → wait-one-release → drop-old "
        "pattern. See agents/migrator.md.",
    ),
    (
        re.compile(
            r"\b(a/?b\s*test|split\s*test|experiment\s+with|compare\s+two)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User wants an A/B experiment. Before generating anything, "
        "force the designing-experiments question format: 'At <state>, do documents that "
        "go via <arm A> have a better/worse <metric> than via <arm B>?'. If they can't "
        "fill that in, the experiment isn't ready. Suggest /frappe-stack:experiment define.",
    ),
    (
        re.compile(
            r"\blet'?s\s+build\s+(?:the\s+)?\w+\s+feature\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User is starting a multi-blueprint feature without a spec. "
        "Suggest writing-specs skill first — the 5-section template (problem / user / "
        "solution-shape / out-of-scope / success-metric) prevents rework. Don't refuse, "
        "just nudge.",
    ),
    (
        re.compile(
            r"\b(install|add|set up|create)\s+(?:a\s+)?(webhook|integration)\b",
            re.IGNORECASE,
        ),
        "[frappe-stack coach] User wants an integration. Load skills/building/"
        "wiring-integrations. Three rules for inbound webhooks: signature verification, "
        "idempotency on event_id, minimum-work pre-auth handler that just queues.",
    ),
]


def main() -> int:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.stdout.write("{}")
        return 0

    prompt: str = (payload.get("prompt") or "").strip()

    # Slash commands are already structured — skip coaching.
    if prompt.startswith("/"):
        sys.stdout.write("{}")
        return 0

    # 1. Hard-block patterns first.
    for pattern, reason in BLOCK_RULES:
        if pattern.search(prompt):
            sys.stdout.write(json.dumps({
                "decision": "block",
                "reason": reason,
            }))
            return 0

    # 2. Coach patterns — collect any matches; concatenate into one context.
    nudges: list[str] = []
    for pattern, ctx in COACH_RULES:
        if pattern.search(prompt):
            nudges.append(ctx)

    if not nudges:
        sys.stdout.write("{}")
        return 0

    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n\n".join(nudges),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
