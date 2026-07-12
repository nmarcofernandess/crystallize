---
name: crystallize-guard
description: Anti-fork check — before you build something new, ask the .context graph whether a canonical form already exists. Read-only, fast, staleness-aware. The day-to-day workhorse that makes forking a justified exception. Use before creating a component, helper, modal, or pattern to check whether one already exists to reuse.
---

The argument is a description of what you're about to create — "a modal to pick a
category", "a helper to validate a money value", "a dashboard for expenses". Your
job is to answer, from the graph, one question: **does a canonical form for this
already exist, so you should reuse/extend instead of fork?**

This skill is read-only. It never writes to `.context/` or to code.

## Step 1 — staleness check first

Read `.context/status.json`. Recompute SHA-256 for the relevant phase's
`fileHashes` without updating them. Use PowerShell `Get-FileHash` on Windows,
`sha256sum` on Linux, or `shasum -a 256` on macOS, matching the portable
digest rules in `/crystallize`. For a machine anti-lie/staleness signal, also
run the project-local validator created by `/crystallize` and factor its verdict
in. Prefer `python3` when available, otherwise `python` on Windows:

```
<python> ".context/_crystallize/tools/validate-context.py" --context .context --repo .
```

If the graph is stale relative to the code, the validator reports dangling paths,
the project-local validator is missing, PyYAML is unavailable, or `.context/`
doesn't exist, say so up front and answer with reduced confidence — a guard
speaking confidently from a rotted map is a footgun:

```
⚠ .context is stale (code changed since last /crystallize) — treat this answer as
a hint, re-run /crystallize <scope> to trust it.
```

## Step 2 — consult Tier-2 only

Read the curated graph, never the raw generated skeleton:
1. The matching `trees/need-<goal>.yaml` if one exists for this kind of thing —
   walk its branches to the recommended existing artifact.
2. The matching `patterns/<name>.yaml` — its `extends` chain, `consumers` counts,
   `rules`, and `anti_patterns`/`forbidden`.
3. The curated `index/components.yaml` for a reuse target by name/purpose.

Nodes marked `status: draft`/`proposed` are lower-confidence — name them as
suggestions, not settled canon.

## Step 3 — answer

**If a canonical form exists:**
```
✋ Reuse, don't fork.
- Canonical: <name> (`path`) — <N> consumers already.
- Extend: <the base/branch the tree points to> for your case.
- Forbidden: <the named parallel implementation this family bans, if any>.
To fork anyway you must justify: which existing branch does your case NOT fit, and
why can't <canonical> be extended to cover it?
```

**If nothing matches (a genuinely new concept):**
```
✅ No canonical form found for "<what>". This looks new.
- Nearest existing: <closest pattern/component, or "none">.
- If you build it, consider running /crystallize <scope> afterward so it enters
  the graph and the next person reuses it instead of re-forking.
```

Keep it short. The value is a fast, honest yes/no with the reuse target named — not
an essay.
