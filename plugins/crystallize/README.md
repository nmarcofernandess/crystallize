# crystallize

Point this at a stable, self-authored prototype and get back: a structural
map, the business and UI intent mined from the code, the semantic
duplication that accumulated during iteration, and an approved
consolidation brief — then apply it one pattern at a time with an
equivalence test proving nothing drifted.

Unlike `code-modernization`, the source here is **trusted** (your own
recent code) and the target is the **same stack** — this isn't a rewrite,
it's canonicalization: same intent, fewer variations, one name per concept.

## Install

```
/plugin marketplace add nmarcofernandess/crystallize
/plugin install crystallize@crystallize
```

## Usage

```
/crystallize                       # whole repo
/crystallize src/apresentacao      # scoped to one area
```

Runs map → mine → diff internally, writes artifacts to
`analysis/crystallize/<area>/`, and stops at a plan-mode approval gate
once `CRYSTALLIZE_BRIEF.md` is ready. Review it, then approve the
patterns you want applied (mark them `"approved"` in `STATUS.json`, or
say so and have the session do it).

```
/crystallize-apply <pattern-id>    # apply one approved pattern
/crystallize-status                # read-only progress report
```

## Artifacts

All under `analysis/crystallize/<area-slug>/`:

- `INVENTORY.md` — entry points, components, domain modules, component graph
- `BUSINESS_INTENT.md` / `UI_INTENT.md` — extracted rules and UI intent
- `VARIATIONS.md` — detected semantic duplication, ranked by impact
- `CRYSTALLIZE_BRIEF.md` — taxonomy, glossary, phased plan (the approval gate)
- `CONSOLIDATION_NOTES.md` — what `/crystallize-apply` actually changed, per pattern
- `STATUS.json` — machine state: phase freshness, gate, pattern statuses

## Agents

- `inventory-mapper` — structural map (map phase)
- `intent-extractor` — business + UI intent (mine phase)
- `pattern-detector` — semantic duplication detection (diff phase)
- `canonical-architect` — target taxonomy + glossary + phased plan, with a
  built-in adversarial pass against over-engineering (brief synthesis)
- `consolidator` — applies one approved pattern (`/crystallize-apply`)

## License

MIT — see repository root.
