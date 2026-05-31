# Code Graph

## Purpose

Code Graph is the relationship evidence layer for harness context.

It extracts observable code relationships so an AI coding agent can route context, identify likely affected files, and avoid guessing project structure from names alone.

This is not a full code intelligence platform, graph database, business knowledge graph, or documentation generator. Generate the smallest relationship map that helps the agent act safely.

## When to Use

Use Code Graph when:

- a project has multiple pages, routes, APIs, services, models, or tests;
- a task requires impact analysis across frontend, backend, data, or test layers;
- Context Pack needs likely files to read or change;
- Project Profile needs evidence for high-risk areas or context structure;
- a refactor may touch multiple modules;
- previous agent runs missed callers, tests, routes, or data-flow dependencies.

## When NOT to Use

Do not generate or require Code Graph when:

- the project is a tiny single-purpose script;
- the task can be completed safely by reading one or two files;
- the graph would only restate the directory tree;
- the project has no recognizable source files;
- the user is asking for human-facing project documentation;
- the graph would be mostly inferred relationships with no evidence.

For small projects, prefer `AGENTS.md`, `CONTEXT-MAP.md`, and `.harness/commands.md`.

## Inputs

Useful inputs include:

- project root path;
- `scripts/scan_project.py` output;
- source files;
- routing files;
- API client files;
- controller/service/model files;
- tests;
- package manager files;
- CI files;
- existing harness files;
- user-provided task description when building a task-specific subgraph.

## Node Types

Supported node types:

| Type | Meaning |
|---|---|
| `file` | Source or generic project file |
| `module` | Internal module or external dependency |
| `page` | UI page, route view, screen, or app page |
| `component` | UI component |
| `route` | Frontend or server route |
| `api` | API path or endpoint |
| `controller` | Request handler/controller layer |
| `service` | Business/service layer |
| `function` | Function or method |
| `class` | Class |
| `model` | Data model/entity/schema |
| `table` | Database table |
| `field` | Database or API field |
| `config` | Config file or config item |
| `test` | Test file or test case |
| `doc` | Documentation file |
| `business_feature` | Business feature only when source-backed |

Do not create business-feature nodes from names alone unless the source is a PRD, README, issue, or explicit user context. Otherwise mark as `UNKNOWN` or do not create the node.

## Edge Types

Supported edge types:

| Type | Meaning |
|---|---|
| `imports` | File/module imports another file/module |
| `calls` | Function, file, page, or service calls another node |
| `renders` | Page renders component |
| `routes_to` | Route maps to page, handler, or endpoint |
| `handles` | Controller/handler handles API or route |
| `reads` | Code reads data table or field |
| `writes` | Code writes data table or field |
| `updates` | Code updates data table or field |
| `depends_on` | General dependency relation |
| `tests` | Test covers or appears to cover another node |
| `documents` | Doc describes node |
| `implements` | Code implements a feature |
| `affects` | Changing one node may affect another node |
| `configures` | Config item affects command, build, or behavior |

## Evidence Rules

Every edge must include:

- `source`: source node id;
- `target`: target node id;
- `type`: edge type;
- `evidence`: file path, symbol, string literal, import statement, route declaration, test naming convention, or command output;
- `confidence`: `high`, `medium`, or `low`;
- `claim_type`: `observed`, `inferred`, or `unknown`.

Never promote an inferred relation to confirmed fact.

Examples:

```json
{
  "source": "file:src/pages/OrderList.tsx",
  "target": "api:/api/orders",
  "type": "calls",
  "evidence": "src/pages/OrderList.tsx: string literal '/api/orders'",
  "confidence": "medium",
  "claim_type": "observed"
}
```

```json
{
  "source": "file:src/services/order.test.ts",
  "target": "file:src/services/order.ts",
  "type": "tests",
  "evidence": "test filename appears to match source filename",
  "confidence": "low",
  "claim_type": "inferred"
}
```

## Confidence Rules

| Confidence | Use When |
|---|---|
| `high` | Relationship is directly observable and unambiguous, such as resolved relative imports |
| `medium` | Relationship is observable but semantic meaning is not fully proven, such as API path string references |
| `low` | Relationship is heuristic, naming-based, or unresolved |
| `unknown` claim_type | The scanner found a clue but cannot safely interpret it |

If more than half of edges are inferred, the graph should include `unknowns` explaining why the project needs deeper analysis.

## Minimal Output

The minimal generated output is:

```text
.harness/code-graph/code_graph.json
```

Optional human-readable summaries may be generated only when they have a clear job:

```text
.harness/code-graph/feature_trace.md
.harness/code-graph/impact_map.md
.harness/code-graph/api_route_map.md
.harness/code-graph/data_flow_map.md
```

Create these lazily. Do not generate empty maps just to satisfy a template.

## Integration with Project Profile

Project Profile may use Code Graph to support:

- structure evidence;
- high-risk area detection;
- context structure recommendation;
- context routing;
- human-review items.

Project Profile must not treat inferred Code Graph edges as confirmed facts.

If the graph conflicts with current code, current code wins and the graph is stale.

## Integration with Context Pack

When `code_graph.json` exists and is not stale, Context Pack may use it to:

- select likely files to read or change;
- identify affected routes, APIs, services, tests, and data nodes;
- include risk edges;
- reduce unrelated context loading.

Context Pack must still include the normal harness controls:

- `AGENTS.md`;
- `CONTEXT-MAP.md`;
- `.harness/commands.md`;
- `.harness/working-boundaries.md`;
- `.harness/testing-and-verification.md`.

Code Graph narrows context; it does not replace harness rules.

## Integration with Evaluate

Evaluate should run Code Graph checks when graph files exist.

Hard failures:

- `code_graph.json` is invalid JSON;
- an edge references a missing node;
- a high-confidence edge has no evidence;
- a path node references a nonexistent project file;
- a high-risk relation lacks an approval rule.

Warnings:

- graph has nodes but no edges;
- most edges are inferred;
- unknowns are empty for a complex project;
- graph appears stale after project changes;
- Context Pack ignores available relevant graph information.

## Stop Conditions

Stop or escalate to human review when:

- the project type cannot be identified;
- relationships are mostly inferred and low confidence;
- route/API/data layers cannot be safely mapped;
- the user asks to infer business rules from filenames only;
- graph and code disagree on critical paths;
- a task touches auth, permission, billing, payment, data deletion, migration, deployment, or public API contracts.

## Common Failures

| Failure | Cause | Prevention |
|---|---|---|
| Pretty but useless graph | Generated a diagram instead of task-useful relationships | Focus on Context Pack and impact analysis |
| False certainty | Inferred relationships marked high confidence | Enforce source/confidence/type |
| Over-generation | Created graph files for tiny projects | Apply Lazy Creation Rule |
| Stale graph | Code changed but graph was not synced | Run Project-State Sync or regenerate graph |
| Business hallucination | Feature names invented from source paths | Mark business meaning UNKNOWN unless source-backed |
| Context bloat | Entire graph loaded for every task | Load only relevant subgraph for Context Pack |
