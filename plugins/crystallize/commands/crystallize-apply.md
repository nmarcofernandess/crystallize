---
description: Apply ONE approved pattern from a crystallize brief — extracts the canonical shape, migrates its instances, and proves equivalence with a test. Refuses to run against a pattern that isn't approved.
argument-hint: <pattern-id> [area]
---

`pattern-id`: required, must match an entry in `STATUS.json.patterns`.
`area` (optional): same `area-slug` resolution as `/crystallize`; defaults
to `whole-repo` if omitted.

## Step 1: Load state and validate

Read `analysis/crystallize/<area-slug>/STATUS.json`. If it doesn't exist,
stop: "No crystallize run found for this area — run /crystallize first."

Find `$1` in `STATUS.json.patterns`. If missing, stop and list the known
`pattern-id`s. If found but `status` is not `"approved"`, stop:

```
Pattern "<pattern-id>" is "<status>", not approved. /crystallize-apply
only runs against patterns the human approved in CRYSTALLIZE_BRIEF.md —
mark it approved in STATUS.json (or re-run /crystallize and approve it
through the plan-mode gate) before applying.
```

## Step 2: Gather the pattern's context

From `VARIATIONS.md`, extract the full `#### Pattern: <pattern-id>` block
(intent, instances, suggested canonical shape). From
`CRYSTALLIZE_BRIEF.md`, extract the taxonomy row and glossary terms that
reference this `pattern-id`.

## Step 3: Apply

Invoke the `consolidator` agent with exactly that context — the pattern's
instance list, its canonical-shape suggestion, and its glossary terms.
Nothing else.

## Step 4: Record the result

Append the agent's returned summary to
`analysis/crystallize/<area-slug>/CONSOLIDATION_NOTES.md` under a
timestamped heading. Update `STATUS.json`: this pattern's `status` →
`"applied"`. If this was the last `"approved"` pattern, set
`STATUS.json.gate` = `"partially_applied"` only if some patterns from the
brief remain `"pending"`/not-yet-approved, or leave `gate` as-is if every
pattern reached a terminal state (`"applied"`/`"discarded"`).

## Step 5: Report

Show the consolidator's summary to the user, including any "Deviations
found" it reported — those need a human decision, not a silent merge into
the canonical shape.
