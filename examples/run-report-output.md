# Run Report Output Example

Input: (after agent task completes)

## Expected Output

```markdown
# Agent Task Run Report

## Task
Add export-to-CSV button to user list

## Context Used
- AGENTS.md
- CONTEXT-MAP.md
- docs/contexts/frontend/CONTEXT.md
- .harness/commands.md
- .harness/working-boundaries.md
- .harness/testing-and-verification.md

## Files Changed
- src/components/UserList.tsx (added export button)
- src/utils/export.ts (new utility)
- src/components/UserList.test.tsx (added test)

## Commands Run
| Command | Result | Notes |
|---|---|---|
| npm run build | pass | |
| npm test | pass | all 12 tests pass |
| npm run lint | pass | |

## Verification Result
- pass

## Boundary Check
- No changes to high-risk areas: yes
- No dependency changes: yes
- Minimal diff: yes

## Problems Encountered
- None: task was straightforward

## Human Review Feedback
- none

## Harness Update Needed
- no
- Reason: Task added new feature within existing module; no new routes, APIs, commands, or risk areas introduced. Existing harness remains accurate.
```
