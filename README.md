# Harness Context Engine

AI agent harness context generation, evaluation, sync, and optimization skill for software projects.

---

## What Problem This Solves

When an AI coding agent starts working on a project without harness context, it:

- Invents commands that don't exist in `package.json`, `Makefile`, or CI workflows
- Doesn't know which files are critical, which are generated, and which are off-limits
- Makes changes to high-risk areas (auth, billing, data) without approval
- Hallucinates business rules or architecture decisions from source-code naming alone
- Cannot verify its own output because it doesn't know the correct verification commands

This skill generates and maintains **harness context** — a thin, verifiable layer of project truth — so agents know what to read, what they can change, what they cannot touch, how to verify their work, and how to capture lessons from failures.

**Key distinction:** This is not a project documentation generator. It produces minimal, task-oriented context files (AGENTS.md, CONTEXT-MAP.md, `.harness/` files) that an agent reads before starting work. The goal is to make agent behavior accurate and safe, not to document the project for humans.

---

## What This Is Not

- **Not a README generator** — harness context is for agents, not for human onboarding
- **Not a project documentation generator** — harness files are minimal and task-focused
- **Not an ADR generator** — architecture decisions must have evidence; this skill does not invent ADRs to satisfy completeness
- **Not a business rule extractor** — does not auto-define business terms from source-code naming alone
- **Not a knowledge base** — no generic patterns, no invented facts, no unverified claims
- **Not a code explanation tool** — harness does not explain how code works, only what constraints and facts apply
- **Not a workflow enforcer** — agents may deviate; harness defines expectations, not rigid processes
- **Not a "fill everything in one file" tool** — harness is split into focused files by concern
- **Not a fact-fabricator** — unverified inferences are marked UNKNOWN, not presented as truth

---

## Capability Status

| Capability | Status | Notes |
|---|---|---|
| **Generate** | partial | Workflow exists in `references/generate.md`. Script infrastructure partially implemented. Format needs validation. |
| **Evaluate** | partial | Hard-fail rules defined in `references/evaluate.md`. Core validation scripts exist but are incomplete. |
| **Project-State Sync** | partial | Workflow defined. Stale detection and diff-based sync not fully automated. |
| **Publication Sync** | planned / partial | Workflow defined in `references/publication-sync.md`. Blocked by Evaluate completeness. |
| **Context Pack** | markdown workflow | Manual workflow only. No automation script yet. Structure defined in `references/context-pack.md`. |
| **Run Report** | markdown workflow | Manual workflow only. Template defined in `references/run-report.md`. |
| **Optimize** | planned | Depends on collected failure records. No implementation. |
| **Diff Review** | early prototype | `scripts/validate_harness_diff.py` exists but is regex-based and rough. |

**Note:** All capabilities marked "partial" or "planned" should not be treated as production-ready. Each may produce incorrect results without human review.

---

## Quick Start

```bash
# Generate harness for a project
hermes chat "generate harness for /path/to/project"

# Evaluate existing harness quality
hermes chat "check harness for /path/to/project"

# Sync harness after project changes
hermes chat "sync harness with project /path/to/project"

# Create a task-specific context pack
hermes chat "create context pack for fixing login bug"
```

---

## File Structure

```
harness-context-engine/
  SKILL.md              # Entry point + capability router
  README.md             # This file
  references/           # Detailed workflow references per capability
    generate.md         # Bootstrap workflow
    evaluate.md         # Three-layer evaluation (Hard Fail + Truth Check + Usability)
    project-state-sync.md
    publication-sync.md
    context-pack.md
    run-report.md
    optimize.md         # stub
    diff-review.md      # early prototype
    source-confidence.md
    output-schemas.md
    templates.md
  scripts/              # Deterministic validation scripts (see Scripts Status)
    scan_project.py
    check_paths.py
    check_commands.py
    validate_source_confidence.py
    compare_harness_to_project.py
    validate_context_map.py
    validate_harness_diff.py
  evals/                # Self-test cases
    evals.json
    fixtures/           # Test project fixtures for eval scenarios
  examples/             # Input/output examples per capability
```

---

## Scripts Status

All scripts are in `scripts/`. Scripts output structured JSON with a unified format:

```json
{
  "status": "pass | fail | warning | unknown",
  "errors": [],
  "warnings": [],
  "evidence": [],
  "unknowns": []
}
```

| Script | Status | Problem |
|---|---|---|
| `scan_project.py` | partial | Basic scan works. Missing: CI recognition, monorepo detection, test config detection, more framework options. Output format needs update to unified schema. |
| `check_commands.py` | partial | Can parse code blocks and tables. Does not handle all edge cases. Unknown commands not always flagged correctly. |
| `validate_context_map.py` | partial | Detects missing references. Does not properly distinguish explicitly marked `MISSING_CONTEXT` from unmarked missing references. |
| `check_paths.py` | stub/partial | Path parsing is rough. Only handles basic patterns. |
| `validate_source_confidence.py` | stub | Exists but lacks robust source/confidence claim detection. |
| `compare_harness_to_project.py` | stub | Exists but lacks proper diff comparison logic. |
| `validate_harness_diff.py` | early prototype | Regex-based only. Cannot parse semantic diff content. |

---

## Evals Status

- `evals/evals.json` exists with 5 eval definitions
- Each eval declares `fixtures_needed` and `fixture_path`
- Currently **no fixtures are populated** — they are declared in `evals.json` but the directories `evals/fixtures/` are empty
- No automated eval runner script exists yet
- Current evals are **definitions, not runnable tests** — they describe expected behavior but cannot be executed programmatically

### Defined Evals

| Name | Tests | Fixtures Needed |
|---|---|---|
| `generate_simple_project_harness` | Generate produces correct minimal harness | `fixtures/simple-react-project` |
| `evaluate_fake_adr` | Evaluate rejects invented ADR | `fixtures/harness-with-fake-adr` |
| `sync_new_route` | Sync detects new module/route | `fixtures/project-with-new-route` |
| `create_context_pack_for_auth_bug` | Context pack for bug-fix task | `fixtures/simple-react-project` |
| `review_harness_diff_weakened_boundary` | Diff review rejects loosened controls | `fixtures/harness-diff-weakened` |

See `evals/README.md` for detailed verification procedures.

---

## Running Scripts Manually

```bash
# Scan project structure
python scripts/scan_project.py /path/to/project

# Validate commands come from real config
python scripts/check_commands.py /path/to/harness /path/to/project

# Validate CONTEXT-MAP references exist
python scripts/validate_context_map.py /path/to/harness [/path/to/project]
```

---

## Core Principle

**Harness context must be traceable, verifiable, and correctable — not just complete.**

Every non-obvious claim in generated harness files must include:

- **source**: file path, config, command output, git diff, or explicit user context
- **confidence**: high / medium / low
- **type**: observed / inferred / unknown

Never present inferred as confirmed fact. Never generate business rules or architecture decisions without source.
