# Output Schemas

## Evaluate Report

```markdown
# Harness Evaluation Report

## Summary
- Hard Fail: yes / no
- Score: X/10
- Status: pass / needs-optimization / fail

## Structure Check
| Item | File | Status | Notes |
|---|---|---|---|
| entry | AGENTS.md | present / missing | |
| routing | CONTEXT-MAP.md | present / missing | |
| context | CONTEXT.md | present / missing | |
| commands | .harness/commands.md | present / missing | |
| workflow | .harness/task-workflow.md | present / missing | |
| boundaries | .harness/working-boundaries.md | present / missing | |
| verification | .harness/testing-and-verification.md | present / missing | |

## Truth Check
| Claim | Source in Doc | Expected | Actual | Confidence | Status |
|---|---|---|---|---|---|
| | | | | | |

## Command Check
| Purpose | Command | Source File | Status | Execution Result |
|---|---|---|---|---|
| | | | | |

## Hard Fail Items (if any)
- [rule]: [file or claim]

## Optimization Suggestions
1. [suggestion]

## UNKNOWN / TODO
- [item]: reason
```

## Project-State Sync Report

```markdown
# Project-State Sync Report

## Summary
- Project path:
- Sync mode: full / diff / post-task
- Hard Fail: yes / no
- Harness update needed: yes / no

## Detected Project Changes
| Change | Path | Type | Source | Confidence |
|---|---|---|---|---|
| | | | | |

## Applied Updates
- [file]: [change summary]

## Needs Human Review
- [item]: reason

## No-op Changes
- [change]: reason

## Evaluate Result
- Hard Fail: yes / no
- Score: X/10
- Status: pass / fail
```

## Publication Sync Report

```markdown
# Publication Sync Report

## Pre-flight Check
- Project-State Sync: done / blocked
- Evaluate: passed / failed
- Hard Fail: none / [items]
- High-risk UNKNOWN: none / [items]

## Publication Target
- [target]

## Diff Summary
- [file]: [change summary]

## Publication Decision
- **published** / **blocked**

## Block Reason (if blocked)
- [reason]
```

## Diff-Review Report

```markdown
# Diff-Review Report

## Changed Files
- [file]: [change summary]

## Review Results
| Rule | Status | Notes |
|---|---|---|
| Hard Fail preserved | pass / fail | |
| Source/Confidence preserved | pass / fail | |
| UNKNOWN markers preserved | pass / fail | |
| Sync Gate path preserved | pass / fail | |
| Post-Task Sync triggers preserved | pass / fail | |
| New files have Source mechanism | pass / fail | |
| Command status not falsified | pass / fail | |

## Decision
- **approved** / **rejected**

## Rejection Reason (if rejected)
- [rule violation details]
```
