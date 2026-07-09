---
description: Consolidate a stable prototype into canonical architecture — maps the area, mines business and UI intent, detects semantic duplication, and synthesizes a consolidation brief for human approval. Single entry point; never call map/mine/diff separately.
argument-hint: [area]
---

`area` (optional): a path within the current project to scope this run.
If omitted, scope is the whole repo (slug: `whole-repo`).

Compute `area-slug` from `$1` (or `whole-repo`): lowercase, replace `/`
and spaces with `-`. All artifacts for this run live in
`analysis/crystallize/<area-slug>/`.

## Step 0: Load or initialize STATUS.json

Read `analysis/crystallize/<area-slug>/STATUS.json` if it exists — schema:

```json
{
  "area": "<area-slug>",
  "phases": {
    "map": { "lastRun": null, "fileHashes": {} },
    "mine": { "lastRun": null, "fileHashes": {} },
    "diff": { "lastRun": null, "fileHashes": {} }
  },
  "gate": "pending",
  "patterns": [],
  "nextSuggestedCommand": null
}
```

If it doesn't exist, create it with the above defaults (all `lastRun`
null, empty `fileHashes`, empty `patterns`).

**Staleness check:** for each phase already run, recompute
`shasum -a 256` for every file listed in its `fileHashes` and compare. If
any differ, or if new files exist in the target area that aren't in
`map`'s `fileHashes`, that phase (and every phase after it) is stale and
must re-run.

## Step 1: map phase (if missing or stale)

Invoke the `inventory-mapper` agent, scoped to `area` (or the whole repo).
Write its output to `analysis/crystallize/<area-slug>/INVENTORY.md`.
Update `STATUS.json`: `phases.map.lastRun` = now, `phases.map.fileHashes`
= hash of every file the agent cited.

## Step 2: mine phase (if missing or stale, or map just re-ran)

Invoke the `intent-extractor` agent, passing it `INVENTORY.md`. Split its
returned output into `analysis/crystallize/<area-slug>/BUSINESS_INTENT.md`
and `.../UI_INTENT.md`. Update `STATUS.json` phases.mine the same way as
Step 1.

## Step 3: diff phase (if missing or stale, or mine just re-ran)

Invoke the `pattern-detector` agent, passing it `INVENTORY.md`,
`BUSINESS_INTENT.md`, and `UI_INTENT.md`. Write its output to
`analysis/crystallize/<area-slug>/VARIATIONS.md`. Parse every `#### Pattern:
<pattern-id>` block into `STATUS.json.patterns` as
`{ id, description: <Intent line>, impact: <parsed N from Impact line>, status: "pending" }`,
preserving any existing entry's `status` if that `pattern-id` was already
present (don't reset an `applied` pattern back to `pending` on a re-run).
Update `phases.diff` the same way.

## Step 4: only when map, mine, and diff are ALL fresh — synthesize the brief

If any phase above just ran due to staleness, stop here and report what
was refreshed; do not synthesize a new brief in the same invocation
against a partially-stale state — re-run `/crystallize` once more to
confirm nothing changed, then proceed. (In practice: if Steps 1–3 made no
changes because everything was already fresh, continue immediately.)

Invoke the `canonical-architect` agent, passing it `INVENTORY.md` and
`VARIATIONS.md`. Write its output as
`analysis/crystallize/<area-slug>/CRYSTALLIZE_BRIEF.md`.

Set `STATUS.json.gate` = `"pending"` if it was previously unset, or leave
as-is if already `"approved"`/`"partially_applied"` (a brief regenerated
after new variations doesn't silently re-approve itself — flag this to
the user explicitly if `gate` was already `"approved"`).

Set `nextSuggestedCommand` to `"review CRYSTALLIZE_BRIEF.md and approve"`.

## Step 5: present and stop

Present a summary of the brief (taxonomy, top patterns by impact, phase
count). **Enter plan mode if the session supports it, and stop — write
nothing further until the user explicitly approves.** Approving here
means the user will tell you which `pattern-id`s move to `"approved"` in
`STATUS.json` (do that update once they confirm) — only then can
`/crystallize-apply` run against them.
