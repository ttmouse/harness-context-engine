# Evaluate Harness

## When to Use

- After Generate completes, to validate generated harness
- After Project-State Sync, to confirm sync did not break harness
- Before Publication Sync, as a pre-flight gate
- After any manual harness edits
- When suspecting harness drift or stale content
- After generating or syncing a code graph

## Inputs

- Project directory with existing harness (AGENTS.md, CONTEXT-MAP.md, .harness/ files)
- Optionally: `scripts/scan_project.py` output for truth comparison
- Optionally: `scripts/check_commands.py` output for command validation
- Optionally: `scripts/validate_context_map.py` output for reference validation
- Optionally: `.harness/code-graph/code_graph.json` and `scripts/validate_code_graph.py` output

## Workflow

Three-layer evaluation. Hard Fail on any critical rule → stop immediately. Do not compute score.

### Layer 1: Hard Fail

If any Hard Fail rule triggers → stop. Report failure. Do not proceed to scoring.

### Layer 2: Truth Check

Compare harness claims against actual project state. Report mismatches.

### Layer 3: Usability Dry Run

Simulate task types and verify correct context is findable.

## Step 1: Structure Check

Read project directory. Confirm required files exist:

```
AGENTS.md
CONTEXT-MAP.md
CONTEXT.md or docs/contexts/*/CONTEXT.md
.harness/commands.md
.harness/task-workflow.md
.harness/working-boundaries.md
.harness/testing-and-verification.md
```

If `.harness/code-graph/code_graph.json` exists, validate it. Code Graph is optional, but an existing graph must be structurally valid.

## Step 2: Hard Fail Rules

**If any triggers → Hard Fail: yes → stop. Do not compute score.**

### Critical (invented content = instant fail)

| Rule | Check |
|---|---|
| invented-commands | Scan .harness/commands.md. Verify all commands exist in package.json / Makefile / CI workflow. |
| invented-paths | Scan all harness files. Verify all paths exist in project. |
| placeholder-overview | Read AGENTS.md overview. Detect "TODO" / "placeholder" / "..." |

### Structural (missing files = instant fail)

| Rule | Check |
|---|---|
| missing-commands | .harness/commands.md must exist |
| missing-testing | .harness/testing-and-verification.md must exist |
| missing-boundaries | .harness/working-boundaries.md must exist |

### Quality (any = fail)

| Rule | Check |
|---|---|
| unsourced-adr | Read docs/adr/*.md. Each ADR must have Source line. No source → fail. |
| unsourced-domain | Read docs/agents/domain.md. Each term must have Source + Confidence. |
| unverified-commands | Verification commands must be marked UNKNOWN or must execute successfully. |
| missing-self-test | Must find Harness Self-Test Report (even if minimal). |
| entry-file-bloat | AGENTS.md content >50% duplicate of other files → fail. |

### Context Map

| Rule | Check |
|---|---|
| missing-context-in-map | CONTEXT-MAP references nonexistent files without marking MISSING_CONTEXT → fail. |

Run: `scripts/validate_context_map.py /path/to/project` to check.

### Code Graph

Only apply these rules if `.harness/code-graph/code_graph.json` or another declared `code_graph.json` exists.

| Rule | Check |
|---|---|
| invalid-code-graph-json | code_graph.json must parse as JSON. |
| graph-edge-missing-node | Every edge source/target must reference an existing node. |
| graph-high-confidence-no-evidence | Any high-confidence edge must include evidence. |
| graph-path-node-missing | Path nodes must reference existing project files when a project path is available. |
| graph-risk-edge-no-approval | High-risk relation must be covered by `.harness/working-boundaries.md` approval rules. |

Run: `scripts/validate_code_graph.py /path/to/code_graph.json /path/to/project` to check.

## Step 3: Truth Check

Rescan project. Verify harness content against reality.

```bash
cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('scripts',{}))"
ls -la src/
find src -maxdepth 2 -type d
```

Fill Truth Check Table:

| Claim | Source in Doc | Expected | Actual | Confidence | Status |
|---|---|---|---|---|---|
| language | package.json engines | TypeScript | TypeScript | high | match |
| module:src/components | src/ directory | exists | exists | high | match |
| module:src/services | src/ directory | exists | NOT FOUND | - | gap |

## Step 4: Command Check

```bash
cd /path/to/project
npm run build 2>&1; echo "EXIT:$?"
npm run test 2>&1; echo "EXIT:$?"
```

| Purpose | Command | Source File | Status | Execution Result |
|---|---|---|---|---|
| dev | npm run dev | package.json scripts | verified | exit 0 |
| build | npm run build | package.json scripts | verified | exit 0 |
| test | npm test | package.json scripts | failed | exit 1 |

**Do NOT mark unexecuted commands as verified.**

## Step 5: Code Graph Check

If a code graph exists:

```bash
python scripts/validate_code_graph.py /path/to/project/.harness/code-graph/code_graph.json /path/to/project
```

Record:

| Check | Status | Notes |
|---|---|---|
| JSON parse | pass / fail | |
| node references | pass / fail | |
| edge evidence | pass / fail | |
| path existence | pass / fail | |
| inferred-edge ratio | pass / warning | |
| graph usefulness | pass / warning | |

Warnings:

- graph has nodes but no edges;
- graph has mostly inferred edges;
- graph unknowns are empty for a complex project;
- graph appears stale after project changes;
- Context Pack ignores available relevant graph information.

## Step 6: Usability Dry Run

Simulate 3 task types. Verify correct context is findable.

- Task A: bug-fix
- Task B: feature
- Task C: refactor/testing

For each: Expected Context → Found / Missing → MISSING_CONTEXT

If Code Graph exists, also verify:

- likely files can be identified from graph evidence;
- high-risk edges appear in stop conditions or approval requirements;
- inferred edges are not treated as confirmed facts.

## Output Format

```
# Harness Evaluation Report

## Summary
- Hard Fail: yes / no
- Score: X/10
- Status: pass / needs-optimization / fail

## Hard Fail Items (if any)
- [rule]: [file or claim that failed]

## Truth Check
[table]

## Command Check
[table]

## Code Graph Check
[table or "not present / not required"]

## Optimization Suggestions
1. [suggestion]

## UNKNOWN / TODO
- [item]: reason
```

See: references/output-schemas.md for full schema.

## Stop Conditions

- **Hard Fail triggers → stop immediately.** Do not compute score. Do not proceed to Truth Check.
- Invented commands found → Hard Fail, stop
- Invented paths found → Hard Fail, stop
- All required files missing → Hard Fail, stop
- Unsourced ADR found → Hard Fail, stop
- Invalid code graph found when graph is declared or used → Hard Fail, stop
- After Hard Fail, report findings and recommend human review

## Related Scripts

| Script | Role in Evaluate |
|---|---|
| `scripts/check_commands.py` | Validates commands against real configs |
| `scripts/validate_context_map.py` | Validates CONTEXT-MAP references |
| `scripts/validate_code_graph.py` | Validates code graph JSON and relationship evidence |
| `scripts/check_paths.py` | Validates all referenced paths exist |
| `scripts/validate_source_confidence.py` | Checks source/confidence coverage |
| `scripts/compare_harness_to_project.py` | Detects stale harness references |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Hard Fail bypassed | Softening rules to avoid failures | Hard Fails must be non-negotiable |
| Unexecuted commands marked verified | Assuming commands work without running | Mark as unverified unless executed |
| MISSING_CONTEXT not flagged | Not checking if references actually exist | Run validate_context_map.py |
| Invented ADR counted as valid | Not checking ADR source field | Enforce Source field requirement |
| Stale harness passed evaluation | Not re-running after project changes | Always run Evaluate after any change |
| Invalid graph trusted | Skipping graph validation | Run validate_code_graph.py before graph-aware Context Pack |
| Pretty graph accepted | Graph has nodes but no useful relationship edges | Treat as warning and avoid using it for impact analysis |
