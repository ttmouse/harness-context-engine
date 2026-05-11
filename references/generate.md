# Generate Harness

## When to Use

- Project has no existing harness context (AGENTS.md, CONTEXT-MAP.md, .harness/)
- Starting a new project and need agent-aware context from the beginning
- Rebuilding harness from scratch after major project restructuring
- The existing harness is too stale to repair via sync

**Do NOT use Generate when:** the project already has a working harness that just needs minor updates. Use Project-State Sync instead.

## Inputs

- Project directory path
- Optionally: existing README, package.json, Makefile, CI workflow files
- Optionally: user-provided project description or domain context
- Optionally: existing scan output from `scripts/scan_project.py`

## Workflow

1. Scan project state (see Step 1)
2. Build Project Profile (see Step 2)
3. Classify context structure from the profile (see Step 3)
4. Generate only necessary harness files (see Step 4)
5. Apply Lazy Creation Rule
6. Apply Grill Before Write for domain, ADR, risk, and boundary claims
7. Add source/confidence/type for non-obvious claims
8. Run Evaluate

Do not scan and directly generate files. Project Profile is the decision layer that prevents template-first harness generation.

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

## Step 2: Build Project Profile

Before writing harness files, produce a Project Profile. See `references/project-profile.md`.

The profile must include:

- project type;
- stack;
- structure;
- source-backed commands;
- risk areas;
- context structure recommendation;
- evidence table;
- unknowns;
- human-review items.

Every non-obvious claim in the profile must include source, confidence, and type.

## Step 3: Classify Context Structure

Use the Project Profile to choose the smallest useful context structure.

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

Do not create multi-context just because the template supports it.

## Step 4: Generate Files

### Required (always)

- AGENTS.md
- .harness/commands.md
- .harness/working-boundaries.md
- .harness/testing-and-verification.md
- .harness/task-workflow.md

### Required when context routing is needed

- CONTEXT-MAP.md
- CONTEXT.md or docs/contexts/*/CONTEXT.md

A very small single-purpose project may use AGENTS.md + CONTEXT.md instead of a multi-file routing system, but it still needs execution controls in .harness/.

### Optional (only if evidence exists)

- .harness/known-risks.md (only if real risks found)
- .harness/code-review.md (only if project has review process or useful review rules)
- .harness/failure-analysis.md (only if previous failures documented or the user requests feedback capture)
- docs/agents/domain.md (only if source-backed domain terms exist)
- docs/adr/*.md (only if decisions have evidence)
- docs/agents/issue-tracker.md (only if project uses issue tracker)
- docs/agents/triage-labels.md (only if project uses labels)

### Conditional

- local AGENTS.md in subproject: only for real independent subprojects
- docs/agents/triage-labels.md: only if project uses GitHub/Gitea labels

## Lazy Creation Rule

Create files lazily. Do not create files only for structural completeness.

Do not create:

- formal ADRs without decision evidence;
- domain.md without source-backed domain terms;
- multi-context structure for a simple project;
- local AGENTS.md without real independent subprojects;
- known-risks.md without observed or explicitly user-provided risks;
- empty TODO files merely to make the tree look complete.

If a fact is not confirmed, mark UNKNOWN / NEEDS HUMAN REVIEW rather than filling the section with guesses.

## Grill Before Write

Use `references/grill-before-write.md` before writing:

- business language;
- domain meaning;
- architecture intent;
- ADR content;
- ownership boundaries;
- high-risk assumptions;
- working-boundary rules.

If code, docs, and user claims conflict, surface the conflict. Do not silently choose one source.

## Step 5: Self-Test (Dry Run)

After generation, simulate 3 task types:

- bug-fix: "Fix login redirect on mobile"
- feature: "Add export-to-CSV button"
- refactor/testing: "Refactor order service to use repository pattern"

For each, verify the agent can:
1. Read correct context files
2. Identify affected files
3. Know verification commands
4. Identify approval requirements
5. Know what remains UNKNOWN or needs human review

## Output Format

Generated files follow templates in `references/templates.md`. Each generated file includes:

- `source` metadata: generated_by, generated_at, confidence
- Source/confidence annotations for non-obvious claims
- UNKNOWN markers for unverified information

Generate should also output:

```md
# Harness Generation Report

## Project Profile Summary

## Context Structure Chosen

## Files Created

## Files Not Created

## Unknowns

## Human Review Needed

## Evaluate Result
```

## Stop Conditions

Stop generation and escalate to human if:

- Project has no recognizable language, framework, or package manager
- Project structure is completely flat with no source directories
- User asks to generate ADR without evidence
- User asks to generate business rules from source-code naming alone
- User asks to copy the same commands into multiple harness files
- Domain or architecture claims are unclear and cannot be safely marked UNKNOWN

## Related References

| Reference | When to Read |
|---|---|
| `references/project-profile.md` | Before choosing harness structure |
| `references/grill-before-write.md` | Before writing domain/ADR/risk/boundary claims |
| `references/source-confidence.md` | For source/confidence/type rules |
| `references/templates.md` | For file templates |

## Related Scripts

| Script | When to Run |
|---|---|
| `scripts/scan_project.py` | Before generation, to collect project facts |
| `scripts/check_commands.py` | After generation, to validate commands |
| `scripts/validate_context_map.py` | After generation, to validate context references |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Template-first harness | Generating files before project understanding | Build Project Profile first |
| Invented ADR | Generating architecture decisions without evidence | Never create formal ADR just to satisfy structure |
| Invented business rules | Deriving business definitions from source-code names | Grill before write; mark as INFERRED or UNKNOWN |
| Duplicate commands | Copying same commands into commands.md and testing-and-verification.md | Write commands in one file, reference from others |
| Bloating CONTEXT.md | Including irrelevant documentation | Keep minimal; add only what agents need for task accuracy |
| Over-splitting simple projects | Creating multi-context by default | Use Project Profile complexity evidence |
| Forgetting to run Evaluate | Skipping validation after generation | Enforce post-generation Evaluate workflow |

## Forbidden

- Do not create formal ADR just to satisfy structure
- Do not generate fake module contexts
- Do not copy commands into multiple files
- Do not generate large generic documentation
- Do not invent paths or commands
- Do not define business rules from source-code naming alone — mark as UNKNOWN
- Do not create files only to make the directory tree look complete

See: references/templates.md for file templates.
