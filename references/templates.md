# Templates

## AGENTS.md

```markdown
# {repo_name}

## Purpose

{project_description or UNKNOWN}

## Entry Rule

Before any task:
1. Read this file
2. Read `CONTEXT-MAP.md`
3. Choose task-specific context from `CONTEXT-MAP.md`
4. Read `.harness/commands.md` before running commands
5. Read `.harness/testing-and-verification.md` before final response

## Non-negotiable Rules

- Do not invent project facts
- Do not modify business code during harness generation
- Do not bypass tests or weaken tests
- Do not change dependencies, build config, auth, permission, billing, data deletion, or deployment config without approval
- Use minimal diff
- Report verification evidence

## Context Files

- Routing: `CONTEXT-MAP.md`
- Commands: `.harness/commands.md`
- Workflow: `.harness/task-workflow.md`
- Boundaries: `.harness/working-boundaries.md`
- Verification: `.harness/testing-and-verification.md`

## Source

- generated_by: harness-context-engine
- generated_at: {ISO timestamp}
- confidence: {high|medium|low}
```

## CONTEXT-MAP.md

```markdown
# Context Map

## Routing Rule

Classify every task by:
1. Change Type
2. Affected Area

Read all matching contexts.

## Change Type Routing

| Change Type | Required Context |
|---|---|
| bug-fix | `.harness/task-workflow.md`, `.harness/testing-and-verification.md` |
| feature | `.harness/task-workflow.md`, `docs/agents/issue-tracker.md` |
| refactor | `.harness/working-boundaries.md`, `docs/adr/` if exists |
| testing | `.harness/commands.md`, `.harness/testing-and-verification.md` |
| docs | `CONTEXT.md` or relevant `docs/contexts/*/CONTEXT.md` |
| investigation | `.harness/known-risks.md`, `docs/adr/` if exists |

## Affected Area Routing

| Area | Required Context |
|---|---|
| frontend | `docs/contexts/frontend/CONTEXT.md` if exists |
| backend | `docs/contexts/backend/CONTEXT.md` if exists |
| database | `docs/contexts/data/CONTEXT.md` if exists, `.harness/working-boundaries.md` |
| auth | `docs/contexts/auth/CONTEXT.md` if exists, `.harness/working-boundaries.md` |
| permission | `docs/contexts/permission/CONTEXT.md` if exists, `.harness/working-boundaries.md` |
| billing | `docs/contexts/billing/CONTEXT.md` if exists, `.harness/working-boundaries.md` |
| build-config | `.harness/commands.md`, `.harness/working-boundaries.md` |
| business-domain | `docs/agents/domain.md` if exists |

## Missing Context Rule

If a referenced context file does not exist, do not invent it.
Record it as `MISSING_CONTEXT` in the report.
```

## .harness/commands.md

```markdown
# Commands

## Command Source Rule

Commands must come from real project files:
- package.json
- Makefile
- CI workflow
- task runner config
- framework config

Do not invent commands.

## Commands

| Purpose | Command | Source | Confidence | Status |
|---|---|---|---|---|
| install | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| dev | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| build | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| test | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| lint | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| typecheck | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |

## Unknowns

- [command]: reason
```

## .harness/working-boundaries.md

```markdown
# Working Boundaries

## Allowed Without Approval

- Small local bug fixes within the requested module
- Updating tests for changed behavior
- Updating local documentation related to changed code

## Requires Approval

- Dependency changes
- Build config changes
- Deployment config changes
- Database schema changes
- Public API contract changes
- Auth / permission changes
- Billing / payment changes
- Data deletion or migration
- Large cross-module refactor

## Forbidden

- Hardcoding secrets or credentials
- Deleting tests to make checks pass
- Weakening validation without explicit product decision
- Modifying generated files without updating the source generator
- Inventing commands, paths, business rules, or architecture decisions

## High-risk Areas

| Area | Path | Risk | Source | Confidence |
|---|---|---|---|---|
| {area} | {path} | {risk} | {source} | {high/medium/low} |
```

## .harness/testing-and-verification.md

```markdown
# Testing and Verification

## Test Method

{自动测试框架名称 或 "UNKNOWN: 当前无自动测试"}

## Verification Commands

| Purpose | Command | Source | Confidence | Status |
|---|---|---|---|---|
| build | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| test | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |
| lint | {command or UNKNOWN} | {source} | {high/medium/low} | verified / unverified / unknown |

## Verification Gate

{必须通过的最低门禁命令，或 "UNKNOWN"}

## Unknowns

- {未确认的测试或验证项}
```

## .harness/task-workflow.md

```markdown
# Task Workflow

## Standard Flow

1. Read `AGENTS.md` and `CONTEXT-MAP.md`
2. Identify change type and affected area
3. Read relevant context files
4. Read `.harness/working-boundaries.md`
5. Make minimal diff
6. Run verification commands
7. Report evidence

## Task-specific Notes

{按任务类型的额外说明}
```
