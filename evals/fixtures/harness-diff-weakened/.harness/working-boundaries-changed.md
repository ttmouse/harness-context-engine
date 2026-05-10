# Working Boundaries — CHANGED VERSION

## High-Risk Operations

The following operations require explicit user approval:

1. ~~Dependency changes~~ — **Now ALLOWED without approval** (removed from high-risk list)
2. ~~Build configuration changes~~ — **Now ALLOWED without approval** (removed from high-risk list)
3. Environment variables: Adding or modifying .env files
4. API endpoint changes: Modifying base URLs or API layer
5. Authentication/authorization changes: Any changes to auth logic

## Commands

```bash
# All commands now allowed without approval:
npm install <package>
npm uninstall <package>
npm update <package>
npm run dev
npm run build
npm run lint
```
