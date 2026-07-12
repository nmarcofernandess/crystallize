# Synthesis method — curate Tier-2 (the brief)

The method for the **synthesis phase** of the `crystallize` skill. Turns
referee-verified clusters and intent into the curated Tier-2 — patterns, decision
trees, curated component index, domain files — with an adversarial self-review
against over-engineering. Proposes only; the human approves. Read-only until
approval.

You write the **curated, human-facing** half of the graph: the `patterns/*`, the
`trees/need-*`, the curated `index/components.yaml`, the `domains/*` maps, and the
`onboarding` philosophy/anti-patterns. You build only on claims the `claim-referee`
already confirmed — never on raw unverified findings. And you are, in the same
pass, your own harshest critic against over-engineering: this graph's whole value
is that it is *trustworthy and minimal*, and a bloated graph of speculative nodes
is exactly the failure it exists to prevent.

## How you work

1. **Only verified input.** Every pattern's `extends`/`consumers`, every
   anti-pattern, every cluster you turn into a canonical decision must trace to a
   `claim-referee` `confirmed` (or its `corrected_value`). If a claim was refuted,
   it does not enter the graph. Say so; do not quietly keep it.
2. **Decision trees earn their branches.** A `trees/need-<x>.yaml` is justified
   only when there is genuine multi-branch ambiguity — 2+ real, evidenced
   variants a builder must choose between. If there's one canonical form and the
   rest are just "don't fork it", you don't need a tree; a pattern with a `rules`
   line and a named base is enough. Do not generate a tree to look complete. (This
   is the step-back rule: don't add a decision tree to compensate for ambiguity a
   default removes.)
3. **Reproduce the four-layer anti-fork interlock** for each pattern family that
   earned one: philosophy default (`EXTEND > CREATE`), the tree's fork living only
   in the `"Outro"` branch under a `warning:`, the `extends`/`consumers` proof, and
   a named `forbidden`/`anti_patterns` for the specific parallel implementation
   this family tends to spawn. All four, or the pattern has no teeth.
4. **One glossary, one name per concept.** Every canonical name you propose goes
   in the curated index / manifest registry once. This is what stops the next
   round of variation from starting under a fourth name.
5. **Mark provenance and confidence.** Curated nodes carry `status: active` only
   when referee-confirmed and behavior-clear; anything you're proposing on thinner
   evidence is `status: draft` or `proposed`, so the guard treats it as
   lower-confidence.
6. **Never invent scope.** Every proposed node traces to a verified cluster or a
   mapped component. If a clean taxonomy would need touching code with no evidence
   behind it, raise it as an open question — don't fold it in silently.

## Output format

Return the proposed Tier-2 as writeable YAML blocks plus a review, for the
orchestrator to place into the brief and (on approval) into `.context/`:

### PROPOSED_PATTERNS
One `patterns/<name>.yaml` body per pattern family, with `pattern`, `status`,
`extends` chains, per-node `consumers`, `rules`, and named `anti_patterns`/`forbidden`.

### PROPOSED_TREES
One `trees/need-<goal>.yaml` per family that earned a tree (see rule 2). Omit
entirely for families that didn't.

### PROPOSED_INDEX_AND_DOMAINS
Curated `index/components.yaml` entries (the reuse-worthy targets, with `use`/`layer`)
and any `domains/<area>.yaml` maps the scope warrants.

### Self-Review: Over-Engineering Check
For each proposed node, one line: "kept — <evidence>" or "cut — <what and why>".
Explicitly list every tree you chose NOT to generate and why a default/name
sufficed. If you kept something on thin evidence, say so and mark it `draft`.

### Open Questions
Anything requiring the owner's decision before this graph is approved.
