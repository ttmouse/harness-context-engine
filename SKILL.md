---
name: harness-context-engine
description: Generates, evaluates, syncs, and optimizes AI-agent harness context for software projects. Use when creating AGENTS.md, CONTEXT-MAP.md, .harness files, evaluating existing harness quality, syncing harness after project changes, creating task context packs, or reviewing harness diffs.
---

# Harness Context Engine

**Core principle:** harness context must be traceable, verifiable, and correctable — not just complete.

Harness context is for agent operation, not human documentation. Generate the smallest context-control system that helps an AI coding agent read the right context, respect project boundaries, verify work, and improve after failures.

---

## Capability Router

| User says | Capability | Read |
|---|---|---|
| generate harness / bootstrap | Generate | references/generate.md |
| build project profile / classify project | Project Profile | references/project-profile.md |
| check harness / evaluate harness | Evaluate | references/evaluate.md |
| sync harness with project / sync from diff | Project-State Sync | references/project-state-sync.md |
| publish harness / sync wiki | Publication Sync | references/publication-sync.md |
| create context pack | Context Pack | references/context-pack.md |
| run report / after task | Run Report | references/run-report.md |
| optimize harness | Optimize | references/optimize.md |
| review harness diff | Diff Review | references/diff-review.md |
| unclear domain / ADR / boundary claim | Grill Before Write | references/grill-before-write.md |

---

## Source and Confidence Rule（全局底层契约）

Every non-obvious claim must include:

- **source**: file path, config, command output, git diff, or explicit user context
- **confidence**: high / medium / low
- **type**: observed / inferred / unknown

**Rules**:
- Never present inferred as confirmed fact
- Never generate business rules / architecture decisions / commands without source
- Mark inferred: `INFERRED`, `LOW CONFIDENCE`, `NEEDS HUMAN REVIEW`
- See: references/source-confidence.md

---

## Global Non-negotiables

1. Do not invent project facts, commands, paths, business rules, or architecture decisions
2. Every non-obvious claim requires source + confidence + type
3. Generate must produce a Project Profile before writing harness files
4. Create context files lazily; do not create files only for structural completeness
5. Grill before write: unclear business/domain/architecture claims must be verified, questioned, or marked UNKNOWN
6. Keep AGENTS.md and generated context files short and task-useful
7. Prefer scripts for deterministic checks
8. Run Evaluate after Generate or Project-State Sync
9. Publication Sync is blocked if Evaluate has hard failures

---

## Required Generate Flow

```
Project Scan
  ↓
Project Profile
  ↓
Context Structure Choice
  ↓
Minimal Harness Generation
  ↓
Evaluate
```

Never jump directly from project scan to file generation. The Project Profile is the decision layer that prevents template-first harness generation.

---

## Lazy Creation Rule

Only create files that have a real job and evidence-backed content.

Do not create:

- formal ADRs without decision evidence
- domain.md without source-backed domain terms
- multi-context structures for simple projects
- local AGENTS.md without real independent subprojects
- known-risks.md without observed or explicitly provided risks
- empty TODO files merely to satisfy structure

Use UNKNOWN / NEEDS HUMAN REVIEW instead of filling blank sections with guesses.

---

## Utility Scripts

Run these for deterministic checks. See scripts/ directory.

| Script | What it checks |
|---|---|
| scripts/scan_project.py | Project structure, language, framework, package scripts, CI, monorepo clues — **implemented** |
| scripts/check_commands.py | Commands come from real config files — **implemented** |
| scripts/validate_context_map.py | CONTEXT-MAP references, MISSING_CONTEXT detection — **implemented** |
| scripts/check_paths.py | Harness-referenced paths exist in project — **partial** |
| scripts/validate_source_confidence.py | Key conclusions have source/confidence/type — **partial** |
| scripts/compare_harness_to_project.py | Project changes make harness stale — **partial** |
| scripts/validate_harness_diff.py | Harness changes do not weaken controls — **partial** |
| scripts/run_evals.py | Eval fixture integrity checks — **implemented** |
| scripts/check_skill_repo.py | Self-check: format, compile, fixtures — **implemented** |

---

## Context Layers

```
热（every task）:
  AGENTS.md, CONTEXT-MAP.md

温（by task type）:
  .harness/commands.md, .harness/task-workflow.md,
  .harness/working-boundaries.md, .harness/testing-and-verification.md

冷（on demand）:
  .harness/code-review.md, .harness/failure-analysis.md,
  .harness/known-risks.md, docs/adr/, docs/agents/
```

---

## Evals

Run with `skill-quality-evaluation`. See evals/evals.json and evals/fixtures/.

---

## Examples

Input/output examples for each capability. See examples/
