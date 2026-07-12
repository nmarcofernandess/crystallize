# crystallize

Point this at a stable, self-authored codebase and it builds a durable
`.context` knowledge graph — the domains, patterns, component index, and
decision trees that make reuse the default and forking a loud, justified
exception. That graph then serves two masters: day-to-day feature work (an
agent reads it before building, so it reuses instead of duplicating) and the
plugin's own consolidation (it finds duplication by asking the graph "does this
already exist?").

Unlike `code-modernization`, the source here is **trusted** (your own recent
code) and the target is the **same stack** — this isn't a rewrite, it's
canonicalization: same intent, fewer variations, one name per concept. Deletion
is an *effect* of generalizing and reusing, never a goal of fewer lines.

Full rationale in [`../../DESIGN.md`](../../DESIGN.md); the graph format in
[`skills/crystallize/references/CONTEXT_SCHEMA.md`](skills/crystallize/references/CONTEXT_SCHEMA.md).

## Install

The repository [installation guide](../../README.md#install) contains
prerequisites, update commands, verification, and troubleshooting. Quick paths:

```bash
# Claude Code
claude plugin marketplace add nmarcofernandess/crystallize --scope user
claude plugin install crystallize@crystallize --scope user

# Codex
codex plugin marketplace add nmarcofernandess/crystallize --ref main
codex plugin add crystallize@crystallize

# Gemini CLI
npx skills add nmarcofernandess/crystallize --skill '*' --agent gemini-cli --global --copy
```

Python 3 and PyYAML `>=6,<7` are required for graph validation. Restart the
host, or reload Gemini skills, after installing.

## Usage

```
/crystallize                 # whole repo — full graph, duplicate detection until dry
/crystallize modais          # specific — one pattern family
/crystallize despesas        # domain — one domain + its patterns
```

Runs map → mine → diff → referee internally, writes the graph to `.context/`,
and stops at a plan-mode approval gate once the brief is ready. Nothing curated
enters the graph until a referee verified it against the code AND you approved
it.

```
/crystallize-apply [cluster-id]   # resumable consolidation campaign — step by step, prove no drift, survives context loss
/crystallize-guard "a modal for X" # anti-fork check: does a canonical form exist?
/crystallize-status               # read-only: freshness, tiers, gate, clusters
```

## The two tiers

The graph keeps generated facts and human judgment in separate files, so trust
is legible:

- **Tier 1 — generated.** `index/components.generated.yaml` (`generated_at`),
  `system_map` skeleton, candidate clusters. A grep/glob walk; safe to refresh.
- **Tier 2 — verified + curated.** `patterns/*`, `trees/need-*`, curated
  `index/components.yaml`, `domains/*`. Enters only after referee-verification +
  human approval. **The guard reads Tier 2 only.**

## Layout

```
.context/
  onboarding.yaml · manifest.yaml
  domains/<area>.yaml · patterns/<name>.yaml · trees/need-<goal>.yaml
  index/components.yaml · index/components.generated.yaml
  status.json · _crystallize/{VARIATIONS,CRYSTALLIZE_BRIEF,CONSOLIDATION_NOTES}.md
```

## Skills and phase methods

Four self-contained skills (`skills/<name>/SKILL.md`) are the portable core:
`crystallize`, `crystallize-apply`, `crystallize-guard`,
`crystallize-status`. Pipeline methods live under the consuming skill's
`references/` directory (run inline, or in isolated subagents where the harness
has them):

- `map-method` — Tier-1 skeleton (generated index + system_map), grep/glob, language-agnostic
- `intent-method` — business + UI intent from the code as informal spec
- `duplicate-method` — semantic duplicate clusters (catalog → categorize → per-category detect); names the canonical destination. Composes `superpowers-lab:finding-duplicate-functions` as an optional TS/JS accelerator
- `referee-method` — re-derives each claim against the cited code (makes Tier-2 true; strongest in an isolated subagent)
- `synthesis-method` — curates the graph, with an anti-over-engineering self-review
- `consolidator-method` — executes one plan step (build canonical / migrate one instance) via Reuse/Altitude, behavior gate + removed-behavior audit, structured outcome for the log

## Validate the graph

```bash
<python> .context/_crystallize/tools/validate-context.py --context .context --repo .
```

Checks every graph file parses, the generated index carries `generated_at`,
every `path:` points to a file that really exists (the anti-lie check), internal
cross-references resolve, and reports `draft`/`proposed` nodes as
lower-confidence. The first `crystallize` run stages this project-local validator
from the skill package. Use `python3` where available or `python` on Windows.

## License

MIT — see repository root.
