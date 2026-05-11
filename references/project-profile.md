# Project Profile

Intermediate judgment artifact produced after scanning the project and before generating harness files. The Project Profile captures what is known, what is uncertain, and what structure the harness should take — preventing template-driven generation that guesses facts.

## When to Use

- After running `scripts/scan_project.py` on the target project
- Before generating any harness files (AGENTS.md, CONTEXT-MAP.md, .harness/)
- When resuming work on a previously profiled project (reuse or refresh the profile)
- As input to Project-State Sync to check if the profile is still accurate

**Do NOT skip the Project Profile.** Generating harness directly from scan output produces template-filler content with invented facts.

## Inputs

- `scripts/scan_project.py` output (JSON)
- Project root directory (for visual inspection of structure)
- README.md, package.json, Makefile, CI workflow files
- User-provided project description or domain context (if any)

## Output Sections

### 1. Summary

One-paragraph factual description of what the project is. No marketing language. No assumptions about business purpose unless observed.

```
## Summary

React-based admin dashboard for internal inventory management.
Source: README.md section 1, package.json name field
Confidence: high (observed from README + package.json)
```

### 2. Project Type

Classify into exactly one type:

- **frontend**: browser UI project with no backend service
- **backend**: server-side API or service with no frontend
- **fullstack**: both frontend and backend in same repo
- **monorepo**: multiple independent packages/apps in single repo
- **library**: reusable package published to registry
- **CLI**: command-line tool
- **mobile**: iOS/Android/React Native app
- **mini-program**: WeChat/Alipay mini-program
- **data/script project**: data processing, ETL, analysis, or automation scripts
- **unknown**: cannot determine from available evidence

Evidence must explain why this classification was chosen.

### 3. Stack

| Layer | Technology | Source | Confidence | Type |
|---|---|---|---|---|
| Language | TypeScript 5.x | tsconfig.json | high | observed |
| Framework | React 18 | package.json dependencies | high | observed |
| Package Manager | npm | package-lock.json | high | observed |
| Build System | Vite 5 | vite.config.ts | high | observed |
| Test Framework | vitest | vitest.config.ts | high | observed |
| CI System | GitHub Actions | .github/workflows/ | high | observed |

Mark unknowns explicitly: `UNKNOWN` or `NEEDS HUMAN REVIEW`.

### 4. Structure

```
Source directories:
  src/                       # exists
  src/components/            # exists
  src/pages/                 # exists
  src/api/                   # does not exist
  src/services/              # inferred from naming, not confirmed

App/Pages/Routes:
  src/pages/Dashboard.tsx    # observed
  src/pages/Reports.tsx      # observed
  src/routes/index.tsx       # observed (contains Route components)

API/Service directories:
  src/api/                   # does not exist
  src/services/              # exists, contains apiClient.ts

Packages/Apps/Services:
  packages/web/              # exists
  packages/server/           # exists

Generated code directories:
  src/generated/             # exists, marked in .gitignore
  dist/                      # exists, in .gitignore
```

**Every structural claim must cite a path.** Unverified paths must be marked explicitly — `inferred from naming`, `does not exist`, `not confirmed`.

### 5. Commands

| Purpose | Command | Source | Confidence | Status |
|---|---|---|---|---|
| dev | npm run dev | package.json scripts.dev | high | source-backed |
| build | npm run build | package.json scripts.build | high | source-backed |
| test | npm run test | package.json scripts.test | high | unverified |
| lint | npm run lint | package.json scripts.lint | high | unverified |
| deploy | npm run deploy | INVENTED: not in package.json | — | invented |

Status values:
- **source-backed**: command found in package.json, Makefile, or CI workflow
- **unverified**: source exists but has not been executed
- **invented**: command claimed without evidence
- **unknown**: cannot determine

### 6. Risk Areas

Check each risk area against observed code structure:

| Risk Area | Present | Evidence | Confidence |
|---|---|---|---|
| auth | Yes | src/auth/ directory, login page | high |
| permission | No | no admin/user role separation found | low (inferred from structure) |
| billing | UNKNOWN | no billing-related files or terms found | — |
| payment | UNKNOWN | no payment processing found | — |
| data deletion | UNKNOWN | no delete operations found in code scan | — |
| migration | No | no migration scripts found | medium |
| deployment | Yes | Dockerfile, .github/workflows/deploy.yml | high |
| generated files | Yes | src/generated/ in .gitignore | high |
| dependency/config changes | Yes | package.json, vite.config.ts are modifiable | high |

**Do not flag a risk unless you have evidence.** Absence of evidence is not evidence of absence — mark as UNKNOWN.

### 7. Context Structure Recommendation

| Dimensions Count | Recommended Structure | Rationale |
|---|---|---|
| 0-1 | single-context | One CONTEXT.md covers all domains |
| 2-3 | sectioned-context | One CONTEXT.md with domain sections |
| 4+ | multi-context | docs/contexts/*/CONTEXT.md per domain |
| monorepo detected | monorepo-context | docs/contexts/<package>/*/CONTEXT.md per package |

Base this on both the 8-dimension complexity classification and observed project structure. A monorepo with 0-1 dimensions still uses monorepo-context.

### 8. Evidence Table

Every non-obvious claim in the Project Profile must have an entry:

| Claim | Source | Type | Confidence |
|---|---|---|---|
| Language: TypeScript | tsconfig.json | observed | high |
| Purpose: inventory management | README.md section 1 | observed | high |
| Auth module exists | src/auth/ directory | observed | high |
| Reports route purpose: UNKNOWN | src/pages/Reports.tsx naming only | inferred | low |

### 9. Unknowns

List all questions that could not be answered from project scan:

- Business purpose of /reports route: UNKNOWN
- Whether auth is JWT or session-based: UNKNOWN (login.ts not inspected)
- Billing provider: NEEDS HUMAN REVIEW

### 10. Human Review Needed

Items that require human confirmation before the harness can be considered accurate:

- Confirm business domain: is this inventory management or order management?
- Confirm auth boundary: does admin role exist?
- Confirm generated code policy: should agents modify src/generated/?

## Output Format

All sections must be present. Write UNKNOWN where evidence is missing. Do not invent answers to fill gaps.

```markdown
# Project Profile

## Summary
...

## Project Type
...

## Stack
[table]

## Structure
...

## Commands
[table]

## Risk Areas
[table]

## Context Structure Recommendation
[recommendation with rationale]

## Evidence Table
[table]

## Unknowns
- [item]: reason

## Human Review Needed
- [item]: reason
```

## Relationship to Harness Generation

The Project Profile is a **judgment document**, not a harness file. It is not written into the target project. It serves as the basis for decisions about:

- Which harness files to create (and which to skip)
- Whether single-context or multi-context structure
- Which commands are trusted vs need verification
- Which risk areas need working-boundary rules
- What domain terms need clarification before writing to CONTEXT.md
- Whether an ADR is warranted

After generation, the Project Profile can be discarded or kept for future sync comparison.

## Stop Conditions

Stop generation and escalate to human if:

- Project type cannot be determined from scan results
- No reliable source directories or config files are found
- User asks to generate business rules from source-code naming alone
- User asks to create ADRs without decision evidence
- Critical risk areas are suspected but cannot be verified

If the project can still be handled safely (no critical unknowns), continue with UNKNOWN markers instead of inventing facts.

## Related Scripts

| Script | Role |
|---|---|
| `scripts/scan_project.py` | Produces raw scan data that feeds the profile |
| `scripts/check_commands.py` | Validates commands for the Commands section |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Profiling from template | Filling sections with guessed data | Every claim needs source + confidence |
| Over-classifying risk | Assuming risk from directory name alone | Mark inferred, not observed |
| Under-reporting unknowns | Leaving sections blank instead of UNKNOWN | Always write UNKNOWN explicitly |
| Skipping evidence table | Thinking profile is internal-only | Evidence table is for Evaluate to cross-check |
| Recommending multi-context by default | Defaulting to complex structure | Base on 8-dimension classification + observed structure |
