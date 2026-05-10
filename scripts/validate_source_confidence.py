#!/usr/bin/env python3
"""
Validate source/confidence coverage in key harness files.

Checks CONTEXT.md, docs/adr/*.md, .harness/known-risks.md,
.harness/working-boundaries.md, and docs/agents/domain.md for
non-trivial claims that lack source/confidence annotations.

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/validate_source_confidence.py /path/to/project
"""
import sys
import json
import re
from pathlib import Path

FILES_TO_CHECK = [
    "CONTEXT.md",
    "docs/contexts/*/CONTEXT.md",
    "docs/agents/domain.md",
    "docs/adr/*.md",
    ".harness/known-risks.md",
    ".harness/working-boundaries.md",
]

# Terms that indicate a non-trivial claim needing source annotation
CLAIM_TERMS = [
    "risk", "architecture", "domain", "behavior", "auth", "permission",
    "billing", "payment", "decision", "boundary", "workflow", "business",
    "purpose", "responsibility", "ownership", "deployment",
]


def validate_source_confidence(project_path: str) -> dict:
    project = Path(project_path)

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "issues": [],
        "files_checked": [],
        "files_with_issues": [],
    }

    if not project.is_dir():
        result["errors"].append(f"Project path does not exist: {project_path}")
        result["status"] = "fail"
        return result

    def check_file(fp: Path):
        """Check a single file for source/confidence issues."""
        try:
            content = fp.read_text()
        except Exception:
            result["warnings"].append(f"Cannot read {fp.relative_to(project)}")
            return

        rel_path = str(fp.relative_to(project))
        result["files_checked"].append(rel_path)
        lines = content.splitlines()
        local_issues = []
        in_code_block = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip code blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Skip headers, separators, empty lines, list markers
            if not stripped or stripped.startswith("#") or stripped.startswith("---"):
                continue
            if stripped.startswith("|") and stripped.endswith("|"):
                # Table row - skip if it has source/confidence columns
                continue

            # Check if line contains a non-trivial claim term
            has_claim_term = any(kw in stripped.lower() for kw in CLAIM_TERMS)
            if not has_claim_term:
                continue

            # Check if line has source/confidence annotation
            has_source = any(
                m in stripped.lower()
                for m in ["source:", "source=", "confidence:", "confidence="]
            )
            has_table_marker = " | " in stripped  # Could be table row
            has_unknown_marker = any(
                m in stripped.upper()
                for m in ["UNKNOWN", "TODO", "NEEDS HUMAN REVIEW", "LOW CONFIDENCE", "INFERRED"]
            )

            if not has_source and not has_table_marker and not has_unknown_marker:
                local_issues.append({
                    "file": rel_path,
                    "line": i + 1,
                    "content": stripped[:120],
                    "issue": "non-trivial claim without source/confidence annotation",
                })

        if local_issues:
            result["files_with_issues"].append(rel_path)
            result["issues"].extend(local_issues)

    # Check all glob patterns
    for pattern in FILES_TO_CHECK:
        for fp in project.glob(pattern):
            check_file(fp)

    result["evidence"].append({
        "source": "validate_source_confidence.py",
        "finding": (
            f"Checked {len(result['files_checked'])} files, "
            f"found {len(result['issues'])} issue(s) in {len(result['files_with_issues'])} file(s)"
        )
    })

    if result["issues"]:
        result["warnings"].append(
            f"{len(result['issues'])} non-trivial claim(s) lack source/confidence annotation"
        )
        result["status"] = "warning"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: validate_source_confidence.py /path/to/project"],
            "warnings": [],
            "evidence": [],
            "unknowns": [],
            "issues": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = validate_source_confidence(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
