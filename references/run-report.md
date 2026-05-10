# Run Report

After each agent task, record what happened and whether harness needs update.

## Output Format

```markdown
# Agent Task Run Report

## Task
{task description}

## Context Used
- [file 1]
- [file 2]

## Files Changed
- [file]: [change summary]

## Commands Run
| Command | Result | Notes |
|---|---|---|
| npm run build | pass / fail | |
| npm test | pass / fail | |

## Verification Result
- pass / fail

## Boundary Check
- No changes to high-risk areas: yes / no
- No dependency changes: yes / no
- Minimal diff: yes / no

## Problems Encountered
- [problem or "None"]

## Human Review Feedback
- [feedback or "none"]

## Harness Update Needed
- yes / no
- Reason: [why or why not]
- Suggested sync mode: full / diff / post-task / none
```

## When to Recommend Project-State Sync

Recommend sync if task added:
- New route / page / API / module
- New command or script
- New dependency or config
- New test or verification path
- New business behavior
- Any change to auth / permission / billing / data

Do NOT recommend sync if:
- Pure bug-fix within existing module
- Cosmetic or documentation change
- No new routes, APIs, commands, or risk areas introduced
