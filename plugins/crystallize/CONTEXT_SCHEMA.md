# The `.context` contract

This is the generic schema `crystallize` produces and `validate-context.py`
enforces. It is language- and project-agnostic: it describes a YAML knowledge
graph, not any particular codebase. The reference exemplar is DietFlow's
hand-authored `.context`; this contract is the reusable generalization of it.

## Governing principle

**The folder is the type discriminator, not the in-file key.** Classify a file by
its directory (`domains/`, `patterns/`, `trees/`, `index/`). A top-level
`pattern:`/`domain:`/`tree:` key is an optional self-label; never require it.

## Two provenance tiers (kept in separate files)

- **Tier 1 — generated.** `index/components.generated.yaml` carries a real
  `generated_at:` timestamp and flat `{path, domain}` entries (including test/util
  files, `domain: unknown` allowed). The `system_map` skeleton (routes → imports)
  is also Tier-1. Derivable by a grep/glob walk; safe to regenerate.
- **Tier 2 — verified + curated.** Everything with human/agent judgment:
  `patterns/*`, `trees/need-*`, curated `index/components.yaml`, `domains/*`,
  `onboarding.yaml`, and the prose parts of `manifest.yaml`. A node enters Tier 2
  only after a referee confirmed its claims against cited code and a human approved
  it. The anti-fork guard reads Tier 2 only.

## Layout

```
.context/
  onboarding.yaml               # philosophy, decision flows, global anti-patterns
  manifest.yaml                 # entry_points + registry + system_map
  domains/<area>.yaml           # per-area maps
  patterns/<name>.yaml          # named reusable patterns
  trees/need-<goal>.yaml        # decision trees
  index/
    components.yaml             # curated reuse targets
    components.generated.yaml   # generated walk (Tier 1)
  status.json                   # plugin process state
  _crystallize/                 # working artifacts (brief, variations, notes)
```

## Per-category shape

### `manifest.yaml`
- `entry_points`: list of `{ question, goto }` — the agent Q→file router. `goto`
  is a graph path or an intra-file anchor (`#system_map.<group>`).
- `domains`, `patterns`, `trees`: name→path registries.
- `index`: `{ components: index/components.yaml }`.
- `system_map`: map of groups → entries; each entry `{ entry, route?, imports[],
  model?, patterns[]?, notes? }`. Skeleton fields are Tier-1; `notes`/`patterns`
  judgment is Tier-2.

### `domains/<area>.yaml`
- Header: `domain:` (optional self-label), `status: active|draft`, `description`.
  Optional `kind: domain-contract` for a DDD map (`owns`/`does_not_own`,
  `ubiquitous_language` with `means`/`not`, `business_rules` with `must`/`must_not`).
- Body: free path-maps grouped by concern, plus optional `rules[]`, `anti_patterns[]`,
  `todo[]`.

### `patterns/<name>.yaml`
- Header envelope (all optional but recommended): `pattern:`, `version:`,
  `status: active|draft|proposed`, `updated:`.
- Body: free, but the reuse-bearing fields the guard relies on are:
  - `extends:` — the is-a chain (`BaseSearchModal extends BaseModal`).
  - `composes:` — has-a, distinct from extends.
  - `consumers:` / `consumers_list:` — count and/or names of what already uses it.
  - `rules[]`, `anti_patterns[]`, `forbidden[]` — the named bans.
  - `when`/`use_when` — scoping.

### `trees/need-<goal>.yaml`
- Header: `tree:` (matches filename), `status`, `description`.
- Body: one `decision: { question, branches[] }`; each branch `{ answer, result }`
  where `result` names an existing artifact via `use:`/`extends:`/`pattern:`. The
  fork lives only in the `"Outro"`/`"Other"` branch, gated by `warning:`.
- `next_steps[]`.

### `index/components.yaml` (curated) vs `.generated.yaml`
- Curated: `Name: { path, domain, layer?, use?, dependents? }` — selective, reuse
  targets only, semantic fields, no timestamp.
- Generated: `generated_at:` + `Name: { path, domain }` — exhaustive, flat.

## The anti-fork interlock (must have all four layers to have teeth)

1. **Philosophy** (`onboarding.philosophy.core`): the `EXTEND > CREATE | COMPOSE >
   DUPLICATE | INTEGRATE > ISOLATE | QUESTION > IMPLEMENT` default.
2. **Trees**: every substantive branch's `result` names an existing artifact; the
   fork is confined to `"Outro"` under a `warning:`.
3. **Proof**: `extends` chains + `consumers` counts — the thing exists and N things
   use it, so forking is expensive.
4. **Named bans**: `forbidden`/`anti_patterns` naming the specific parallel
   implementation the family tends to spawn.

## Freshness

All freshness fields optional. Accept both `updated:` and `last_updated:`. Tolerate
a trailing parenthetical on a date value (parse the leading `YYYY-MM-DD`). Carry
`status: draft|proposed` forward as a low-confidence flag.

## Cross-references

Plain strings: `patterns/modal.yaml#BaseSearchModal` (`file#dotted.anchor`),
`#system_map.<group>` (intra-file). Referenced paths must exist in the real tree —
`validate-context.py` checks this.
