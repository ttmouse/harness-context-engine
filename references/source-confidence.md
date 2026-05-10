# Source and Confidence

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
