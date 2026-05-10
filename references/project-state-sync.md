# Project-State Sync

## When to Use

- After project code changes (new files, routes, APIs, dependencies)
- After git pull with significant changes
- Post-task: when Run Report indicates harness may be stale
- Before a new agent task on a project last synced more than a week ago

**Not a publication step.** Sync updates the local harness context to match the current project state. It does not publish to Git, wiki, or any external destination. See Publication Sync for that.

## Inputs

- Project directory with existing harness
- Git diff or current project state snapshot
- Optionally: `scripts/scan_project.py` output
- Optionally: `scripts/compare_harness_to_project.py` output

## Workflow

Use when project code changed and harness may be stale.

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

## Stop Conditions

- **Hard Fail from Evaluate → stop.** Do not proceed to Publication Sync.
- No detectable change → report no-op, no harness update needed
- Only cosmetic changes → skip sync, report as no-op
- Low-confidence changes only → propose updates but do not auto-apply

## Related Scripts

| Script | Role |
|---|---|
| `scripts/scan_project.py` | Scans current project state for comparison |
| `scripts/compare_harness_to_project.py` | Detects stale references and new files |
| `scripts/validate_context_map.py` | Validates updated CONTEXT-MAP references |
| `scripts/check_commands.py` | Validates commands in updated harness |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Sync not run before tasks | No workflow enforcement | Always run Sync before new tasks on changed projects |
| Auto-applying low-confidence changes | Treating inference as observation | Mark NEEDS HUMAN REVIEW for inferred changes |
| Skipping Evaluate after sync | Assuming sync cannot break harness | Always run Evaluate after sync |
| Treating Sync as publication | Confusing local sync with remote publish | Sync updates local files; Publication Sync handles remote |
| Missing new routes/modules | Scan scope too narrow | Check src/, pages/, routes/, API directories systematically
