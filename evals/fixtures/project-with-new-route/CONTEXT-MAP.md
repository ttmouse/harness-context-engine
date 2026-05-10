# Context Map

## Task Routing

| Task Type | Hot | Warm | Cold |
|---|---|---|---|
| bug-fix | AGENTS.md, CONTEXT-MAP.md | .harness/commands.md | — |
| feature | AGENTS.md, CONTEXT-MAP.md | .harness/commands.md | — |

## Routes

```
/ → Dashboard
/settings → Settings
```

## Structure

```
src/
├── App.tsx
└── pages/
    ├── Dashboard.tsx
    └── Settings.tsx
```

## Validation

```bash
npm run build
```
