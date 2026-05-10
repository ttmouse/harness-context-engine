# Evaluate Harness

Three-layer evaluation. Hard Fail on any critical rule → stop immediately.

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

## Step 5: Usability Dry Run

Simulate 3 task types. Verify correct context is findable.

- Task A: bug-fix
- Task B: feature
- Task C: refactor/testing

For each: Expected Context → Found / Missing → MISSING_CONTEXT

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

## Optimization Suggestions
1. [suggestion]

## UNKNOWN / TODO
- [item]: reason
```

See: references/output-schemas.md for full schema.
