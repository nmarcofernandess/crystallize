---
description: Read-only report on a crystallize run — phase freshness, graph tiers, approval gate, pending clusters, and the next step. Never writes anything.
argument-hint: [scope]
---

Read `.context/status.json`. If absent: "No crystallize run found. Run
/crystallize [scope] to start." Otherwise report, strictly read-only:

1. **Phases** — for `map`, `mine`, `diff`: last run, and whether stale now
   (recompute `fileHashes` the way `/crystallize` does, compare, do NOT write the
   recomputed values back).
2. **Graph tiers** — does `.context/index/components.generated.yaml` exist and what
   is its `generated_at`? How many curated nodes exist (patterns, trees, curated
   index entries)? Flag any node marked `status: draft`/`proposed` as
   lower-confidence.
3. **Gate** — `pending`/`approved`/`partially_applied`, and whether
   `.context/_crystallize/CRYSTALLIZE_BRIEF.md` exists and is fresh relative to the
   three phase inputs.
4. **Clusters** — a table `cluster-id | mechanism | mass | status`, grouped by
   status, highest-mass pending first.
5. **Next step** — `status.json.nextSuggestedCommand` if set, else derive:
   - any phase stale/missing → `/crystallize [scope]`
   - gate `pending` and brief exists → "review and approve CRYSTALLIZE_BRIEF.md"
   - clusters approved but not applied → `/crystallize-apply <highest-mass pending id> [scope]`
   - graph stale vs code → `/crystallize [scope]` to refresh before trusting the guard
