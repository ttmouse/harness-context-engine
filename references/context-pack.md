# Context Pack

## When to Use

- Agent is starting a new task and needs focused context, not the entire harness
- Task is isolated to a specific area (auth, frontend, billing, etc.)
- Task type is clear: bug-fix, feature, refactor, testing, docs, or investigation
- Need to minimize token usage by loading only relevant context files

**Do NOT use Context Pack when:** the task scope is unclear or covers multiple areas. In that case, load the full harness and let the agent route itself.

## Inputs

- Task description or issue text
- Existing harness (AGENTS.md, CONTEXT-MAP.md, .harness/ files)
- CONTEXT-MAP.md for routing decisions

## Workflow

Given a task or issue, generate minimal task-specific context pack.

1. Classify the task (change type + affected areas)
2. Consult CONTEXT-MAP.md for context routing
3. Select only relevant context files
4. Build minimal context pack
5. Include required verification and stop conditions

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

## Stop Conditions

- Task description is too vague to classify → request clarification
- Task covers multiple unrelated areas → recommend full harness instead
- No relevant context files found → return minimal pack with just AGENTS.md and CONTEXT-MAP.md
- Harness itself is missing or stale → recommend running Generate or Sync first

## Related Scripts

| Script | Role |
|---|---|
| `scripts/scan_project.py` | Helps classify project structure for context |
| `scripts/validate_context_map.py` | Ensures referenced context files exist |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Including unrelated context | Loading all harness files instead of filtering | Strictly route through CONTEXT-MAP |
| Missing critical context | Too aggressive filtering | Include at minimum AGENTS.md + CONTEXT-MAP.md |
| Inventing file paths | Guessing where files might be | Only reference files from existing harness or scan |
| Context pack too large | Including entire documentation | Keep focus on task-specific files only
