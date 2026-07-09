---
name: crystallize-apply
description: Run the consolidation campaign — apply approved duplicate clusters one step at a time, durably and resumably. Each cluster has its own plan + append-only log so a fresh agent can pick up mid-campaign without losing its place or redoing work. Use to apply, consolidate, or continue a crystallize campaign.
---

This is the big, slow phase. Treat it as a **resumable campaign**, never a
one-shot: the work outlasts a context window, so state on disk — not memory — is
the source of truth. Do the smallest durable unit, record it, then the next. The
per-step worker method is in `references/consolidator-method.md`; on a
harness with isolated subagents you may run each step in one, otherwise inline.

The argument is an optional `cluster-id`.

## Step 1 — resolve which cluster to work

Read `.context/status.json`. If absent: "No crystallize run found — run
/crystallize first." Then pick the cluster:

- **cluster-id given** → that cluster. If its `status` is not
  `approved`/`in_progress`/`blocked`, stop: only clusters the human approved can be
  applied.
- **no argument** → resume the campaign: the `execution.active` cluster if one is
  `in_progress`; else the highest-mass `approved` cluster. If none, report the
  campaign is done (or nothing is approved yet) and stop.

If the chosen cluster is `blocked`, show its `blockedReason` and ask the user to
confirm the blocker is resolved before continuing.

## Step 2 — load or build the plan (immutable once started)

Plan lives at `.context/_crystallize/execution/<cluster-id>/plan.json`.

- **Absent** → build it from the cluster's `#### Cluster` block in `VARIATIONS.md`
  and its canonical form in `CRYSTALLIZE_BRIEF.md`. Ordered steps:
  - `s0` — `build-canonical`: create the shared form (glossary name from the
    brief). Verification = the repo's own typecheck/build for that area.
  - `s1..sN` — one `migrate-instance` per instance, each carrying its
    `file:line` ref and a `verification.command` (the narrowest relevant test the
    repo has for that area) with `expected: pass`.
  Write `plan.json` with `schema_version: "crystallize.exec.v1"`. **Never rewrite
  a plan that already exists** — it is the immutable contract the log is measured
  against.
- **Present** → use it as-is.

Set `status.json`: cluster `status` → `in_progress`, `execution.active` →
`<cluster-id>`, `execution.progress[<cluster-id>]` = `{ steps_total, steps_done,
state: "in_progress" }`.

## Step 3 — find the resume point

Read `.context/_crystallize/execution/<cluster-id>/log.jsonl` (append-only; may be
empty/absent). The set of `step_id`s with `outcome: "done"` are complete. The
resume point is the **first plan step not marked done**. Everything before it is
finished — do not rebuild the canonical, do not re-migrate a migrated instance.

## Step 4 — execute steps, one at a time, logging each

For each step from the resume point onward:

1. Run the **consolidator method** (`references/consolidator-method.md`)
   for **that one step only** — pass the step's kind, its `ref` (for migrate), the
   canonical form + glossary name, and the `verification.command`. It does exactly
   that unit, runs the behavior gate, and returns a structured outcome.
2. **Append one line** to `log.jsonl`: `{ step_id, outcome: "done|blocked|failed",
   proof: "<command> → <result>", removed_behavior_audit, deviations }`. Append
   only — never rewrite prior lines.
3. Update `execution.progress[<cluster-id>].steps_done` and re-derive `state`.
4. **If the outcome is not `done`** (behavior gate failed, a dropped guard, or an
   instance that doesn't match the cluster): STOP the cluster. Set cluster
   `status` → `blocked`, `execution.progress[...].state` → `blocked`,
   `blockedReason` = the reason. Report the clean resume point and stop — do not
   limp on to the next step or the next cluster. A half-applied cluster that keeps
   going is how the mess starts.

## Step 5 — close the cluster

When every plan step is `done`: cluster `status` → `applied`; append the
consolidator's cluster summary to `.context/_crystallize/CONSOLIDATION_NOTES.md`;
confirm the graph updates landed (pattern `extends`/`consumers`, curated index);
set `execution.active` → the next `approved` cluster (or null). Run the
project-local graph validator created by `/crystallize`. Prefer `python3` when
available, otherwise `python` on Windows. If the tool or PyYAML is missing, stop
and report the explicit prerequisite instead of skipping validation:

```
<python> ".context/_crystallize/tools/validate-context.py" --context .context --repo .
```

## Step 6 — report

Show: the cluster's progress (`steps_done/steps_total`), the behavior proof of the
steps run this session, any deviations/suspected bugs preserved (these need a human
decision, never a silent merge), and the next command — `/crystallize-apply` to
continue the campaign, or the resolved blocker if one stopped it.
