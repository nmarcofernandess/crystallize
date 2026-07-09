# Crystallize

Crystallize is an Agent Skills plugin — it installs on **Claude Code and Codex**
(and any harness that reads the [Agent Skills](https://agentskills.io) format) —
that turns a stable, self-authored codebase into a durable `.context` knowledge
graph, and keeps it that way:

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

The portable core is the `skills/` tree — one `SKILL.md` per capability, read by
any Agent Skills harness. Everything else is a thin per-harness adapter.

```text
.claude-plugin/marketplace.json       # Claude Code marketplace catalog
.agents/plugins/marketplace.json      # Codex marketplace catalog
DESIGN.md                             # rationale, the five design locks
plugins/crystallize/
  .claude-plugin/plugin.json          # Claude Code plugin manifest
  .codex-plugin/plugin.json           # Codex plugin manifest
  skills/                             # ← portable core: crystallize, -apply, -guard, -status
    <name>/SKILL.md
  assets/references/                  # phase methods the skills read (map, mine, diff, referee, synthesis, consolidator)
  scripts/validate-context.py         # structural graph validator
  CONTEXT_SCHEMA.md                   # the generic .context contract
  README.md                           # plugin usage
```

Do not copy this plugin into product repositories. Install this marketplace from
Git and keep this repository as the source.

## Install

**Claude Code**

```
/plugin marketplace add nmarcofernandess/crystallize
/plugin install crystallize@crystallize
```

**Codex**

```
codex plugin marketplace add nmarcofernandess/crystallize --ref main
codex plugin add crystallize@crystallize
```

The four capabilities are invoked as skills (`/crystallize`, `/crystallize-apply`,
`/crystallize-guard`, `/crystallize-status` — namespaced by the harness). On a
harness with isolated subagents, the pipeline phases may fan out for stronger
verification independence; without them they run inline in sequence — same result.

## Capabilities

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

## Portability, honestly

The `skills/` core is [Agent Skills](https://agentskills.io) — an open standard
adopted by ~40 products (Claude Code, Codex, Copilot, Cursor, Gemini CLI, VS Code,
…). What travels across all of them is the `SKILL.md` instructions and their
bundled reference methods. The manifests, marketplace catalogs, and any subagent
dispatch are per-harness — this repo ships the Claude Code and Codex adapters. So
"works on any AI" precisely means "works on any harness that adopted Agent Skills";
on one that hasn't, you can still point the agent at a `SKILL.md` directly.

## License

MIT. See `LICENSE`.
