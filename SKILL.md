---
name: harness-context-engine
description: Generates, evaluates, syncs, and optimizes AI-agent harness context for software projects. Use when creating AGENTS.md, CONTEXT-MAP.md, .harness files, evaluating existing harness quality, syncing harness after project changes, creating task context packs, or reviewing harness diffs.
---

# Harness Context Engine

**Core principle:** harness context must be traceable, verifiable, and correctable — not just complete.

---

## Capability Router

| User says | Capability | Read |
|---|---|---|
| generate harness / bootstrap | Generate | references/generate.md |
| check harness / evaluate harness | Evaluate | references/evaluate.md |
| sync harness with project / sync from diff | Project-State Sync | references/project-state-sync.md |
| publish harness / sync wiki | Publication Sync | references/publication-sync.md |
| create context pack | Context Pack | references/context-pack.md |
| run report / after task | Run Report | references/run-report.md |
| optimize harness | Optimize | references/optimize.md |
| review harness diff | Diff Review | references/diff-review.md |

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
3. Keep AGENTS.md and generated context files short and task-useful
4. Prefer scripts for deterministic checks
5. Run Evaluate after Generate or Project-State Sync
6. Publication Sync is blocked if Evaluate has hard failures

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
