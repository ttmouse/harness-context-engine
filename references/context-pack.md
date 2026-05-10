# Context Pack

Given a task or issue, generate minimal task-specific context pack.

## Input

- Task description or issue text

## Output

```markdown
# Context Pack

## Task
{task description}

## Classification
- Change Type: bug-fix / feature / refactor / testing / docs / investigation
- Affected Areas: frontend, backend, auth, database, etc.
- Risk Level: low / medium / high

## Must Read
1. AGENTS.md
2. CONTEXT-MAP.md
3. [relevant context files from CONTEXT-MAP]

## Likely Files to Change
- [file 1]
- [file 2]

## Do Not Touch
- [protected area 1] (reason)
- [protected area 2] (reason)

## Required Verification
- [command 1]: must pass
- [command 2]: must pass

## Stop Conditions
- [condition 1]
- [condition 2]

## Human Approval Required If
- Any change to [high-risk area]
- Any change to [boundary area]
```

## Rules

- Do not include unrelated context
- Keep minimal
- Only include files from existing harness or directly observable project files
- Do not invent file paths
