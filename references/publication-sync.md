# Publication Sync

Publish evaluated harness to external destination (Git, Gitea Wiki, internal wiki, team docs, knowledge base).

## Pre-flight Check（All must pass → publish. Any fails → block.）

1. Project-State Sync has been run
2. Evaluate passes (no Hard Fail)
3. All high-risk UNKNOWN items are resolved or marked NEEDS HUMAN REVIEW
4. Diff summary generated

## Workflow

1. Confirm pre-flight check passed
2. Identify publication target
3. Generate diff summary
4. Execute publication
5. Confirm publication

## Block If

- Evaluate has Hard Fail
- Any high-risk UNKNOWN unresolved
- Project-State Sync not run
- Diff-review rejected (if Diff-Review requested)

## Output Format

```
# Publication Sync Report

## Pre-flight Check
- Project-State Sync: done / blocked
- Evaluate: passed / failed
- Hard Fail: none / [items]
- High-risk UNKNOWN: none / [items]

## Publication Target
- [Git / Gitea Wiki / internal wiki / team docs / knowledge base]

## Diff Summary
- [file]: [change summary]

## Publication Decision
- **published** / **blocked**

## Block Reason (if blocked)
- [reason]
```
