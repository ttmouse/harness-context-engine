# Project-State Sync Output Example

Input: `sync harness with project ~/Projects/my-react-app`

## Expected Output

```markdown
# Project-State Sync Report

## Summary
- Project path: ~/Projects/my-react-app
- Sync mode: full
- Hard Fail: no
- Harness update needed: yes

## Detected Project Changes

| Change | Path | Type | Source | Confidence |
|---|---|---|---|---|
| New route | src/routes/Settings.tsx | structural | git diff | high |
| New dependency | package.json | risk | git diff | high |
| Config change | vite.config.ts | risk | git diff | high |

## Applied Updates

- CONTEXT-MAP.md: added settings route to frontend area routing
- known-risks.md: added vite.config.ts to build-config high-risk area

## Needs Human Review

- New auth flow in src/auth/: please confirm if this introduces new permission boundary

## No-op Changes

- README.md: cosmetic formatting change, no harness impact
- package-lock.json: lockfile sync, no functional change

## Evaluate Result

- Hard Fail: no
- Score: 9/10
- Status: pass
```
