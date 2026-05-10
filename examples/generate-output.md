# Generate Output Example

Input: `generate harness for ~/Projects/my-react-app`

## Expected AGENTS.md

```markdown
# my-react-app

## Purpose

React admin dashboard for managing product inventory.
Source: README.md section 1
Confidence: high

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
- generated_at: 2026-05-10T12:00:00Z
- confidence: medium
```

## Expected .harness/commands.md

```markdown
# Commands

## Command Source Rule

Commands must come from real project files.
Do not invent commands.

## Commands

| Purpose | Command | Source | Confidence | Status |
|---|---|---|---|---|
| install | npm install | package.json scripts | high | verified |
| dev | npm run dev | package.json scripts | high | verified |
| build | npm run build | package.json scripts | high | verified |
| test | npm run test | package.json scripts | high | verified |
| lint | npm run lint | package.json scripts | high | unverified |
```
