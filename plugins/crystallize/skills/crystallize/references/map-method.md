# Map method — Tier-1 skeleton

The method for the **map phase** of the `crystallize` skill. Builds the Tier-1
verifiable skeleton — the generated component index and the `system_map` — by
walking the codebase with grep/glob. Language-agnostic, read-only, no semantic
judgment. On a harness with isolated subagents you may run this in one; otherwise
perform it inline.

You produce the **Tier-1 skeleton** of a `.context` knowledge graph: the part a
machine can derive and a human can verify at a glance. You make **no judgment
calls** — no "this is the canonical one", no anti-patterns, no decision-tree
branches. That is Tier-2 work for other agents. Your output is facts with
`generated_at` provenance.

## What Tier-1 is

Two things, both mechanically derivable:

1. **`index/components.generated.yaml`** — an exhaustive walk of the code units
   in scope. One entry per file that defines a component/module/hook:
   `Name: { path, domain }`. `domain` is a coarse guess from the path (the top
   folder under the source root, or `unknown` if you can't tell). Include test
   and util files; do not filter. This mirrors the reference schema's generated
   index exactly — flat, complete, timestamped.

2. **`system_map` skeleton** — routes/entry files → the modules and components
   they import. Trace real imports; do not infer relationships you didn't read.
   Fields per entry: `entry` (file), `route` (if derivable), `imports` (the
   modules/components it pulls in), `model` (if a data type is obvious). Leave
   prose/judgment fields (`notes`, `cross_module` intent, `label`) empty — Tier-2
   fills those.

## How you work

- **Grep/glob, not AST.** Stay language-agnostic. Find definitions by
  convention (`export function`, `export const`, `class`, `def`, route file
  naming) and imports by grepping import/require/use statements. Never depend on
  a compiler or a stack-specific tool.
- **Count, don't estimate.** For any `consumers`/`used-by` number you emit, grep
  the actual import sites first. A wrong count here poisons Tier-2 downstream.
- **Cite provenance.** Emit a `generated_at` marker (ask the orchestrator for a
  timestamp; never fabricate one) and, for every entry, the `path` you actually
  found.
- **Scope obeys the request.** If given a pattern family (`modais`) or a domain
  (`despesas`), walk only that slice. If given nothing, walk the whole source
  root.
- **Read-only and host-native.** Prefer `rg` and `git ls-files` when available.
  On Windows, PowerShell `Get-ChildItem`/`Select-String` are valid; on Unix,
  `find`/`grep`/`wc` are valid. Never require one shell, and never create or
  modify files — return findings; the orchestrating skill writes them.

## Output format

Return two clearly separated blocks the skill will write verbatim:

### GENERATED_INDEX
```yaml
generated_at: <timestamp the orchestrator gave you>
components:
  <Name>:
    path: <repo-relative path>
    domain: <top-folder guess | unknown>
```

### SYSTEM_MAP_SKELETON
```yaml
system_map:
  <group>:
    <entry-name>:
      entry: <file>
      route: <route or ~>
      imports: [<module/component>, ...]
      model: <type or ~>
```

### Confidence & Gaps
Bullet list: dynamic imports you couldn't resolve, files whose role was unclear,
anything a human should confirm before Tier-2 builds on it.
