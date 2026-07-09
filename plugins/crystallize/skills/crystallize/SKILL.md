---
name: crystallize
description: Build or refresh the .context knowledge graph for a scope, detect duplicate clusters, and synthesize a consolidation brief for human approval. Single entry point; classifies scope and runs the smallest honest pass. Never rewrites code. Use when asked to crystallize, consolidate, dedupe, or build a .context for a codebase, domain, or component family.
---

This skill orchestrates a pipeline of phases. Each phase's method is a bundled
reference under `../../assets/references/`; read it when you reach that phase and
follow it. On a harness with isolated subagents you may run a phase in its own
subagent — recommended for the referee step, where independence is a correctness
feature; otherwise run each phase inline in sequence. The pipeline and its outputs
are identical either way.

`scope` (the argument, optional) decides the size of the run. Classify it:

- **specific** — a pattern family name (`modais`, `cards`, `filters`): build/refresh
  only that `patterns/<x>.yaml` (+ its tree, if earned) and flag its forks.
- **domain** — a domain path or name (`src/despesas`, `despesas`): one
  `domains/<x>.yaml` plus the patterns that domain uses.
- **whole** — no argument: the full graph, with duplicate detection looping until
  it runs dry.

Everything lives under `.context/` at the repo root (create it if absent). Process
bookkeeping lives at `.context/status.json` and `.context/_crystallize/`; the graph
files (`domains/`, `patterns/`, `trees/`, `index/`, `manifest.yaml`, `onboarding.yaml`)
stay pristine for day-to-day agents.

## Step 0 — load or init status.json

Read `.context/status.json` (schema below). Create it with defaults if absent.

```json
{
  "scope": "<specific|domain|whole>:<name or whole-repo>",
  "phases": {
    "map":  { "lastRun": null, "fileHashes": {} },
    "mine": { "lastRun": null, "fileHashes": {} },
    "diff": { "lastRun": null, "fileHashes": {} }
  },
  "gate": "pending",
  "clusters": [],
  "execution": { "active": null, "progress": {} },
  "nextSuggestedCommand": null
}
```

`clusters[].status` is one of `pending | approved | in_progress | applied |
blocked | discarded`. The `execution` block is the resume pointer for the apply
campaign — `/crystallize-apply` owns it (see that command); `/crystallize` only
initializes it.

**Staleness:** for each phase already run, recompute `shasum -a 256` for its
`fileHashes` and compare. Any mismatch, or new in-scope files absent from `map`'s
hashes, makes that phase and every later phase stale — they must re-run.

## Step 1 — map (Tier-1 skeleton; if missing or stale)

Run the **map method** (`../../assets/references/map-method.md`) for the scope.
Pass it the current timestamp for `generated_at` (never invent one). Write:
- `.context/index/components.generated.yaml` (its GENERATED_INDEX)
- the SYSTEM_MAP_SKELETON into `.context/manifest.yaml#system_map`

Update `status.json` `phases.map`.

## Step 2 — mine (intent; if missing or stale, or map re-ran)

Run the **mine method** (`../../assets/references/intent-method.md`) for the scope,
using the generated index as a map of where to look. Keep its BUSINESS_INTENT and
UI_INTENT as working input under
`.context/_crystallize/` — this is proposal material, not yet graph.

Update `status.json` `phases.mine`.

## Step 3 — diff (duplicate clusters; if missing or stale, or mine re-ran)

Run the **diff method** (`../../assets/references/duplicate-method.md`) with the
generated index + both intent tracks. It runs catalog → categorize → per-category
detect (never full-catalog comparison —
that's noise). Cost-tier the passes: categorization is cheap (a haiku-class model
is enough to bucket by domain); the per-category duplicate detection is the
careful, expensive pass (opus-class) — this split is the efficiency win, don't run
the whole thing at one tier. If `superpowers-lab:finding-duplicate-functions` is
installed and the code is TS/JS, its `extract-functions.sh` + per-category prompt
are a proven accelerator for the catalog + detection — the detector may use them
and map results into the cluster format.

Write its VARIATIONS to `.context/_crystallize/VARIATIONS.md`. Parse each
`#### Cluster: <cluster-id>` into `status.json.clusters` as
`{ id, intent, category, mechanism, confidence, recommendation, mass, risk, status: "pending" }`,
preserving the `status` of any cluster-id already present (never reset an
`applied` cluster).

For a **whole** scope, loop map→mine→diff until two consecutive diff rounds add no
new cluster (loop-until-dry). For **specific**/**domain**, one pass is enough.

Update `status.json` `phases.diff`.

## Step 4 — referee (make Tier-2 true)

Before anything curated is proposed, verify. For each cluster and each candidate
canonical claim (its `extends`/base, its consumer counts, its "these instances
are equivalent"), run the **referee method** (`../../assets/references/referee-method.md`)
— one claim at a time, and (where subagents exist) in isolation. Drop or correct
every claim the referee refutes/corrects. Only verified claims proceed.

## Step 5 — synthesize the brief (only when map, mine, diff are all fresh)

If any phase just re-ran due to staleness, stop and report what refreshed; re-run
`/crystallize` once to confirm nothing changed, then continue. (If Steps 1–3
changed nothing, continue immediately.)

Run the **synthesis method** (`../../assets/references/synthesis-method.md`) with
the verified clusters + intent. Write its PROPOSED_* blocks into
`.context/_crystallize/CRYSTALLIZE_BRIEF.md` (not yet into
the live graph). The brief is: the proposed patterns/trees/index/domains, the
over-engineering self-review, and the open questions.

Set `gate` to `"pending"` (or leave `"approved"`/`"partially_applied"` as-is; if it
was already `"approved"` and new clusters appeared, flag that to the user — a
regenerated brief does not silently re-approve). Set `nextSuggestedCommand` to
`"review .context/_crystallize/CRYSTALLIZE_BRIEF.md and approve"`.

## Step 6 — present and stop

Summarize the brief: scope, top clusters by mass, which pattern families earned a
decision tree and which didn't, open questions. **Enter plan mode if supported and
stop — write nothing into the live graph until the user approves.** Approving means
the user names which clusters/nodes are accepted; on their confirmation, promote
the approved Tier-2 blocks from the brief into `.context/` (patterns, trees,
curated index, domains, manifest registry) and mark those clusters `"approved"` in
`status.json`. Only then can `/crystallize-apply` run.

After promoting anything into the live graph, run the bundled validator and report
its result — a promoted node that points at a file which doesn't exist is a lie the
graph must not keep. The validator is at `scripts/validate-context.py` under this
plugin's root (Claude Code exposes it as `${CLAUDE_PLUGIN_ROOT}`; other harnesses
via their own plugin-root variable — resolve it however your harness bundles skill
resources):

```
python3 "<plugin-root>/scripts/validate-context.py" --context .context --repo .
```

If it reports errors (dangling paths, unresolved references), fix them before
declaring the run done — do not leave the graph in a failing state.
