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
  skills/                             # portable, self-contained Agent Skills
    crystallize/
      SKILL.md
      references/                     # map, mine, diff, referee, synthesis, schema
      scripts/validate-context.py     # structural graph validator
    crystallize-apply/
      SKILL.md
      references/consolidator-method.md
    crystallize-guard/SKILL.md
    crystallize-status/SKILL.md
  README.md                           # plugin usage
```

Do not copy this plugin into product repositories. Install this marketplace from
Git and keep this repository as the source.

## Install

Version `0.3.1` is the minimum supported release. Version `0.3.0` contained an
unsupported Claude manifest field and could not be installed by current Claude
Code.

### Prerequisites

- Git, plus a current release of the target agent CLI.
- Python 3 for the structural graph validator.
- PyYAML in the Python environment used by the agent:

```bash
python -m pip install "PyYAML>=6.0,<7"
```

On systems where Python 3 is exposed as `python3`, use `python3 -m pip`
instead. Crystallize stops with an explicit prerequisite error if PyYAML is
missing; validation is never silently skipped.

Reference documentation: [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[Gemini CLI Agent Skills](https://geminicli.com/docs/cli/using-agent-skills/),
and the [universal skills CLI](https://github.com/vercel-labs/skills).

### Claude Code: native marketplace

```bash
claude plugin marketplace add nmarcofernandess/crystallize --scope user
claude plugin install crystallize@crystallize --scope user
claude plugin list --json
```

Restart Claude Code after installation. The skills are namespaced by the plugin,
for example `/crystallize:crystallize` and
`/crystallize:crystallize-guard`.

### Codex: native marketplace

```bash
codex plugin marketplace add nmarcofernandess/crystallize --ref main
codex plugin add crystallize@crystallize
codex plugin list --json
```

Start a new Codex thread after installation so the new skills are loaded. Codex
shows them under the `crystallize:` namespace.

### Gemini CLI

The repository contains four self-contained Agent Skills. Install all four with
the universal Agent Skills installer:

```bash
npx skills add nmarcofernandess/crystallize --skill '*' --agent gemini-cli --global --copy
gemini skills list
```

Inside Gemini CLI, run `/skills reload` after installing, then `/skills list`
to verify discovery. Gemini activates skills from the prompt; it does not expose
the Claude plugin slash-command namespace.

### Other Agent Skills harnesses

Inspect the available skills, then let the installer detect a supported agent:

```bash
npx skills add nmarcofernandess/crystallize --list
npx skills add nmarcofernandess/crystallize --skill '*'
```

Use `--global` for a user-wide install or omit it for project scope. The
installer supports Codex, Claude Code, Gemini CLI, Cursor, GitHub Copilot,
OpenCode, and other Agent Skills hosts. Native Claude/Codex marketplace installs
remain preferred because they preserve plugin version and marketplace metadata.

### Update

```bash
# Claude Code
claude plugin marketplace update crystallize
claude plugin update crystallize@crystallize

# Codex
codex plugin marketplace upgrade crystallize
codex plugin add crystallize@crystallize

# Gemini CLI / universal Agent Skills installs
npx skills update crystallize crystallize-apply crystallize-guard crystallize-status --global
```

Restart the host, or start a new session/thread, after updating.

### Troubleshooting

- `Unrecognized key: "displayName"`: refresh the marketplace and confirm that
  `0.3.1` or newer is installed.
- `No module named yaml`: install PyYAML with the same Python interpreter the
  agent runs.
- Plugin installed but skills are absent: restart Claude/Codex; in Gemini run
  `/skills reload`.
- Testing a non-main branch: Claude accepts a full Git URL with `#branch`;
  Codex accepts `--ref branch`. Do not replace a stable marketplace source
  accidentally.

The four capabilities are invoked as skills (`crystallize`,
`crystallize-apply`, `crystallize-guard`, `crystallize-status`; exact
namespacing depends on the host). On a harness with isolated subagents, the
pipeline phases may fan out for stronger verification independence; without
them they run inline in sequence with the same artifacts and gates.

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

The `skills/` core is [Agent Skills](https://agentskills.io), and every skill
keeps its required references or scripts inside its own directory so standalone
installers do not produce partial packages. Claude Code and Codex use native
marketplace adapters. Gemini CLI and other compatible hosts use the portable
skills directly. Harness-specific features such as namespacing, isolated
subagents, and reload behavior remain host-specific; the graph contract,
approval gate, and output artifacts stay the same.

## License

MIT. See `LICENSE`.
