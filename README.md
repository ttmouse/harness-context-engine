# Harness Context Engine

AI agent harness context generation, evaluation, sync, and optimization skill for software projects.

---

## What Problem This Solves

When an AI coding agent starts working on a project without harness context, it may:

- invent commands that do not exist in `package.json`, `Makefile`, or CI workflows;
- miss files that are generated, sensitive, or off-limits;
- change high-impact project areas without approval;
- hallucinate business rules or architecture decisions from source-code naming alone;
- fail to verify work because it does not know the correct commands or acceptance path.

This skill generates and maintains **harness context** — a thin, verifiable layer of project truth — so agents know what to read, what they can change, what they must not touch, how to verify their work, and how to capture lessons from failures.

**Key distinction:** this is not a project documentation generator. It produces minimal, task-oriented context files that help an agent operate safely inside a project.

---

## Core Workflow

```text
Project Scan
  ↓
Project Profile
  ↓
Context Structure Choice
  ↓
Minimal Harness Generation
  ↓
Evaluate
  ↓
Context Pack / Project-State Sync / Run Report
```

The Project Profile is the decision layer between scan and generation. It prevents template-first harness generation by forcing the agent to record observed project facts, unknowns, confidence, and the reason for choosing single-context, sectioned-context, multi-context, or monorepo-context.

---

## What This Is Not

- **Not a README generator** — harness context is for agents, not for human onboarding.
- **Not a project documentation generator** — harness files are minimal and task-focused.
- **Not an ADR generator** — architecture decisions must have evidence; this skill does not invent ADRs to satisfy completeness.
- **Not a business rule extractor** — it does not auto-define business terms from source-code naming alone.
- **Not a knowledge base** — no generic patterns, no invented facts, no unverified claims.
- **Not a fact-fabricator** — unverified inferences are marked UNKNOWN, not presented as truth.

---

## Capability Status

| Capability | Status | Notes |
|---|---|---|
| **Generate** | partial | Workflow exists in `references/generate.md`; now requires Project Profile before writing files. |
| **Project Profile** | reference workflow | Defines the scan-to-generation decision artifact in `references/project-profile.md`. |
| **Grill Before Write** | reference workflow | Prevents weak inferences from becoming harness facts. See `references/grill-before-write.md`. |
| **Evaluate** | partial | Hard-fail rules defined in `references/evaluate.md`; core validation scripts exist but are incomplete. |
| **Project-State Sync** | partial | Workflow defined; stale detection and diff-based sync are not fully automated. |
| **Publication Sync** | planned / partial | Workflow defined in `references/publication-sync.md`; blocked by Evaluate completeness. |
| **Context Pack** | markdown workflow | Manual workflow only. Structure defined in `references/context-pack.md`. |
| **Run Report** | markdown workflow | Manual workflow only. Template defined in `references/run-report.md`. |
| **Optimize** | planned | Depends on collected failure records. |
| **Diff Review** | early prototype | `scripts/validate_harness_diff.py` exists but is regex-based and rough. |

**Note:** capabilities marked partial or planned should not be treated as production-ready. Human review is still required.

---

## Quick Start

```bash
# Generate harness for a project
hermes chat "generate harness for /path/to/project"

# Build only the Project Profile first
hermes chat "build project profile for /path/to/project"

# Evaluate existing harness quality
hermes chat "check harness for /path/to/project"

# Sync harness after project changes
hermes chat "sync harness with project /path/to/project"

# Create a task-specific context pack
hermes chat "create context pack for fixing login bug"
```

---

## File Structure

```text
harness-context-engine/
  SKILL.md
  README.md
  references/
    project-profile.md
    grill-before-write.md
    generate.md
    evaluate.md
    project-state-sync.md
    publication-sync.md
    context-pack.md
    run-report.md
    optimize.md
    diff-review.md
    source-confidence.md
    output-schemas.md
    templates.md
  scripts/
    scan_project.py
    check_paths.py
    check_commands.py
    validate_source_confidence.py
    compare_harness_to_project.py
    validate_context_map.py
    validate_harness_diff.py
    run_evals.py
    check_skill_repo.py
  evals/
    evals.json
    fixtures/
  examples/
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

| Script | Status | Notes |
|---|---|---|
| `scan_project.py` | partial | Basic scan works; broader CI, monorepo, and test-framework detection can improve. |
| `check_commands.py` | partial | Parses tables and code blocks; validates against package.json, Makefile, and CI workflows. |
| `validate_context_map.py` | partial | Detects missing references and supports MISSING_CONTEXT markers. |
| `check_paths.py` | stub/partial | Path parsing is rough. |
| `validate_source_confidence.py` | stub/partial | Needs stronger claim detection. |
| `compare_harness_to_project.py` | stub/partial | Needs better project-vs-harness stale detection. |
| `validate_harness_diff.py` | early prototype | Regex-based only. |
| `run_evals.py` | implemented static check | Verifies eval definitions and fixtures; does not call a model. |
| `check_skill_repo.py` | implemented static check | Checks repo format, fixtures, scripts, and structural issues. |

---

## Evals Status

- `evals/evals.json` exists with behavioral eval definitions.
- `evals/fixtures/` is populated with controlled fixture projects.
- `scripts/run_evals.py` performs static fixture and eval-definition checks.
- Full behavioral testing still requires a model-based `skill-quality-evaluation` run.

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

# Check eval fixture integrity
python scripts/run_evals.py

# Check this skill repository itself
python scripts/check_skill_repo.py
```

---

## Core Principle

**Harness context must be traceable, verifiable, and correctable — not just complete.**

Every non-obvious claim in generated harness files must include:

- **source**: file path, config, command output, git diff, or explicit user context;
- **confidence**: high / medium / low;
- **type**: observed / inferred / unknown.

Never present inferred as confirmed fact. Never generate business rules or architecture decisions without source.

---

## Two Rules That Prevent Template-First Harness

### 1. Create files lazily

Only create files that have a real job and evidence-backed content. Do not create ADRs, domain files, multi-context structures, local AGENTS.md files, or known-risk files only to make the tree look complete.

### 2. Grill before write

When domain language, architecture intent, boundaries, or project meaning are unclear, inspect code and existing context first. If evidence is insufficient, ask one targeted clarification question or mark UNKNOWN / NEEDS HUMAN REVIEW.
