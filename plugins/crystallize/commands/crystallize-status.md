---
description: Read-only report on a crystallize run — phases completed and when, staleness, approval gate state, and pattern status. Suggests the next command.
argument-hint: [area]
---

`area` (optional): same `area-slug` resolution as `/crystallize`; defaults
to `whole-repo`.

Read `analysis/crystallize/<area-slug>/STATUS.json`. If it doesn't exist,
report: "No crystallize run found for this area. Run /crystallize
[area] to start."

Otherwise report, read-only (never write anything in this command):

1. **Phases:** for `map`, `mine`, `diff` — last run timestamp, and
   whether it's currently stale (recompute file hashes the same way
   `/crystallize` does, compare against stored `fileHashes`, without
   updating the stored values).
2. **Gate:** current value (`pending`/`approved`/`partially_applied`),
   and whether `CRYSTALLIZE_BRIEF.md` exists and is fresh relative to the
   three phase files.
3. **Patterns:** a table — `pattern-id | status | impact` — grouped by
   status, most-impactful pending pattern first.
4. **Next step:** `STATUS.json.nextSuggestedCommand` if set, otherwise
   derive one: if any phase is stale or missing → `/crystallize [area]`;
   if the gate is `pending` and the brief exists → "review and approve
   CRYSTALLIZE_BRIEF.md"; if patterns are approved but not applied →
   `/crystallize-apply <highest-impact pending pattern-id> [area]`.
