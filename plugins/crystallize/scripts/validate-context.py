#!/usr/bin/env python3
"""
validate-context.py — structural validator for a .context knowledge graph.

Language- and project-agnostic: it validates the YAML graph itself, never the
target code. Enforces the core "the graph must be TRUE" lock:

  1. every .context/*.yaml parses
  2. index/components.generated.yaml carries a generated_at
  3. every `path:` in the graph points to a file that really exists (anti-lie)
  4. every internal file cross-reference (file#anchor / graph-relative path)
     resolves to a real graph file
  5. reports nodes marked status: draft|proposed as lower-confidence

Exit code 0 = clean, 1 = validation failures, 2 = cannot run (missing dep / no graph).

Usage:  validate-context.py [--context DIR] [--repo ROOT]
        (defaults: --context ./.context  --repo .)
"""
import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("validate-context: needs PyYAML — `pip install pyyaml` (or run in an env that has it).", file=sys.stderr)
    sys.exit(2)


def walk_yaml(context_dir):
    for root, _dirs, files in os.walk(context_dir):
        if os.sep + "_crystallize" in root:  # working artifacts, not graph
            continue
        for f in files:
            if f.endswith((".yaml", ".yml")):
                yield os.path.join(root, f)


def iter_strings(node):
    """Yield every string value anywhere in a parsed YAML tree."""
    if isinstance(node, dict):
        for v in node.values():
            yield from iter_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_strings(v)
    elif isinstance(node, str):
        yield node


def find_paths(node):
    """Yield string values sitting under a `path:` (or `*_path`) key."""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and (k == "path" or str(k).endswith("_path")):
                yield v
            else:
                yield from find_paths(v)
    elif isinstance(node, list):
        for v in node:
            yield from find_paths(v)


REF_RE = re.compile(r"^(?:\./)?(?:\.context/)?([A-Za-z0-9_./-]+\.ya?ml)(#.*)?$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", default=".context")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()

    ctx = args.context
    repo = args.repo
    if not os.path.isdir(ctx):
        print(f"validate-context: no graph at {ctx} — run /crystallize first.", file=sys.stderr)
        sys.exit(2)

    errors, warnings, low_conf = [], [], []
    parsed = {}

    # 1. parse every graph YAML
    for path in walk_yaml(ctx):
        try:
            with open(path, encoding="utf-8") as fh:
                parsed[path] = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            errors.append(f"parse error: {path}: {e}")

    # 2. generated index must carry generated_at
    gen = os.path.join(ctx, "index", "components.generated.yaml")
    if os.path.isfile(gen):
        data = parsed.get(gen)
        if not (isinstance(data, dict) and data.get("generated_at")):
            errors.append(f"{gen}: missing generated_at (Tier-1 provenance marker)")
    else:
        warnings.append(f"{gen}: absent — no Tier-1 generated index yet")

    graph_files = {os.path.relpath(p, repo) for p in parsed}

    for path, data in parsed.items():
        if data is None:
            continue

        # 3. every `path:` must resolve against the repo
        for p in find_paths(data):
            target = os.path.normpath(os.path.join(repo, p))
            if not os.path.exists(target):
                errors.append(f"{os.path.relpath(path, repo)}: dangling path `{p}` (graph references a file that does not exist)")

        # 4. internal file#anchor references must resolve to a graph file
        for s in iter_strings(data):
            m = REF_RE.match(s)
            if not m:
                continue
            ref_file = m.group(1)
            candidates = {
                os.path.normpath(os.path.join(ctx, ref_file)),
                os.path.normpath(os.path.join(repo, ref_file)),
            }
            if not any(os.path.isfile(c) for c in candidates):
                # only complain when it looks like a graph ref (yaml) we own
                rel_ctx = os.path.normpath(os.path.join(ctx, ref_file))
                if rel_ctx.startswith(os.path.normpath(ctx)):
                    warnings.append(f"{os.path.relpath(path, repo)}: unresolved graph reference `{s}`")

        # 5. draft/proposed = lower confidence
        if isinstance(data, dict):
            st = str(data.get("status", "")).lower()
            if st in ("draft", "proposed"):
                low_conf.append(f"{os.path.relpath(path, repo)} (status: {st})")

    # report
    def section(title, items):
        if items:
            print(f"\n{title} ({len(items)}):")
            for it in items:
                print(f"  - {it}")

    section("ERRORS", errors)
    section("WARNINGS", warnings)
    section("LOW-CONFIDENCE NODES", low_conf)

    total_graph = len([p for p in parsed if "_crystallize" not in p])
    print(f"\nvalidate-context: {total_graph} graph files, {len(errors)} errors, "
          f"{len(warnings)} warnings, {len(low_conf)} low-confidence.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
