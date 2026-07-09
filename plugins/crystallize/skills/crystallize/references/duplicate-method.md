# Diff method — semantic duplicate clusters

The method for the **diff phase** of the `crystallize` skill. Detects semantic
duplication (catalog → categorize → per-category detect), assigns a stable
`cluster-id`, names the canonical destination, ranks by mass safely reclaimable.
Read-only. Run inline, or in isolated subagents (one per category) where available.

You find **semantic** duplication, not literal duplication. A linter or `jscpd`
finds copy-pasted blocks; you find the same intent expressed twice in different
clothes — different names, different control flow, same underlying rule, helper,
or user problem. This is the failure mode of organically-grown and LLM-written
codebases: a new function/component gets created instead of the existing one
reused. Each thing you find becomes a **cluster** — a set of instances that want
to collapse into one canonical form.

## Method: catalog → categorize → detect (don't skip a step)

Going straight to "find duplicates" over a whole codebase produces noise.
Categorize first so the comparison is focused, then compare within a category.

1. **Catalog (cheap, deterministic).** Extract the definitions in scope —
   exported functions/methods and components — into a flat list of
   `{ file, name, line, signature, context }`. Focus on **exported/public**
   surface; internal one-off helpers rarely duplicate across files.
   - **Optional accelerator (TS/JS only):** if the
     `superpowers-lab:finding-duplicate-functions` skill is installed, its
     `extract-functions.sh` produces exactly this catalog (ripgrep + jq) and its
     `find-duplicates-prompt.md` is a proven per-category detector — use them and
     map the results into the cluster format below. Do not depend on it; if it's
     absent or the language isn't TS/JS, build the catalog yourself with
     grep/glob (language-agnostic).
2. **Categorize (cheap model).** Bucket each catalog entry by *what it does*, not
   how — validation, string/format, date, error-handling, http/api,
   data-transform, money/number, UI surface (modal/form/table), etc. Only a
   category with **3+ entries** is worth comparing.
3. **Detect (this is the expensive, careful pass).** Within each category,
   compare implementations and group same-intent ones into clusters. Read the
   cited code — not just names — to judge how differently each instance behaves.

## Classify every cluster

- **Mechanism** — say which:
  - **Reuse** — N re-implementations of one thing → call one helper/component.
  - **Altitude** — N special cases bolted on shared infra → generalize the
    underlying mechanism so the special cases disappear.
  If the instances only *look* alike but genuinely diverge in behavior, it is not
  a cluster — drop it.
- **Confidence** — HIGH (same input→output semantics), MEDIUM (same purpose,
  minor differences), LOW (possibly related, worth investigating).
- **Recommendation** — CONSOLIDATE (real duplicates, keep the best-named/tested
  one as survivor), INVESTIGATE (need to read more before deciding — flag for
  human), KEEP_SEPARATE (look similar, serve distinct purposes).
  **When in doubt, INVESTIGATE, not CONSOLIDATE** — a wrong merge breaks behavior.

## Guardrails (the mistakes this phase must not make)

- **Focus on the exported surface.** Don't catalog every internal helper.
- **Never skip categorization** — full-catalog comparison is noise.
- **Rank by mass safely reclaimable, not raw count.** 2 instances × 200 lines,
  behavior-identical, outranks 5 × 10 lines with subtle drift. Weight by lines
  *and* by how confidently the collapse preserves behavior.
- **Name the destination.** A cluster without a named canonical target (and, if
  one instance is already the de-facto base, the `extends` target) is not
  actionable.
- **Generic utilities** (identity, noop, thin wrappers) are often intentionally
  duplicated — don't flag them.
- **Never manufacture work.** One occurrence is not a cluster.

## High-risk zones (point the catalog here first)

`utils/`·`helpers/`·`lib/` (general utilities), validation, error formatting,
path manipulation, string/case/truncation, date formatting, API response
shaping, and — for UI — modal/form/table/dashboard families. These accumulate
duplicates fastest.

## Stable IDs

Assign each cluster a `kebab-case` `cluster-id`, descriptive, unlikely to collide
(`money-value-validation`, `expense-modal-layout`). This id is what
`/crystallize-apply <cluster-id>` references later.

## Output format

### VARIATIONS
Ranked by mass safely reclaimable, descending:

```
#### Cluster: <cluster-id>
- **Intent:** <the one rule/problem/helper these express>
- **Category:** <validation | string-utils | modal | ... >
- **Mechanism:** Reuse | Altitude
- **Confidence:** HIGH | MEDIUM | LOW
- **Recommendation:** CONSOLIDATE | INVESTIGATE | KEEP_SEPARATE
- **Instances:**
  - `file:line` — <how this instance differs; null/edge-case handling>
  - `file:line` — <how this instance differs>
- **Mass:** ~<N> lines across <M> instances
- **Canonical destination / survivor:** <the single form; name the extends-target
  or the survivor to keep>
- **Behavior-preservation risk:** Low | Medium | High — <what could drift>
```

### Confidence & Gaps
Anything you suspect is duplication but couldn't confirm without owner context.
