# Generate Harness

## When to Use

- Project has no existing harness context (AGENTS.md, CONTEXT-MAP.md, .harness/)
- Starting a new project and need agent-aware context from the beginning
- Rebuilding harness from scratch after major project restructuring
- The existing harness is too stale to repair via sync

**Do NOT use Generate when:** the project already has a working harness that just needs minor updates. Use Project-State Sync instead.

## Inputs

- Project directory path
- `scripts/scan_project.py` output (run it first)
- Project Profile (built during generation; see `references/project-profile.md`)
- Optionally: existing README, package.json, Makefile, CI workflow files
- Optionally: user-provided project description or domain context

## Workflow

1. **Scan Project** — Run `scripts/scan_project.py` and inspect project structure
2. **Build Project Profile** — Synthesize scan data into a Project Profile (see `references/project-profile.md`)
3. **Classify Context Structure** — Use the profile to decide single-context, sectioned, multi-context, or monorepo-context
4. **Generate Minimal Harness** — Create only files that have content; follow Lazy Creation rules
5. **Run Evaluate** — Always run Evaluate after generation

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

## Step 3: Build Project Profile

Generate a Project Profile before deciding which harness files to create. See `references/project-profile.md`.

The profile captures:
- Project type and structure facts
- Source-backed commands vs invented vs unknown
- Risk areas with evidence levels
- Context structure recommendation
- Unknowns that need human review
- Evidence table for every non-obvious claim

**Do not skip the profile.** Direct generation from scan output produces template-driven content with invented facts.

## Step 4: Generate Harness Files

### Lazy Creation Rule

Create files **only when you have content to write**. Do not create files for structural completeness.

| File | Create When | If No Content |
|---|---|---|
| AGENTS.md | always (minimal entry-point) | Write project name + UNKNOWN purpose |
| CONTEXT-MAP.md | always (context routing) | Write skeleton with MISSING_CONTEXT markers |
| CONTEXT.md or docs/contexts/*/CONTEXT.md | domain terms exist | **Do not create** empty; skip until terms exist |
| .harness/commands.md | always (operation safety) | Write commands with UNKNOWN status |
| .harness/working-boundaries.md | risk areas identified | Write UNKNOWN for unassessed areas |
| .harness/testing-and-verification.md | always (verification gate) | Write UNKNOWN for unconfirmed verification |
| .harness/task-workflow.md | always (task guidance) | Write default workflow |
| .harness/known-risks.md | only if risks observed or user-provided | **Do not create** empty |
| .harness/code-review.md | only if code review process observed | **Do not create** empty |
| .harness/failure-analysis.md | only if previous failures documented | **Do not create** empty |
| docs/agents/domain.md | only if source-backed domain terms exist | **Do not create** empty |
| docs/adr/*.md | only if evidence shows real decision | **Do not create** empty; write ADR TODO instead |
| docs/agents/issue-tracker.md | only if project uses issue tracker | **Do not create** empty |
| local AGENTS.md in subproject | only for real independent subprojects | **Do not create** empty |
| docs/agents/triage-labels.md | only if project uses labels | **Do not create** empty |

**Key rules:**

- **Never** create an ADR file just to satisfy harness structure. Only create ADR when all three are true: (1) hard to reverse, (2) surprising without context, (3) real trade-off was made. Otherwise write ADR TODO.
- **Never** create domain.md unless there are source-backed domain terms to document.
- **Never** create multi-context directories (docs/contexts/*/) unless the project profile recommends multi-context.
- **Never** create known-risks.md with filler. No observed risk = no file.
- **Do not** mark UNKNOWN items as TODO for later creation. UNKNOWN is the correct state until evidence arrives.
- **Do not** create a file today because it "might be needed tomorrow." Create it when the content exists.

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

## Output Format

Generated files follow templates in `references/templates.md`. Each generated file includes:

- `source` metadata: generated_by, generated_at, confidence
- Source/confidence annotations for non-obvious claims
- UNKNOWN markers for unverified information

## Stop Conditions

Stop generation and escalate to human if:

- Project has no recognizable language, framework, or package manager
- Project structure is completely flat with no source directories
- User asks to generate ADR without evidence
- User asks to generate business rules from source-code naming alone
- User asks to copy the same commands into multiple harness files

## Related Scripts

| Reference / Script | When to Use |
|---|---|
| `references/project-profile.md` | After scan, before generation — build the profile |
| `scripts/scan_project.py` | Before generation, to collect project facts |
| `scripts/check_commands.py` | After generation, to validate commands |
| `scripts/validate_context_map.py` | After generation, to validate context references |
| `references/grill-before-write.md` | During generation, when business terms are unclear |
| `references/source-confidence.md` | During generation, for claim annotation rules |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Skipping Project Profile | Generating harness directly from scan output | Always build project profile before generating files |
| Creating files for completeness | Following old "Required (always)" rule | Apply Lazy Creation: only create files with content |
| Invented ADR | Generating architecture decisions without evidence | Never create formal ADR just to satisfy structure |
| Invented business rules | Deriving business definitions from source-code names | Mark as INFERRED or UNKNOWN; never present as fact |
| Duplicate commands | Copying same commands into commands.md and testing-and-verification.md | Write commands in one file, reference from others |
| Bloating CONTEXT.md | Including irrelevant documentation | Keep minimal; add only what agents need for task accuracy |
| Forgetting to run Evaluate | Skipping validation after generation | Enforce post-generation Evaluate workflow |
| Creating empty ADR "for later" | Writing ADR TODO as formal ADR | ADR TODO is a note, not a file. Only create ADR file when decision exists.

## Forbidden

- Do not skip the Project Profile
- Do not create files for structural completeness
- Do not create formal ADR just to satisfy structure
- Do not create domain.md without source-backed domain terms
- Do not generate fake module contexts
- Do not copy commands into multiple files
- Do not generate large generic documentation
- Do not invent paths or commands
- Do not define business rules from source-code naming alone — mark as UNKNOWN
- Do not write ADR TODO as a formal ADR file
- Do not create known-risks.md with filler content

See: references/templates.md for file templates.
