# Harness Context Engine

AI agent harness context generation, evaluation, sync and optimization engine.

## Overview

This skill generates and maintains project harness context for AI coding agents. It ensures agents receive accurate, source-backed, task-appropriate context without hallucination.

## Capabilities

- **Generate**: Bootstrap harness from zero for new projects
- **Evaluate**: Assess harness quality (Hard Fail + Truth Check + Usability)
- **Project-State Sync**: Update harness after project code changes
- **Publication Sync**: Publish validated harness to external destinations
- **Context Pack**: Generate minimal task-specific context bundle
- **Optimize**: Reduce repeated agent failures based on failure records
- **Diff Review**: Reject harness changes that weaken control systems

## Quick Start

```
hermes chat "generate harness for /path/to/project"
hermes chat "check harness for /path/to/project"
hermes chat "sync harness with project /path/to/project"
```

## File Structure

```
harness-context-engine/
  SKILL.md              # Entry point + capability router
  references/            # Detailed workflows per capability
  scripts/              # Deterministic validation scripts
  evals/                # Skill self-test cases
  examples/             # Input/output examples
```
