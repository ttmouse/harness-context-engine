# Project Profile

## Purpose

Project Profile is the required intermediate artifact between project scan and harness generation.

Do not scan a project and immediately generate harness files. First build a Project Profile so the harness structure is based on observed project facts, not a generic template.

The Project Profile answers:

- What kind of project is this?
- What stack and structure were observed?
- What commands are source-backed?
- What relationship evidence exists between files, routes, APIs, services, models, tests, and docs?
- What risk areas exist?
- What context structure should be generated?
- What is still unknown or needs human review?

## When to Use

Use Project Profile during Generate and Project-State Sync when the agent needs to understand the current project state before writing or updating harness files.

Use it before:

- generating a new harness;
- deciding single-context vs multi-context;
- deciding whether a Code Graph is useful;
- updating CONTEXT-MAP.md after project changes;
- creating a task-specific Context Pack for a project with unclear structure;
- deciding whether a claim is observed, inferred, or unknown.

## Inputs

- Project root path
- `scripts/scan_project.py` output, if available
- `scripts/generate_code_graph.py` output, if available and useful
- Existing README or docs, if available
- package manager files such as package.json, pnpm-workspace.yaml, Makefile, pyproject.toml, go.mod, Cargo.toml
- CI workflow files, if available
- Existing AGENTS.md, CONTEXT-MAP.md, CONTEXT.md, or .harness files, if present
- Optional user-provided project description

## Workflow

1. Run or perform project scan.
2. Optionally run Code Relationship Scan when relationship evidence would improve routing or impact analysis.
3. Record observed facts with source paths.
4. Separate observed facts from inferred meaning.
5. Identify unknowns and human-review items.
6. Choose a context structure recommendation.
7. Use the profile to decide which harness files to create.

## Project Type

Classify the project as one of:

- frontend
- backend
- fullstack
- monorepo
- library
- CLI
- mobile
- mini-program
- data/script project
- unknown

If multiple categories apply, explain which one is primary and why.

Do not guess project type from repository name alone.

## Stack

Capture source-backed stack facts:

| Field | Examples | Evidence |
|---|---|---|
| language | TypeScript, Python, Go, Java | package/config/source files |
| framework | React, Vue, Next.js, FastAPI | dependencies/config/files |
| package manager | npm, pnpm, yarn, pip, poetry | lockfile/package config |
| build system | Vite, Next, Turbo, Make | config/scripts |
| test framework | Vitest, Jest, Pytest | dependencies/config/scripts |
| CI system | GitHub Actions, GitLab CI | workflow files |

If not found, mark UNKNOWN.

## Structure

Capture observed project structure:

- source directories;
- apps/packages/services layout;
- page or route directories;
- API or service layer directories;
- generated code directories;
- config directories;
- test directories;
- docs/harness directories.

Every structural claim must cite a path.

## Relationship Evidence

Use Code Graph output only when it helps explain how the project is connected.

Capture relationship evidence such as:

- file import relationships;
- page-to-route relationships;
- page/API-client-to-API path references;
- controller-to-service clues;
- service/model/data clues;
- test-to-source clues;
- doc-to-feature or doc-to-module clues;
- high-risk cross-module edges.

Relationship evidence must include:

| Claim | Source | Type | Confidence |
|---|---|---|---|
| `src/pages/orders.tsx` references `/api/orders` | `src/pages/orders.tsx` string literal | observed | medium |
| `order.test.ts` appears to test `order.ts` | filename match | inferred | low |

Do not treat Code Graph inferred edges as confirmed project truth.

If Code Graph is unavailable, stale, or too weak, state that the profile is based on project scan and direct inspection only.

## Commands

Classify commands as:

- source-backed: command exists in config such as package.json, Makefile, CI workflow;
- verified: command was actually run successfully;
- unverified: command exists but was not executed;
- unknown: no reliable command found;
- invented: command was written in harness but not found in project sources.

Source-backed does not mean verified.

## Risk Areas

Identify risk areas only from observed evidence or explicit user context.

Common risk areas:

- auth;
- permission;
- billing;
- payment;
- data deletion;
- database migration;
- deployment;
- environment config;
- generated files;
- public API contracts;
- dependency/config changes;
- cross-module relationship edges that affect multiple project areas.

If risk is inferred from naming only, mark as INFERRED and LOW CONFIDENCE.

## Context Structure Recommendation

Choose one:

| Structure | Use When |
|---|---|
| single-context | small project, one app, limited risk, simple structure |
| sectioned-context | one project with clear frontend/backend/data/domain sections but still one deployable unit |
| multi-context | multiple modules, risk areas, domains, runtimes, or independent task areas |
| monorepo-context | apps/packages/services with independent commands or deployables |

Do not generate multi-context just because the template supports it.

Relationship evidence may increase confidence in sectioned-context, multi-context, or monorepo-context only when it shows real independent areas or high-impact cross-area dependencies.

## Output Format

```md
# Project Profile

## Summary

## Project Type

## Stack

## Structure

## Relationship Evidence
| Claim | Source | Type | Confidence |
|---|---|---|---|

## Commands

## Risk Areas

## Context Structure Recommendation

## Evidence Table
| Claim | Source | Type | Confidence |
|---|---|---|---|

## Unknowns

## Human Review Needed
```

## Stop Conditions

Stop and ask for clarification if:

- project type cannot be determined;
- no reliable source directories or config files are found;
- user asks to generate business rules from naming alone;
- user asks to create ADRs without decision evidence;
- critical risk areas are suspected but cannot be verified.

If the project can still be handled safely, continue with UNKNOWN markers instead of inventing facts.

## Related Scripts

| Script | Role |
|---|---|
| `scripts/scan_project.py` | Collects project facts for profile generation |
| `scripts/generate_code_graph.py` | Collects optional relationship evidence |
| `scripts/validate_code_graph.py` | Checks relationship evidence quality when a graph exists |
| `scripts/check_commands.py` | Confirms command source backing |
| `scripts/validate_context_map.py` | Validates generated context references |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Template-first harness | Generating files before understanding project state | Build Project Profile first |
| Invented project purpose | Deriving purpose from repo name or folder names | Mark UNKNOWN unless source-backed |
| Over-splitting context | Creating multi-context for a simple project | Use complexity evidence |
| Graph-first overreach | Generating code graph for tiny projects or with weak evidence | Apply Lazy Creation Rule |
| Missing risk boundaries | Failing to detect auth/data/deploy areas | Review Project Profile risk areas and relationship evidence |
| False certainty | Presenting inferred claims as facts | Use source/confidence/type |
