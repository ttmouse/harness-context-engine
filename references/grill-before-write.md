# Grill Before Write

## Purpose

Grill Before Write prevents the skill from turning weak inferences into harness facts.

When business language, architecture intent, ownership boundary, or risk meaning is unclear, do not write it as fact. First challenge the claim, inspect available evidence, and either confirm it, surface a conflict, ask a targeted question, or mark it UNKNOWN.

This reference is inspired by the discipline of grilling a plan against existing code, context, and domain language before updating project context.

## When to Use

Use this whenever the agent is about to write or update:

- domain language;
- business rules;
- module ownership;
- architecture intent;
- ADR content;
- risk boundaries;
- task routing assumptions;
- CONTEXT.md or docs/contexts/* content;
- known-risks or working-boundaries.

Do not use this for obvious observed facts such as file paths, package scripts, or config values. Those should be cited directly.

## Core Rule

Use this order:

1. Inspect code and existing harness/context.
2. If code or docs answer it, write with source/confidence/type.
3. If code conflicts with existing context or user claim, surface the conflict.
4. If code cannot answer it, ask one targeted clarification question.
5. If no answer is available, mark UNKNOWN / NEEDS HUMAN REVIEW.

## What Counts as Unclear

A claim is unclear when it relies on meaning rather than direct observation.

Examples:

| Claim Type | Safe Handling |
|---|---|
| "Reports means revenue reporting" | Inferred from name only; mark LOW CONFIDENCE unless docs/code confirm |
| "This service owns billing" | Confirm from code/docs or mark UNKNOWN |
| "We chose this architecture for scalability" | Requires ADR or explicit source; do not invent |
| "Auth changes are high risk" | Can be a general risk, but cite observed auth files or mark inferred |
| "This route is admin-only" | Verify in route guards, middleware, docs, or tests |

## Conflict Handling

If user claim, code, existing CONTEXT.md, and ADR disagree, do not silently choose one.

Output:

```md
# Context Conflict

## Conflict

## Sources

| Source | Claim |
|---|---|

## Possible Interpretations

## Recommended Clarification Question

## Safe Temporary Handling
```

Safe temporary handling usually means:

- keep existing harness unchanged;
- mark the item UNKNOWN;
- add NEEDS HUMAN REVIEW;
- avoid generating ADR/domain facts until clarified.

## Clarification Question Rules

Ask only one targeted question at a time.

Good questions:

- "Is Reports a financial reporting area, an operational dashboard, or only a placeholder route?"
- "Is this dependency change allowed without approval, or should it remain Requires Approval?"
- "Does this domain term come from product language, customer language, or code-only naming?"

Bad questions:

- "Please explain the whole project."
- "What should I write in the context?"
- "Can you confirm everything?"

## Write Rules

When writing after grilling:

- observed facts may be written as confirmed;
- inferred meaning must be marked INFERRED;
- unsupported claims must remain UNKNOWN;
- disputed claims must be listed as conflicts;
- formal ADRs require decision evidence;
- domain.md requires source-backed domain terms.

## Stop Conditions

Stop and escalate if:

- a requested harness update would encode a business rule with no source;
- a requested ADR has no real decision evidence;
- a risk boundary is being weakened without explicit approval;
- code and docs contradict each other on a safety-critical area;
- the agent cannot identify whether a claim is observed or inferred.

## Related References

| Reference | Relationship |
|---|---|
| `references/source-confidence.md` | Defines source/confidence/type markings |
| `references/project-profile.md` | Captures uncertain facts before generation |
| `references/generate.md` | Uses Grill Before Write before creating domain/ADR/risk files |
| `references/project-state-sync.md` | Uses conflict handling when code and harness diverge |
| `references/diff-review.md` | Blocks weakened harness rules |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Business meaning invented from route name | Agent treats naming as fact | Ask or mark UNKNOWN |
| Fake ADR | Agent explains architecture after the fact | Require decision evidence |
| Silent conflict overwrite | Agent picks one source without saying so | Use Context Conflict format |
| Over-questioning | Agent asks broad questions instead of inspecting code | Inspect code first; ask one targeted question only |
| Low-confidence rule becomes permanent | Inference is written as confirmed | Use INFERRED / LOW CONFIDENCE / NEEDS HUMAN REVIEW |
