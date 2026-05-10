# Context Pack Output Example

Input: `create context pack for fixing login redirect bug on mobile`

## Expected Output

```markdown
# Context Pack

## Task
Fix login redirect bug on mobile

## Classification
- Change Type: bug-fix
- Affected Areas: frontend, auth
- Risk Level: medium

## Must Read
1. AGENTS.md
2. CONTEXT-MAP.md
3. docs/contexts/frontend/CONTEXT.md (if exists)
4. docs/contexts/auth/CONTEXT.md (if exists)
5. .harness/working-boundaries.md
6. .harness/testing-and-verification.md
7. .harness/task-workflow.md

## Likely Files to Change
- src/auth/login.tsx
- src/routes/AuthRouter.tsx

## Do Not Touch
- src/payment/ (billing-related, requires approval)
- src/admin/ (permission-restricted)
- vite.config.ts (build config, requires approval)
- package.json (dependency changes, requires approval)

## Required Verification
- npm run build: must pass
- npm test: must pass

## Stop Conditions
- Login redirect works on mobile viewport (375px)
- No console errors
- Build passes

## Human Approval Required If
- Any change to auth/permission logic
- Any change to session or token handling
- Any dependency addition
- Any routing changes outside login flow
```
