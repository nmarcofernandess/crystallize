---
description: Apply ONE approved duplicate cluster from the crystallize brief — collapse its instances into the canonical form, prove behavior didn't drift against the repo's own harness, and update the .context graph. Refuses clusters that aren't approved.
argument-hint: <cluster-id> [scope]
---

`cluster-id`: required, must match an entry in `.context/status.json.clusters`.
`scope` (optional): same classification as `/crystallize`; used only to resolve
which `.context` you're in (a repo has one `.context/` at root, so this is almost
always inferable).

## Step 1 — load and validate

Read `.context/status.json`. If absent: "No crystallize run found — run
/crystallize first." Find `$1` in `clusters`. If missing, stop and list the known
cluster-ids. If its `status` is not `"approved"`, stop:

```
Cluster "<id>" is "<status>", not approved. /crystallize-apply only runs against
clusters the human approved in CRYSTALLIZE_BRIEF.md. Approve it (re-run
/crystallize and approve through the gate) before applying.
```

## Step 2 — gather context

From `.context/_crystallize/VARIATIONS.md`, extract the full `#### Cluster: <id>`
block (intent, mechanism, instances, canonical destination, behavior-preservation
risk). From `.context/_crystallize/CRYSTALLIZE_BRIEF.md` and the live graph,
extract the canonical form's pattern entry and the glossary name it must use.

## Step 3 — apply

Invoke `consolidator` with exactly that context — the cluster's instance list, its
mechanism (Reuse or Altitude), its canonical destination, its glossary name.
Nothing else. The consolidator runs the behavior gate (the repo's own tests/
typecheck) and the removed-behavior audit itself.

## Step 4 — record

Append the consolidator's summary to `.context/_crystallize/CONSOLIDATION_NOTES.md`
under a timestamped heading. Set this cluster's `status` → `"applied"`. Set `gate`
→ `"partially_applied"` while any cluster remains not-yet-terminal; leave it as-is
once every cluster is `"applied"`/`"discarded"`. Confirm the consolidator's graph
updates landed in `.context/` (pattern `extends`/`consumers`, curated index).

## Step 5 — report

Show the consolidator's summary, and surface loudly:
- the **behavior proof** (exact command + result) — if it didn't pass, the cluster
  is NOT done; leave it `"approved"` and report the failure honestly.
- any **deviations / suspected bugs** it preserved — those need a human decision,
  not a silent merge.
