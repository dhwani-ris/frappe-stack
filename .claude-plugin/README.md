# Plugin manifest

This directory holds the Claude Code plugin manifest for `frappe-stack`.

## Files

| File | Purpose |
|---|---|
| `plugin.json` | Plugin manifest — name, version, author, repo. Required. |
| `marketplace.json` | Marketplace listing — required because Claude Code installs plugins via marketplaces, not direct git URLs. |

## Install (private — direct git URL)

Claude Code plugins must be installed via a marketplace. This repo is a single-plugin marketplace — the plugin and marketplace share the same git URL.

```text
# 1. Register this repo as a marketplace
/plugin marketplace add https://github.com/dhwani-ris/frappe-stack.git

# 2. Install the plugin
/plugin install frappe-stack@frappe-stack
```

The install string is `<plugin-name>@<marketplace-name>`. Both happen to be `frappe-stack` here.

## Namespace

Skills, agents, and commands are auto-namespaced from the manifest `name` field. Examples:

- Slash command file `commands/init.md` → invoked as `/frappe-stack:init`
- Skill folder `skills/designing-forms/SKILL.md` → loaded as `frappe-stack:designing-forms`
- Agent file `agents/engineer.md` → spawned as `frappe-stack:engineer`

Do **not** prefix filenames with `fs-` — the namespace handles disambiguation. (D-02 in `PLAN.md` updated to reflect this; the original `/fs-` proposal pre-dated the manifest research.)

## Versioning

`version` in `plugin.json` is set to `0.1.0` for the v0.1 release. Bump on every release tag. Until then, Claude Code falls back to the git commit SHA, so users on `main` always pick up the latest commit.

## Hooks

Hook definitions land in `../hooks/hooks.json` in **Phase 6**. See `PLAN.md §7` for the list.
