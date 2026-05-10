# Optimize Harness

**Goal: reduce repeated agent failures, not make documents longer.**

## Input Sources

1. Latest Harness Self-Test Report
2. Recent failed agent tasks
3. Recent CI / build / test failures
4. Human review corrections
5. `.harness/failure-analysis.md`
6. UNKNOWN / TODO list
7. Recent repeated mistakes
8. Recent over-edit or unsafe-change cases

## Workflow

1. Collect failure records
2. Identify failure patterns
3. For each pattern:
   - What failure does it prevent?
   - Which file to update?
   - Is it feedforward (prevention) / feedback (correction) / routing (context routing)?
   - Should a test, command, or static check be added instead of documentation?
4. Propose optimizations
5. Apply only high-confidence changes
6. Run Evaluate

## For Each Optimization, Explain

1. What failure or risk it prevents
2. Which file should be updated
3. Whether it adds feedforward, feedback, or routing
4. Whether a script/test should be added instead of docs

## Output Format

```markdown
# Harness Optimization Report

## Input Sources
- [source 1]
- [source 2]

## Optimizations
| Optimization | File To Update | Type | Reason |
|---|---|---|---|
| | | feedforward / feedback / routing | |

## Changes Applied
- [file]: [summary]

## Changes Rejected
- [rejected change]: reason

## Evaluate Result After Optimize
- Hard Fail: yes / no
- Score: X/10
```

## Do NOT

- Add rules without evidence of failure
- Make documents longer without clear benefit
- Add generic best-practice rules that aren't project-specific
- Optimize without running Evaluate after
