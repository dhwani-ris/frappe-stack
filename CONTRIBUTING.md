# Contributing to frappe-stack

Thanks for considering a contribution. This is a Claude Code plugin + a Frappe support app, so contributions span markdown (skills / agents / commands / docs), JSON (hooks / DocType definitions / fixtures), and Python (`stack_core`).

## Quick orientation

Read these in order:

1. [`README.md`](./README.md) — what this is and what's in the box
2. [`docs/architecture.md`](./docs/architecture.md) — how the pieces fit
3. [`PRD.md`](./PRD.md) — what we're building and why
4. [`SECURITY.md`](./SECURITY.md) — non-negotiable guardrails
5. [`CLAUDE.md`](./CLAUDE.md) — order of precedence + working notes for Claude Code sessions

## Ground rules

- **Conventional commits**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`. Body explains *why*, not *what*.
- **One logical change per commit / PR.** Don't bundle phases, don't mix unrelated fixes.
- **No skipping hooks** (`--no-verify`) and no force-pushing protected branches.
- **Tests come first** for `stack_core` Python — RED → GREEN → REFACTOR. Coverage gate ≥ 80% on changed lines.
- **Security review** is mandatory for anything touching `apps/stack_core/api/`, `hooks/`, `.claude-plugin/hook_scripts/`, or any Frappe permission code. Use the `security-reviewer` agent or tag `@security-rotation`.
- **Don't bypass `SECURITY.md` non-negotiables.** No `ignore_permissions=True`, no `allow_guest=True` without review, no f-string SQL, no hardcoded role checks, no hardcoded credentials.

## Setting up to contribute

### Prerequisites

- Claude Code (for testing the plugin)
- Frappe v15+ bench (for testing `stack_core`)
- Python 3.10+
- Node 18+ (only for Playwright E2E)
- `gh` CLI (for `pr_opener.py` smoke tests)

### Clone + install

```bash
git clone https://github.com/dhwani-ris/frappe-stack.git
cd frappe-stack
```

For `stack_core`:

```bash
cd /path/to/frappe-bench
bench get-app stack_core /path/to/frappe-stack/apps/stack_core
bench --site test_site install-app stack_core
```

For the plugin (in Claude Code):

```text
/plugin marketplace add /path/to/frappe-stack
/plugin install frappe-stack@frappe-stack
```

## What kind of contribution?

### Adding a skill

1. Decide the category: `building/`, `process/`, `platform/`, or `builder-protocol/`.
2. Create `skills/<category>/<kebab-name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: <kebab-name>
   description: <when to load — start with "Use when…" or list trigger phrases in PM-natural language>
   ---
   ```
3. Body: when to load, conversation flow if applicable, worked example, anti-patterns to refuse.
4. Add a row to [`docs/skills.md`](./docs/skills.md) under the right section.
5. Open a PR with the `skill` label.

**Skill ergonomics test:** does the description trigger on PM-natural phrases ("I need a form for…") rather than jargon ("create a DocType")?

### Adding an agent

1. Create `agents/<name>.md` with frontmatter:
   ```yaml
   ---
   name: <name>
   description: <when to invoke — proactively / when triggered>
   tools: <minimum needed>
   model: haiku | sonnet | opus
   ---
   ```
2. Body: workflow steps, refuses, pairs-with.
3. Add a row to [`docs/agents.md`](./docs/agents.md).
4. Open a PR with the `agent` label.

### Adding a slash command

1. Create `commands/<name>.md` with frontmatter:
   ```yaml
   ---
   description: <one sentence>
   argument-hint: <example invocation>
   ---
   ```
2. Body: what it does, arguments, refuses-if, examples.
3. Add a row to [`docs/commands.md`](./docs/commands.md).
4. Mirror any refusals into [`docs/hooks.md`](./docs/hooks.md) so the hook layer enforces them.

### Adding a hook

Hooks are security-sensitive. Triple-check before opening the PR.

1. Pick the lifecycle event (`UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `Stop`).
2. Write `.claude-plugin/hook_scripts/<name>.py`. Read stdin, write stdout JSON. See existing scripts for the contract.
3. Add the entry to `hooks/hooks.json` under the right top-level key.
4. Add a regression test under `tests/hooks/test_<name>.py`. Prove the hook fires on the bad input and approves the good input.
5. Add a row to [`docs/hooks.md`](./docs/hooks.md).
6. Open a PR with the `hook` and `security` labels — security review mandatory.

### Adding a `stack_core` feature

1. Open an issue first to discuss the design.
2. Write tests first (`apps/stack_core/stack_core/<module>/test_<name>.py`).
3. Run `bench --site test_site run-tests --app stack_core --coverage` — must be ≥ 80% on changed lines.
4. Run `bench --site test_site run-tests --app stack_core` against `frappe-semgrep-rules` (no CRITICAL / HIGH).
5. Update relevant docs (`docs/architecture.md` if data flow changes, `docs/skills.md` if skill behavior changes).
6. Open a PR with the `stack_core` label.

### Fixing a bug

1. Open an issue with reproduction steps.
2. Write a regression test that fails on `main`.
3. Implement the fix.
4. Test passes.
5. Open a PR linked to the issue.

### Improving documentation

1. PRs welcome on any file under `docs/`, the four protocol files, or `README.md`.
2. Use the `docs` conventional-commit prefix.
3. No code changes in a docs PR — keep them separate.

## PR review

Every PR runs through the `reviewer` and `tester` agents (when CI is wired in `infra/`). Until then, the maintainer runs them manually.

Pass criteria:
- ✓ 0 CRITICAL / 0 HIGH from reviewer
- ✓ All tests pass; coverage ≥ 80% on changed lines
- ✓ Conventional-commit messages
- ✓ Docs updated to match the change
- ✓ One logical change

## Security disclosure

If you find a security issue, **do not open a public issue**. Email `noreply@dhwaniris.com` (replace with the project's security contact when established) with:

1. Description of the vulnerability
2. Reproduction steps
3. Affected versions / files
4. Suggested fix if known

You'll get acknowledgement within 48 hours and a fix timeline within a week.

## Code of conduct

Be respectful. Be helpful. Assume good intent. If a contributor's behavior makes the community worse, raise it with the maintainer.

## Questions?

- Open a discussion (when GitHub Discussions is enabled).
- Or open an issue with the `question` label.
