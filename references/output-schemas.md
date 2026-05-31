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
| code graph | .harness/code-graph/code_graph.json | present / missing / not required | |

## Truth Check
| Claim | Source in Doc | Expected | Actual | Confidence | Status |
|---|---|---|---|---|---|
| | | | | | |

## Command Check
| Purpose | Command | Source File | Status | Execution Result |
|---|---|---|---|---|
| | | | | |

## Code Graph Check
| Check | Status | Notes |
|---|---|---|
| JSON parse | pass / fail / not present | |
| node references | pass / fail / not present | |
| edge evidence | pass / fail / not present | |
| path existence | pass / fail / skipped | |
| inferred-edge ratio | pass / warning / not present | |
| graph usefulness | pass / warning / not present | |

## Hard Fail Items (if any)
- [rule]: [file or claim]

## Optimization Suggestions
1. [suggestion]

## UNKNOWN / TODO
- [item]: reason
```

## Code Graph JSON

`code_graph.json` may be stored at `.harness/code-graph/code_graph.json` when relationship evidence is useful.

It can also be emitted by `scripts/generate_code_graph.py` and validated by `scripts/validate_code_graph.py`.

```json
{
  "project": {
    "name": "",
    "type": "",
    "root": "",
    "generated_at": "",
    "confidence": "high | medium | low",
    "main_languages": [],
    "frameworks": []
  },
  "nodes": [
    {
      "id": "",
      "type": "file | module | page | component | route | api | controller | service | function | class | model | table | field | config | test | doc | business_feature",
      "name": "",
      "path": "",
      "description": "",
      "source": "",
      "confidence": "high | medium | low",
      "claim_type": "observed | inferred | unknown"
    }
  ],
  "edges": [
    {
      "source": "",
      "target": "",
      "type": "imports | calls | renders | routes_to | handles | reads | writes | updates | depends_on | tests | documents | implements | affects | configures",
      "description": "",
      "evidence": "",
      "confidence": "high | medium | low",
      "claim_type": "observed | inferred | unknown"
    }
  ],
  "features": [
    {
      "name": "",
      "entry_points": [],
      "implementation_nodes": [],
      "data_nodes": [],
      "test_nodes": [],
      "risk_points": [],
      "unknowns": []
    }
  ],
  "risk_edges": [
    {
      "edge": "",
      "reason": "",
      "approval_required": true,
      "recommended_verification": []
    }
  ],
  "unknowns": []
}
```

Rules:

- Every edge must include evidence.
- High-confidence edges must be directly observable.
- Inferred edges must not be used as confirmed project facts.
- Business-feature nodes require source-backed business context.
- Empty graphs or node-only graphs should not be used for impact analysis.

## Context Pack

```markdown
# Context Pack

## Task
{task description}

## Classification
- Change Type:
- Affected Areas:
- Risk Level:

## Must Read
1. AGENTS.md
2. CONTEXT-MAP.md
3. [relevant harness/context files]

## Likely Files to Read
- [file]

## Likely Files to Change
- [file]

## Affected Relationships
| Source | Relationship | Target | Evidence | Confidence |
|---|---|---|---|---|
| | | | | |

## Do Not Touch
- [protected area] (reason)

## Required Verification
- [command]: must pass

## Stop Conditions
- [condition]

## Human Approval Required If
- [condition]
```

## Project-State Sync Report

```markdown
# Project-State Sync Report

## Summary
- Project path:
- Sync mode: full / diff / post-task
- Hard Fail: yes / no
- Harness update needed: yes / no
- Code graph update needed: yes / no / not present

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
| Code graph evidence not weakened | pass / fail | |

## Decision
- **approved** / **rejected**

## Rejection Reason (if rejected)
- [rule violation details]
```
