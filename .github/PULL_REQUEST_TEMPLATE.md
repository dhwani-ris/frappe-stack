<!--
Thanks for contributing! Fill out the sections below — the maintainer
runs the reviewer + tester agents against this PR before merging.
-->

## Summary

<!-- 1–3 bullets. What does this PR change and why? -->

-

## Type of change

- [ ] feat — new capability
- [ ] fix — bug fix
- [ ] refactor — no behavior change
- [ ] docs — documentation only
- [ ] test — tests only
- [ ] chore — tooling / housekeeping
- [ ] perf — performance
- [ ] ci — CI / build pipeline

## Scope

- [ ] skill: `skills/<…>/SKILL.md`
- [ ] agent: `agents/<…>.md`
- [ ] command: `commands/<…>.md`
- [ ] hook: `hooks/hooks.json` + `.claude-plugin/hook_scripts/<…>.py`
- [ ] docs / Builder Protocol files
- [ ] other

## Test plan

<!-- How did you verify this works? Bullet list of TODOs the reviewer can check off. -->

- [ ]
- [ ]

## Reviewer + tester output

<!-- Paste output (or attach as a comment). For now this is manual; CI will
auto-run when infra/ lands. -->

```
reviewer: <CRITICAL / HIGH / MEDIUM / LOW counts>
tester:   <pass count / coverage>
```

## Security checklist (mandatory for hooks, generated configs, Server Scripts)

- [ ] No `ignore_permissions=True`
- [ ] No `allow_guest=True` without explicit security review
- [ ] No f-string / `.format()` / `%` SQL — parameterized only
- [ ] No hardcoded role-name string checks
- [ ] No hardcoded credentials / API keys / tokens
- [ ] Every new `@frappe.whitelist()` calls `frappe.has_permission()` first
- [ ] Every new mutation API uses the `@audited` decorator
- [ ] Every new DocType has `track_changes=1` if it stores business data

## Docs updated

- [ ] `docs/<catalog>.md` reflects the new surface (if applicable)
- [ ] `CHANGELOG.md` entry added under `[Unreleased]`
- [ ] `HEARTBEAT.md` stamped if this closed a phase / decision

## Closes / refs

<!-- Issue numbers. -->

Closes #
