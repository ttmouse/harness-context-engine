#!/usr/bin/env python3
"""
Check harness-referenced paths exist in project.

Scans all harness files (.harness/*.md, AGENTS.md, CONTEXT-MAP.md, CONTEXT.md)
and validates file paths referenced within them.

Outputs unified JSON with status, errors, warnings, evidence, unknowns.

Usage:
    python scripts/check_paths.py /path/to/project
"""
import sys
import json
import re
from pathlib import Path


def check_paths(project_path: str) -> dict:
    project = Path(project_path)

    result = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "evidence": [],
        "unknowns": [],
        "missing_paths": [],
        "existing_paths": [],
    }

    if not project.is_dir():
        result["errors"].append(f"Project path does not exist: {project_path}")
        result["status"] = "fail"
        return result

    # Find all harness files
    harness_files = (
        list(project.glob(".harness/*.md"))
        + list(project.glob("AGENTS.md"))
        + list(project.glob("CONTEXT-MAP.md"))
        + list(project.glob("CONTEXT.md"))
        + list(project.glob("docs/**/*.md"))
    )

    if not harness_files:
        result["warnings"].append(
            "No harness files found (.harness/*.md, AGENTS.md, CONTEXT-MAP.md, CONTEXT.md)"
        )
        result["status"] = "warning"
        return result

    result["evidence"].append({
        "source": "check_paths.py",
        "finding": f"Found {len(harness_files)} harness files to scan"
    })

    # Pattern to find file paths in markdown
    path_pattern = re.compile(
        r'[`"\']?((?:src|lib|app|docs|config|scripts|tests|public|\.harness|components|pages|routes)/'
        r'[a-zA-Z0-9_/\-.]*\.(?:tsx?|jsx?|py|json|ya?ml|toml|md|css|scss|less|html|env))[`"\']?'
    )

    missing_count = 0
    existing_count = 0

    for hf in harness_files:
        try:
            content = hf.read_text()
        except Exception:
            result["warnings"].append(f"Cannot read {hf.relative_to(project)}")
            continue

        for match in path_pattern.finditer(content):
            path_str = match.group(1)

            # Resolve relative to project
            resolved = project / path_str

            if not resolved.exists():
                result["missing_paths"].append({
                    "file": str(hf.relative_to(project)),
                    "path": path_str,
                })
                missing_count += 1
            else:
                if existing_count < 50:  # Cap for readability
                    result["existing_paths"].append({
                        "file": str(hf.relative_to(project)),
                        "path": path_str,
                    })
                existing_count += 1

    result["evidence"].append({
        "source": "check_paths.py",
        "finding": f"Found {existing_count} existing paths, {missing_count} missing paths"
    })

    if missing_count > 0:
        result["errors"].append(f"{missing_count} referenced path(s) do not exist in project")
        result["status"] = "fail"

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "fail",
            "errors": ["Usage: check_paths.py /path/to/project"],
            "warnings": [],
            "evidence": [],
            "unknowns": [],
            "missing_paths": [],
            "existing_paths": [],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = check_paths(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
