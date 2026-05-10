# Project-State Sync

Use when project code changed and harness may be stale.

## Workflow

1. Scan current project state or git diff
2. Detect change type (structural, behavioral, command, risk, domain, decision, verification)
3. Compare changes against existing harness
4. Propose updates before applying
5. Apply only high-confidence observed updates
6. Mark uncertain items as NEEDS HUMAN REVIEW
7. Run Evaluate

## Step 1: Scan

```bash
git status
git diff --stat HEAD~5

# package.json changes
cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('deps:', list(d.get('dependencies',{}).keys())); print('scripts:', list(d.get('scripts',{}).keys()))"

# new files
find src -type f -name "*.tsx" -o -name "*.ts" | sort

# routes
grep -r "Route" src/ --include="*.tsx" --include="*.ts" | head -20

# API endpoints
grep -r "api/" src/ --include="*.ts" | head -20
```

Scan range: files, pages, routes, API, services, packages, build/test/CI config, schema, auth/permission/billing/data changes.

Run: `scripts/compare_harness_to_project.py /path/to/project`

## Step 2: Classify Changes

| Change Type | Meaning | Harness Update |
|---|---|---|
| structural | directory, module, page, route, API change | Update CONTEXT-MAP / CONTEXT |
| behavioral | feature behavior change | Update CONTEXT / testing-and-verification |
| command | command, script, CI change | Update commands.md |
| risk | permission, login, payment, data, dependency, config change | Update working-boundaries / known-risks |
| domain | new business concept, state, flow | Update domain.md (with source/confidence) |
| decision | new architecture choice or boundary change | Write ADR TODO, not formal ADR |
| verification | new test, new verification path | Update testing-and-verification.md |
| no-op | cosmetic or no harness impact | Record as no harness update needed |

## Step 3: Propose Updates

Output plan before applying:

- Which files need update
- Why update needed
- Source (what diff/file shows this)
- Confidence level
- Whether human confirmation needed

## Step 4: Apply Safe Updates

**Auto-apply (high confidence, observed)**:
- Real existing paths
- Real existing commands
- Observed modules, pages, routes, APIs from diff

**Requires human confirmation**:
- New business rule explanation
- New architecture decision
- New permission boundary
- Only-from-naming inferred business terms

## Step 5: Run Evaluate

After update, run Evaluate. Hard Fail → block Publication Sync.

## Update Harness When

- New page/route/API/module changes future agent navigation
- New command changes verification
- New dependency/config changes risk boundary
- New business behavior changes context
- Existing harness references deleted/renamed files
- Repeated failure reveals missing rule

## Do NOT Update Harness When

- Change is purely cosmetic
- Code already self-describes the detail
- Change is temporary experiment
- Evidence is low-confidence and unconfirmed

## Output Format

```
# Project-State Sync Report

## Summary
- Project path:
- Sync mode: full / diff / post-task
- Hard Fail: yes / no
- Harness update needed: yes / no

## Detected Project Changes
[table: Change | Path | Type | Source | Confidence]

## Applied Updates
- [file]: [change summary]

## Needs Human Review
- [item]: reason

## No-op Changes
- [change]: reason

## Evaluate Result
- Hard Fail: yes / no
- Score: X/10
- Status: pass / fail
```
