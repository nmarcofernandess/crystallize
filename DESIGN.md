# Crystallize — Design

## What it is

Crystallize is a `.context` engine. You point it at a stable, self-authored
codebase and it produces a durable YAML knowledge graph — `.context/` — that
makes reuse the default and forking a loud, justified exception. The graph
serves two masters: day-to-day feature work (an agent reads it before building,
so it reuses instead of duplicating) and the plugin's own consolidation process
(it finds duplication by asking the graph "does this already exist?").

It is the mirror of `code-modernization`: that plugin treats a legacy codebase
as unknown and untrusted and migrates it to a new stack. Crystallize treats the
code as your own recent work — the intent is known, the stack doesn't change —
and the goal is to cut accumulated variation down to one canonical shape per
concept before it hardens into permanent debt.

It is **generic**: nothing here is specific to any one project. The reference
exemplar of a hand-authored `.context` is DietFlow's, but that is an example of
the target shape, not a dependency.

## The five design locks (non-negotiable)

1. **The graph must be TRUE.** A plausibly-wrong `.context` is worse than none —
   future agents build on the lie and the guard enforces it. State of the art
   here is the most trustworthy graph, not the richest generator.

2. **Two honesty tiers, kept in separate files** (DietFlow's own `.context`
   already splits provenance this way):
   - **Tier 1 — auto-generated, verifiable skeleton.** `index/components.generated.yaml`
     (carries `generated_at`), the `system_map` skeleton, and candidate
     duplicate clusters. Derived by grep/glob walk — language-agnostic, cheap,
     re-runnable.
   - **Tier 2 — verified + human-curated judgment.** Canonical decisions,
     `anti_patterns`, `trees/need-*` branches, the curated `index/components.yaml`.
     Enters the durable graph ONLY after (a) a referee re-derives each claim
     against the cited code and (b) the human approves it in the brief. **The
     anti-fork guard reads Tier 2 only.** This kills over-engineering
     structurally: nothing persists that wasn't verified and approved, so the
     plugin cannot invent a 50-file taxonomy.

3. **Deletion is an effect, never a goal.** Mass disappears legitimately in two
   ways only: Altitude (N special cases collapse into one general mechanism) and
   Reuse (N re-implementations collapse into one helper). Pursuing "fewer lines"
   as the objective is a bug. The often-cited "90% smaller" is a possible
   consequence of generalizing — or it isn't, and that's fine.

4. **Behavior preservation is a hard gate.** Every consolidation runs the
   repository's own test/typecheck harness (whatever it is) plus a
   removed-behavior audit: for every deleted line, name the invariant it
   enforced and where it is re-established. Consolidating is not bug-fixing —
   anything that smells like a bug routes to a separate pass, never gets
   silently "fixed" mid-consolidation.

5. **Staleness blocks.** The guard refuses or warns when the graph is stale
   relative to the code. A guard answering confidently from a rotted map is a
   footgun.

## Scope proportionality

`/crystallize [scope]` classifies the request and does the smallest honest run:

- **specific** — a pattern family (`/crystallize modais`): builds/refreshes just
  that `patterns/<x>.yaml` + its `trees/need-<x>.yaml`, flags forks.
- **domain** — a domain path or name (`/crystallize despesas`): one
  `domains/<x>.yaml` plus related patterns.
- **whole** — no argument: full `.context`, duplicate detection looping until it
  runs dry.

## The anti-fork mechanism ("suffering to fork")

`/crystallize-guard "I'm about to build a modal for X"` reads Tier 2 (trees +
patterns + component index) and answers: *does a canonical form already exist?*
If yes, it names the existing base and its consumer count and points at the
decision-tree branch. Forking then requires an explicit justification for why
the case fits no existing branch. Read-only, fast, staleness-aware — the
day-to-day workhorse, usable in review/CI.

The anti-fork force is a four-layer interlock reproduced from the reference
schema: philosophy (`EXTEND > CREATE`) → decision-tree branches (the fork lives
only in the `"Outro"` branch, gated by `warning:`) → `extends`/`consumers` proof
(this thing exists and N things already use it) → named `forbidden`/`anti_patterns`
(the specific parallel implementation this pattern tends to spawn, banned by
hand).

## What we took from Superflow (only this)

Organization, not machinery. A dedicated folder, a map/status file, all
artifacts co-located, a defined process. No router, no phase-budget enum, no
classifier script, no skill tree. Crystallize stays its own thing; the two are
not blended.

## Generated `.context/` layout

```
.context/
  onboarding.yaml               # philosophy + decision flows + global anti-patterns   (Tier 2)
  manifest.yaml                 # the map: entry_points + registry + system_map        (skeleton T1 / prose T2)
  domains/<area>.yaml           # per-area maps (plain, or kind: domain-contract)       (Tier 2)
  patterns/<name>.yaml          # named patterns: extends/consumers/anti_patterns       (Tier 2, referee-verified)
  trees/need-<goal>.yaml        # decision trees                                         (Tier 2)
  index/
    components.yaml             # curated reuse targets, semantic fields                 (Tier 2)
    components.generated.yaml   # machine walk, {path, domain}, generated_at             (Tier 1)
  status.json                   # process state: phases, file hashes, gate, clusters     (plugin)
  _crystallize/
    VARIATIONS.md               # detected duplicate clusters (working artifact)
    CRYSTALLIZE_BRIEF.md        # the approval-gate artifact
    CONSOLIDATION_NOTES.md      # what /crystallize-apply changed, per cluster
```

The graph files are kept pristine for day-to-day agents; `status.json` and
`_crystallize/` hold the plugin's own bookkeeping, co-located but out of the way.

Folder is the type discriminator (not the in-file key). Every freshness field is
optional. `status: draft|proposed` marks lower-confidence nodes.

## Surface

- `/crystallize [scope]` — build/refresh the graph for the scope, detect
  duplicate clusters, synthesize the brief, stop at the approval gate.
- `/crystallize-apply <cluster-id>` — consolidate one approved cluster into its
  canonical form, behavior gate + removed-behavior audit, update the graph.
- `/crystallize-guard <what>` — anti-fork check, read-only, staleness-aware.
- `/crystallize-status [scope]` — read-only: freshness, tiers, gate, pending
  clusters, next step.

## Agents

- `context-mapper` — Tier-1 skeleton (generated index + system_map) via grep/glob,
  language-agnostic, read-only.
- `intent-extractor` — business rules + UI intent from the code as informal spec.
- `duplicate-detector` — semantic duplicate clusters; assigns `cluster-id`, names
  the canonical destination, ranks by mass-reclaimed-safely. Method: catalog →
  categorize (cheap model) → per-category detect (careful model), with a
  HIGH/MEDIUM/LOW × CONSOLIDATE/INVESTIGATE/KEEP_SEPARATE model and "when in doubt,
  INVESTIGATE". Composes the `superpowers-lab:finding-duplicate-functions` toolbox
  as an optional accelerator on TS/JS (reuse over reinvention — the plugin obeys
  its own thesis); language-agnostic grep/glob otherwise.
- `claim-referee` — re-derives each proposed canonical claim / `extends` / anti-
  pattern against the cited code and confirms or refutes it. The gate that makes
  Tier 2 true.
- `context-architect` — synthesizes verified clusters into the curated graph
  (patterns, trees, curated index, domains), with an adversarial over-engineering
  self-review (does this tree branch earn itself, or does a default/name suffice?).
- `consolidator` — applies one approved cluster via Altitude + Reuse, behavior
  gate against the repo's own harness, removed-behavior audit, updates the graph.
