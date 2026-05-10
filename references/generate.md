# Generate Harness

## Workflow

1. Scan project state (see Step 1)
2. Classify project complexity (see Step 2)
3. Decide single-context or multi-context
4. Generate only necessary harness files
5. Add source/confidence for non-obvious claims
6. Run Evaluate

## Step 1: Project Scan

```
Root:
  package.json, Cargo.toml, go.mod, Podfile
  README.md, README.txt
  vite.config.ts, webpack.config.js, tailwind.config.js
  tsconfig.json, .eslintrc, .prettierrc
  Makefile, CMakeLists.txt

Source:
  src/, lib/, app/, internal/
  main entry files
  routing config
  component directory structure
  service/API layer directories
```

Run: `scripts/scan_project.py /path/to/project`

## Step 2: Classify Complexity

Use 8 dimensions:

1. Multiple deployable apps or services
2. Multiple business domains
3. Multiple runtimes
4. High-risk domains (auth, permission, billing, data deletion, migration)
5. Multiple technology stacks
6. Independent build or test pipelines
7. Clear team/owner boundaries
8. Large legacy areas or generated code

| Dimensions | Structure |
|---|---|
| 0-1 | single-context |
| 2-3 | single-context + sectioned CONTEXT.md |
| 4+ | multi-context + docs/contexts/*/CONTEXT.md |

## Step 3: Generate Files

### Required (always)

- AGENTS.md
- CONTEXT-MAP.md
- CONTEXT.md or docs/contexts/*/CONTEXT.md
- .harness/commands.md
- .harness/working-boundaries.md
- .harness/testing-and-verification.md
- .harness/task-workflow.md

### Optional (only if evidence exists)

- .harness/known-risks.md (only if real risks found)
- .harness/code-review.md (only if project has review process)
- .harness/failure-analysis.md (only if previous failures documented)
- docs/agents/domain.md (only if source-backed terms exist)
- docs/adr/*.md (only if decisions have evidence)
- docs/agents/issue-tracker.md (only if project uses issue tracker)
- docs/agents/triage-labels.md (only if project uses labels)

### Conditional

- local AGENTS.md in subproject: only for real independent subprojects
- docs/agents/triage-labels.md: only if project uses GitHub/Gitea labels

## Step 4: Self-Test (Dry Run)

After generation, simulate 3 task types:

- bug-fix: "Fix login redirect on mobile"
- feature: "Add export-to-CSV button"
- refactor/testing: "Refactor order service to use repository pattern"

For each, verify the agent can:
1. Read correct context files
2. Identify affected files
3. Know verification commands
4. Identify approval requirements

## Forbidden

- Do not create formal ADR just to satisfy structure
- Do not generate fake module contexts
- Do not copy commands into multiple files
- Do not generate large generic documentation
- Do not invent paths or commands

See: references/templates.md for file templates.
