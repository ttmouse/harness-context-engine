# Evaluate Output Example

Input: `evaluate harness for ~/Projects/my-react-app`

## Expected Output

```markdown
# Harness Evaluation Report

## Summary
- Hard Fail: no
- Score: 9/10
- Status: pass

## Structure Check

| Item | File | Status | Notes |
|---|---|---|---|
| entry | AGENTS.md | present | |
| routing | CONTEXT-MAP.md | present | |
| context | CONTEXT.md | present | |
| commands | .harness/commands.md | present | |
| workflow | .harness/task-workflow.md | present | |
| boundaries | .harness/working-boundaries.md | present | |
| verification | .harness/testing-and-verification.md | present | |

## Truth Check

| Claim | Source in Doc | Expected | Actual | Confidence | Status |
|---|---|---|---|---|---|
| language | package.json | TypeScript | TypeScript | high | match |
| framework | package.json deps | React | React | high | match |
| module:src/components | src/ directory | exists | exists | high | match |
| module:src/api | src/ directory | exists | NOT FOUND | - | gap |

## Command Check

| Purpose | Command | Source File | Status | Execution Result |
|---|---|---|---|---|
| dev | npm run dev | package.json scripts | verified | exit 0 |
| build | npm run build | package.json scripts | verified | exit 0 |
| test | npm test | package.json scripts | failed | exit 1 |

## Optimization Suggestions

1. **Add src/api to module list**: Truth Check gap detected
```
