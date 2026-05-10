# Diff Review

## When to Use

- Harness files have been modified (manual edit or Optimize)
- Before approving any harness change PR/merge request
- When reviewing if an optimization has weakened controls
- As a gate before Publication Sync

**Key principle:** Diff Review is specifically concerned with whether changes **weaken** control systems. Adding new rules or restrictions is generally acceptable. Moving from "Requires Approval" to "Allowed" is not.

## Inputs

- Git diff of harness files (before/after)
- Current harness files for context
- Previous Evaluate report (if available)

## Workflow

Review harness changes for weakening of control systems.

1. Get the diff of changed harness files
2. Check each review rule against the diff
3. If any rule violated → reject changes
4. Report specific violations

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

## Stop Conditions

- Any single violation → reject immediately. No partial approval.
- If diff is empty or only cosmetic → no review needed, skip
- If no harness files were changed → skip

## Related Scripts

| Script | Role |
|---|---|
| `scripts/validate_harness_diff.py` | Automated regex-based diff checking (early prototype) |
| `scripts/check_commands.py` | Validates command status changes |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Missing weakened boundaries | Focusing on additions, not removals | Always check what was removed or relaxed |
| Approving "Requires Approval" → "Allowed" moves | Not recognizing this as weakening | Flag any approval-level downgrade |
| Missing command status falsification | Not checking if unverified → verified without execution | Cross-check with check_commands.py output |
| Reviewing only additions | Only checking what's new, not what changed | Always review full diff, not just added lines
