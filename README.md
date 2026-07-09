# Crystallize

Crystallize is a Claude Code plugin that turns a stable, self-authored codebase
into a durable `.context` knowledge graph — and keeps it that way:

```text
codebase -> map -> mine -> diff -> referee -> brief (human approval) -> apply, one cluster at a time
                                                         |
                                                    .context/  <- read every day, before you build
```

It is the mirror of the official `code-modernization` plugin: that one treats a
legacy codebase as *unknown and untrusted* and migrates it to a new stack.
Crystallize treats the codebase as *your own recent work* — the intent is known,
the stack doesn't change — and its job is to cut accumulated variation
(duplicated modals, duplicated validators, inconsistent naming) down to one
canonical shape per concept, then hold the line so it doesn't drift back.

The `.context/` graph is the product. It makes reuse the default and forking a
justified exception, and `/crystallize-guard` enforces that day to day. Deletion
is an *effect* of generalizing and reusing — never a goal of fewer lines.

This repository is the marketplace root: product repositories consume
`crystallize`, they do not host it.

## Repository Shape

```text
.claude-plugin/marketplace.json     # Claude Code marketplace catalog
DESIGN.md                           # rationale, the five design locks
plugins/crystallize/
  .claude-plugin/plugin.json        # Claude Code plugin manifest
  CONTEXT_SCHEMA.md                 # the generic .context contract
  agents/                           # 6 specialist subagents
  commands/                         # /crystallize, -apply, -guard, -status
  scripts/validate-context.py       # structural graph validator
  README.md                         # plugin usage
```

Do not copy this plugin into product repositories. Install this marketplace from
Git and keep this repository as the source.

## Install In Claude Code

```
/plugin marketplace add nmarcofernandess/crystallize
/plugin install crystallize@crystallize
```

## Commands

- **`/crystallize [scope]`** — single entry point. Classifies scope
  (specific / domain / whole), runs map → mine → diff → referee against a
  `.context/status.json` state file (skipping fresh phases), writes the Tier-1
  graph, and synthesizes a brief of proposed Tier-2 judgment. Stops at a
  plan-mode approval gate. Never rewrites code, and nothing curated persists
  until a referee verified it and you approved it.
- **`/crystallize-apply [cluster-id]`** — runs the resumable consolidation
  campaign. Applies approved clusters step by step (build the canonical form, then
  migrate each instance), proving behavior didn't drift against the repo's own test
  harness at every step. Each cluster has an immutable `plan.json` and an
  append-only `log.jsonl` under `.context/_crystallize/execution/`, so a fresh agent
  resumes exactly where it stopped — never redoing work, never leaving a cluster
  half-applied. Refuses anything not `approved`.
- **`/crystallize-guard "<what you're about to build>"`** — anti-fork check.
  Reads the curated graph, tells you whether a canonical form already exists and
  what to extend. Read-only, staleness-aware.
- **`/crystallize-status [scope]`** — read-only: phase freshness, graph tiers,
  gate state, pending clusters, next step.

See `DESIGN.md` for the design locks and `plugins/crystallize/README.md` for full
usage.

## License

MIT. See `LICENSE`.
