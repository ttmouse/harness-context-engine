# Harness Context Engine

AI agent harness context generation, evaluation, sync and optimization engine.

---

## What Problem This Solves

When an AI coding agent starts working on a project without harness context, it:
- Invents commands that don't exist
- Doesn't know which files are critical
- Makes changes to high-risk areas without approval
- Hallucinates business rules or architecture decisions

This skill generates and maintains project harness context — a thin, verifiable layer of project truth — so agents work accurately.

---

## What This Is Not

- **Not a project documentation generator** — harness files are minimal, task-focused, not comprehensive
- **Not a knowledge base** — no generic patterns, no invented facts
- **Not a code explanation tool** — harness does not explain how code works, only what constraints and facts apply
- **Not a workflow enforcer** — agents may deviate; harness defines expectations, not rigid processes

---

## Capabilities

| Capability | Description | Status |
|---|---|---|
| **Generate** | Bootstrap harness from zero for new projects | Implemented |
| **Evaluate** | Assess harness quality: Hard Fail + Truth Check + Usability | Implemented |
| **Project-State Sync** | Update harness after project code changes | Implemented |
| **Publication Sync** | Publish validated harness to external destinations (Gitea wiki) | Implemented |
| **Context Pack** | Generate minimal task-specific context bundle | Implemented |
| **Run Report** | Summarize agent's harness usage after a task | Implemented |
| **Optimize** | Reduce repeated agent failures based on failure records | Stub (roadmap) |
| **Diff Review** | Reject harness changes that weaken control systems | Stub (roadmap) |

---

## Quick Start

```bash
hermes chat "generate harness for /path/to/project"
hermes chat "check harness for /path/to/project"
hermes chat "sync harness with project /path/to/project"
hermes chat "create context pack for fixing login bug"
```

---

## File Structure

```
harness-context-engine/
  SKILL.md              # Entry point + capability router
  README.md             # This file
  references/           # Detailed workflows per capability
    generate.md         # Bootstrap workflow
    evaluate.md         # Quality assessment
    project-state-sync.md
    publication-sync.md
    context-pack.md
    run-report.md
    optimize.md         # stub
    diff-review.md      # stub
    source-confidence.md
    output-schemas.md
    templates.md
  scripts/              # Deterministic validation scripts
    scan_project.py     # implemented
    check_paths.py      # stub
    check_commands.py   # implemented
    validate_source_confidence.py  # stub
    compare_harness_to_project.py  # stub
    validate_context_map.py        # implemented
    validate_harness_diff.py       # stub
  evals/                # Self-test cases (run with skill-quality-evaluation)
    evals.json
    fixtures/            # Test projects (P3: not yet populated)
  examples/             # Input/output examples per capability
```

---

## Scripts

Run deterministic checks on a generated harness. Scripts output structured JSON.

```bash
# Scan project structure
python scripts/scan_project.py /path/to/project

# Validate commands come from real config
python scripts/check_commands.py /path/to/harness /path/to/project

# Validate CONTEXT-MAP references exist
python scripts/validate_context_map.py /path/to/harness /path/to/project
```

All scripts output:
```json
{
  "status": "pass | fail | unknown",
  "errors": [],
  "warnings": [],
  "evidence": []
}
```

**Status values:**
- `pass`: All checks passed
- `fail`: Problems found
- `unknown`: Cannot determine (script requests human review)

---

## Evals

Evals verify this skill behaves correctly. Run with `skill-quality-evaluation`:

```
Load skill-quality-evaluation.
Run Path B behavioral test for harness-context-engine on task: generate harness for ~/Projects/components-demo
```

### Available Evals

| Name | Tests | Fixtures Needed |
|---|---|---|
| `generate_simple_project_harness` | Generate produces correct minimal harness | simple-react-project |
| `evaluate_fake_adr` | Evaluate rejects invented ADR | harness-with-fake-adr |
| `sync_new_route` | Sync detects new module | project-with-new-route |
| `create_context_pack_for_auth_bug` | Context pack for bug-fix task | — (uses WEB-share) |
| `review_harness_diff_weakened_boundary` | Diff review rejects loosened controls | harness-diff-weakened |

### Running Evals Manually

```bash
# From skill root
python scripts/scan_project.py ~/Projects/components-demo
python scripts/check_commands.py ~/Projects/XM/project/WEB-share ~/Projects/XM/project/WEB-share
python scripts/validate_context_map.py ~/Projects/XM/project/WEB-share ~/Projects/XM/project/WEB-share
```

---

## Core Principle

**Harness context must be traceable, verifiable, and correctable — not just complete.**

Every non-obvious claim in generated harness files must include:
- **source**: file path, config, command output, git diff, or explicit user context
- **confidence**: high / medium / low
- **type**: observed / inferred / unknown

Never present inferred as confirmed fact. Never generate business rules or architecture decisions without source.
