#!/usr/bin/env python3
"""
Validate harness diff does not weaken control systems.

Detects patterns like "Requires Approval" moved to "Allowed",
verification requirements removed, Hard Fail rules deleted,
and command status falsification.

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/validate_harness_diff.py /path/to/project [diff_file]
"""
import sys
import json
import re
from pathlib import Path

WEAKENING_PATTERNS = [
    (re.compile(r"Requires Approval.*?Allowed", re.DOTALL),
     "Requires Approval moved to Allowed — control weakened"),
    (re.compile(r"verification.*?removed", re.IGNORECASE | re.DOTALL),
     "Verification requirement removed"),
    (re.compile(r"Hard Fail.*?removed", re.IGNORECASE | re.DOTALL),
     "Hard Fail rule removed"),
    (re.compile(r"Source.*?Confidence.*?removed", re.IGNORECASE | re.DOTALL),
     "Source/Confidence requirement removed"),
    (re.compile(r"UNKNOWN.*?replaced", re.IGNORECASE | re.DOTALL),
     "UNKNOWN marker replaced with fake data"),
    (re.compile(r"approval.*?not.*?required", re.IGNORECASE | re.DOTALL),
     "Approval requirement removed"),
    (re.compile(r"\+\s*-.*?Requires Approval", re.DOTALL),
     "Requires Approval item deleted"),
    (re.compile(r"unverified.*?verified", re.IGNORECASE | re.DOTALL),
     "Command status changed from unverified to verified without evidence"),
]


def validate_harness_diff(project_path: str, diff_text: str = None) -> dict:
    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "violations": [],
    }

    project = Path(project_path)
    if not project.is_dir():
        result["errors"].append(f"Project path does not exist: {project_path}")
        result["status"] = "fail"
        return result

    if diff_text is None:
        # Read from git diff
        import subprocess
        try:
            proc = subprocess.run(
                ["git", "diff", "--no-color"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            diff_text = proc.stdout
        except FileNotFoundError:
            result["errors"].append("git not found in PATH")
            result["status"] = "fail"
            return result
        except subprocess.TimeoutExpired:
            result["errors"].append("git diff timed out")
            result["status"] = "unknown"
            return result
        except Exception as e:
            result["errors"].append(f"Could not get git diff: {e}")
            result["status"] = "unknown"
            return result

    if not diff_text or not diff_text.strip():
        result["warnings"].append("Diff is empty or no harness files changed")
        result["status"] = "warning"
        return result

    # Filter to only harness-related files
    harness_patterns = [
        "AGENTS.md", "CONTEXT-MAP.md", "CONTEXT.md",
        ".harness/", "docs/adr/", "docs/agents/",
    ]
    relevant_lines = []
    in_relevant_file = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            in_relevant_file = any(p in line for p in harness_patterns)
        if in_relevant_file:
            relevant_lines.append(line)

    if not relevant_lines:
        result["warnings"].append("No harness files changed in diff")
        result["status"] = "warning"
        return result

    result["evidence"].append({
        "source": "git diff",
        "finding": f"Found {len(relevant_lines)} relevant diff lines (harness files only)"
    })

    filtered_diff = "\n".join(relevant_lines)

    # Check each weakening pattern
    for pattern, description in WEAKENING_PATTERNS:
        matches = pattern.findall(filtered_diff)
        if matches:
            # Get context around each match
            for m in re.finditer(pattern, filtered_diff):
                start = max(0, m.start() - 60)
                end = min(len(filtered_diff), m.end() + 60)
                context = filtered_diff[start:end].replace("\n", " | ")
                result["violations"].append({
                    "rule": description,
                    "context": context[:200],
                })

    if result["violations"]:
        result["errors"].append(
            f"Found {len(result['violations'])} weakening violation(s) — diff rejected"
        )
        result["status"] = "fail"

    result["evidence"].append({
        "source": "validate_harness_diff.py",
        "finding": f"Found {len(result['violations'])} violation(s) in diff"
    })

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: validate_harness_diff.py /path/to/project [diff_file]"],
            "warnings": [],
            "evidence": [],
            "unknowns": [],
            "violations": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    diff_text = None
    if len(sys.argv) > 2:
        diff_file = Path(sys.argv[2])
        if diff_file.exists():
            diff_text = diff_file.read_text()

    result = validate_harness_diff(sys.argv[1], diff_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
