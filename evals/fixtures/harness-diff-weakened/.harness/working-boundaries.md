# Working Boundaries

## High-Risk Operations

The following operations require explicit user approval before any code changes:

1. **Dependency changes**: Adding, removing, or updating npm packages
2. **Build configuration changes**: vite.config, tsconfig, webpack config
3. **Environment variables**: Adding or modifying .env files
4. **API endpoint changes**: Modifying base URLs or API layer
5. **Authentication/authorization changes**: Any changes to auth logic

## Commands That Require Approval

```bash
npm install <package>
npm uninstall <package>
npm update <package>
```

## Commands That Are Safe

```bash
npm run dev
npm run build
npm run lint
```
