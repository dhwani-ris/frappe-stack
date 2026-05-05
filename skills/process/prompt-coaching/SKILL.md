---
name: prompt-coaching
description: Reference for what the coach_user_prompt UserPromptSubmit hook does. Read this if you're surprised by an injected nudge or a blocked prompt; it lists every pattern the coach reacts to. Triggers on phrases like "why did it block my prompt", "what's coach_user_prompt", "why am I getting suggestions".
---

# Prompt coaching — what the UserPromptSubmit hook does

Every free-text prompt (anything that doesn't start with `/`) goes through `.claude-plugin/hook_scripts/coach_user_prompt.py` before Claude sees it. The hook does one of three things:

1. **Approve unchanged** — most prompts. The hook is silent.
2. **Inject coaching context** — adds a hidden `[frappe-stack coach] …` system reminder so Claude routes the work correctly. The user never sees this; only Claude does.
3. **Block** — refuses the prompt. The user sees the reason and re-types.

False positives are worse than missed nudges. The patterns are conservative.

## What gets BLOCKED (refused with reason)

| Pattern | Reason |
|---|---|
| Real Aadhaar (12-digit `nnnn nnnn nnnn`) | Real PII in prompts is forbidden. Use `<aadhaar>` placeholder. |
| Real PAN (`AAAAA9999A`) | Real PII in prompts is forbidden. Use `<pan>` placeholder. |
| Real Indian mobile (10-digit starting 6-9) | Real PII in prompts is forbidden. Use `<phone>` placeholder. |
| `DROP TABLE` / `TRUNCATE TABLE` | Hard-delete is policy-blocked. Use status flags for soft-delete on user data. |
| "force merge" / "bypass review" / "skip review" | Reviewer + tester are non-negotiable. |
| `git push --force <branch>` to main / master / develop / release | Refused for protected branches. |

## What gets COACHED (context injected)

| Phrase pattern | Nudge |
|---|---|
| "make/build a form / doctype / registration" | Suggests `/frappe-stack:build doctype <Name>` |
| "make/build a workflow / approval flow" | Suggests `/frappe-stack:build workflow "<Name>"` |
| "make/build a dashboard / chart / KPI" | Suggests `/frappe-stack:build dashboard …` + push for the decision the chart supports |
| "make/build a report / csv export" | Suggests `/frappe-stack:build report …` + the report-type decision tree |
| "deploy to prod" / "push to production" | Redirect to `/frappe-stack:promote` (prod is git-only) |
| "no permissions" / "anyone can" / "public form" / "allow_guest" | Default-deny reminder; refuse `allow_guest=True` |
| "Code / Password / Attach / Signature field" | Elevated fieldtype gate; suggest alternatives |
| "rename the field" / "change the name of the column" | Route to migrator agent; force the patch sequence |
| "A/B test" / "split test" / "compare two" / "experiment with" | Force the question format; suggest `/frappe-stack:experiment define` |
| "let's build the X feature" | Nudge `writing-specs` skill first |
| "set up a webhook" / "add an integration" | Load `wiring-integrations` skill rules (signature, idempotency, minimum-work) |

## Why a hook and not just better skill descriptions

Skills only fire when the engineer agent loads them. The user's typed prompt happens *before* any agent. Without the UserPromptSubmit hook, a vague PM ask reaches the model uncoached and gets a plausible-but-suboptimal answer (no slash command, no skill, no guardrail).

The hook closes that gap.

## How to silence a false positive

If a coach rule is over-firing on legitimate prompts:

1. Open `.claude-plugin/hook_scripts/coach_user_prompt.py`.
2. Tighten the regex (more specific) or move the entry to a stricter list.
3. Run the existing repo regression tests (when added in `tests/hooks/test_coach.py` — TODO).
4. Don't disable the hook entirely — surface the regex change in the PR.

## What it does NOT do

- Detect risk in *file content* (that's `block_credential_leak.py` and `block_ignore_permissions.py` PreToolUse hooks).
- Detect risk in *bash commands* (that's `block_dangerous_bash.py` and `block_direct_prod_api.py`).
- Time-based gates (Friday-afternoon promote rule lives in the deployer agent, not here — too time-dependent for a regex hook).
- Personalize per user. Coaches everyone the same way; defer per-user tuning to v0.2+.
