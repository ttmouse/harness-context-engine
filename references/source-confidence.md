# Source and Confidence

## When to Use

- Every time a non-obvious claim is made in harness files
- When defining business terms, architecture decisions, or commands
- When marking inferred information vs observed facts
- During Evaluate: to verify existing claims have proper attribution

## Inputs

- Content of harness files (AGENTS.md, CONTEXT.md, .harness/*.md, docs/adr/*.md, docs/agents/domain.md)
- Project source files for verification
- Command outputs for verification

## Core Rule

Every non-obvious claim must include source, confidence, and type.

## Fields

- **source**: file path, config path, README section, test file, command output, git diff, or explicit user-provided context
- **confidence**: high / medium / low
- **type**: observed / inferred / unknown

## Type Definitions

- **observed**: directly found in project files, command output, or git diff
- **inferred**: inferred from naming, structure, or usage pattern
- **unknown**: cannot be confirmed

## Rules

1. Never present inferred information as confirmed fact
2. Never generate formal ADR from inference alone
3. Never define business terms from source-code names alone
4. Never generate commands without source
5. Never generate paths that don't exist in the project
6. If source is missing, mark `UNKNOWN` or `NEEDS HUMAN REVIEW`
7. Confidence low → add `LOW CONFIDENCE` or `INFERRED` marker

## Marking Examples

```
## Observed (high confidence)
- Language: TypeScript (source: package.json engines field, confidence: high)

## Inferred (low confidence)
- Auth module: "uses JWT" (source: src/auth/login.ts + naming, confidence: low, type: inferred)

## Unknown
- Billing provider: "UNKNOWN: cannot confirm from codebase"
```

## Stop Conditions

- Source unverifiable → mark UNKNOWN, do not assert
- Multiple conflicting sources → report ambiguity, mark medium/low confidence
- Only source-code naming available → mark as inferred, never as observed
- No source at all → flag as NEEDS HUMAN REVIEW

## Related Scripts

| Script | Role |
|---|---|
| `scripts/validate_source_confidence.py` | Checks key harness files for source/confidence coverage |
| `scripts/scan_project.py` | Provides observed project facts for cross-reference |

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Presenting inferred as fact | Treating naming conventions as business definitions | Mark as INFERRED, add LOW CONFIDENCE |
| Omission of source | Assuming obviousness | Every non-obvious claim needs source |
| Confidence inflation | Rating medium/low claims as high | Be conservative with confidence |
| Source not specific enough | "from codebase" instead of exact file path | Use specific file paths as source
