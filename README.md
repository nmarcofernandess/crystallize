# Crystallize

Crystallize is a Claude Code plugin that consolidates a stable,
self-authored prototype into canonical, reusable architecture:

```text
prototype -> map -> mine -> diff -> brief (human approval) -> apply, one pattern at a time
```

It is the mirror image of the official `code-modernization` plugin: that
one treats a legacy codebase as *unknown and untrusted*, migrating it to a
new stack. Crystallize treats the codebase as *your own recent work* —
the intent is already known, the stack doesn't change, and the goal is to
cut accumulated variation (duplicated modals, duplicated validators,
inconsistent naming) down to one canonical shape per concept, before it
hardens into permanent debt.

This repository is the marketplace root: product repositories consume
`crystallize`, they do not host it.

## Repository Shape

```text
.claude-plugin/marketplace.json     # Claude Code marketplace catalog
plugins/crystallize/
  .claude-plugin/plugin.json        # Claude Code plugin manifest
  agents/                           # Specialist subagents (map/mine/diff/brief/apply)
  commands/                         # /crystallize, /crystallize-apply, /crystallize-status
  README.md                         # Plugin usage
```

Do not copy this plugin into product repositories. Install this
marketplace from Git and keep this repository as the source.

## Install In Claude Code

```
/plugin marketplace add nmarcofernandess/crystallize
/plugin install crystallize@crystallize
```

## Commands

- **`/crystallize [area]`** — single entry point. Internally runs map →
  mine → diff against a `STATUS.json` state file (skipping phases that
  are already fresh), then synthesizes a `CRYSTALLIZE_BRIEF.md` and stops
  at a plan-mode approval gate. Never rewrites code.
- **`/crystallize-apply <pattern-id>`** — applies one approved pattern
  from the brief: extracts the canonical shape, migrates its instances,
  proves equivalence with a test. Refuses to run against anything not
  marked `approved`.
- **`/crystallize-status [area]`** — read-only report: phase freshness,
  gate state, pattern statuses, suggested next command.

See `plugins/crystallize/README.md` for full usage and artifact details.

## License

MIT. See `LICENSE`.
