# Commands

## Command Source Rule

Commands must come from real project files. Do not invent commands.

## Commands

| Purpose | Command | Source | Confidence | Status |
|---|---|---|---|---|
| install | npm install | package.json | high | verified |
| dev | npm run dev | package.json | high | verified |
| build | npm run build | package.json | high | verified |
| deploy | npm run deploy-to-prod | INVENTED — not in package.json | unknown | unverified |
| test | npm run test-all | INVENTED — no test script in package.json | unknown | unverified |
| migrate | npm run db-migrate | INVENTED — not in any config | unknown | unverified |
