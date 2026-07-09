# Mine method — business + UI intent

The method for the **mine phase** of the `crystallize` skill. Extracts business
rules and UI/layout intent from the code as an informal spec of what the owner
meant. Read-only. Run inline, or in an isolated subagent where available.

You read code the owner wrote recently and knows works, and you extract **why it
exists**, in two tracks: business intent and UI intent. The code is a proof of
concept — its shape is disposable, its intent is what later phases must preserve.
What you produce feeds the Tier-2 curation (domain files and pattern candidates);
it is proposal material, not yet durable graph.

## How you work

- **Given/When/Then for business rules.** Every calculation, validation, or state
  transition becomes a Given/When/Then card with a `file:line` citation. If the
  same rule appears in more than one place, list every occurrence under the same
  card — never create duplicate cards. That co-occurrence is exactly what the
  duplicate-detector needs flagged as one item.
- **Name the problem, not the widget, for UI intent.** For every screen or modal,
  write what user problem it solves ("registrar uma nova despesa parcelada"), not
  what components render it. Then separately note the concrete pattern used today
  (a modal? a stepped form? a slide-over?).
- **Distinguish the rule from how this instance wrote it.** Two modals that both
  validate "valor must be positive, ≤2 decimals" express the same rule even if one
  uses a regex and the other a manual parse. Extract the rule once; note both
  instances as evidence.
- **Cite everything.** No card without a `file:line`. A rule supported only by a
  comment or a string literal — not by executable code — is not a rule; flag the
  discrepancy instead of recording it.

## Output format

Two sections, matching the two tracks the orchestrator will carry into curation:

### BUSINESS_INTENT
```
#### Rule: <short name>
- **Given:** <precondition>
- **When:** <trigger>
- **Then:** <outcome>
- **Instances:** `file:line`, `file:line`, ...
- **Confidence:** High | Medium | Low
```

### UI_INTENT
```
#### Flow: <short name>
- **Problem solved:** <one sentence, business language>
- **Current pattern:** <modal / stepped form / inline edit / etc.>
- **Instances:** `file:line`, `file:line`, ...
- **Notable variation:** <if this flow's pattern differs from a similar flow
  elsewhere, say so and point at it — raw material for the duplicate-detector>
```

### Confidence & Gaps
Anything inferred rather than confirmed, and what you'd ask the owner.
