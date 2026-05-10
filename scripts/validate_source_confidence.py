#!/usr/bin/env python3
"""
Validate source/confidence coverage in key harness files.
Status: stub
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

def validate_source_confidence(project_path: str) -> dict:
    project = Path(project_path)
    issues = []

    def check_file(fp: Path):
        try:
            content = fp.read_text()
        except Exception:
            return

        # Look for key conclusion lines (nontrivial claims)
        lines = content.splitlines()
        in_table = False
        for i, line in enumerate(lines):
            if line.startswith("|"):
                in_table = True
                continue
            if not line.startswith("|") and in_table:
                in_table = False

            # Skip empty, headers, code blocks
            if not line.strip() or line.strip().startswith("#") or line.strip().startswith("```"):
                continue

            # Rough heuristic: lines containing business terms or high-confidence claims
            # that lack source annotation
            if any(kw in line.lower() for kw in ["risk", "architecture", "domain", "behavior", "auth", "permission"]):
                # Check if line has source/confidence markers
                has_source = any(m in line for m in ["source:", "Source:", "source=", "confidence:", "Confidence:"])
                has_table_source = " | " in line  # table row with cells

                if not has_source and not has_table_source:
                    issues.append({
                        "file": str(fp.relative_to(project)),
                        "line": i+1,
                        "content": line.strip()[:100],
                        "issue": "nontrivial claim without source/confidence"
                    })
        except Exception as e:
            issues.append({"file": str(fp), "error": str(e)})

    for pattern in FILES_TO_CHECK:
        for fp in project.glob(pattern):
            check_file(fp)

    return {
        "issues": issues,
        "status": "pass" if not issues else "fail"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_source_confidence.py /path/to/project")
        sys.exit(1)
    result = validate_source_confidence(sys.argv[1])
    print(json.dumps(result, indent=2))
