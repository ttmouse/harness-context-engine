# Diff Review

Review harness changes for weakening of control systems.

## When to Trigger

- Harness files changed
- Optimize executed
- Anyone questions whether control systems were loosened

## Review Rules

**If any rule violated → reject changes.**

| Rule | What to Check |
|---|---|
| Hard Fail preserved | Evaluate Hard Fail rules not deleted or lowered |
| Source/Confidence preserved | New content has Source + Confidence |
| UNKNOWN markers preserved | UNKNOWN not replaced with fake data |
| Sync Gate path preserved | Publication Sync still requires Project-State Sync + Evaluate |
| Post-Task Sync triggers preserved | 7 check questions still present |
| New files have Source mechanism | New harness files include source/confidence |
| Command status not falsified | unverified not changed to verified |

## Specific Hard Fails

- Requires Approval moved to Allowed without evidence → **reject**
- verification requirement removed → **reject**
- Hard Fail removed → **reject**
- command marked verified without execution → **reject**
- ADR/domain fact added without source → **reject**
- UNKNOWN/TODO deleted without resolution → **reject**
- high-risk area removed without source → **reject**

## Output Format

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
