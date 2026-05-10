# Evals

Self-test cases for harness-context-engine. Each eval tests a specific capability
against a controlled fixture project.

## Eval Definitions

Defined in `evals.json`. Each entry describes:

- **name**: unique identifier
- **description**: what it tests
- **query**: the prompt to use when testing
- **expected_behavior**: list of pass/fail criteria
- **fixture_path**: which fixture directory is needed
- **status**: current readiness

## Available Evals

| Name | Tests | Fixture | Runnable? |
|---|---|---|---|
| `generate_simple_project_harness` | Generate produces correct minimal harness | `fixtures/simple-react-project` | Partial (requires model) |
| `evaluate_fake_adr` | Evaluate rejects invented ADR | `fixtures/harness-with-fake-adr` | Partial (requires model) |
| `sync_new_route` | Sync detects new module/route | `fixtures/project-with-new-route` | Partial (requires model) |
| `create_context_pack_for_auth_bug` | Context pack for bug-fix task | `fixtures/simple-react-project` | Partial (requires model) |
| `review_harness_diff_weakened_boundary` | Diff review rejects loosened controls | `fixtures/harness-diff-weakened` | Partial (requires model) |

## Fixture Descriptions

### fixtures/simple-react-project

A minimal React + Vite + TypeScript project with:

- `package.json` with dev, build, preview, lint scripts (no test)
- `README.md` describing the project
- `src/main.tsx` and `src/App.tsx`
- `vite.config.ts`, `tsconfig.json`

**Test scenarios:**
- Generate: should produce AGENTS.md, CONTEXT-MAP.md, .harness/ files
- Commands: should extract dev/build/preview/lint from package.json
- Should NOT invent test commands (no test script exists)
- Context Pack: should classify bug-fix task correctly

### fixtures/harness-with-fake-adr

A project with harness that contains invented ADRs and commands:

- `AGENTS.md` — basic project description
- `CONTEXT-MAP.md` — task routing table (references .harness/commands.md)
- `.harness/commands.md` — mix of real and invented commands
- `docs/adr/adr-001.md` — ADR entries with NO Source/Confidence lines

**Test scenarios:**
- Evaluate Hard Fail: should detect invented commands (deploy-to-prod, test-all, db-migrate)
- Evaluate Hard Fail: should flag ADRs missing source/confidence
- Should NOT pass evaluation

### fixtures/project-with-new-route

A project with a stale harness that needs syncing:

- `AGENTS.md` — marked as STALE HARNESS
- `CONTEXT-MAP.md` — only lists Dashboard and Settings routes
- `src/App.tsx` — imports Dashboard, Settings, AND Reports (new route)
- `src/pages/Dashboard.tsx`, `Settings.tsx`, `Reports.tsx`

**Test scenarios:**
- Sync: should detect /reports route is not in CONTEXT-MAP
- Should propose updating CONTEXT-MAP to include Reports
- Should NOT invent business meaning for the /reports route

### fixtures/harness-diff-weakened

A project with two versions of working-boundaries.md:

- `.harness/working-boundaries.md` — original with strict controls
- `.harness/working-boundaries-changed.md` — weakened version

**Original** requires approval for: dependency changes, build config, env vars, API endpoints, auth.
**Changed** moves dependency changes and build config to "Allowed without approval".

**Test scenarios:**
- Diff Review: should reject the weakened boundaries
- Should flag "Requires Approval moved to Allowed" for dependency changes
- Should flag "Requires Approval moved to Allowed" for build config changes

## Static Verification (No Model Required)

Run these scripts against fixtures to verify basic functionality:

```bash
# Test scan_project.py against simple-react-project
python scripts/scan_project.py evals/fixtures/simple-react-project

# Test check_commands.py against harness-with-fake-adr
python scripts/check_commands.py evals/fixtures/harness-with-fake-adr evals/fixtures/simple-react-project

# Test validate_context_map.py (will detect missing files)
python scripts/validate_context_map.py evals/fixtures/harness-with-fake-adr evals/fixtures/simple-react-project

# Static fixture integrity check
python scripts/run_evals.py
```

## Expected Script Outputs

### scan_project.py on simple-react-project

- language: typescript
- framework: react
- package_manager: npm
- scripts: dev, build, preview, lint
- Should detect Vite bundler

### check_commands.py on harness-with-fake-adr

- source_backed: npm install, npm run dev, npm run build
- invented: npm run deploy-to-prod, npm run test-all, npm run db-migrate
- status: fail

### validate_context_map.py on project-with-new-route

- CONTEXT-MAP.md references .harness/commands.md which does NOT exist
- If .harness/commands.md not marked as MISSING_CONTEXT → should flag as missing

## Running Full Behavioral Tests

Full evaluation requires a model-based skill-quality-evaluation run:

```
Load skill-quality-evaluation.
Run Path B behavioral test for harness-context-engine on task: generate harness for evals/fixtures/simple-react-project
```

## Current Status

- evals.json: defined (5 evals)
- fixtures: populated (4 fixture projects)
- static scripts: runnable (scan_project, check_commands, validate_context_map)
- behavioral evals: require model interaction (not automated)
