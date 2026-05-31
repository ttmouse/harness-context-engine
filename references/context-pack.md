# Context Pack

## When to Use

- Agent is starting a new task and needs focused context, not the entire harness
- Task is isolated to a specific area (auth, frontend, billing, etc.)
- Task type is clear: bug-fix, feature, refactor, testing, docs, or investigation
- Need to minimize token usage by loading only relevant context files
- A code graph exists and can help select likely files or affected relationships

**Do NOT use Context Pack when:** the task scope is unclear or covers multiple unrelated areas. In that case, load the full harness and let the agent route itself.

## Inputs

- Task description or issue text
- Existing harness (AGENTS.md, CONTEXT-MAP.md, .harness/ files)
- CONTEXT-MAP.md for routing decisions
- Optional `.harness/code-graph/code_graph.json` for relationship-aware routing
- Existing Project Profile when project structure is unclear

## Workflow

Given a task or issue, generate minimal task-specific context pack.

1. Classify the task (change type + affected areas)
2. Consult CONTEXT-MAP.md for context routing
3. If `code_graph.json` exists and is relevant, search related nodes and edges
4. Select only relevant context files
5. Select likely project files to read or change
6. Include affected files, risk edges, and unknowns
7. Build minimal context pack
8. Include required verification and stop conditions

## Graph-aware Context Pack

When `.harness/code-graph/code_graph.json` exists:

1. Search graph nodes by task terms, affected areas, route names, API paths, feature names, and file paths.
2. Expand only the relevant neighborhood:
   - direct imports;
   - API calls and handlers;
   - route/page relationships;
   - source/test relationships;
   - data/model relationships when observed;
   - high-risk edges.
3. Add likely files from the relevant subgraph.
4. Add graph unknowns or stale warnings.
5. Do not include the full graph unless the task is an investigation of the graph itself.

If the graph is missing, stale, invalid, or irrelevant, fall back to normal CONTEXT-MAP routing.

Current code is the source of truth. If graph and code conflict, mark graph stale and do not rely on it.

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
4. [relevant code graph summary or subgraph only if useful]

## Likely Files to Read
- [file 1]
- [file 2]

## Likely Files to Change
- [file 1]
- [file 2]

## Affected Relationships
| Source | Relationship | Target | Evidence | Confidence |
|---|---|---|---|---|
| [source] | [edge type] | [target] | [evidence] | [high/medium/low] |

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
- Only include files from existing harness, directly observable project files, or validated code graph nodes
- Do not invent file paths
- Do not infer business meaning from code graph edges
- Treat `inferred` and `low confidence` relationships as clues, not facts
- Include graph evidence only when it changes what the agent should read, avoid, or verify

## Stop Conditions

- Task description is too vague to classify → request clarification
- Task covers multiple unrelated areas → recommend full harness instead
- No relevant context files found → return minimal pack with just AGENTS.md and CONTEXT-MAP.md
- Harness itself is missing or stale → recommend running Generate or Sync first
- code_graph.json exists but fails validation → ignore graph and recommend graph sync
- Task touches high-risk areas without clear approval rule → stop for human approval

## Related Scripts

| Script | Role |
|---|---|
| `scripts/scan_project.py` | Helps classify project structure for context |
| `scripts/generate_code_graph.py` | Builds optional relationship evidence |
| `scripts/validate_code_graph.py` | Validates graph before using it for Context Pack |
| `scripts/validate_context_map.py` | Ensures referenced context files exist |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Including unrelated context | Loading all harness files instead of filtering | Strictly route through CONTEXT-MAP |
| Missing critical context | Too aggressive filtering | Include at minimum AGENTS.md + CONTEXT-MAP.md |
| Inventing file paths | Guessing where files might be | Only reference files from existing harness, scan, or validated graph |
| Trusting stale graph | Code changed after graph generation | Validate or regenerate graph |
| Context pack too large | Including entire documentation or full graph | Keep focus on task-specific files and subgraph |
