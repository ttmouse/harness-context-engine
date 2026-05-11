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

### Core Loop

```
Project Scan  →  Project Profile  →  Harness Generation  →  Evaluate
      ↑                                                         │
      │                                                         ▼
  Run Report / Optimize  ←  Project-State Sync  ←  Context Pack
```

- **Project Scan** gathers facts from code structure, configs, and scripts
- **Project Profile** is a judgment artifact that prevents template-driven generation
- **Harness Generation** follows Lazy Creation rules — only files with content
- **Evaluate** validates the harness with Hard Fail rules
- **Context Pack** loads only relevant context for a specific task
- **Project-State Sync** updates harness after code changes
- **Run Report / Optimize** capture failures and prevent repeats

---

## What This Is Not

- **Not a README generator** — harness context is for agents, not for human onboarding
- **Not a project documentation generator** — harness files are minimal and task-focused
- **Not an ADR generator** — architecture decisions must have evidence; ADR is created only when all three criteria are met (hard to reverse, surprising without context, real trade-off)
- **Not a business rule extractor** — does not auto-define business terms from source-code naming alone; always marks inferred terms as INFERRED
- **Not a knowledge base** — no generic patterns, no invented facts, no unverified claims
- **Not a code explanation tool** — harness does not explain how code works, only what constraints and facts apply
- **Not a workflow enforcer** — agents may deviate; harness defines expectations, not rigid processes
- **Not a "fill everything in one file" tool** — harness is split into focused files by concern
- **Not a fact-fabricator** — unverified inferences are marked UNKNOWN, not presented as truth
- **Not a template filler** — Generate does not create files for structural completeness; files are created lazily only when content exists

---

## Capability Status

| Capability | Status | Notes |
|---|---|---|
| **Generate** | partial | Workflow updated: Project Profile + Lazy Creation + Grill Before Write. `references/generate.md` restructured. New `references/project-profile.md`, `references/grill-before-write.md`. Script infrastructure partially implemented. Format validation incomplete. |
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
  references/             # Detailed workflow references per capability
    generate.md         # Bootstrap workflow (with Project Profile + Lazy Creation rules)
    project-profile.md  # Intermediate judgment artifact: scan→profile→generate
    grill-before-write.md # Business term verification before writing
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

- `evals/evals.json` exists with 7 eval definitions
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
| `generate_then_context_pack` | Generate → Context Pack for bug-fix task; uses generated CONTEXT-MAP, flags auth/routing risk | `fixtures/project-with-new-route` |
| `sync_then_task` | Project-State Sync → Reports route task; detects missing route, does not invent business meaning | `fixtures/project-with-new-route` |

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

---

## Key Concepts

### Project Profile (Pre-Generation Judgment)

[Project Profile](references/project-profile.md) is an intermediate artifact produced after scanning the project and before generating harness files. It captures:

- Project type, stack, structure, and commands with evidence levels
- Risk areas with source-backed confidence
- Context structure recommendation (single/sectioned/multi/monorepo)
- Evidence table for every non-obvious claim

**Why it matters:** Prevents template-driven generation. Without it, Generate guesses project facts and writes them as truth.

### Lazy Creation

Files are created **only when content exists**, not for structural completeness. Key rules:

- No ADR file without a real decision (hard to reverse, surprising, real trade-off)
- No domain.md without source-backed domain terms
- No known-risks.md without observed or user-provided risks
- No multi-context structure unless complexity requires it
- UNKNOWN is the correct state; do not create empty TODO files

**Why it matters:** Empty files with fillers become fake context. Agents read them and act on false information.

### Grill Before Write

When business language, architecture intent, ownership boundary, or risk meaning is unclear, follow this order:

1. Inspect code first
2. Check existing harness/context
3. Ask one targeted question (if code doesn't answer)
4. Mark UNKNOWN if no answer
5. Surface conflicts explicitly (don't pick sides)

**Why it matters:** A wrong fact in harness is worse than UNKNOWN. Wrong facts mislead every subsequent agent task.

See [references/grill-before-write.md](references/grill-before-write.md) for full process and conflict output format.
